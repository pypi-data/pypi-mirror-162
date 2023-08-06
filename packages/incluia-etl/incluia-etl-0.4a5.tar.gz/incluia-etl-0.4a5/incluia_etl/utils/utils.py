import datetime
import random
import re

import boto3
import numpy as np
import shapely

s3_client = boto3.client('s3')


def hour_to_day_period(h=None):
    """
    Simple function that returns the following mapping:
    0 if current hor between [0, 5]
    1 if current hor between [6, 11]
    2 if current hor between [12, 17]
    3 if current hor between [18, 23]
    The output is an index of an array of floats, that represent
    parameters of a distribution (mean and var)
    that can modify the request frequency.
    """
    hour_periods = np.array([6, 12, 18, 24])
    hour_periods_condition = hour_periods - 1
    if h <= hour_periods_condition[0]:
        index = 0
    elif h <= hour_periods_condition[1]:
        index = 1
    elif h <= hour_periods_condition[2]:
        index = 2
    else:
        index = 3
    return index


def smooth_request_transition(current_hour=None, vector_schedule=None):
    """
    To make the transition frequency smooth we redefine the var and mean
    statistics when they are close to the change of period.
    This transition occurs within the previous hour before the change.
    """

    hour_periods = np.array([6, 12, 18, 24])
    hour_periods_condition = hour_periods - 1  # hours before a transition of frequency

    current_minute = datetime.datetime.now().minute

    i = hour_to_day_period(current_hour)  # compute current index i
    statistic = vector_schedule[i]
    if current_hour in hour_periods_condition:
        # from the vector schedule, keep the current statistic and the next.
        i_next = (i + 1) % 4
        current_stat = vector_schedule[i]
        next_stat = vector_schedule[i_next]

        # define a random variable that as minutes goes by, it approaches to 1.
        time_ratio = random.uniform(current_minute, 60) / 60
        # define a statistic that approaches to statistic_max as time goes by
        # and such that its domain is between current_stat and next_stat
        statistic = (1 - time_ratio) * current_stat + time_ratio * next_stat

    return statistic


def latency_param(latency_init=None, latency_final=None, n_days=None, start_date=None):
    """
    Changes the latency parameter smoothly.
    latency_init: float. The initial latency of requests.
    latency_final: float. The final latency of requests.
    n_days: integer. Days transcurred to reach from
    latency_init to latency_final
    start_date : str. Starting date written as Y-m-d, example 2021-01-15
    """
    start_date_datetime = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    days_transcurred = (datetime.datetime.now() - start_date_datetime).days
    slope = (latency_final - latency_init) / n_days
    latency = slope * days_transcurred + latency_init
    latency = max([latency, latency_final])
    return latency


def autolabel(rects=None, ax=None):
    """
    Attach a text label above each bar in *rects*, displaying its height.
    """
    for rect in rects:
        height = rect.get_height()
        ax.annotate(
            '{}'.format(height) + ' %',
            xy=(rect.get_x() + rect.get_width() / 2, height),
            xytext=(0, 3),
            textcoords="offset points",
            ha='center',
            va='bottom',
        )


def reduce_precision_geom(x, n: int):
    """
    Rounds Geometry column precision to n digits.
    """
    out = shapely.wkt.loads(shapely.wkt.dumps(x, rounding_precision=n))
    return out
