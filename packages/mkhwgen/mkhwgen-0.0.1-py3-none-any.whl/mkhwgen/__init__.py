# wgen 모형 상수
import datetime
import random
from itertools import groupby
import numpy as np
from dateutil.rrule import DAILY, rrule

np.seterr(divide='ignore')

ma = np.array([0.793829301403771, 0.08391540308836, 0.521425037422897, 0.00])
mb = np.array([0.07690527017422, 0.840595387409395, 0.0667184295637582, 0.428752436555732])
param = {
    'dry': {
        'trend_nor_mean': {
            'tmax': {
                'a': -0.157304725787696,
                'b': 1.48869472867181,
                'c': 4.6958058788417,
                'd': 406.886309998549,
            },
            'tmin': {
                'a': -0.00394997401492529,
                'b': 1.40791160427342,
                'c': 4.30750058421063,
                'd': 366.859340500296,
            },
        },
        'trend_nor_std': {
            'tmax': {
                'a': -0.0283527221692006,
                'b': -1.04426786280185,
                'c': 3.73017205722288,
                'd': 334.704415386978,
            },
            'tmin': {
                'a': 0.0377287542392459,
                'b': -0.904508859101637,
                'c': 4.26790279881636,
                'd': 363.922581738313,
            },
        },
        'trend_mean': {
            'tmax': {
                'mean': 0,  # not used
                'std': 9.05669788790852,
            },
            'tmin': {
                'mean': 0,  # not used
                'std': 9.34792793190601,
            },
        },
        'trend_std': {
            'tmax': {
                'mean': 3.06748595641587,
                'std': 0.849787354651005,
            },
            'tmin': {
                'mean': 2.73551943730644,
                'std': 0.729960713557897,
            },
        },
    },
    'wet': {
        'trend_nor_mean': {
            'tmax': {
                'a': -0.0911059856205227,
                'b': 1.43147122410071,
                'c': 4.51310628089473,
                'd': 390.80229865128,
            },
            'tmin': {
                'a': -0.0162999813609278,
                'b': 1.40298104832027,
                'c': 4.30969353717956,
                'd': 370.074143483734,
            },
        },
        'trend_nor_std': {
            'tmax': {
                'a': 0.0832602260921684,
                'b': -0.307941530917107,
                'c': 4.59057144349635,
                'd': 393.812223275959,
            },
            'tmin': {
                'a': 0.226730275363952,
                'b': -1.06770961172921,
                'c': 4.77593982659491,
                'd': 426.925696696405,
            },
        },
        'trend_mean': {
            'tmax': {
                'mean': 0,  # not used
                'std': 8.17314848092467,
            },
            'tmin': {
                'mean': 0,  # not used
                'std': 8.59389351476127,
            },
        },
        'trend_std': {
            'tmax': {
                'mean': 2.99301775933085,
                'std': 1.01339096230845,
            },
            'tmin': {
                'mean': 2.55486596660728,
                'std': 1.09737347903176,
            },
        },
    },
}

def temperature_part(condition, jday, trend_mean_tmin_mean, trend_mean_tmax_mean, old_tmin, old_tmax):
    #
    #  mean 계열의 계산
    #
    a = param[condition]['trend_nor_mean']['tmax']['a']
    b = param[condition]['trend_nor_mean']['tmax']['b']
    c = param[condition]['trend_nor_mean']['tmax']['c']
    d = param[condition]['trend_nor_mean']['tmax']['d']
    tmax = a + b * np.sin(2 * np.pi * jday / d + c)

    a = param[condition]['trend_nor_mean']['tmin']['a']
    b = param[condition]['trend_nor_mean']['tmin']['b']
    c = param[condition]['trend_nor_mean']['tmin']['c']
    d = param[condition]['trend_nor_mean']['tmin']['d']
    tmin = a + b * np.sin(2 * np.pi * jday / d + c)

    tmax = param[condition]['trend_mean']['tmax']['std'] * tmax + trend_mean_tmax_mean
    tmin = param[condition]['trend_mean']['tmin']['std'] * tmin + trend_mean_tmin_mean

    generated_tmax = tmax
    generated_tmin = tmin

    #
    #  std 계열의 계산
    #
    tmax = random.gauss(0, param[condition]['trend_nor_mean']['tmax']['b'])
    tmin = random.gauss(0, param[condition]['trend_nor_mean']['tmin']['b'])

    tmax = np.sum(np.array([old_tmax, old_tmin, tmax, tmin]) * ma)
    tmin = np.sum(np.array([old_tmax, old_tmin, tmax, tmin]) * mb)

    old_tmin = tmin
    old_tmax = tmax

    m = param[condition]['trend_std']['tmax']['mean']
    s = param[condition]['trend_std']['tmax']['std']
    a = param[condition]['trend_nor_std']['tmax']['a']
    b = param[condition]['trend_nor_std']['tmax']['b']
    c = param[condition]['trend_nor_std']['tmax']['c']
    d = param[condition]['trend_nor_std']['tmax']['d']
    tmax *= m + s * (a + b * np.sin(2 * np.pi * jday / d + c))

    m = param[condition]['trend_std']['tmin']['mean']
    s = param[condition]['trend_std']['tmin']['std']
    a = param[condition]['trend_nor_std']['tmin']['a']
    b = param[condition]['trend_nor_std']['tmin']['b']
    c = param[condition]['trend_nor_std']['tmin']['c']
    d = param[condition]['trend_nor_std']['tmin']['d']
    tmin *= m + s * (a + b * np.sin(2 * np.pi * jday / d + c))

    generated_tmax += tmax
    generated_tmin += tmin

    return generated_tmin, generated_tmax, old_tmin, old_tmax

def rain_part(rr, old_rain_total):
    pwd = 0.75 * (0.000881 * rr + 0.1988)
    pww = 0.25 + pwd
    log = np.maximum(rr, 0)
    d_rain = 1.4478 * log * log - 5.9353 * log + 7.99
    beta = 0.5212 * np.exp(0.7792 * log)
    alpha = d_rain / beta

    rain_total = 0
    if old_rain_total > 0 and pww >= random.random():
        rain_total = 1
    if old_rain_total == 0 and pwd >= random.random():
        rain_total += 1

    # 평년 월강수량이 0인 격자는 추정 강수량도 0으로 지정함
    gamma = random.gammavariate(alpha, beta)
    if rain_total > 0 and log != 0:
        generated_rain = gamma
    else:
        generated_rain = 0

    return generated_rain, rain_total


def wgen(year, monthly_tmin, monthly_tmax, monthly_rain):
    results = []

    # 평년 월평균 자료의 연평균자료를 만듦
    tmin_mean = np.mean(monthly_tmin)
    dry_tmin_mean = tmin_mean * 1.0415 - 0.7219
    wet_tmin_mean = tmin_mean * 0.9324 + 1.7066

    # 평년 월평균 자료의 연평균자료를 만듦
    tmax_mean = np.mean(monthly_tmax)
    dry_tmax_mean = tmax_mean * 0.9505 + 1.5332
    wet_tmax_mean = tmax_mean * 1.0408 - 1.9851

    monthly_rain = np.maximum(monthly_rain, 0)

    # time-series variation의 초기값은 난수를 이용함
    old_tmax = random.random()
    old_tmin = random.random()
    # 강우발생 관련 배열(rain_total)의 초기값은 0으로 함
    old_rain_total = 0.
    
    begin = datetime.date(year, 1, 1)
    until = datetime.date(year, 12, 31)
    dates = rrule(DAILY, begin, until=until)
    monthly_dates = groupby(dates, key=lambda x: x.month)

    # 월별(1-12)로 처리함
    for month, dates in monthly_dates:
        dates = list(dates)
        nn = monthly_tmin[month - 1]
        xx = monthly_tmax[month - 1]
        rr = monthly_rain[month - 1]

        tmax_ary = np.empty(len(dates))
        tmin_ary = np.empty(len(dates))
        rain_ary = np.empty(len(dates))

        # 일별로 처리함
        for i, current_date in enumerate(dates):
            jday = current_date.timetuple().tm_yday

            generated_rain, old_rain_total = rain_part(rr, old_rain_total)

            if old_rain_total >= 1:
                generated_tmin, generated_tmax, old_tmin, old_tmax = temperature_part('wet', jday, wet_tmin_mean, wet_tmax_mean, old_tmin, old_tmax)
            else:
                generated_tmin, generated_tmax, old_tmin, old_tmax = temperature_part('dry', jday, dry_tmin_mean, dry_tmax_mean, old_tmin, old_tmax)

            tmax_ary[i] = generated_tmax
            tmin_ary[i] = generated_tmin
            rain_ary[i] = generated_rain

        tmax_ary += (xx - np.mean(tmax_ary))
        tmin_ary += (nn - np.mean(tmin_ary))
        rain_ary *= (rr / np.sum(rain_ary))

        rain_ary[np.isinf(rain_ary)] = 0

        for i, (tmin, tmax, rain) in enumerate(zip(tmin_ary, tmax_ary, rain_ary)):
            results.append([
                i,
                round(tmin, 1),
                round(tmax, 1),
                round(rain, 1)
            ])

    return results


def generate(year, repeat, *, monthly_tmin, monthly_tmax, monthly_rain, rand_seed=None):
    random.seed(rand_seed)

    results = []

    for i in range(repeat):
      generated_weather = wgen(year, monthly_tmin, monthly_tmax, monthly_rain)
      results.extend([i, *x] for x in generated_weather)

    return results
