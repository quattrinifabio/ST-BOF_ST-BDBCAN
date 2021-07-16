# ST-BOF_ST-BDBCAN
Spatio-Temporal Behavioral Outlier Factor (ST-BOF) and Spatio-Temporal Behavioral Density-based Clustering of Applications with Noise (ST-BDBCAN) implementation in Python.

This approach starts by dividing the attributes of the data in two categories: 

1. Contextual attributes: define the “location” of the data, either spatial or temporal.
2. Behavioral attributes: describe the features of an instance.

The code is composed by two main algorithms: 

1. ST-BOF: measures the outlierness of an object with respect to its behavioral attributes, using the neighborhood defined by the spatio-temporal attributes.
2. ST-BDBCAN: detects outliers by grouping objects with similar behavioral attributes as clusters and identifies objects with abnormal behavioral attributes as outliers based on their spatiotemporal locality. Thus, given an instance, this algorithm uses the spatio-temporal attributes to identify its neighborhood and the behavioral attributes to analyse the data.

As distance metric it is used a weighted Manhattan distance, where the weights are 1 by default but can be explicitly modified by the user.

The code is able to perform clustering of a dataset of spatio-temporal located entities, and with the optional parameter -t it is possible to make it run considering just one of these, ignoring the neighbors.

# Input

The program requires two files as input, both in csv format:

- Distances: file containing the distances between the locations, with structure [id1, id2, dist], with id1 < id2.
- Dataset: file containing the data to be clustered, with structure [id, timestamp, behavioral_feature1, behavioral_feature2]

# Output

The program generates two output files:

- A txt with the run details.
- A copy of the original dataset with a new column called clusterID, containing for each tuple the ID of the assigned cluster (the points classified as noise are assigned to the cluster -1).

# Usage

To start the program run cluster.py

```
Usage: cluster.py [PARAMETERS]

  Clusterize Spatio-Temporal data using ST-BOF and ST-BDBCAN. 

Parameters:
  -d --distances FILE  			File with pairwise distances (.csv).
  -f --file FILE              	Dataset (.csv).
  -b --behavioral             	Names of Behavioral attributes.
  -minPts               	  	Number of neighboring points considered for ST-BOF.
  -k            			  	Rank of neighbor used to define the k-distance.
  -pct              			Percentage of variation accepted in ST-Behavioral Reachable Density.
  -stbdbcan_minPts             	Number of neighboring points considered for ST-BDBCAN.
  -minPts_cluster               Minimum cluster cardinality.

  -bw --bweights              	Behavioral attributes Weights [optional, default 1].
  -sw --sweights             	Spatial attributes Weights [optional, default 1].
  -tw --tweights  				Temporal attribute Weights [optional, default 1].
  -t --temporal                 Name of sensor for temporal run mode [optional].

```

# References

@article{ST-BDBCAN,
author = {Duggimpudi, Maria Bala and Abbady, Shaaban and Chen, Jian and Raghavan, Vijay},
year = {2019},
month = {07},
pages = {1-24},
title = {Spatio-Temporal Outlier Detection Algorithms Based on Computing Behavioral Outlierness Factor},
volume = {122},
journal = {Data \& Knowledge Engineering},
doi = {10.1016/j.datak.2017.12.001}
}
