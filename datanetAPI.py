'''
 *
 * Copyright (C) 2020 CBA research group, Technical University of Catalonia.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at:
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
'''

# -*- coding: utf-8 -*-

import os, tarfile, pathlib, numpy, math, networkx, queue

class Sample:
    """
    Class used to contain the results of a single iteration in the dataset
    reading process.
    
    ...
    
    Attributes
    ----------
    pkt_by_network : double
        Overall number of packets transmitteds in network
    loses_by_network : double
        Overall number of packets lost in network
    delay_network : double
        Overall delay in network
    result_matrix : NxN matrix
        Matrix where each cell [i,j] contains aggregated and flow-level
        information about transmission parameters between source i and
        destination j.
    traffic_matrix : NxN matrix
        Matrix where each cell [i,j] contains aggregated and flow-level
        information about size and time distributions between source i and
        destination j.
    routing_matrix : NxN matrix
        Matrix where each cell [i,j] contains the path, if it exists, between
        source i and destination j.
    topology_matrix : NxN matrix
        Matrix where each cell [i,j] equals to the bandwidth between node i
        and node j (hence they are adjacent), or equals to -1 (hence both
        nodes are not adjacent).
    """
    
    _pkt_by_network = None
    _loses_by_network = None
    _delay_network = None
    
    _result_matrix = None
    _traffic_matrix = None
    _routing_matrix = None
    _topology_matrix = None
        
    def get_result_matrix(self):
        """
        Returns the result_matrix of this Sample instance.
        """
        
        return self.result_matrix
    
    def get_srcdst_result(self, src, dst):
        """
        

        Parameters
        ----------
        src : int
            Source node.
        dst : int
            Destination node.

        Returns
        -------
        Dictionary
            Information stored in the Result matrix for the requested src-dst.

        """
        return self.result_matrix[src, dst]
        
    def get_traffic_matrix(self):
        """
        Returns the traffic_matrix of this Sample instance.
        """
        
        return self.traffic_matrix
    
    def get_srcdst_traffic(self, src, dst):
        """
        

        Parameters
        ----------
        src : int
            Source node.
        dst : int
            Destination node.

        Returns
        -------
        Dictionary
            Information stored in the Traffic matrix for the requested src-dst.

        """
        
        return self.traffic_matrix[src, dst]
        
    def get_routing_matrix(self):
        """
        Returns the routing_matrix of this Sample instance.
        """
        
        return self.routing_matrix
    
    def get_srcdst_routing(self, src, dst):
        """
        

        Parameters
        ----------
        src : int
            Source node.
        dst : int
            Destination node.

        Returns
        -------
        Dictionary
            Information stored in the Routing matrix for the requested src-dst.

        """
        return self.routing_matrix[src, dst]
        
    def get_topology_matrix(self):
        """
        Returns the topology_matrix of this Sample instance.
        """
        
        return self.topology_matrix
    
    def get_srcdst_topology(self, src, dst):
        """
        

        Parameters
        ----------
        src : int
            Source node.
        dst : int
            Destination node.

        Returns
        -------
        Dictionary
            Information stored in the Topology matrix for the requested src-dst.

        """
        return self.topology_matrix[src, dst]
        
    def _set_result_matrix(self, m):
        """
        Sets the result_matrix of this Sample instance.
        """
        
        self.result_matrix = m
        
    def _set_traffic_matrix(self, m):
        """
        Sets the traffic_matrix of this Sample instance.
        """
        
        self.traffic_matrix = m
        
    def _set_routing_matrix(self, m):
        """
        Sets the traffic_matrix of this Sample instance.
        """
        
        self.routing_matrix = m
        
    def _set_topology_matrix(self, m):
        """
        Sets the topology_matrix of this Sample instance.
        """
        
        self.topology_matrix = m
        
    def _set_pkt_by_network(self, x):
        """
        Sets the pkt_by_network of this Sample instance.
        """
        
        self.pkt_by_network = x
        
    def _set_loses_by_network(self, x):
        """
        Sets the loses_by_network of this Sample instance.
        """
        
        self.loses_by_network = x
        
    def _set_delay_network(self, x):
        """
        Sets the delay_network of this Sample instance.
        """
        
        self.delay_network = x
    
    def _get_path_for_srcdst(self, src, dst):
        """
        Returns the path between node src and node dst.
        """
        
        return self.routing_matrix[src, dst]
    
    def _get_timedis_for_srcdst (self, src, dst):
        """
        Returns the time distribution of traffic between node src and node dst.
        """
        
        return self.traffic_matrix[src, dst]['TimeDist']
    
    def _get_eqlambda_for_srcdst (self, src, dst):
        """
        Returns the equivalent lambda for the traffic between node src and node
        dst.
        """
        
        return self.traffic_matrix[src, dst]['EqLambda']
    
    def _get_timedistparams_for_srcdst (self, src, dst):
        """
        Returns the time distribution parameters for the traffic between node
        src and node dst.
        """
        
        return self.traffic_matrix[src, dst]['TimeDistParams']
    
    def _get_sizedist_for_srcdst (self, src, dst):
        """
        Returns the size distribution of traffic between node src and node dst.
        """
        
        return self.traffic_matrix[src, dst]['SizeDist']
    
    def _get_avgpktsize_for_srcdst_flow (self, src, dst):
        """
        Returns the average packet size for the traffic between node src and
        node dst.
        """
        
        return self.traffic_matrix[src, dst]['AvgPktSize']
    
    def _get_sizedistparams_for_srcdst (self, src, dst):
        """
        Returns the time distribution of traffic between node src and node dst.
        """
        
        return self.traffic_matrix[src, dst]['SizeDistParams']
    
    def _get_resultdict_for_srcdst (self, src, dst):
        """
        Returns the dictionary with all the information for the communication
        between node src and node dst regarding communication parameters.
        """
        
        return self.result_matrix[src, dst]
    
    def _get_trafficdict_for_srcdst (self, src, dst):
        """
        Returns the dictionary with all the information for the communication
        between node src and node dst regarding size and time distribution
        parameters.
        """
        
        return self.traffic_matrix[src, dst]

class ParsingTool:
    """
    Class containing all the functionalities to read the dataset line by line
    by means of an iteratos, and generate a Sample instance with the
    information gathered.
    """
    
    def __init__ (self, data_folder, intensity_values):
        """
        Initialization of the PasringTool instance

        Parameters
        ----------
        data_folder : str
            Folder where the dataset is stored.
        dict_queue : Queue
            Auxiliar data structures used to conveniently move information
            between the file where they are read, and the matrix where they
            are located.
        intensity_values : int or array [x, y]
            User-defined intensity values used to constrain the reading process
            to these/this value/range of values.

        Returns
        -------
        None.

        """
        
        self.data_folder = data_folder
        self.dict_queue = queue.Queue()
        self.intensity_values = intensity_values

    def _readRoutingFile(self, routing_file, netSize):
        """
        Pending to compare against getSrcPortDst

        Parameters
        ----------
        routing_file : str
            File where the routing information is located.
        netSize : int
            Number of nodes in the network.

        Returns
        -------
        R : netSize x netSize matrix
            Matrix where each  [i,j] states what port node i should use to
            reach node j.

        """
        
        R = numpy.zeros((netSize, netSize)) - 1
        src = 0
        for line in routing_file:
            line = line.decode()
            camps = line.split(',')
            dst = 0
            for port in camps[:-1]:
                R[src][dst] = port
                dst += 1
            src += 1
        return (R)

    def _getSrcPortDst(self, G):
        """
        Pending to compare against readRoutingFile

        Parameters
        ----------
        G : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        
        node_port_dst = {}
        for node in G:
            port_dst = {}
            node_port_dst[node] = port_dst
            for destination in G[node].keys():
                port = G[node][destination][0]['port']
                node_port_dst[node][port] = destination
        return(node_port_dst)

    def _getAllPaths(self, G,routing_file):
        """

        Parameters
        ----------
        G : graph
            Graph representing the network.
        routing_file : str
            File where the information about routing is located.

        Returns
        -------
        MatrixPath : NxN Matrix
            Matrix where each cell [i,j] contains the path to go from node
            i to node j.

        """
        
        netSize = G.number_of_nodes()
        node_port_dst = self._getSrcPortDst(G)
        R = self._readRoutingFile(routing_file, netSize)
        MatrixPath = numpy.empty((netSize, netSize), dtype=object)
        for src in range (0,netSize):
            for dst in range (0,netSize):
                node = src
                path = [node]
                while (R[node][dst] != -1):
                    out_port = R[node][dst];
                    next_node = node_port_dst[node][out_port]
                    path.append(next_node)
                    node = next_node
                MatrixPath[src][dst] = path[0:len(path)]
        return (MatrixPath)

    def _get_graph_for_tarfile(self, tar):
        """
        

        Parameters
        ----------
        tar : str
            tar file where the graph file is located.

        Returns
        -------
        ret : graph
            Graph representation of the network.

        """
        
        for member in tar.getmembers():
            if 'graph' in member.name:
                f = tar.extractfile(member)
                ret = networkx.read_gml(f, destringizer=int)
                return ret

    def _check_intensity(self, file):
        """
        

        Parameters
        ----------
        file : str
            Name of the data file that needs to be filtered by intensity.

        Returns
        -------
        2 if the range of intensities treates in the file satisfies the needs
        of the user.
        1 if there may be lines in the file that do not fulfill the user
        requirements.
        0 if the file does not fulfill the user-defined intensity requirements.

        """
        
        aux = file.split('_')
        aux = aux[2]
#        User introduced range of intensities
        if(len(self.intensity_values) > 1):
            if(len(aux) > 1):
                aux = aux.split('-')
                aux = list(map(int, aux))
                if(aux[0] == self.intensity_values[0]) and (aux[1] == self.intensity_values[1]):
                    return 2
                elif(aux[0] > self.intensity_values[1]) or (self.intensity_values[0] > aux[1]):
                    return 0
                else:
                    return 1
                    
            else:
                aux = int(aux)
                if(aux in range(self.intensity_values[0, self.intensity_values[1]+1])):
                    return 2
                else: 
                    return 0
#        User introduced single intensity
        else:
            if(len(aux) > 1):
                aux = aux.split('-')
                aux = list(map(int, aux))
                if(self.intensity_values[0] in range(aux[0], aux[1]+1)):
                    return 2
                else:
                    return 0
            else:
                aux = int(aux)
                if aux == self.intensity_values[0]: return 2
                else: 
                    return 0

    def _create_topology_matrix(self, graph):
        """
        

        Parameters
        ----------
        graph : graph
            Graph representing the network.

        Returns
        -------
        mat : nXn matrix
            Matrix where, for each cell [i,j], the bandwidth between the two
            adjacent nodes i and j is given. If i and j are not adjacent, a -1
            is placed instead.

        """
        
        mat = numpy.full((graph.number_of_nodes(), graph.number_of_nodes()), -1)
        for node in range(0,graph.number_of_nodes()):
            for adj in graph[node]:
                cap = graph[node][adj][0]['bandwidth']
                cap = cap[:len(cap)-4]
                cap = float(cap)
                mat[node,adj] = cap
                # print (mat)
        return mat

    def __iter__(self):
        """
        

        Yields
        ------
        s : Sample
            Sample instance containing information about the last line read
            from the dataset.

        """
        
        topology_matrix_for_dataset = None
        g = None
        graph_read = False
        for root, dirs, files in os.walk(pathlib.Path(self.data_folder)):
            for file in files:
                if(file == "graph_attr.txt"):
                    g = networkx.read_gml(os.path.join(root, file), destringizer=int)
                    topology_matrix_for_dataset = self._create_topology_matrix(g)
                    graph_read = True
            if(not graph_read):
                print('Unable to find the graph information file')
                break
            for file in files:
                if(file.endswith("tar.gz")):
                    
                    if (len(self.intensity_values) == 0): feasibility_of_file = 2
                    else: feasibility_of_file = self._check_intensity(file)
                    
                    if(feasibility_of_file != 0):
                        tar = tarfile.open(os.path.join(root, file), 'r:gz')
                        dir_info = tar.next()
                        routing_file = tar.extractfile(dir_info.name+"/Routing.txt")
                        results_file = tar.extractfile(dir_info.name+"/simulationResults.txt")
                        traffic_file = tar.extractfile(dir_info.name+"/traffic.txt")
                        flowresults_file = tar.extractfile(dir_info.name+"/flowSimulationResults.txt")
                        
                        routing_matrix_for_tar = numpy.empty((g.number_of_nodes(), g.number_of_nodes()), dtype=object)
                        routing_matrix_for_tar = self._getAllPaths(g, routing_file)
                        while(True):
                            s = Sample()
                            results_line = results_file.readline()
                            traffic_line = traffic_file.readline()
                            flowresults_line = flowresults_file.readline()
                            if (len(results_line) == 0) or (len(traffic_line) == 0):
                                break
                            if (feasibility_of_file == 1):
                                tmp = str(traffic_line)
                                tmp = tmp.split('|')
                                specific_intensity = tmp[0]
                                specific_intensity = specific_intensity[2:len(specific_intensity)-1]
                                specific_intensity = float(specific_intensity)
                                if(specific_intensity < self.intensity_values[0]) or (specific_intensity > self.intensity_values[1]):
                                    continue
                                
                            self._process_flow_results_traffic_line(results_line, traffic_line, flowresults_line, s)
                            s._set_routing_matrix(routing_matrix_for_tar)
                            s._set_topology_matrix(topology_matrix_for_dataset)
                            yield s
                    else:
                        continue
    
    def _process_flow_results_traffic_line(self, rline, tline, fline, s):
        """
        

        Parameters
        ----------
        rline : str
            Last line read in the results file.
        tline : str
            Last line read in the traffic file.
        fline : str
            Last line read in the flows file.
        s : Sample
            Instance of Sample associated with the current iteration.

        Returns
        -------
        None.

        """
        
        q_flows = queue.Queue()
        r = str(rline)
        r = r[2:len(r)-4]
        first_params = r.split('|')[0]
        first_params = first_params.split(',')
        first_params = list(map(float, first_params))
        s._set_pkt_by_network(first_params[0])
        s._set_loses_by_network(first_params[1])
        s._set_delay_network(first_params[2])
        r = r.split('|')[1].split(';')
        
        f = str(fline)
        f = f[2:len(f)-4]
        f = f.split(';')
        
        t  = str(tline)
        t = t[2:len(t)-4]
        t = t.split('|')[1].split(';')
        
        m_result = []
        m_traffic = []
        for i in range(0,len(r), int(math.sqrt(len(r)))):
            new_result_row = []
            new_traffic_row = []
            for j in range(i, i+int(math.sqrt(len(r)))):
                dict_result_srcdst = {}
                aux_agg = r[j].split(',')
                aux_agg = list(map(float, aux_agg))
                dict_result_agg = {'PktsDrop':aux_agg[2], "AvgDelay":aux_agg[3], "AvgLnDelay":aux_agg[4], "p10":aux_agg[5], "p20":aux_agg[6], "p50":aux_agg[7], "p80":aux_agg[8], "p90":aux_agg[9], "Jitter":aux_agg[10]}
                
                aux_result_flows = f[j].split(':')
                lst_result_flows = []
                for flow in aux_result_flows:
                    dict_result_tmp = {}
                    tmp_result_flow = flow.split(',')
                    tmp_result_flow = list(map(float, tmp_result_flow))
                    q_flows.put([tmp_result_flow[0], tmp_result_flow[1], tmp_result_flow[2]])
                    dict_result_tmp = {'PktsDrop':tmp_result_flow[2], "AvgDelay":tmp_result_flow[3], "AvgLnDelay":tmp_result_flow[4], "p10":tmp_result_flow[5], "p20":tmp_result_flow[6], "p50":tmp_result_flow[7], "p80":tmp_result_flow[8], "p90":tmp_result_flow[9], "Jitter":tmp_result_flow[10]}
                    lst_result_flows.append(dict_result_tmp)
                
                dict_traffic_srcdst = {}
                dict_traffic_agg = {'AvgBw':aux_agg[0],
                                    'PktsGen':aux_agg[1]}
                lst_traffic_flows = []
                aux_traffic_flows = t[j].split(':')
                for flow in aux_traffic_flows:
                    dict_traffic_tmp = {}
                    tmp_traffic_flow = flow.split(',')
                    tmp_traffic_flow = list(map(float, tmp_traffic_flow))
                    temp = self._timedistparams(tmp_traffic_flow)
                    partial = temp[0]
                    if partial is not None:
                        final = self._sizedistparams(tmp_traffic_flow, temp[1], partial)
                        q_values_for_flow = q_flows.get()
                        final['AvgBw'] = q_values_for_flow[0]
                        final['PktsGen'] = q_values_for_flow[1]
                        dict_traffic_tmp = final
                    lst_traffic_flows.append (dict_traffic_tmp)
                
                
                dict_result_srcdst['AggInfo'] = dict_result_agg
                dict_result_srcdst['Flows'] = lst_result_flows
                dict_traffic_srcdst['AggInfo'] = dict_traffic_agg
                dict_traffic_srcdst['Flows'] = lst_traffic_flows
                new_result_row.append(dict_result_srcdst)
                new_traffic_row.append(dict_traffic_srcdst)
                
            m_result.append(new_result_row)
            m_traffic.append(new_traffic_row)
        m_result = numpy.asmatrix(m_result)
        m_traffic = numpy.asmatrix(m_traffic)
        s._set_result_matrix(m_result)
        s._set_traffic_matrix(m_traffic)

    def _timedistparams(self, data):
        """
        

        Parameters
        ----------
        data : str
            Portion of the traffic file line where the data regarding the time
            distribution is contained.

        Returns
        -------
        [info, continuationPoint] : dictionary
            Dictionary containing the info collected until now, and the point
            of the overall traffic file line where the parsing process should
            continue.

        """
        
        temp = {}
    #    print(data[0])
        if data[0] == 0: 
            temp['TimeDist'] = 'EXPONENTIAL_T'
            params = {}
            params['EqLambda'] = data[1]
            params['AvgPktsLambda'] = data[2]
            params['ExpMaxFactor'] = data[3]
            temp['TimeDistParams'] = params
            return [temp, 4]
        elif data[0] == 1:
            temp['TimeDist'] = 'DETERMINISTIC_T'
            params = {}
            params['EqLambda'] = data[1]
            params['AvgPktsLambda'] = data[2]
            temp['TimeDistParams'] = params
            return [temp, 3]
        elif data[0] == 2:
            temp['TimeDist'] = 'UNIFORM_T'
            params = {}
            params['EqLambda'] = data[1]
            params['MinPktLambda'] = data[2]
            params['MaxPktLambda'] = data[3]
            temp['TimeDistParams'] = params
            return [temp, 4]
        elif data[0] == 3:
            temp['TimeDist'] = 'NORMAL_T'
            params = {}
            params['EqLambda'] = data[1]
            params['AvgPktsLambda'] = data[2]
            params['StdDev'] = data[3]
            temp['TimeDistParams'] = params
            return [temp, 4]
        elif data[0] == 4:
            temp['TimeDist'] = 'ONOFF_T'
            params = {}
            params['EqLambda'] = data[1]
            params['PktsLambdaOn'] = data[2]
            params['AvgTOff'] = data[3]
            params['AvgTOn'] = data[4]
            params['ExpMaxFactor'] = data[5]
            temp['TimeDistParams'] = params
            return [temp, 6]
        elif data[0] == 5:
            temp['TimeDist'] = 'PPBP_T'
            params = {}
            params['EqLambda'] = data[1]
            params['BurstGenLambda'] = data[2]
            params['Bitrate'] = data[3]
            params['ParetoMinSize'] = data[4]
            params['ParetoMaxSize'] = data[5]
            params['ParetoAlfa'] = data[6]
            params['ExpMaxFactor'] = data[7]
            temp['TimeDistParams'] = params
            return [temp, 8]
        else: return [None, None]
    
    def _sizedistparams(self, data, starting_point, ret):
        """
        

        Parameters
        ----------
        data : str
            Portion of the traffic file line where the data regarding the size
            distribution is contained.
        starting_point : int
            Point of the overall traffic file line where the extraction of
            data regarding the size distribution should start.
        ret : dictionary
            Dictionary returned by the previous parsing process. The one that
            handled the time distribution data extraction.

        Returns
        -------
        ret : dictionary
            Updated dictionary with all the information abour size and time
            distribution in the current traffic file line.

        """
        
        if data[starting_point] == 0:
            ret['SizeDist'] = 'DETERMINISTIC_S'
            params = {}
            params['AvgPktSize'] = data[starting_point+1]
            ret['SizeDistParams'] = params
        elif data[starting_point] == 1:
            ret['SizeDist'] = 'UNIFORM_S'
            params = {}
            params['AvgPktSize'] = data[starting_point+1]
            params['MinSize'] = data[starting_point+2]
            params['MaxSize'] = data[starting_point+3]
            ret['SizeDistParams'] = params
        elif data[starting_point] == 2:
            ret['SizeDist'] = 'BINOMIAL_S'
            params = {}
            params['AvgPktSize'] = data[starting_point+1]
            params['PktSize1'] = data[starting_point+1]
            params['PktSize2'] = data[starting_point+1]
            ret['SizeDistParams'] = params
        elif data[starting_point] == 3:
            ret['SizeDist'] = 'GENERIC_S'
            params = {}
            params['AvgPktSize'] = data[starting_point+1]
            params['NumCandidates'] = data[starting_point+2]
            candSizeProb = {}
            for i in range(0, data[starting_point+2] * 2, 2):
                candSizeProb["Size_%d"%(i/2)] = data[starting_point+3+i]
                candSizeProb["Prob_%d"%(i/2)] = data[starting_point+4+i]
            params['PairsSizeProb'] = candSizeProb
            ret['SizeDistParams'] = params
        return ret

# tool = ParsingTool('d:/Master_MIRI/BNN/API/nsfnetbw/', [])
#tool = ParsingTool('./nsfnetbw/', [])
#it = iter(tool)
# for out in it:
#     # print('----')
#     # print(out.pkt_by_network)
#     # print(out.loses_by_network)
#     # print(out.delay_network)
#     # print(out.get_result_matrix())
#     # print(out.get_topology_matrix())
#     # print(out.get_routing_matrix())
#     # print(out.get_resultdict_for_srcdst(0, 1)['Flows']['0']['p80'])
#     # print(out.traffic_matrix[0,1]['Flows']['0'])
#     # print(out.topology_matrix)
#     # print(out.routing_matrix)
#     print(out.topology_matrix)
#m = next(it).get_traffic_matrix()[0,1]
#print(m)