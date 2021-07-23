# ST-BOF_ST-BDBCAN
Spatio-Temporal Behavioral Outlier Factor (ST-BOF) and Spatio-Temporal Behavioral Density-based Clustering of Applications with Noise (ST-BDBCAN) implementation in Python.

From now on the document uses the following naming conventions: 

- *Data*: the dataset to be clustered.
- *Entity*: a unique entity with an associated temporal series and a location in the space, identified in the data by a unique id (numeric or literal). In the provided demo an entity corresponds to a traffic sensor.

This approach starts by dividing the attributes of the data in two categories: 

1. **Contextual attributes**: define the spatio-temporal “location” of the data.
2. **Behavioral attributes**: describe the features of an instance. For example, in our demo they are the traffic flow and the speed of the vehicles.

The code is composed by two main algorithms: 

1. ***ST-BOF***: measures the outlierness of an observation with respect to its behavioral attributes, using the neighborhood defined by the spatio-temporal attributes. This outlier factor is less 1 when an observation has behavioral attributes similar to the ones of the neighbors, and greater than 1 when they are different.
2. ***ST-BDBCAN***: detects outliers by grouping observations with similar behavioral attributes as clusters and identifies observations with abnormal behavioral attributes as outliers based on their spatiotemporal locality. Thus, given an instance, this algorithm uses the spatio-temporal attributes to identify its neighborhood and the behavioral attributes to analyze the data. The points that can’t be assigned to any cluster are labelled as noise.

As distance metric it is used a weighted Manhattan distance, where the weights are 1 by default but can be explicitly modified by the user.

The code is able to perform clustering of a dataset of spatio-temporal located entities, thus considering for each observation the closest spatio-temporal neighbors.

With the optional parameter -t [entity_id] it is possible to run the computation considering just one entity, filtering out and ignoring all spatial neighboring datapoints and treating observations of the entity as a temporal series. 

# Input

The program requires two files as input, both in csv format:

- <u>Distances</u>: file containing the distances between the locations, with structure *[id1, id2, dist]*, with id1 < id2.
- <u>Dataset</u>: file containing the data to be clustered, with structure *[id, timestamp, behavioral_feature1, behavioral_feature2]*.

# Output

The program generates two output files:

- A copy of the original dataset with a new column called *clusterID*, containing for each tuple the ID of the assigned cluster (the points classified as noise are assigned to the cluster -1).
- A text file with the run details.

# Usage

To start the program run *cluster.py*

```
Usage: python cluster.py [PARAMETERS]

  Clusterize Spatio-Temporal data using ST-BOF and ST-BDBCAN. 

Parameters:
  -d --distances FILE           File with pairwise distances (.csv).
  -f --file FILE                Dataset (.csv).
  -b --behavioral               Names of Behavioral attributes.
  -minPts                       Number of neighboring points considered for ST-BOF.
  -k                            Rank of neighbor used to define the k-distance.
  -pct                          Percentage of accepted variation in ST-Behavioral Reachable Density.
  -stbdbcan_minPts              Number of neighboring points considered for ST-BDBCAN.
  -minPts_cluster               Minimum cluster cardinality.

  -mnp --minNoisePercentage     Minimum percentage of noise points expected [optional, default 1]
  -bw --bweights                Behavioral attributes Weights [optional, default 1].
  -sw --sweights                Spatial attributes Weights [optional, default 1].
  -tw --tweights                Temporal attribute Weights [optional, default 1].
  -t --temporal                 Name of the entity for temporal run mode [optional].
```

# Demos

In the folder demos are provided two examples of program runs, one considering the dataset as a spatio-temporal series and the  other considering only one sensor, thus ignoring the neighbors.

The demos are performed on traffic data, captured by several sensors distributed in the city of Modena, Italy. The dataset contains 13349 observations given by the aggregated readings of traffic flow (the number of vehicles) and mean speed (in km/h), every 15 minutes, from the 25th of April, 2019 to the 27th of April, 2019. The file demo_spatial_distances.csv contains the spatial distances between the sensors, in meters.

## Spatio-Temporal Clustering

To run the program the command is:

```
python cluster.py -d demos/demo_spatial_distances.csv -f demos/sensor_traffic_observations.csv -b sum_flow avg_speed -minPts 20 -k 4 -pct 0.2 -stbdbcan_minPts 20 -minPts_cluster 5
```

To specify the optional parameters:

```
python cluster.py -d demos/demo_spatial_distances.csv -f demos/sensor_traffic_observations.csv -b sum_flow avg_speed -minPts 20 -k 4 -pct 0.2 -stbdbcan_minPts 20 -minPts_cluster 5 -mnp 1 -bw 1 1 -sw 1 -tw 1
```

The run (which takes some minutes) produces the two output files *sensor_traffic_observations_results.csv* and *sensor_traffic_observations_results.txt*. The datapoints are divided in 32 clusters, with a 2% percentage of anomalies and a ST-BOFUB = 2.05. The following image contains a visualization of the datapoints colored by their assigned cluster id:

```
![alt text](https://github.com/quattrinifabio/ST-BOF_ST-BDBCAN/blob/master/images/spatio_temporal_clusters.png)
```

<img src="(https://github.com/quattrinifabio/ST-BOF_ST-BDBCAN/blob/master/images/spatio_temporal_clusters.png?raw=true" style="zoom: 67%;" />

This figure shows the same datapoints, colored with yellow if they are classified as anomalies and by violet otherwise:

<img src="https://raw.githubusercontent.com/quattrinifabio/ST-BOF_ST-BDBCAN/blob/master/images/spatio_temporal_anomalies.png?raw=true" style="zoom: 67%;" />

## Temporal Clustering

The same code with the addition of -t [sensor_id] tells the program to ignore all other sensors and consider only the temporal series of the specified sensor_id, composed by 288 observations.

Tu run the demo:

```
python cluster.py -d demos/demo_spatial_distances.csv -f demos/sensor_traffic_observations.csv -b sum_flow avg_speed -minPts 20 -k 4 -pct 0.2 -stbdbcan_minPts 20 -minPts_cluster 5 -t R002_S2
```

To specify the optional parameters:

```
python cluster.py -d demos/demo_spatial_distances.csv -f demos/sensor_traffic_observations.csv -b sum_flow avg_speed -minPts 20 -k 4 -pct 0.2 -stbdbcan_minPts 20 -minPts_cluster 5 -t R002_S2 -mnp 1 -bw 1 1 -sw 1 -tw 1
```

The running produces the two output files *sensor_traffic_observations_results_R002_S2.csv* and *sensor_traffic_observations_results_R002_S2.txt*. The datapoints are divided in 3 clusters, with a 9.4% percentage of anomalies and a ST-BOFUB = 3.4. 

The image contains a graphic visualization of the results, with the points colored by their cluster id and the anomalies in orange:

<img src="https://raw.githubusercontent.com/quattrinifabio/ST-BOF_ST-BDBCAN/blob/master/images/temporal_result_flow.png?raw=true" style="zoom: 80%;" />

<img src="https://raw.githubusercontent.com/quattrinifabio/ST-BOF_ST-BDBCAN/blob/master/images/temporal_result_speed.png?raw=true" style="zoom: 80%;" />

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
