import re
import io
import networkx as nx
import os
import numpy as np
#from halp.undirected_hypergraph import UndirectedHypergraph
import copy
import matplotlib.pyplot as plt
import random
from itertools import *
#import gate_new
import pandas as pd



def gate(gate_type, input1):
    if gate_type == "NOT":
        '''
            Calculate the probability of a logic NOT on the input value.
            Arguments:
            input1 -- Input value
        '''
        final_input = None
        if type(input1) is list:
            if (len(input1) > 1):
                raise Exception('not_prob input > 1 not supported')
            final_input = input1[0]
        else:
            final_input = input1
        if final_input is None:
            print("ERROR:: Invalid input to NOT gate (input = \"" + input1 + "\"")
        else:
            return   1 - final_input;

    if gate_type == "AND":
        '''
            Calculate the probability of a logic AND on all the input values.
            Arguments:
            input -- List of input values
        '''
        final_value = 1
        for value in input1:
            final_value *= float(value);
        return final_value

    if gate_type == "OR":
        '''
            Calculate the probbility of a logic OR on all the input values.
            Arguments:
            input -- List of input values
        '''
        temp_value = 1
        for value in input1:
            temp_value *= (1 - float(value))
        return 1 - temp_value

    if gate_type == "BUFF":
        '''
            Calculate the probability of a logic BUF on the input value.
            Arguments:
            input -- Input value
        '''
        final_input = None
        if type(input1) is list:
            if (len(input1) > 1 ):
                raise Exception('not_prob input > 1 not supported')
            final_input = input1[0]
        else:
            final_input = input1
        if final_input is None:
            print("ERROR:: Invalid input to NOT gate (input = \"" + input + "\"")
        else:
            return final_input

def calculate_prob(gate_type, input1):
    if gate_type == "NOT":
        probab = gate(gate_type="NOT", input1=input1)
    elif gate_type == "OR":
        probab = gate(gate_type="OR", input1=input1)
    elif gate_type == "AND":
        probab = gate(gate_type="AND", input1=input1)
    elif gate_type == "NAND":
        probab = gate(gate_type="NOT", input1=gate(gate_type="AND", input1=input1))
    elif gate_type == "NOR":
        probab = gate(gate_type="NOT", input1=gate(gate_type="OR", input1=input1))
    elif gate_type == "BUFF":
        probab = gate(gate_type="BUFF", input1=input1)
    else:
        print("Fetal ERROR: Gate type not recognized")

    return probab

vcode_name = 'b19_C_C4'
vcode_path = "./final_benchmarks/" + vcode_name + ".bench"
with io.open(vcode_path, "rt") as f:  # rt read as text mode
    code = f.read()

code = code.splitlines()

inputnets = []
outputnets = []
nets = []
wires = []
node_names = []
node_type = []
node_node = []

net_pattern = r'(.+)=(.+)'  # like .abc123(abc123)
input_pattern = r'INPUT\((.+)\)'  # like input abc123
output_pattern = r'OUTPUT\((.+)\)'  # like output abc123

for code_line in code:
    if code_line.startswith("#"):
        continue
    if code_line == '':
        continue
    if re.findall(input_pattern, code_line):
        inputnets.append(re.findall(input_pattern, code_line)[0])
    elif re.findall(output_pattern, code_line):
        outputnets.append(re.findall(output_pattern, code_line)[0])
    elif re.findall(net_pattern, code_line):
        head = re.findall(r'(.+) =', code_line)[0]
        gate_name = re.findall(r'= (.+)\(', code_line)[0]
        input_nets = re.findall(r'\((.+)\)', code_line)[0].replace(' ', '')
        input_nets_list = input_nets.split(',')

        node_type.append(gate_name)
        node_names.append(head)
        node_node.append(input_nets_list)


    else:
        print("Fetal Error: Pattern not found")


# def read_lib1(gate):
#     if (gate=='TX' or gate=='IV' or gate=='BU' or gate=='AN4' or gate=='AN3' or gate=='AN2' or gate=='ND4' or gate=='ND3' or gate=='ND2' or gate=='OR4' or gate=='OR3' or gate=='OR2' or gate=='NR4' or gate=='NR3' or gate=='NR2' or gate=='EO' or gate=='MUX21H' or gate=='FD1S' or gate=='FD1S2'):
#         code = 0
#     elif gate=='FDMASK' or gate=='FD1':
#         code = 1
#     else:
#         code = np.nan
#
#     return code

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

input_net = inputnets
out_net = outputnets

input_main = inputnets
out_main = outputnets
####################################################################################################################################################################
# Calculating probability:
####################################################################################################################################################################

G = nx.DiGraph()

# adding input nodes:
for gates in input_main:
    G.add_node(gates, type='input', prob=None, switch=0, stage=0, switch_freq=0, orient=0, prob_done=0)

# adding gate nodes:
i=0
for gates in node_names:
    G.add_node(gates, type=node_type[i], prob=None, switch=0, stage=0, switch_freq=0, orient=0, prob_done=0)
    i+=1


# adding edges to the graph:
i=0
for line in node_node:
    for pins in line:
        G.add_edge(pins, node_names[i], dir=0)

    i+=1

# Removing empty nodes:
empty_nodes = []
for node in G.nodes:
    if list(G.successors(node)).__len__()==0 and list(G.predecessors(node)).__len__()==0:
        print(node, G.nodes[node])
        empty_nodes.append(node)

for node in empty_nodes:
    G.remove_node(node)
    input_main.remove(node)


# Setting input gate probs to 0.5:
for node in input_main:
    G.nodes[node]['prob'] = 0.5
    G.nodes[node]['prob_done'] = 1

# Creating stages by greening and calculating gate probs:
green = []
red = []
stage = 1
for node in input_main:
    green.append(node)
    G.nodes[node]['stage'] = stage

while 1:
    greening=0
    for node in G.nodes:
        if node in green:
            continue

        temp = 1
        for pred in list(G.predecessors(node)):
            if pred not in green:
                temp=0
        if temp == 1:
            input_values = []
            for pred in list(G.predecessors(node)):
                input_values.append(G.nodes[pred]['prob'])
                if G.nodes[pred]['prob_done'] == 0:
                    print("Fetal Error: input gates are not assigned probs yet")
            green.append(node)
            #print(node)
            if G.nodes[node]['type'] == 'input':
                print("Fetal Error: gate type set as input")
            G.nodes[node]['stage'] = stage
            G.nodes[node]['prob'] = calculate_prob(gate_type=G.nodes[node]['type'], input1=input_values)
            G.nodes[node]['prob_done'] = 1
            #print(node)
            greening+=1

    stage+=1
    print(stage)
    if greening == 0:
        break

for node in G.nodes:
    if node not in green:
        red.append(node)

# ########################################################################################################################
# ## Creating stages:##
# ########################################################################################################################
# node_stage = []
# node_stage.append([])
I = copy.deepcopy(G)
# counter=I.number_of_nodes()
# for nets in input_main:
#     I.nodes[nets]['stage'] = 1
#     counter-=1
#
# current_stage = input_main
# stage_num = 2
#
# for i in range(0,I.number_of_nodes()):
#     temp = []
#     for nets in current_stage:
#         for nets1 in list(I.successors(nets)):
#             if I.nodes[nets1]['stage'] == 0:
#                 I.nodes[nets1]['stage'] = stage_num
#                 temp.append(nets1)
#                 counter-=1
#     stage_num+=1
#     node_stage.append(current_stage)
#     current_stage = temp
#     #print(counter)
#     if counter == 0:
#         break
# node_stage.append(current_stage)
# # Labeling forward and backward edges: 0:unassigned, 1:forward, 2:backward
# forward = 0
# backward = 0
# test = []
#
# for edges in list(I.edges):
#     if I.nodes[edges[0]]['stage'] < I.nodes[edges[1]]['stage']:
#         I.edges[edges]['dir'] = 1
#         forward+=1
#     elif I.nodes[edges[0]]['stage'] >= I.nodes[edges[1]]['stage']:
#         I.edges[edges]['dir'] = 2
#         backward+=1
#         I.nodes[edges[0]]['orient'] = 1
#         test.append(edges[0])

# # Generating random inputs:
# rand_num_len = input_main.__len__() -2 + list(set(test)).__len__()
# input_feed = []
# all_feed = []
# for i in range(0,rand_num_len):
#     num = random.randint(0,1)
#     input_feed.append(num)
# all_feed.append(input_feed)
# # setting clock signal:

# #######################################################################################################################
# ## input sandbox:
#
# # Creating 1M sample of size input_main:
# input_num = input_main.__len__()
# sample_size = 2**input_num
# a = []
# for i in range(0,1000000):
#     while 1:
#         temp = random.randint(0,sample_size-1)
#         if temp not in a:
#             a.append(temp)
#             break
#     if (len(a) % 1000) == 0:
#         print(len(a))
#
# # # Creating 1 sample of size input_main + backward_node_len:
# # rand_num_len = input_main.__len__() + list(set(test)).__len__()
# # input_feed = []
# # for i in range(0,rand_num_len):
# #     num = random.randint(0,1)
# #     input_feed.append(num)
#
# # x = []
# # for i in range(0, len(a)):
# #    x.append(str(bin(a[i])))
# # print(x.zfill(6))
# # b = format(1, 'b').zfill(8)
# # print(b)
# # print(b[0])
#
#
#
#
# # Assigning input feed to input and reverse nodes:
# i=0
# for nets in list(I.nodes):
#     if (I.nodes[nets]['type'] == 'input'):
#         I.nodes[nets]['value'] = input_feed[i]
#         i+=1
#
# ########################################################################################################################
# ## Experiment:
# # for node in list(out_main):
# #     print(list(I.predecessors(node)))
#
# # for edges in list(I.edges):
# #     if I.edges[edges]["dir"] == 2:
# #         print(edges)
#
#
#
# # i=0
# # for edge in list(I.edges):
# #     if I.nodes[edge[0]]['stage'] == I.nodes[edge[1]]['stage']:
# #         print(edge)
# #         i+=1
# ########################################################################################################################
#
# # Running simulator:
# # for nets in I.nodes():
# #     #print(nets)
# #     if (I.nodes[nets]['type'] == 'not') | (I.nodes[nets]['type'] == 'dff'):
# #         I.nodes[nets]['type1'] = I.nodes[nets]['type']
# #     else:
# #         I.nodes[nets]['type1'] = re.findall(r'(.+)_', nets)
#
# max_stage = 0
# for nets in I.nodes():
#     if I.nodes[nets]['stage'] > max_stage:
#         max_stage = I.nodes[nets]['stage']
#
#
# for run in range(1,5):
#     input_counter = 0
#     input_stage_values = []
#     num_iter = 1000000
#     assigned_gates_all = []
#     for i in range(0, num_iter):
#         assigned_gates = 0
#         for stage in range(1, max_stage + 1):
#             if stage == 1:  # Randomize input stage
#                 x = format(a[input_counter], 'b').zfill(input_num)
#                 # Assigning input feed to input and reverse nodes:
#                 j = 0
#                 for nets in list(I.nodes):
#                     if (I.nodes[nets]['type'] == 'input'):
#                         I.nodes[nets]['value'] = x[j]
#                         j += 1
#                 input_counter+=1
#                 # clk_master = int(not clk_master)
#                 # I.nodes['CK']['value'] = clk_master
#                 # I.nodes['VDD']['value'] = 1
#                 assigned_gates += len(node_stage[1])
#
#             else:
#                 for nodes in node_stage[stage]:
#                     input_net = []
#                     for pred in list(I.predecessors(nodes)):
#                         value = I.nodes[pred]['value']
#                         if value == None:
#                             print("Fetal Error: Cannot find inputs for ", nodes)
#                         input_net.append(value)
#
#                     temp = gate_new.Gate(nodes, I.nodes[nodes]['type'])
#                     out = temp.logic_output(input_net)
#                     if I.nodes[nodes]['value'] != out:
#                         I.nodes[nodes]['switch'] += 1
#
#                     I.nodes[nodes]['value'] = out
#                     assigned_gates += 1
#         # print(assigned_gates)
#         assigned_gates_all.append(assigned_gates)
#         if i % 100 == 0:
#             print(run, ': ', i)
#

file_name = './final_benchmarks/' + vcode_name + '_no_loop_run' + '.gpickle'
nx.write_gpickle(I, file_name)
#     # for i in range(0, len(assigned_gates_all)):
#     #     if assigned_gates_all[i] != 5885:
#     #         print("Error")
#
# # # Finding rare nodes:
prob_values = []
rare_prob = 0.05
for node in I.nodes:
   prob_values.append([node, I.nodes[node]['prob']])

# for node in I.nodes:
#    prob_values.append(I.nodes[node]['prob'])

prob_values.sort(key = lambda prob_values: prob_values[1])
# prob_values.sort(key = lambda prob_values: prob_values)
rare_nodes = prob_values[0:int(rare_prob*len(prob_values))]
for i in range(0,len(prob_values)):
    if prob_values[i][1] > 0.05:
        break

# Creating histogram:
prob_values1 = []
for values in prob_values:
    prob_values1.append(values[1])

plt.hist(prob_values1)

# # all_gates = []
# # rare_prob = 0.05
# # for nodes in list(I.nodes):
# #     if (I.nodes[nodes]['type'] != 'input') & (I.nodes[nodes]['type'] != 'output'):
# #         all_gates.append([nodes, I.nodes[nodes]['switch']])
# #
# # all_gates.sort(key = lambda all_gates: all_gates[1])
# # rare_nodes = all_gates[0:int(rare_prob*len(all_gates))]
#
#
# # node_count = int(rare_prob*I.number_of_nodes())
# # rare_nodes = []
# # for i in range(0,num_iter+1):
# #     for nets in list(I.nodes):
# #         if (I.nodes[nets]['switch'] == i) & (I.nodes[nets]['type']!='input'):
# #             rare_nodes.append(nets)
# #             node_count-=1
# #     if node_count<=0:
# #         break
# # x = np.zeros(1000001)
# # for net in I.nodes():
# #     x[I.nodes[net]['switch']] +=1
# # A = []
#
