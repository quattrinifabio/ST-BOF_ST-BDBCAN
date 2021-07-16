"""
Spatio-Temporal Behavioral Outlier Factor (ST-BOF) implementation for traffic sensors

@author Fabio Quattrini
"""

import numpy as np
from sklearn.neighbors import NearestNeighbors
import distances


class STBOF:
    """
    The Spatio-Temporal Behavioral Outlier Factor measures the outlierness of an object only with respect to its
    behavioral attributes and spatio spatio-temporal attributes are used as the contextual attributes (to define
    the neighborhood).

    It measures the local deviation of density (in behavioral attributes) in a given sample with respect to its
    spatio-temporal neighbors. The locality is given by k-nearest neighbors.

    Parameters
    ---------
    data: pandas dataframe with shape (id, datetime, behavioral_attribute1, behavioral_attribute2 ...)
        Dataset.

    k : positive int
        Number of neighbors used to define the k-distance, usually in the range from 3 to 9.

    min_pts: positive int
        Number of neighbors considered for the density, usually in the range from 10 to 45.

    spatial_distances: numpy array
        The spatial distances for all the points.

    alpha_b: array of positive int, default=1
        Specifies the weights for the behavioral attributes.

    beta_s: positive int, default=1
        Weight for spatial attributes.

    gamma_t: positive int, default=1
        Weight for temporal attributes.

    Attributes
    ----------
    outlier_factor_: ndarray of shape (n_points)
        The ST-BOF of the samples. This factor reveals the extent to which p is similar (<1) or different (>1) in its
        behavior w.r.t its spatio-temporal neighbors.

        It is the average of the ratios of the spatio-temporal reachability density of a point and those of its
        minPts-nearest neighbors.

    neighbors_indices_: ndarray of shape (n_points, minPts)
        Contains for each point (row) the indexes of its neighbors.

    neighbors_distances_: ndarray of shape (n_points, minPts)
        Contains for each point (row) the st distances of its neighbors.

    neighbors_behavioral_distances_: ndarray of shape (n_points, minPts)
        Contains for each point (row) the behavioral distances of its neighbors.

    stbrd_: ndarray of shape (n_points)

    """

    def __init__(self, data, min_pts, k, spatial_distances, alpha_b, beta_s, gamma_t):
        """

        Parameters
        ----------
        data: pd Dataframe
        min_pts: int
        k: int
        spatial_distances: numpy square array
        alpha_b: list
        beta_s: int
        gamma_t: int
        """
        self.data = data
        self.k = k
        self.minPts = min_pts
        self.spatial_distances = spatial_distances
        self.alpha_b = alpha_b
        self.beta_s = beta_s
        self.gamma_t = gamma_t

        self.outlier_factor_ = np.zeros(len(data))
        self.stbrd_ = np.zeros(len(data))
        self.neighbors_indices_ = np.ndarray(shape=(len(data), self.minPts))
        self.neighbors_distances_ = np.ndarray(shape=(len(data), self.minPts))
        self.neighbors_behavioral_distances_ = np.ndarray(shape=(len(data), self.minPts))

    def fit_predict(self):
        """
        Fits the model to the data, computing the outlier score for all the points.
        :return: ndarray with the outlier factors
        """

        self.neighbors_indices_, self.neighbors_distances_ = self.find_neighbors(self.minPts)
        self.compute_neighbors_behavioral_distances(self.neighbors_indices_)

        # Computes the behavioral reachable distances of each point (the firsts in every row) wrt their neighbours
        behavioral_reach_dist_k_ = self.behavioral_reach_dist_k(self.neighbors_indices_)
        self.stbrd_ = np.average(behavioral_reach_dist_k_, axis=1)
        self.stbrd_ = np.power(self.stbrd_, -1)

        # Each row contains the ratios of the st-brd of p to p's min_pts nearest spatio temporal neighbors
        st_brd_ratios = (self.stbrd_[self.neighbors_indices_] / self.stbrd_[:, np.newaxis])

        # The ST-BOF is the average of the ratios
        self.outlier_factor_ = np.average(st_brd_ratios, axis=1)

    def find_neighbors(self, pts):

        metric_params = {"pairwise_sd": self.spatial_distances, "beta_s": self.beta_s, "gamma_t": self.gamma_t}
        neighs = NearestNeighbors(n_neighbors=pts + 1, algorithm='auto', metric=distances.st_distance,
                                  metric_params=metric_params)

        neighs.fit(self.data)
        neighbors_distances_, neighbors_indices_ = neighs.kneighbors(self.data)

        return neighbors_indices_[:, 1:], neighbors_distances_[:, 1:]

    def behavioral_reach_dist_k(self, neigh_indices):

        behavioral_distances_k = self.neighbors_behavioral_distances_[neigh_indices, self.k - 1]
        behavioral_reach_dist_k = np.maximum(self.neighbors_behavioral_distances_, behavioral_distances_k)
        return behavioral_reach_dist_k

    def compute_neighbors_behavioral_distances(self, neigh_indices):
        for row_index, row in enumerate(neigh_indices):
            p = self.data.iloc[row_index]
            for col_index, col in enumerate(row):
                self.neighbors_behavioral_distances_[row_index][col_index] = \
                    distances.behavioral_distance(self.alpha_b, p, self.data.iloc[col])
