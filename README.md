# DataNet API Documentation

- [DataNet API Documentation](#datanet-api-documentation)
  - [1 Introduction](#1-introduction)
  - [2 How does it work?](#2-how-does-it-work)
  - [3 How to use the API](#3-how-to-use-the-api)
  - [4 Structure of a Sample object](#4-structure-of-a-sample-object)
    - [4.1 Parameters of time distributions](#41-parameters-of-time-distributions)
    - [4.2 Parameters of packet size distributions](#42-parameters-of-packet-size-distributions)
    - [4.3 List of node parameters for topology\_object](#43-list-of-node-parameters-for-topology_object)
    - [4.4 List of link parameters for topology\_object](#44-list-of-link-parameters-for-topology_object)
    - [4.5 List of node parameters for physical\_topology\_object](#45-list-of-node-parameters-for-physical_topology_object)
    - [4.6 List of link parameters for physical\_topology\_object](#46-list-of-link-parameters-for-physical_topology_object)
  - [5 API methods to read information from a Sample object](#5-api-methods-to-read-information-from-a-sample-object)
  - [Credits](#credits)


## 1 Introduction
This Python API is intended to provide users with a simple and intuitive way to access the information contained in the associated datasets. Following a user-oriented approach, the API aims to abstract users from the internal details of our datasets, thus making much easier extracting the information.

This version is associated to the datasets of the Graph Neural Networking challenge 2023. You can find more information about this competition at the following links:

https://bnn.upc.edu/challenge/gnnet2023

https://bnn.upc.edu/challenge/gnnet2023/dataset

## 2 How does it work?

Beyond the complex structure of the datasets, which include many files distributed in different directories, this API provides sequentially samples (one at a time) structured in a user-friendly way. 

Two main components can be distinguished to understand how to use this API: (i) the iterator, and (ii) a sample instance. The iterator is in charge of reading and processing a sample from the dataset, while a sample is an object produced by the iterator that contains all the information of a sample in a well-structured manner.

## 3 How to use the API

We provide below a simple code snippet to initialize the iterator object of the API and obtain sequentially samples from the dataset:

````python
import datanetAPI
reader = datanetAPI.DatanetAPI(<pathToDataset >, [shuffle])
it = iter(reader)
for sample in it:
  <process sample code>
````

First of all, the user needs to download and import this Python library (line 1). Then, an instance of `datanetAPI` can be initialized (line 2), where `pathToDataset` should point to the root directory of the dataset to be processed. *Note that this dataset should be uncompressed in advance*. Finally, `shuffle` is a boolean that by default is 'false' and indicates if the sample files should be shuffled before being processed. Afterwards, the iterator object can be created (line 3).
Once the iterator object is created, samples can be sequentially extracted using a “for” loop (line 4). 

Alternatively, the next(it) method can be used to read only the next sample. This enables, for instance, read only “n” samples from the dataset using:

````python
for i in range(n):
    sample = next(it)
````
The DatanetAPI object also provides the following methods:
* `reader.get_available_files()`: Return a list of all the dataset files located in the <pathToDataset> directory which is specified in the initialization of the object and its subdirectories. Each element of the list is a tuple containing the path of the file and the file itself.
* `reader.set_files_to_process(tuple_list)`: Specify a sublist of files to be processed by the iterator. The files should be a subset of the files obtained with get_available_files(). This function should always be used before creating the iterator.

The next section describes in detail all the information that a sample object contains and some methods to extract it.

## 4 Structure of a Sample object

This section describes how the data is structured within a sample object.

Every sample is a container including information about: (i) a network topology, (ii) parameters used to generate the traffic in our testbed, (iii) a physical path and routing configuration, (iv) some metrics (delay, jitter and loss) measured in our testbed resulting from the network configuration (i.e., topology + traffic distribution + routing) and (v) object with packets per flow information. All this information is provided for every source-destination pair of the network.

*Note*: we consider only a path connecting every source-destination (src-dst) pair, however there can be one or more flows traversing the same src-dst path. If there are more than one flows, performance measurements can be individually obtained for each. 

Specifically, every sample instance is comprised by multiple attributes, all of which can be accessed through getter methods (e.g., the *global_packets* can be obtained through `sample.get_global_packets()`). The included attributes are as follows:

* *global_packets*: Number of packets transmitted in the network per seconds (packets/seconds).
* *global_losses*: Packets lost in the network per seconds (packets/seconds).
* *global_delay*: Average per-packet delay over all the packets transmitted in the network (seconds).
* *max_link_load*: This variable is used to define the maximum link load when generating the traffic matrix of the scenario. It is an indicator of the load of the network. The higher the number, more loaded the network is. 
* *performance_matrix*: Matrix with aggregate src-dst and flow-level performance measurements (delay, jitter and loss) measured on each src-dst pair (see more details below). 
* *traffic_matrix*: Matrix with the time and size distributions used to generate traffic for each src-dst pair (see more details below). 
* *routing_matrix*: Matrix with the list of routers used to connect every src-dst pair (see more details below).
* *physical_path_matrix*: Matrix with the list of ports used to interconnect every src-dst pair (see more details below).
* *topology_object*: It uses a Graph object from the Networkx library including topology-related information at the node and link-level (see more details below).
* *physical_topology_object*: It uses a Graph object from the Networkx library describing the physical interconnection  between  traffic generators, routers and switches. (see more details below).
* *pkts_info*: Matrix with information of all packets generated for each src-dst pair (see more details below).

**performance_matrix**: This is a matrix that indexes performance measurements at the level of src-dst pairs. Particularly, it considers that more than one flow can be exchanged on each src-dst pair. Hence, it provides performance measurements at two levels of granularity: (i) for all aggregate flows on each src-dst pair, and (ii) for every flow individually. Every element of this matrix (i.e., `performance_matrix[src,dst]`) contains a dictionary with the following keys: 
* ‘AggInfo’: dictionary with performance measurements for all aggregate flows between a specific [src,dst] pair. 
  * ‘PktsDrop’: packets dropped per seconds over the path [src,dst]. (packets/second)
  * ‘AvgDelay’: average per-packet delay over the packets transmitted on path [src,dst] (seconds)
  * ‘AvgLnDelay’: average of the natural logarithm of the per-packet delay over the all packets transmitted on path [src, dst]. 
  * ‘p10Delay’, ‘p20Delay’, ‘p50Delay’, ‘p80Delay’, ‘p90Delay’: percentiles (10, 20, 50, 80, and 90) of the per-packet delay distribution on path [src,dst]. (seconds)
  * ‘Jitter’: Variance of the per-packet delay over the packets transmitted on path [src,dst]. This is var(packet_delay)
* ‘Flows’: List of dictionaries with performance measurements for each flow between node i and node j. Flows on each src-dst pair are indexed by a numerical ID (e.g., `performance_matrix[0,1]['Flows'][0]`). Note that all the flows of a src-dst pair follow the same path but may have different traffic distributions, thereby performance may vary between them. Each flow contains the following keys:
  * ‘PktsDrop’: packets dropped per seconds on the flow. (packets/second)
  * ‘AvgDelay’: average per-packet delay on the flow. (seconds) 
  * ‘AvgLnDelay’: average of the natural logarithm of the per-packet delay over the all packets transmitted on the flow. i.e., “avg(ln(packet_delay))”
  * ‘p10Delay’, ‘p20Delay’, ‘p50Delay’, ‘p80Delay’, ‘p90Delay’: percentiles (10, 20, 50, 80, and 90) of the per-packet delay distribution on the flow. (seconds)
  * ‘Jitter’: variance of the per-packet delay (i.e., jitter) on the flow. i.e., var(packet_delay)

Thus, assuming *perf* is the performance_matrix of a sample, we may access to the information as follows:
```python
perf = sample.get_performance_matrix()

# dictionary with the performance measurements for the communication between node *src* and node *dst*
perf[src,dst]
# Dictionary with performance metrics on aggregate traffic between node *src* and node *dst*
perf[src,dst]['AggInfo']
# We can use this dictionary to access specific params
perf[src,dst]['AvgDelay']

# flow-level performance metrics on traffic between node *src* and node *dst*
perf[src,dst]['Flows']
# Dictionary with performance metrics for flow 0 traffic between node *src* and node *dst*
perf[src,dst]['Flows'][0]
# We can use this dictionary to access specific params
perf[src,dst]['Flows'][0]['PktsDrop′']
```

*NOTE:* in the context of the Graph Neural Networking challenge 2023, the performance_matrix contains the values to be predicted by the solutions to the challenge, and hence it will not be available to those samples belonging to the test dataset.

**traffic_matrix:** This matrix indexes traffic-related information at the level of src-dst pairs. Similar to performance_matrix, it provides traffic information at two levels of granularity: (i) for all aggregate flows on each src-dst pair, and (ii) for every flow individually. Every element of this matrix (i.e., traffic_matrix[src,dst]) contains a dictionary with the following keys:
* ‘AggInfo’: dictionary with traffic measurements for all aggregate flows between a specific [src,dst] pair. 
  * ‘AvgBw’: average bandwidth from node *src* to node *dst* (bits/second).
  * ‘PktsGen’: packets generated from node *src* to node *dst* per seconds (packets/second).
  * ‘AvgPktSize’: average packet size over the packets transmitted on path [src,dst] (bits)
  * ‘p10PktSize’, ‘p20PktSize’, ‘p50PktSize’, ‘p80PktSize’, ‘p90PktSize’: percentiles (10, 20, 50, 80, and 90) of the packet size  distribution on path [src,dst]. (bits)
  * ‘VarPktSize’: Variance of the packet size over the packets transmitted on path [src,dst].
* ‘Flows’: List of dictionaries with flow-level traffic information for each flow between node *src* and node *dst*. It includes the traffic measurements for each flow and the parameters used to generate the traffic flow in our traffic generator (see the different inter-packet arrival time and packet size distributions considered, and a list of parameters used in each of these distributions in Sections 4.1 and 4.2).
  * ‘TimeDis’: inter-packet arrival time distribution used to generate the traffic of the flow (see possible time distributions in Section 4.1).
  * ‘TimeDistParams’: dictionary with the parameters of the specific inter-packet arrival time distribution (see the parameters of each time distribution in Section 4.1). 
    * ‘Rate’: Bitrate per seconds (bits/seconds).
    * ‘On_Rate': Transmission bitrate of the packets during the burst (bits/second).
    * 'Pkts_per_burst': Number of packets containing each burst (packets).
    * 'IBG': Inter Burst Gap is the time since a burst ends and starts a new one (seconds).
  * ‘SizeDist’: packet size distribution used for the flow (see possible packet size distributions in Section 4.2).
  * ‘SizeDistParams’: dictionary with the parameters of the specific size distribution (see the parameters of each packet size distribution in Section 4.2). 
    * ‘AvgPktSize’: Average packet size (bits).
  * ‘AvgBw’: average bandwidth for this flow (bits/seconds).
  * ‘PktsGen’: packets generated by this flow per second (packets/second).
  * ‘AvgPktSize’: average packet size over the packets transmitted on the flow (bits)
  * ‘p10PktSize’, ‘p20PktSize’, ‘p50PktSize’, ‘p80PktSize’, ‘p90PktSize’: percentiles (10, 20, 50, 80, and 90) of the packet size  distribution over the packets transmitted on the flow. (bits)
  * ‘VarPktSize’: Variance of the packet size over the packets transmitted on the flow.
  * ‘ToS’: Type of Service associated to this flow defined as an integer. 

Data within traffic_matrix is structured in a similar way as in performance_matrix. The information is indexed by every src-dst pair. However, in this case the possible parameters of the inter-packet arrival time and packet size distributions depend on the types of distribution used. For instance, in case of multi burst inter-packet time distribution, the parameters of the first flow can be accessed using the following lines of code:

```python
traffic_matrix[src,dst]['Flows'][0]['TimeDistParams']['On_Rate']
traffic_matrix[src,dst]['Flows'][0]['TimeDistParams']['Pkts_per_burst']
traffic_matrix[src,dst]['Flows'][0]['TimeDistParams']['IBG']
```
*Note*: The flow indices are the same in both the traffic_matrix and the performance_matrix, meaning that the fields in `traffic_matrix[src,dst]['Flows'][0]` and `performance_matrix[src,dst]['Flows'][0]` refer to the same flow.


*Note*: If the dataset only has one flow per path, then traffic and performance measurements over the aggregate traffic on a src-dst pair are the same as flow-level measurements on the only flow in that src-dst pair. This applies to performance_matrix and traffic_matrix. For instance:
`performance_matrix[0,1]['AggInfo']['AvgDelay']) = performance_matrix[0,1]['Flows'][0][AvgDelay])`. In the case of traffic_matrix, using information at the flow-level is recommended (e.g., `traffic_matrix[0,1]['Flows'][0]`), since it includes additional information not considered at the level of aggregate traffic.

**routing_matrix**: This matrix describes the routing configuration (level 3). Particularly, it includes all the paths connecting every src-dst pair. Assuming *route* is a routing_matrix, `route[src,dst]` returns a list  describing the path from node *src* to node *dst*. Particularly, this list includes the IDs of the routers that the path traverses. Note that all the flows sharing the same src-dst pair follow the same path. 

**physical_path_matrix**: This matrix describes the physical path traffic, which is described as the ordered sequence of traversed links which form the path from src to dst. Particularly, each link is identified through its outgoing port number at the source and ingoing port number at the destination, and includes all the links between the switches, routers and traffic generators. Assuming *route* is a physical_path_matrix, `route[src,dst]` returns a list of ports describing the path from node *src* to node *dst*, including traffic generators, routers and switches.

If a path traverses n physical links, the size of the returned list will be equal to 2\*n. This is because each link will represented twice, by its outgoing port number at the source and ingoing port number at the destination. Even position of the lists (0, 2, 4...) will be occupied by the outgoing ports, while the odd position of the list (1, 3, 4...) will be occupied by the ingoing ports.

Both outgoing and ingoing ports are identified as a string with the following format:
```
"<src node type><src node id>-<next hop node type><next hop node id>-<port count>"
```
`<src node type><src node id>` can be used to identify the elements in the network. The node type can be:
  * 't': Traffic generator
  * 'r': Router
  * 's': Switch

The node id is a unique number for each element in the network. In case of the routers, the node number matches the index in the traffic_matrix, performance_matrix and other attributes. Port count is to identify the port when there is more than one port connected to next hop node.
It is considered that the first port is in the position 0 of the list.

For instance, the traffic from router 0 to router 1 is directly connected. The `routing_matrix[0,1]` is `[0,1]` but the physical_path_matrix is:
```
physical_path_matrix[0,1] = ['t10-s9-0', 's9-t10-0', 's9-r0-0', 'r0-s9-0', 'r0-s9-2', 's9-r0-2', 's9-r1-1', 'r1-s9-1', 'r1-s9-0', 's9-r1-0', 's9-t11-0', 't11-s9-0']
```
Note that the physical path, besides indicating us the involved links, it also tells us that the flow was generated in the traffic generator *t10*, and ends at traffic generator *t11*, and the switch *s9* was involved.

*Note*: due to the structure of the testbed's topology and the nature of how packets are captured and recorded, it is impossible for there to be congestion in the first link between the originating traffic generator and the first switch ('t10-s9-0', 's9-t10-0' in the example above). As a result, the delay introduced in this link is negligible, and can be safely discarded when studying how the flow's route will affect the packet delay.

**topology_object**: This is a Graph object form the Networkx library that provides information about the network topology. Particularly, this object encodes information on nodes and links (i.e., edges). Assuming *g* is a graph object of a sample instance, we can access the data as follows:
* `g.nodes`: Returns a list with all the node IDs. 
* `g.nodes[id]`: Returns a dictionary with all the information parameters of the selected node *id* (see more details of the node parameters Section 4.3).
* `g.edges`: Returns a list of tuples describing the topology edges. Each tuple is described as (src node ID, dst node ID, link ID). The link ID is always ‘0’ as only one link for the same src-dst pair is supported at this moment.
* `g[src][dst][0]`: Dictionary with the information parameters of the (directed) link between node *src* and node *dst* (see more details of the link parameters in Section 4.4).

**physical_topology_object**: This is a Graph object form the Networkx library describing the physical interconnection  between  traffic generators, routers and switches. Particularly, this object encodes information on nodes and links (i.e., edges). Assuming *g* is a graph object of a sample instance, we can access the data as follows:
* `g.nodes`: Returns a list with all the node IDs. 
* `g.nodes[id]`: Returns a dictionary with all the information parameters of the selected node *id* (see more details of the node parameters Section 4.5).
* `g.edges`: Returns a list of tuples describing the topology edges. Each tuple is described as (src node ID, dst node ID, link ID). The link ID is always ‘0’ as only one link for the same src-dst pair is supported at this moment.
* `g[src][dst][0]`: Dictionary with the information parameters of the (directed) link between node *src* and node *dst* (see more details of the link parameters in Section 4.6).

**pkts_info**: This object is a numpy matrix. For each src-dst returns a dictionary where the key is a ToS and the value is a list of lists. There is one list per flow using the same order than the flows described in traffic matrix or the performance matrix. The list contain information for each packet of the flow. This information is stored as a tuple of three elements: the generation timestamp in *nanoseconds* (not to be confused with other elements of the sample being described in seconds), the packet size in bits, and the delay in seconds. If a packet has been dropped, the delay value is not present in the tuple.

Thus, assuming *pinfo* is the pkts_info object of a sample, `pinfo[src,dst][tos][numflow]` returns the list of tuples with per packet information of packets transmitted in the flow *numflow* of the src-dst path with ToS *tos*.

*Note:* in the 2023 challenge dataset all flows are sent with ToS = 0.

*Note*: the scenarios that form the samples in this dataset take 10 seconds to complete. Out of those, only the packets from the final 5 seconds are recorded and stored in pkts_info.

*Warning:* the timestamps are added to the packet by the traffic generator. In the testbed the dataset was generated from, there are two traffic generator. The clocks of both traffic generator are **NOT** synchronized. This means that timestamps between two packets generated in the different traffic generator must not be compared. HOWEVER, since all packets in the same flow (and path) originate from the same traffic generator, their timestamps can be safely compared.


### 4.1 Parameters of time distributions
We configure the Traffic Generator with the following inter-packet arrival time distributions for different flows in the network:

* TimeDist.CBR_T: Rate 
* TimeDist.MULTIBURST_T: On_Rate, Pkts_per_burst, IBG


### 4.2 Parameters of packet size distributions

We configure the Traffic Generator with the following packet size distributions for different flows generated in the network:

* SizeDist.DETERMINISTIC_S: AvgPktSize 


### 4.3 List of node parameters for topology_object

All the possible node parameters are listed below:

* ‘levelsQoS’: Number of supported QoS classes
* ‘schedulingPolicy’: Policy used to serve the QoS queues. At this moment only 'FIFO' is used.

### 4.4 List of link parameters for topology_object

All the possible node parameters are listed below:

* ‘port’: Port number of the source node that links with destination node.
* ‘bandwidth’: Link bandwidth (bits/seconds) 
* ‘weight’: Not used yet

### 4.5 List of node parameters for physical_topology_object

All the possible node parameters are listed below:

* ‘type’: Type of device. It could be 'r' for router, 's' for switch, 'tc' for traffic generator client and 'ts' for traffic generator server.

### 4.6 List of link parameters for physical_topology_object

All the possible node parameters are listed below:

* ‘port’: Identifier of the port. It can be interpreted as <src node type><src node id>-<next hop node type><next hop node id>-<port count>
The node type can be:
  * 't': Traffic generator
  * 'r': Router
  * 's': Switch
Port count is to identify the port when there is more than one port connected to next hop node.
* ‘bandwidth’: Link bandwidth (bits/seconds) 


## 5 API methods to read information from a Sample object

The API includes methods to obtain more easily some information from a sample object. This includes different matrices and dictionaries described above. Thus, the user can use the following methods (hereafter, we assume that s is a sample object obtained from the iterator):

* `s.get_global_packets()`: Returns the number of packets transmitted in the network per seconds of the sample.
* `s.get_global_losses()`: Returns the number of packets dropped in the network per seconds of the sample.
* `s.get_global_delay()`: Returns the average per-packet delay over all the packets transmitted in the network in seconds of the sample.
* `s.get_max_link_load()`: Returns the maximum link utilization to generate the traffic matrix of the sample.
* `s.get_performance_matrix()`: Returns the performance_matrix. See more details about the performance_matrix in the previous section.
* `s.get_srcdst_performance(src,dst)`: Directly returns a dictionary with the performance measurements (e.g., delay, jitter, loss) stored in performance_matrix for a particular src-dst pair. See more details about the performance_matrix in the previous section.
* `s.get_traffic_matrix()`: Returns the traffic_matrix. See more details about the traffic_matrix in the previous section.
* `s.get_srcdst_traffic(src,dst)`: Directly returns a dictionary with information that the traffic_matrix stores for a particular src-dst pair. See more details about the traffic_matrix in the previous section.
* `s.get_routing_matrix()`: Returns the routing_matrix. See more details about the routing_matrix in the previous section.
* `s.get_srcdst_routing(src,dst)`: Returns a list with the routing path that connects node *src* with node *dst*. 
* `s.get_physical_path_matrix()`: Returns the physical_path_matrix. See more details about the physical_path_matrix in the previous section.
* `s.get_srcdst_physical_path(src,dst)`: Returns a list with the ports used to connect node *src* with node *dst*. 
* `s.get_topology_object()`: Returns a Networkx Graph object with routers and links parameters 
* `s.get_physical_topology_object()`:  Returns a Networkx Graph object desvribing how  nodes (traffic generator, routers and switches) are physicaly interconnected.
* `s.get_network_size()`: Returns the number of nodes in the topology. 
* `s.get_srcdst_link_bandwidth(src,dst)`: Returns the bandwidth in bits/seconds of the link between node *src* and node *dst* in case there is a link between both nodes, otherwise it returns -1.
* `s.get_pkts_info_object()`: Return the pkts_info object.
* `s.get_sample_id()`: Returns a tuple with the file and id containing this sample. 
* `s.get_capture_time()`: Returns the duration of the capture process ignoring the transitory period where no packets are captured.

## Credits
This project would not have been possible without the contribution of:
* [Arnau Badia](https://github.com/arnaubadia) - Barcelona Neural Networking center, Universitat Politècnica de Catalunya
* [Albert López](https://github.com/albert-lopez) - Barcelona Neural Networking center, Universitat Politècnica de Catalunya
* [Jose Suárez-Varela](https://github.com/jsuarezv) - Barcelona Neural Networking center, Universitat Politècnica de Catalunya
* Adrián Manco Sánchez - Barcelona Neural Networking center, Universitat Politècnica de Catalunya
* Víctor Sendino Garcia - Barcelona Neural Networking center, Universitat Politècnica de Catalunya
* [Pere Barlet Ros](https://github.com/pbarlet) - Barcelona Neural Networking center, Universitat Politècnica de Catalunya
* Albert Cabellos Aparicio - Barcelona Neural Networking center, Universitat Politècnica de Catalunya
