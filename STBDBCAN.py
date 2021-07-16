"""
Spatio-Temporal Behavioral Density Based Clustering of Application with Noise (ST-BDBCAN)

@author Fabio Quattrini
"""

import numpy as np
from tqdm import tqdm

from sklearn.neighbors import NearestNeighbors
import distances


class STBDBCAN:
    """
    Perform ST-BDBCAN clustering from a set of points

    Parameters
    ---------
    data: Dataframe
        Dataset of points

    st_bofub:
        Spatio-Temporal Behavioral Outlier Factor Upper Bound

    pct:
        Percentage of variation in ST-BRD when checking for the spatio-temporal direct behavioral reachability
        of one point with another point

    stbdbcan_minPts : int, default = 10
        Minimum number of spatio-temporal neighborhood points to be considered

    minPts_cluster:
        Minimum number of points in a cluster

    stbof: STBOF object
        Object in charge of computing the ST-BOF of the points

    Attributes
    ----------
    neighbors_indices_: ndarray of shape (n_points, stbdbcan_minPts)
        Contains for each point (row) the indexes of its neighbors.

    labels_: ndarray of shape (n_points)
        Cluster labels for each point in the data.
        Label -1 is for NOISE samples and label -2 for UNCLASSIFIED samples

    """

    def __init__(self, data, st_bofub, pct, stbdbcan_minPts, minPts_cluster, stbof, spatial_distances, beta_s, gamma_t):
        """

        Parameters
        ----------
        data: pd dataframe
        st_bofub: float
        pct: float
        stbdbcan_minPts: int
        minPts_cluster: int
        stbof: STBOF class
        spatial_distances: numpy square array
        beta_s: int
        gamma_t: int
        """
        self.data = data
        self.st_bofub = st_bofub
        self.pct = pct
        self.stbdbcan_minPts = stbdbcan_minPts
        self.minPts_cluster = minPts_cluster
        self.stbof = stbof

        # Initially all samples are unclassified.
        self.labels_ = np.full(shape=(len(self.data),), fill_value=-2, dtype=np.intp)
        self.neighbors_indices_ = np.ndarray(shape=(len(data), self.stbdbcan_minPts))

        # Sets up the objects for finding neighbors
        metric_params = {"pairwise_sd": spatial_distances, "beta_s": beta_s, "gamma_t": gamma_t}
        self.neighs = NearestNeighbors(n_neighbors=stbdbcan_minPts + 1, algorithm='auto', metric=distances.st_distance,
                                       metric_params=metric_params)

        self.neighs.fit(self.data)

    def cluster(self):
        """
        Perform ST-BDBCAN clustering
        """

        # ID of the current cluster
        clusterID = 0

        # Remember: the ST-BOF and ST-BRD of each point is already computed by ST-BOF class

        # Outer loop responsible to pick new seed points (points from which to grow a new cluster)
        # Once a seed point is found, a new cluster is created and it is grown by the "expandCluster" method
        # If from the seed point is not possible to create a cluster then it is classified as noise
        for i in tqdm(range(0, len(self.data))):

            # Only unclassified points can be seed points
            if self.labels_[i] == -2:
                if self.stbof.outlier_factor_[i] <= self.st_bofub:
                    if self.expand_cluster(i, clusterID):
                        clusterID += 1
                else:
                    # The current point is noise
                    self.labels_[i] = -1

        return 1

    def expand_cluster(self, p_index, clusterID):
        """
        Assign the point p to a st behavioral based cluster and performs a regional query to retrieve the st neighbours
        :param p_index: the index of the point p in the data
        :param clusterID: the ID of the current cluster
        :return:
        """

        # Assign the cluster label to the seed point
        self.labels_[p_index] = clusterID

        seeds = self.neighs.kneighbors(self.data.iloc[p_index].values.reshape(1, -1), return_distance=False)[0, 1:]
        temp_cluster_indexes = []

        # Evaluate if the neighbours of the original seed point may be part of its cluster
        for curr_point in seeds:
            if self.labels_[curr_point] == -2 or self.labels_[curr_point] == -1:
                if self.st_dbr(curr_point, p_index):
                    if self.stbof.outlier_factor_[curr_point] <= self.st_bofub:
                        temp_cluster_indexes.append(curr_point)

        if len(temp_cluster_indexes) < self.minPts_cluster:
            # If the candidate cluster has not enough points, label the original seed point as noise
            self.labels_[p_index] = -1
            return False

        for temp_point_index in temp_cluster_indexes:
            self.labels_[temp_point_index] = clusterID

            _, temp_point_neigh_indexes = self.neighs.kneighbors(self.data.iloc[temp_point_index].values.reshape(1, -1))
            temp_point_neigh_indexes = temp_point_neigh_indexes[0, 1:]

            for temp_point_neigh_index in temp_point_neigh_indexes:
                if self.labels_[temp_point_neigh_index] == -2 or self.labels_[temp_point_neigh_index] == -1:
                    if self.st_dbr(temp_point_neigh_index, temp_point_index):
                        if self.stbof.outlier_factor_[temp_point_neigh_index] <= self.st_bofub:
                            if temp_point_neigh_index not in temp_cluster_indexes:
                                temp_cluster_indexes.append(temp_point_neigh_index)
        return True

    def st_dbr(self, p_index, o_index):
        """
        Function to compute Spatio-Temporal Direct Behavioral Reachability
        :param p_index: index of current point
        :param o_index: index of other point
        :return: bool
        """

        if self.stbof.stbrd_[p_index] > (self.stbof.stbrd_[o_index] / (1 + self.pct)):
            if self.stbof.stbrd_[p_index] < (self.stbof.stbrd_[o_index] * (1 + self.pct)):
                return True
        else:
            return False
