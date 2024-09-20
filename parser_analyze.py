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

# Putting saved graph names in a list:
circuit_name = "s9234_1mRun_new"
runs = range(0,5)
graphs = []
for run in runs:
    graph_name = circuit_name + str(run) + ".gpickle"
    graphs.append(graph_name)

all_gates_main = []
zero_nodes_main = []
all_graphs = []
# Reading in the graphs:
for graph in graphs:
    A1 = nx.read_gpickle(graph)
    all_graphs.append(A1)
    # Finding rare nodes:
    all_gates = []
    rare_prob = 0.05
    for nodes in list(A1.nodes):
        if (A1.nodes[nodes]['type'] != 'input') & (A1.nodes[nodes]['type'] != 'output'):
            all_gates.append([nodes, A1.nodes[nodes]['switch']])

    all_gates_main.append(all_gates)

    zero_gates = []
    for gates in all_gates:
        if gates[1] == 0:
            zero_gates.append(gates[0])

    zero_nodes_main.append(zero_gates)


# all_gates.sort(key = lambda all_gates: all_gates[1])
# rare_nodes = all_gates[0:int(rare_prob*len(all_gates))]

# Finding common nodes:
inter_set = []
for zero_nodes in zero_nodes_main:
    inter_set.append(set(zero_nodes))

intersect_list = list(set.intersection(*map(set,inter_set)))

# Intersect analyze sandbox:
orient = []
for nodes in intersect_list:
    orient.append([all_graphs[0].nodes[nodes]['orient'], all_graphs[1].nodes[nodes]['orient'], all_graphs[2].nodes[nodes]['orient'], all_graphs[3].nodes[nodes]['orient'], all_graphs[4].nodes[nodes]['orient']])

vcode_name = "b01_C.bench"
with io.open(vcode_name, "rt") as f:  # rt read as text mode
    code = f.read()

code = code.splitlines()

inputnets = []
outputnets = []
nets = []
wires = []
node_names = []
node_node = []

net_pattern = r'(.+)=(.+))'  # like .abc123(abc123)
# device_pattern = r'\.\w*\('  # include .abc123(
input_pattern = r'INPUT\((.+)\)'  # like input abc123
output_pattern = r'OUTPUT\((.+)\)'  # like output abc123

for code_line in code:
    if code_line.startswith("#"):
        continue
    elif code_line == "":
        continue
    elif re.findall(input_pattern, code_line):
        inputnets.append(re.findall(input_pattern, code_line)[0])
    elif re.findall(output_pattern, code_line):
        outputnets.append(re.findall(output_pattern, code_line)[0])
    elif re.findall(net_pattern, code_line):
        head = re.findall(r'(.+) =', code_line)[0]
        gate = re.findall(r'= (.+)\(', code_line)[0]
        input_nets = re.findall(r'\((.+)\)', code_line)[0].replace(' ', '')
        input_nets_list = input_nets.split(',')
        if head not in wires:
            wires.append(head)
        for nets in input_nets_list:
            if nets not in wires:
                wires.append(nets)

    else:
        print("Fetal Error: Pattern not found")