"""
Methods for computing the distances.
Behavioral distance: the values of flow and speed are scaled to [0,1], to give both the same weight
used Manhattan for both

Spatio-temporal distance: the units are meters and minutes with the same weight.

@author Fabio Quattrini
"""

import numpy as np


def behavioral_distance(alpha_b, p, o):
    """
    Computes the Behavioral distance of point p wrt point o
    :param alpha_b: array of weights for the behavioral features
    :param p: datapoint p, [id, timestamp, behavioral_attribute1, behavioral_attribute2 ...]
    :param o: datapoint o, [id, timestamp, behavioral_attribute1, behavioral_attribute2 ...]
    :return: the behavioral distance
    """

    behavioral_distance_ = np.dot(np.abs(p[2:] - o[2:]), alpha_b) + 1e-10

    return behavioral_distance_


def st_distance(p, o, pairwise_sd, beta_s, gamma_t):
    """
    Spatio-Temporal distance of a sensor p with respect to a sensor o
    :param p: datapoint p, [id, timestamp, behavioral_attribute1, behavioral_attribute2 ...]
    :param o: datapoint o, [id, timestamp, behavioral_attribute1, behavioral_attribute2 ...]
    :param pairwise_sd: precomputed spatial distances of the sensors
    :param beta_s: weights for the spatial attributes
    :param gamma_t: weights for the temporal attributes
    :return: float, distance
    """

    spatial_distance_ = spatial_distance(p, o, pairwise_sd)
    temporal_distance_ = temporal_distance(p, o)

    # Combining the distances with their weights
    spatioTemporal_distance = beta_s * spatial_distance_ + gamma_t * temporal_distance_

    return spatioTemporal_distance


def temporal_distance(p, o):
    """
    Computes the temporal distance in minutes
    :param p: first datapoint [id, timestamp, behavioral_attribute1, behavioral_attribute2 ...]
    :param o: second datapoint
    :return: the difference in seconds
    """
    datetime_p = p[1]
    datetime_o = o[1]

    if datetime_o < datetime_p:
        temporal_distance_ = (datetime_p - datetime_o)
    else:
        temporal_distance_ = (datetime_o - datetime_p)

    return temporal_distance_ / 60


def spatial_distance(p, o, pairwise_sd):
    """
    Retrieves the spatial distance in meters between two sensors
    :param p: first datapoint [id, timestamp, behavioral_attribute1, behavioral_attribute2 ...]
    :param o: second datapoint [id, timestamp, behavioral_attribute1, behavioral_attribute2 ...]
    :param pairwise_sd: symmetric matrix encoding the distances
    :return: the spatial distance
    """

    id1 = int(p[0])
    id2 = int(o[0])
    sp_distance_ = pairwise_sd[id1, id2]

    # The distances are in meters
    return sp_distance_
