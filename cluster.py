"""
Main
@author Fabio Quattrini
"""

import pandas as pd
import time
from datetime import datetime
import numpy as np
from sklearn import preprocessing
import argparse
import datetime as dt

import STBOF
import STBDBCAN


def cluster():
    # ------------ Retrieving Parameters ------------

    parser = argparse.ArgumentParser(description='Spatio-Temporal Behavioral Density-based Clustering of Applications '
                                                 'with Noise (ST-BDBCAN) using Spatio-Temporal Behavioral Outlier '
                                                 'Factor (ST-BOF)')
    parser.add_argument('-d', '--distances', type=str, help="File with pairwise distances (.csv).", required=True)
    parser.add_argument('-f', '--file', type=str, help="Dataset (.csv).", required=True)
    parser.add_argument('-b', '--behavioral', type=str, nargs='+', help='Names of Behavioral attributes', required=True)

    parser.add_argument('-minPts', type=int, help='Number of neighboring points considered for ST-BOF', required=True)
    parser.add_argument('-k', type=int, help='Rank of neighbor used to define the k-distance', required=True)
    parser.add_argument('-pct', type=float, help='Percentage of variation accepted in ST-Behavioral Reachable Density',
                        required=True)
    parser.add_argument('-stbdbcan_minPts', type=int, help='Number of neighboring points considered for ST-BDBCAN',
                        required=True)
    parser.add_argument('-minPts_cluster', type=int, help='Minimum cluster cardinality', required=True)

    parser.add_argument('-bw', '--bweights', nargs='+', type=float, help='Behavioral attributes Weights',
                        required=False)
    parser.add_argument('-mnp', '--minNoisePercentage', type=float, help='Minimum % of noise points expected',
                        default=1, required=False)
    parser.add_argument('-sw', '--sweights', type=float, help='Spatial attributes Weights', default=1, required=False)
    parser.add_argument('-tw', '--tweights', type=float, help='Temporal attribute Weights', default=1, required=False)
    parser.add_argument('-t', '--temporal', type=str, help="Name of sensor for temporal mode", required=False)
    args = parser.parse_args()

    distances_file = args.distances
    data_file = args.file
    behavioral_attributes = args.behavioral
    id_temporal = args.temporal
    min_noise_percentage = args.minNoisePercentage
    beta_s = args.sweights
    gamma_t = args.tweights

    if args.bweights is not None:
        if len(args.bweights) != len(args.behavioral):
            raise ValueError("The number of behavioral features and behavioral weights must be equal")
        alpha_b = args.bweights
    else:
        alpha_b = np.ones(len(args.behavioral))

    minPts = args.minPts
    k = args.k
    pct = args.pct
    stbdbcan_minPts = args.stbdbcan_minPts
    minPts_cluster = args.minPts_cluster

    # ------------ Load and preprocess Pairwise Distances ------------

    # Distances file format: id1, id2, dist
    # Loading and preparing the data
    spatial_distances = pd.read_csv(distances_file)
    # Substitution of the labels with numerical IDs
    le = preprocessing.LabelEncoder()
    le.fit(spatial_distances['id1'])
    spatial_distances['id1'] = le.transform(spatial_distances['id1'])
    spatial_distances['id2'] = le.transform(spatial_distances['id2'])
    # ST-BOF uses a numpy array that contains in position [id1, id2] the distance of entity id1 and id2
    spatial_distances_np = spatial_distances.pivot(index='id1', columns='id2', values='dist').fillna(0).to_numpy()
    spatial_distances_np += spatial_distances_np.transpose()

    # ------------ Load and preprocess the Dataset ------------

    # Dataset tuples structure: [id, datetime, behavioral_attribute1, behavioral_attribute2 ...]
    # Loading and preparing the observations
    data = pd.read_csv(data_file)
    # data = data[:400]

    # If temporal mode is selected select the specified entity
    if id_temporal is not None:
        data = data[data['id'] == id_temporal]

    data['id'] = le.transform(data['id'])

    # Scale the values from 0 to 1, to equally weight flow and speed
    min_max_scaler = preprocessing.MinMaxScaler()
    data[behavioral_attributes] = min_max_scaler.fit_transform(data[behavioral_attributes])

    # Converting the time column from datetime to epoch
    data['time'] = (pd.to_datetime(data['time']) - dt.datetime(1970, 1, 1)).dt.total_seconds()

    # ------------ ST-BOF ------------

    stbof = STBOF.STBOF(data=data, min_pts=minPts, k=k, spatial_distances=spatial_distances_np,
                        alpha_b=alpha_b, beta_s=beta_s, gamma_t=gamma_t)

    # String containing a duplicate of the screen output to be saved in a txt file
    r = ''
    msg = ""
    if id_temporal is not None:
        msg = "Temporal mode selected, analyzing entity {}\n".format(id_temporal)
    msg += "Using " + str(len(data)) + " points\nDistance functions features weights: Spatial: " + str(beta_s) + \
          ", Temporal: " + str(gamma_t) + ", Behavioral: " + str(alpha_b) + "\nComputing ST-Behavioral Outlier Factor\n"
    msg += "Parameters: minPts={}, k={}".format(minPts, k)
    print(msg)
    r += msg + "\n"

    start = datetime.now()
    stbof.fit_predict()
    msg = "Done. Elapsed time: {} \n------------------------------------------------".format(datetime.now() - start)
    print(msg)
    r += msg + "\n"

    # ------------ ST-BDBCAN ------------

    # Computing the ST-BOF Upper Bound, over which a point is termed as a spatio-temporal outlier
    # The upper bound is set as the ST-BOF of the specified percentile (1-percentile point by default)
    st_bofub_index = round(len(data) * min_noise_percentage / 100)
    st_bofub = np.sort(stbof.outlier_factor_)[-st_bofub_index]

    msg = "Setting the ST-BOFUB as the ST-BOF of point {}, Minimum Noise Percentage = {}%\nCurrent ST-BOFUB = {}" \
          "\nComputing ST-BDBCAN...\nParameters: ST-BOFUB={}, pct={}, BDBCAN_minPts={}, minPts_cluster={}".format(
           st_bofub_index, min_noise_percentage, st_bofub, st_bofub, pct, stbdbcan_minPts, minPts_cluster)
    print(msg)
    r += msg + "\n"

    # Sleep used to stabilize the progress bar inside STBDBCAN
    time.sleep(2)
    start = datetime.now()
    stbdbcan = STBDBCAN.STBDBCAN(data=data, st_bofub=st_bofub, pct=pct, stbdbcan_minPts=stbdbcan_minPts,
                                 minPts_cluster=minPts_cluster, stbof=stbof, spatial_distances=spatial_distances_np,
                                 beta_s=1, gamma_t=1)
    stbdbcan.cluster()

    noise_pts_number = len(stbdbcan.labels_[stbdbcan.labels_ == -1])
    msg = "Done. Elapsed time: {}\n------------------------------------------------\nNumber of clusters = {}\n" \
          "Unclassified: {}\nNoise:{}\n------------\nPercentage of noise points = {}".format(
        datetime.now() - start, np.max(stbdbcan.labels_), len(stbdbcan.labels_[stbdbcan.labels_ == -2]),
        noise_pts_number, noise_pts_number * 100 / len(data))

    print(msg)
    r += msg + "\n"

    # ------------ Reverting back the preprocessing and saving results ------------
    data['id'] = le.inverse_transform(data['id'])
    data[behavioral_attributes] = min_max_scaler.inverse_transform(data[behavioral_attributes])
    data["time"] = pd.to_datetime(data["time"], unit='s')
    data["clusterID"] = stbdbcan.labels_
    to_save_fileName = data_file[:-4] + "_results"
    if id_temporal is not None:
        to_save_fileName += "_{}".format(id_temporal)
    data.to_csv(to_save_fileName + ".csv", index=False)

    text_file = open(to_save_fileName + ".txt", "w")
    text_file.write(r)
    text_file.close()


if __name__ == '__main__':
    cluster()
