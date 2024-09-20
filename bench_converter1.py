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
#import gate_new
import pandas as pd

def gate_converter(gate_type, pin_num):
    pin_count = str(pin_num)
    if (gate_type=="AND") or (gate_type=="OR") or (gate_type=="NAND") or (gate_type=="NOR") or (gate_type=="XOR") or (gate_type=="XNOR"):
        gate_out = gate_type + pin_count + "X1_RVT"
    elif (gate_type=="DFF") or (gate_type=="BUFF"):
        gate_out = "DFFX1_RVT"
    elif (gate_type=="NOT"):
        gate_out = "INVX1"
    else:
        print("Gate type not recognized!!")
        gate_out = None

    return gate_out

# gate_converter(gate_type="CLK", pin_num=3)

vcode_name = "b01_C"
# vcode_name_full = './final_benchmarks/output_circuits/' + vcode_name + '_inputed' + '.bench'
vcode_name_full = vcode_name  + '.bench'
with io.open(vcode_name_full, "rt") as f:  # rt read as text mode
    code = f.read()

code = code.splitlines()
# line = []
# for i in range(len(code)):
#     if not (code[i].startswith('#') or code[i] == ''):
#         line.append(code[i])


inputnets = []
outputnets = []
nets = []
wires = []
node_names = []
node_type = []
node_node = []
pos_wires = []

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
        pos_wires.append(head)
        for net in input_nets_list:
            pos_wires.append(net)

    else:
        print("Fetal Error: Pattern not found")


input_net = inputnets
out_net = outputnets

input_main = inputnets
out_main = outputnets

wires = []
for i in range(len(node_node)):
    wires.append(node_names[i])
    for j in range(len(node_node[i])):
        wires.append(node_node[i][j])

wires = list(set(wires))
for i in range(len(input_main)):
    if input_main[i] in wires:
        wires.remove(input_main[i])

for i in range(len(out_main)):
    if out_main[i] in wires:
        wires.remove(out_main[i])

####################################################################################################################################################################
# Generating and saving networkx graph:
####################################################################################################################################################################

G = nx.DiGraph()

# adding input nodes:
for gates in input_main:
    G.add_node(gates, type='input')

# adding output nodes:
for gates in out_main:
    G.add_node(gates, type='output')

# adding gate nodes:
i=0
node_id_list = []
for gates in node_names:
    node_ID = 'G' + str(i)
    node_id_list.append(node_ID)
    G.add_node(node_ID, type=node_type[i])
    i+=1

# adding wire nodes:
for wire in wires:
    G.add_node(wire, type='wire')

# adding edges to the graph:
i=0
for line in node_node:
    G.add_edge(node_id_list[i], node_names[i], type='output')
    for pins in line:
        G.add_edge(pins, node_id_list[i], type='input')

    i+=1

# Saving networkx graph:
nx.readwrite.write_gml(G, vcode_name+".gml")


# # Removing empty nodes:
# empty_nodes = []
# for node in G.nodes:
#     if list(G.successors(node)).__len__()==0 and list(G.predecessors(node)).__len__()==0:
#         print(node, G.nodes[node])
#         empty_nodes.append(node)
#
# for node in empty_nodes:
#     G.remove_node(node)
#     input_main.remove(node)
#
#
# pos_wires1 = list(set(pos_wires))
# for net in inputnets:
#     if net in pos_wires1:
#         pos_wires1.remove(net)
#
# for net in outputnets:
#     if net in pos_wires1:
#         pos_wires1.remove(net)
#
# out_circuit_path = './final_benchmarks/output_circuits/' + vcode_name + '.v'
# with open(out_circuit_path, "w") as out_circuit:
#
#
#     out_circuit.write("module {} ({},{});\n".format(vcode_name,', '.join(input_main), ', '.join(out_main)))
#     out_circuit.write("\n")
#     out_circuit.write("input {};\n".format(', '.join(input_main)))
#     out_circuit.write("\n")
#     out_circuit.write("output {};\n".format(', '.join(out_main)))
#     out_circuit.write("\n")
#     out_circuit.write("wire {};".format(', '.join(pos_wires1)))
#     out_circuit.write("\n")
#     out_circuit.write("\n")
#
#     # for i in wires1:
#     #     out_circuit.write("wire {};\n".format(i))
#     # # out_circuit.write("wire {};\n".format(','.join(wire_out)))
#     # # out_circuit.write("\n")
#
#     i=0
#     gate_ID = 0
#     pin_names = ['A', 'B', 'C', 'D', 'Y']
#     for nodes in node_names:
#         gate_name = "Gate" + str(gate_ID)
#         node_node_encap = []
#         j=0
#         for port in node_node[i]:
#             temp_name = '.' + pin_names[j] + '(' + port + ')'
#             j+=1
#             node_node_encap.append(temp_name)
#
#         node_out_encap = '.' + pin_names[-1] + '(' + nodes + ')'
#
#         node_type_RVT = gate_converter(gate_type=node_type[i], pin_num=len(node_node[i]))
#         out_circuit.write("{} {} ( {}, {} );\n".format(node_type_RVT, gate_name, ', '.join(node_node_encap) , node_out_encap))
#         i+=1
#         gate_ID += 1
#
#     out_circuit.write("endmodule")