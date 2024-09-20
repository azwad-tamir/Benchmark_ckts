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

# # Correcting input output and wire patterns:
# allin1 = []
# for net in allin:
#     net = net.replace(' ','')
#     if net.find('[') != -1:
#         result = re.search('\[(.*):', net)
#         for i in range(0,int(result.group(1))+1):
#             allin1.append("{}[{}]".format(re.search('\](.*)', net).group(1), i))
#     else:
#         allin1.append(net)
#
# allout1 = []
# for net in allout:
#     net = net.replace(' ','')
#     if net.find('[') != -1:
#         result = re.search('\[(.*):', net)
#         for i in range(0,int(result.group(1))+1):
#             allout1.append("{}[{}]".format(re.search('\](.*)', net).group(1), i))
#     else:
#         allout1.append(net)
#
# allwires = []
# for net in wires_main:
#     net = net.replace(' ','')
#     if net.find('[') != -1:
#         result = re.search('\[(.*):', net)
#         for i in range(0,int(result.group(1))+1):
#             allwires.append("{}[{}]".format(re.search('\](.*)', net).group(1), i))
#     else:
#         allwires.append(net)

#
# # part 1 object:
# obj1 = vparser('Part1.v')
# x1 = obj1.gethygraph()
# #input_net1 = obj1.inputnets
# #out_net1 = obj1.outputnets
# get_net1 = obj1.getNets
# get_net1_flat = [item for sublist in get_net1 for item in sublist]
# get_net1_flat = list(set(get_net1_flat))
# node_names1 = obj1.node_names
# #allout1 = obj1.allOutputs
# #allin1 = obj1.allIntputs
# node_node1 = obj1.node_node
# #wires1 = obj1.wires
# in_master = []
#
#
#
#
# # part 2 object:
# obj2 = vparser('Part2.v')
# x2 = obj2.gethygraph()
# #input_net2 = obj2.inputnets
# #out_net2 = obj2.outputnets
# get_net2 = obj2.getNets
# get_net2_flat = [item for sublist in get_net2 for item in sublist]
# get_net2_flat = list(set(get_net2_flat))
# node_names2 = obj2.node_names
# #allout2 = obj2.allOutputs
# #allin2 = obj2.allIntputs
# node_node2 = obj2.node_node
# #wires2 = obj2.wires
#
# ########################################################################################################################
# # Intersection:
# net_all = list(set(get_net1_flat + get_net2_flat))
# inter_main = list(set(get_net1_flat).intersection(get_net2_flat))
# net_all1 = [item for item in get_net1_flat if item not in inter_main]
# input_part1 = list(set(net_all1).intersection(allin1))
# output_part1 = list(set(net_all1).intersection(allout1))
# wires_part1 = list(set(net_all1).intersection(allwires))
#
# net_all2 = [item for item in get_net2_flat if item not in inter_main]
# input_part2 = list(set(net_all2).intersection(allin1))
# output_part2 = list(set(net_all2).intersection(allout1))
# wires_part2 = list(set(net_all2).intersection(allwires))
#
# # cleaning wires:
# allin1 = clean(allin1)
# allout1 = clean(allout1)
# allwires = clean(allwires)
# node_names = clean(node_names)
# node_node = clean(node_node)
# i=0
# for net in get_net:
#     get_net[i] = clean(get_net[i])
#     i+=1
# node_node = clean2(node_node)
#
# input_part1 = clean(input_part1)
# output_part1 = clean(output_part1)
# wires_part1 = clean(wires_part1)
# inter_main = clean(inter_main)
# node_names1 = clean(node_names1)
# node_node1 = clean(node_node1)
# i=0
# for net in get_net1:
#     get_net1[i] = clean(get_net1[i])
#     i+=1
# node_node1 = clean2(node_node1)
#
# input_part2 = clean(input_part1)
# output_part2 = clean(output_part1)
# wires_part2 = clean(wires_part1)
# node_names2 = clean(node_names2)
# node_node2 = clean(node_node2)
# i=0
# for net in get_net2:
#     get_net2[i] = clean(get_net2[i])
#     i+=1
# node_node2 = clean2(node_node2)

########################################################################################################################
# Writing to file:

# Converting to .in file format:
# Changing inputs to I#
# get_net_in = copy.deepcopy(get_net)
# in_num = 1
# for input in allin1:
#     i=0
#     for net in get_net_in:
#         j=0
#         for net_net in net:
#             if net_net == input:
#                 get_net_in[i][j] = "I{}".format(in_num)
#                 #print(get_net_in[i][j])
#             j+=1
#         i+=1
#     in_num+=1
#
# # Changing outputs to #
# get_net_in_out = copy.deepcopy(get_net_in)
# out_num = 1
# for output in allout1:
#     i=0
#     for net in get_net_in_out:
#         j=0
#         for net_net in net:
#             if net_net == output:
#                 get_net_in_out[i][j] = "{}".format(out_num)
#                 #print(get_net_in[i][j])
#             j+=1
#         i+=1
#     out_num+=1
#
# # Changing wires to #
# get_net_in_out_wire = copy.deepcopy(get_net_in_out)
# wire_num = out_num
# for wire in allwires:
#     i=0
#     for net in get_net_in_out_wire:
#         j=0
#         for net_net in net:
#             if net_net == wire:
#                 get_net_in_out_wire[i][j] = "{}".format(wire_num)
#                 #print(get_net_in[i][j])
#             j+=1
#         i+=1
#     wire_num+=1
#
# with open("empty_wires.v", "w") as empty_wires_file:
#     empty_wires_file.write("{};\n".format(', '.join(empty_wires)))
#
# with open("output_circuit.in", "w") as out_circuit:
#     # out_circuit.write("module aes_cipher ({},{});\n".format(', '.join(allin1), ', '.join(allout1)))
#     # out_circuit.write("\n")
#     # out_circuit.write("input {};\n".format(', '.join(allin1)))
#     # out_circuit.write("\n")
#     # out_circuit.write("output {};\n".format(', '.join(allout1)))
#     # out_circuit.write("\n")
#     # out_circuit.write("wire {};\n".format(', '.join(allwires)))
#     # out_circuit.write("\n")
#
#     # for i in wires1:
#     #     out_circuit.write("wire {};\n".format(i))
#     # out_circuit.write("wire {};\n".format(','.join(wire_out)))
#     # out_circuit.write("\n")
#
#     i=0
#     for nodes in node_names:
#         out_circuit.write("{} {} {} {}\n".format(get_net_in_out_wire[i][(get_net_in_out_wire[i].__len__()-1)], node_node[i], nodes, ' '.join(get_net_in_out_wire[i][0:(get_net_in_out_wire[i].__len__()-1)])))
#         i+=1

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

# Generating random inputs:
rand_num_len = input_main.__len__() + list(set(test)).__len__()
input_feed = []
all_feed = []
for i in range(0,rand_num_len):
    num = random.randint(0,1)
    input_feed.append(num)
all_feed.append(input_feed)
# setting clock signal:

i=0
for nets in list(I.nodes):
    if (I.nodes[nets]['type'] == 'input') | (I.nodes[nets]['orient'] == 1):
        I.nodes[nets]['value'] = input_feed[i]
        i+=1

########################################################################################################################
## Experiment:
# for node in list(out_main):
#     print(list(I.predecessors(node)))

# for edges in list(I.edges):
#     if I.edges[edges]["dir"] == 2:
#         print(edges)



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

max_stage = 0
for nets in I.nodes():
    if I.nodes[nets]['stage'] > max_stage:
        max_stage = I.nodes[nets]['stage']

input_stage_values = []
num_iter = 1000000
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

nx.write_gpickle(I, "s9234_1mRun2.gpickle")
for i in range(0,len(assigned_gates_all)):
    if assigned_gates_all[i] != 5885:
        print("Error")

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

