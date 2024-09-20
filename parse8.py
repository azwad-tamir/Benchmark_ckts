import networkx as nx
import re
import os
import io
import numpy as np
#from halp.undirected_hypergraph import UndirectedHypergraph
import copy
import matplotlib.pyplot as plt
import random
import vparser
from itertools import *
import gate_new
import pandas as pd



def read_lib1(gate):
    if (gate=='TX' or gate=='IV' or gate=='BU' or gate=='AN4' or gate=='AN3' or gate=='AN2' or gate=='ND4' or gate=='ND3' or gate=='ND2' or gate=='OR4' or gate=='OR3' or gate=='OR2' or gate=='NR4' or gate=='NR3' or gate=='NR2' or gate=='EO' or gate=='MUX21H' or gate=='FD1S' or gate=='FD1S2'):
        code = 0
    elif gate=='FDMASK' or gate=='FD1':
        code = 1
    else:
        code = np.nan

    return code

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
#obj = vparser('s13207.v')
obj = vparser.vparser('s9234.v')
#obj = vparser('s9234.v')
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

## The cleaned up versions of the nets are:
## wires_main; input_main and out_main
##


####################################################################################################################################################################
# Calculating probability:
####################################################################################################################################################################

G = nx.DiGraph()

# adding input nodes:
for gate in input_main:
    G.add_node(gate, type='input', value=None, switch=0, stage=0, switch_freq=0, orient=0, type1=None, color=0)

#adding output nodes:
for gate in out_main:
    G.add_node(gate, type='output', value=None, switch=0, stage=0, switch_freq=0, orient=0, type1=None, color=0)

# adding gate nodes:
i=0
for gate in node_node:
    G.add_node(gate, type=node_names[i], value=None, switch=0, stage=0, switch_freq=0, orient=0, type1=None, color=0)
    i+=1

# adding wire nodes:
for gate in wires_main:
    G.add_node(gate, type='wire', value=None, switch=0, stage=0, switch_freq=0, orient=0, type1=None, color=0)

num = np.zeros(100)
for net in get_net:
    num[net.__len__()]+=1


# adding edges to the graph:
i=0
for net in get_net:
    rule = read_lib1(node_names[i])
    if rule == np.nan:
        print("Fetal Error")
        break
    pins = list(range(0,len(net)))
    out_pins = []
    out_pins.append(rule)
    input_pins = list(set(pins)-set(out_pins))

    # adding output edges:
    for pins in out_pins:
        G.add_edge(node_node[i], net[pins], dir=0)
        # print(node_node[i], '-->', net[pins])
    # adding input edges:
    for pins in input_pins:
        G.add_edge(net[pins],node_node[i], dir=0)
        # print(net[pins], ' --> ', node_node[i])

    i+=1

# Analysing empty wires:
i=0
empty_wires = []
for net in wires_main:
    if((list(G.predecessors(net)).__len__()==0)):
        #G.remove_node(net)
        empty_wires.append(net)
        i+=1
print(i)

j=0
empty_wires1 = []
for net in wires_main:
    if((list(G.successors(net)).__len__()==0)):
        empty_wires1.append(net)
        j+=1

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
            # print(list(G.predecessors(net)),' --> ', net1)
        G.remove_node(net)

## Removing DFFs:
# i=0
# for nets in list(G.nodes):
#     if G.nodes[nets]['type'] == 'FD1':
#         if len(list(G.predecessors(nets))) != 2:
#             print("prb")
#         for succ in list(G.successors(nets)):
#             G.add_edge(list(G.predecessors(nets))[1], succ)
#
#         G.remove_node(nets)
#         i+=1


########################################################################################################################
## Creating color mapping: ##
########################################################################################################################

# initializing variables:
nodes = list(G.nodes)
green = []
red = []

# setting inputs to green:
green = green.__add__(input_main)
for nets in input_main:
    nodes.remove(nets)

shaddy = 0
gentle = 0
i=0
while(1):
    print(i)
    nodes_len = nodes.__len__()
    for nets in nodes:
        pred_all = list(G.predecessors(nets))
        temp = 1
        for pred in pred_all:
            if pred not in green:
                temp = 0

        if temp == 1:
            green.append(nets)
            nodes.remove(nets)
            G.nodes[nets]['color'] = 1
            gentle+=1

    if nodes.__len__() == nodes_len:
        for nets in nodes:
            pred_all = list(G.predecessors(nets))
            temp = 0
            for pred in pred_all:
                if pred not in green:
                    temp += 1

            if temp <= 1:
                green.append(nets)
                nodes.remove(nets)
                shaddy+=1
                G.nodes[nets]['color'] = 2
                break

    i+=1
    if nodes.__len__() == 0:
        break


########################################################################################################################
## Experiment:
green = []
red = []
error = []
for nets in list(G.nodes):
    if G.nodes[nets]['color'] == 1:
        green.append(nets)
    elif G.nodes[nets]['color'] == 2:
        red.append(nets)
    else:
        print(nets)
        error.append(nets)

# i=0
# for edge in list(I.edges):
#     if I.nodes[edge[0]]['stage'] == I.nodes[edge[1]]['stage']:
#         print(edge)
#         i+=1
########################################################################################################################

# Running simulator:
# for nets in I.nodes():
#     #print(nets)
#     if (I.nodes[nets]['type'] == 'not') | (I.nodes[nets]['type'] == 'dff'):
#         I.nodes[nets]['type1'] = I.nodes[nets]['type']
#     else:
#         I.nodes[nets]['type1'] = re.findall(r'(.+)_', nets)

# Coping G to I:
I = nx.DiGraph()
I = copy.deepcopy(G)

max_stage = 0
for nets in I.nodes():
    print(I.nodes[nets]['stage'])
    if I.nodes[nets]['stage'] > max_stage:
        max_stage = I.nodes[nets]['stage']

input_stage_values = []
#num_iter = 1000000
num_iter = 10
assigned_gates_all = []
for i in range(0,num_iter):
    assigned_gates = 0
    for stage in range(1,max_stage+1):
        if stage==1: # Randomize input stage
            while(1):
                input_values = np.random.choice([0,1], size=len(node_stage[1]), replace=True)
                if list(input_values) not in input_stage_values:
                    break
            input_stage_values.append(list(input_values))
            assigned_gates += len(node_stage[1])
        else:
            for nodes in node_stage[stage]:
                input_net = []
                for pred in list(I.predecessors(nodes)):
                    value = I.nodes[pred]['value']
                    if value == None:
                        print("Fetal Error: Cannot find inputs for ", nodes)
                    input_net.append(value)

                temp = gate_new.Gate(nodes, I.nodes[nodes]['type'])
                out = temp.logic_output(input_net)
                if I.nodes[nodes]['value'] != out:
                    I.nodes[nodes]['switch'] += 1

                I.nodes[nodes]['value'] = out
                assigned_gates+=1
    # print(assigned_gates)
    assigned_gates_all.append(assigned_gates)
    if i%100 == 0:
        print(i)

nx.write_gpickle(I, "s9234_10mRun1.gpickle")
for i in range(0,len(assigned_gates_all)):
    if assigned_gates_all[i] != 5885:
        print("Error")

# I = nx.DiGraph()
# I = nx.read_gpickle("s9234_1mRun1.gpickle")

# Finding rare nodes:
all_gates = []
rare_prob = 0.05
for nodes in list(I.nodes):
    if (I.nodes[nodes]['type'] != 'input') & (I.nodes[nodes]['type'] != 'output'):
        all_gates.append([nodes, I.nodes[nodes]['switch']])

all_gates.sort(key = lambda all_gates: all_gates[1])
rare_nodes = all_gates[0:int(rare_prob*len(all_gates))]


# node_count = int(rare_prob*I.number_of_nodes())
# rare_nodes = []
# for i in range(0,num_iter+1):
#     for nets in list(I.nodes):
#         if (I.nodes[nets]['switch'] == i) & (I.nodes[nets]['type']!='input'):
#             rare_nodes.append(nets)
#             node_count-=1
#     if node_count<=0:
#         break
# x = np.zeros(1000001)
# for net in I.nodes():
#     x[I.nodes[net]['switch']] +=1
# A = []

