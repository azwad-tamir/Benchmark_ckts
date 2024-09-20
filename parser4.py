import networkx as nx
import re
import os
import io
import numpy as np
#from halp.undirected_hypergraph import UndirectedHypergraph
import copy
import matplotlib.pyplot as plt
import random

from itertools import *

class vparser(object):

    def __init__(self, vcode_name):
        self.vcode_name = vcode_name
        with io.open(self.vcode_name, "rt") as f:  # rt read as text mode
            code = f.read()
        code = code.split(';')
        self.vcode = [w.replace('\n', '') for w in code]

    def gethygraph(self):

        '''generate the hypergraph dict from verilog code'''

        # regex patterns
        module_pattern = r'module\s(.+)'  # like input abc123
        endmodule_pattern = 'endmodule'
        wire_pattern = r'wire\s(.+)'  # like input abc123
        net_pattern = r'\.\w*\(([^\)]+?)\)'  # like .abc123(abc123)
        device_pattern = r'\.\w*\('  # include .abc123(
        input_pattern = r'input\s(.+)'  # like input abc123
        output_pattern = r'output\s(.+)'  # like output abc123
        index_pattern = r'\[[0-9]*:0\]\s'  # like [123:0]
        netindex_pattern = r'\[[0-9]*\]'  # like [123]
        device_pattern_re = re.compile(device_pattern)
        hygraphdict = {}
        self.inputnets = []
        self.outputnets = []
        self.getNets = []
        self.nets = []
        self.module = []
        self.net_wires = []
        self.node_names = []
        self.node_node = []
        self.allOutputs = []
        self.allIntputs = []
        self.wires = []
        name = self.vcode[0][self.vcode[0].find("module") + 6:].split(' ')
        self.id = name[1]

        for i in range(len(self.vcode)):
            #print(self.vcode)
            if self.vcode[i].startswith("//"):
                continue
            # get wires
            iswire = re.findall(wire_pattern, self.vcode[i])
            isinput = re.findall(input_pattern, self.vcode[i])
            isoutput = re.findall(output_pattern, self.vcode[i])
            ismodule = re.findall(module_pattern, self.vcode[i])
            isendmodule = re.findall(endmodule_pattern, self.vcode[i])
            if ismodule:
                self.module.append(ismodule)
            elif isendmodule:
                continue
            elif iswire:
                self.wires.append(iswire)

            # identity input nets
            elif isinput:
                inputs = isinput[0].split(", ")  # split each input by '' , ''
                self.allIntputs += inputs
                inputs = [re.sub(index_pattern, '', w) for w in inputs]
                # if 'clk' in inputs:
                #     inputs.remove('clk')
                self.inputnets += inputs  # Get the inputs

            elif isoutput:
                outputs = isoutput[0].split(", ")
                self.allOutputs += outputs
                # print("outputs are: ", outputs)
                outputs = [re.sub(index_pattern, '', w) for w in outputs]
                self.outputnets += outputs  # Get the outputs

            else:
                self.nets.append(self.vcode[i])
                temp_net = self.vcode[i]
                temp_net = temp_net.replace('(',' ')
                temp_net = temp_net.replace(')', '')
                temp_net = temp_net.replace(',', ' ')
                items = temp_net.split()
                self.node_names.append(items[0])
                self.node_node.append(items[1])
                self.getNets.append(items[2:items.__len__()])

# Creating gates:
def _not(input):
    """Perform a logic NOT on the input value.
    Keyword arguments:
    input -- Input value
    """

    final_input = None

    # If the input is a list, then take the first element.
    if type(input) is list:
        if (len(input) > 1 ):
            print('not_prob input > 1 not supported')
        final_input = input[0]
    # Otherwise, take the input as is.
    else:
        final_input = input[0]

    # If the input was still not assigned, then display an error.
    if final_input is None:
        print("ERROR:: Invalid input to NOT gate (input = ", input)

    # Otherwise, evaluate the NOT logic.
    else:
        # If input is logic 1, then return a logic 0.
        if final_input is 1:
            return 0
        # Otherwise, return a logic 1.
        else:
            return 1

def _dff(input):
    """Perform a logic DFF on the input value.

    Keyword arguments:
    input -- Input value
    """
    final_input = None

    # If the input is a list, then take the first element.
    if type(input) is list:
        if (len(input) > 1 ):
            print('not_prob input > 1 not supported')
        final_input = input[0]

    # Otherwise, take the input as it is.
    else:
        final_input = input

    # If the input was still not assigned, then display an error.
    if final_input is None:
        print("ERROR:: Invalid input to dff gate (input = ", input)

    # Otherwise, evaluate the NOT logic.

    else:
        return final_input

def _and(input):
    """Perform a logic AND on all the input values.

    Keyword arguments:
    input -- List of input values
    """
    # If there is a logic 0 at any moment, then simply return a logic 0.
    for value in input:
        if value is 0:
            return 0

    # Otherwise, return 1 if no logic 0 is found.
    return 1

def _or(input):
    """Perform a logic OR on all the input values.

    Keyword arguments:
    input -- List of input values
    """
    # If there is a logic 1 at any moment, then simply return a logic 1.
    for value in input:
        if value is 1:
            return 1

    # Otherwise, return 0 if no logic 1 is found.
    return 0

def _nor(input):
    """Perform a logic OR on all the input values.

    Keyword arguments:
    input -- List of input values
    """
    temp = 0
    # If there is a logic 1 at any moment, then simply return a logic 1.
    for value in input:
        if value is 1:
            temp = 1
    # Otherwise, return 0 if no logic 1 is found.
    return int(not(temp))

def _nand(input):
    """Perform a logic AND on all the input values.

    Keyword arguments:
    input -- List of input values
    """
    temp = 1
    # If there is a logic 0 at any moment, then simply return a logic 0.
    for value in input:
        if value is 0:
            temp = 0

    # Otherwise, return 1 if no logic 0 is found.
    return int(not(temp))

def _out(input):
    return input[0]

def calculate_output(gate_type, input):
    if gate_type == 'dff':
        return _dff(input)
    elif gate_type == 'not':
        return _not(input)
    elif gate_type == 'and':
        return _and(input)
    elif gate_type == 'nand':
        return _nand(input)
    elif gate_type == 'or':
        return _or(input)
    elif gate_type == 'nor':
        return _nor(input)
    elif gate_type == 'output':
        return _out(input)
    else:
        print("Unknown gate type: ", gate_type)
        return None

def clean(x):
    #y = []
    i=0
    for net in x:
        net = net.replace('/', 'F')
        net = net.replace('\\', 'B')
        x[i] = net
        i+=1
        #print(y)
    return x

def clean2(x):
    i=0
    for net in x:
        net = net.replace('[', '')
        net = net.replace(']', '')
        x[i] = net
        i+=1
    return x

# Main file object:
obj = vparser('s13207.v')
obj.gethygraph()
input_net = obj.inputnets
out_net = obj.outputnets
get_net = obj.getNets
node_names = obj.node_names
#allout = obj.allOutputs
#allin = obj.allIntputs
node_node = obj.node_node
wires = obj.wires
wires_new = [item for sublist in wires for item in sublist]
# get_net_all = list(set(get_net_all))
# out_out = input_net

# fixing wires:
wires1 = []
for i in wires_new:
    temp = str(i).replace(' ','')
    wires1.append(temp.replace(',',', '))

wires_main = []
for net in wires1:
    wire2 = net.replace(' ', '')
    wire3 = wire2.split(",")
    wires_main.extend(wire3)

# fixing inputs:
input1 = []
for i in input_net:
    temp = str(i).replace(' ','')
    input1.append(temp.replace(',',', '))

input_main = []
for net in input1:
    wire2 = net.replace(' ', '')
    wire3 = wire2.split(",")
    input_main.extend(wire3)
# removing VDD,CK and GND from input nodes:
input_main = list(set(input_main)-set(['CK', 'VDD', 'GND']))

# fixing outputs:
out_net1 = []
for i in out_net:
    temp = str(i).replace(' ','')
    out_net1.append(temp.replace(',',', '))

out_main = []
for net in out_net1:
    wire2 = net.replace(' ', '')
    wire3 = wire2.split(",")
    out_main.extend(wire3)

####################################################################################################################################################################
# Calculating probability:
####################################################################################################################################################################

G = nx.DiGraph()

# adding input nodes:
for gate in input_main:
    G.add_node(gate, type='input', value=None, switch=0, stage=0, switch_freq=0, orient=0, type1=None)

#adding output nodes:
for gate in out_main:
    G.add_node(gate, type='output', value=None, switch=0, stage=0, switch_freq=0, orient=0, type1=None)

# adding gate nodes:
i=0
for gate in node_node:
    G.add_node(gate, type=node_names[i], value=None, switch=0, stage=0, switch_freq=0, orient=0, type1=None)
    i+=1

# adding wire nodes:
for gate in wires_main:
    G.add_node(gate, type='wire', value=None, switch=0, stage=0, switch_freq=0, orient=0, type1=None)

num = np.zeros(100)
for net in get_net:
    num[net.__len__()]+=1


# adding edges to the graph:
i=0
for net in get_net:
    if net[0] == 'CK':
        G.add_edge(node_node[i], net[1], dir=0)
        # print(node_node[i] + ' -->  ' + net[net.__len__()-1])
        for net_in in net[2:net.__len__()]:
            G.add_edge(net_in, node_node[i], dir=0)
            # print(net_in, ' --> ', node_node[i])
        i+=1
    else:
        G.add_edge(node_node[i], net[0], dir=0)
        #print(node_node[i] + ' -->  ' + net[net.__len__()-1])
        for net_in in net[1:net.__len__()]:
            G.add_edge(net_in,node_node[i], dir=0)
            #print(net_in, ' --> ', node_node[i])
        i+=1



# Removing empty wires:
i=0
empty_wires = []
for net in wires_main:
    if((list(G.predecessors(net)).__len__()==0) | (list(G.successors(net)).__len__()==0)):
        G.remove_node(net)
        empty_wires.append(net)
        i+=1
print(i)
    #print(list(G.successors(net)).__len__())
# for net in allwires:
#     if G.has_node(net):
#         for net1 in list(G.predecessors(net)) + list(G.successors(net)):
#             if G.nodes[net1]['type'] == 'wire':
#                 print(net1)

# Removing wires from the graph:
for net in wires_main:
    if G.has_node(net):
        if (list(G.predecessors(net)).__len__()) != 1:
            print("Fetal Error: Check wire predecessor")

for net in wires_main:
    if G.has_node(net):
        for net1 in list(G.successors(net)):
            G.add_edge(list(G.predecessors(net))[0], net1, dir=0)
            #print(list(G.predecessors(net)),' --> ', net1)
        G.remove_node(net)

########################################################################################################################
## Creating stages:##
########################################################################################################################
node_stage = []
node_stage.append([])
I = copy.deepcopy(G)
counter=I.number_of_nodes()
for nets in input_main:
    I.nodes[nets]['stage'] = 1
    counter-=1

current_stage = input_main
stage_num = 2

for i in range(0,I.number_of_nodes()):
    temp = []
    for nets in current_stage:
        for nets1 in list(I.successors(nets)):
            if I.nodes[nets1]['stage'] == 0:
                I.nodes[nets1]['stage'] = stage_num
                temp.append(nets1)
                counter-=1
    stage_num+=1
    node_stage.append(current_stage)
    current_stage = temp
    #print(counter)
    if counter == 0:
        break
node_stage.append(current_stage)
# Labeling forward and backward edges: 0:unassigned, 1:forward, 2:backward
forward = 0
backward = 0
test = []

for edges in list(I.edges):
    if I.nodes[edges[0]]['stage'] < I.nodes[edges[1]]['stage']:
        I.edges[edges]['dir'] = 1
        forward+=1
    elif I.nodes[edges[0]]['stage'] >= I.nodes[edges[1]]['stage']:
        I.edges[edges]['dir'] = 2
        backward+=1
        I.nodes[edges[0]]['orient'] = 1
        test.append(edges[0])

# Generatign random inputs:
rand_num_len = input_main.__len__() + list(set(test)).__len__()
input_feed = []
all_feed = []
for i in range(0,rand_num_len):
    num = random.randint(0,1)
    input_feed.append(num)
all_feed.append(input_feed)

i=0
for nets in list(I.nodes):
    if (I.nodes[nets]['type'] == 'input') | (I.nodes[nets]['orient'] == 1):
        I.nodes[nets]['value'] = input_feed[i]
        i+=1


# Running simulator:
# for nets in I.nodes():
#     #print(nets)
#     if (I.nodes[nets]['type'] == 'not') | (I.nodes[nets]['type'] == 'dff'):
#         I.nodes[nets]['type1'] = I.nodes[nets]['type']
#     else:
#         I.nodes[nets]['type1'] = re.findall(r'(.+)_', nets)

max_stage = 0
for nets in I.nodes():
    if I.nodes[nets]['stage'] > max_stage:
        max_stage = I.nodes[nets]['stage']

num_iter = 1000000
for i in range(0,num_iter):
    for stage in range(1,max_stage+1):
        for nodes in node_stage[stage]:
            input_net = []
            for pred in list(I.predecessors(nodes)):
                value = I.nodes[pred]['value']
                if value == None:
                    print("Fetal Error: Cannot find inputs for ", nodes)
                input_net.append(value)
            if stage==1:
                I.nodes[nodes]['value'] = random.randint(0, 1)
            else:
                out = calculate_output(I.nodes[nodes]['type'], input_net)
                if I.nodes[nodes]['value'] != out:
                    I.nodes[nodes]['switch'] += 1
                I.nodes[nodes]['value'] = out
    if i%100 == 0:
        print(i)
nx.write_gpickle(I, "aes_cipher_1mRun1.gpickle")

# Finding rare nodes:
rare_prob = 0.01
node_count = int(rare_prob*I.number_of_nodes())
rare_nodes = []
for i in range(0,num_iter+1):
    for nets in list(I.nodes):
        if (I.nodes[nets]['switch'] == i) & (I.nodes[nets]['type']!='input'):
            rare_nodes.append(nets)
            node_count-=1
    if node_count<=0:
        break
x = np.zeros(1000001)
for net in I.nodes():
    x[I.nodes[net]['switch']] +=1



# # Cheking whether all nodes has assigned values:
# NO = np.zeros(101)
# for nets in list(I.nodes):
#     NO[I.nodes[nets]['switch']] +=1
# #print(NO)
#
#
# # calling Gate class:
# I = nx.DiGraph()
# I.add_nodes_from(['N1','N2','N3','N6','N7'],type='input', prob=0.5, prob_has = 1)
# I.add_nodes_from(['NAND2_1','NAND2_2','NAND2_3','NAND2_4','NAND2_5','NAND2_6'],type='NAND2X1', prob=0, prob_has = 0)
# I.add_nodes_from(['N22','N23'],type='output', prob=0, prob_has=1)
# I.add_edge('N1','NAND2_1')
# I.add_edge('N3','NAND2_1')
# I.add_edge('N3','NAND2_2')
# I.add_edge('N6','NAND2_2')
# I.add_edge('N2','NAND2_3')
# I.add_edge('NAND2_2','NAND2_3')
# I.add_edge('N7','NAND2_4')
# I.add_edge('NAND2_2','NAND2_4')
# I.add_edge('NAND2_1','NAND2_5')
# I.add_edge('NAND2_3','NAND2_5')
# I.add_edge('NAND2_3','NAND2_6')
# I.add_edge('NAND2_4','NAND2_6')
# I.add_edge('NAND2_5','N22')
# I.add_edge('NAND2_6','N23')
#
# def calculate_prob(I, net):
#     input = []
#     for pred_net in list(I.predecessors(net)):
#         if I.nodes[pred_net]['prob_has'] == 0:
#             I = calculate_prob(I, pred_net)
#         else:
#             input.append(I.nodes[pred_net]['prob'])
#
#     A = Gate(net, I.nodes[net]['type'], input)
#     I.nodes[net]['prob'] = A.output_probability(input)
#     I.nodes[net]['prob_has'] = 1
#     return I
#
# net_net = ['NAND2_1','NAND2_2','NAND2_3','NAND2_4','NAND2_5','NAND2_6']
# for net in node_node:
#     if G.nodes[net]['prob_has'] == 0:
#         G = calculate_prob(G,net)
#
# for i in range(0,1000):
#     for net in node_node:
#         input = []
#         if G.nodes[net]['prob_has'] == 0:
#             pred_list = list(G.predecessors(net))
#             j=0
#             for pred in pred_list:
#                 if G.nodes[pred]['prob_has'] == 0:
#                     j=1
#                 else:
#                     input.append(G.nodes[pred]['prob'])
#             if j == 0:
#                 A = Gate(net, G.nodes[net]['type'], input)
#                 G.nodes[net]['prob'] = A.output_probability(input)
#                 G.nodes[net]['prob_has'] = 1
#                 print(net)
#
# # Fining simple cycles:
# cycles = list(nx.simple_cycles(G))
# nets = list(nx.find_cycle(G, orientation='original'))
#
# #deleting nodes with cycles
# num=0
# cycles = []
# for i in range(0,10000):
#     nets = list(nx.find_cycle(G, orientation='original'))
#     print(nets)
#     G.remove_node(nets[0][0])
#
#
# print(I.nodes(data='prob'))
#
#
#
# list(G.nodes(data=True))[0]
# G.add_node(1, time='5pm')
# list(G.nodes(data= 'time'))[0][1]


