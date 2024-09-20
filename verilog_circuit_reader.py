import re
import io
import networkx as nx
import os
import numpy as np
import copy
import matplotlib.pyplot as plt
import random
from itertools import *
import pandas as pd

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
            if iswire:
                self.wires.append(iswire)

            # get inout nets
            isinput = re.findall(input_pattern, self.vcode[i])
            isoutput = re.findall(output_pattern, self.vcode[i])

            # identity input nets
            if isinput:
                inputs = isinput[0].split(", ")  # split each input by '' , ''
                self.allIntputs += inputs
                inputs = [re.sub(index_pattern, '', w) for w in inputs]
                # if 'clk' in inputs:
                #     inputs.remove('clk')
                self.inputnets += inputs  # Get the inputs

            if isoutput:
                outputs = isoutput[0].split(", ")
                self.allOutputs += outputs
                # print("outputs are: ", outputs)
                outputs = [re.sub(index_pattern, '', w) for w in outputs]
                self.outputnets += outputs  # Get the outputs

            isdevice = device_pattern_re.search(self.vcode[i])  # check if the string contains device description

            if isdevice:
                nets = re.findall(net_pattern, self.vcode[i])  # extract all the nets connecting to the device (Wires)
                # print("nets is {}".format(nets))
                nets = [w.replace(' ', '') for w in nets]
                self.getNets.append(nets)
                instances = self.vcode[i].split()  # get the device name and the type as the array [type, name]
                self.node_names.append(instances[0])
                self.node_node.append(instances[1])
                #print("instances is {}".format(instances))
                #print('instances are: ', instances[1])

                # construct dict for the hypergraph
                for count, key in enumerate(nets):
                    isio = re.sub(netindex_pattern, '', key)  # remove [0-9] in netnames
                    if key not in hygraphdict:
                        for i in range(len(instances)):
                            if instances[i] != '':  # get rid of the '' in the instance names
                                if isio in self.inputnets:
                                    hygraphdict[key] = [[instances[i], instances[i + 1], 'input']]
                                elif isio in self.outputnets:
                                    hygraphdict[key] = [[instances[i], instances[i + 1], 'output']]
                                else:
                                    hygraphdict[key] = [[instances[i], instances[i + 1]]]
                                break

                    else:
                        for i in range(len(instances)):
                            if instances[i] != '':  # get rid of the '' in the instance names
                                if isio in self.inputnets:
                                    hygraphdict[key].append([instances[i], instances[i + 1], 'input'])
                                elif isio in self.outputnets:
                                    hygraphdict[key].append([instances[i], instances[i + 1], 'output'])
                                else:
                                    hygraphdict[key].append([instances[i], instances[i + 1]])
                                break

        print(len(self.node_names))
        return hygraphdict

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


# Main file object:
obj = vparser('output_circuit.v')
x = obj.gethygraph()
input_net = obj.inputnets
out_net = obj.outputnets
get_net = obj.getNets
node_names = obj.node_names
allout = obj.allOutputs
allin = obj.allIntputs
node_node = obj.node_node

input_main = input_net
out_main = out_net

########################################################################################################################
# Converting to bench:
with open("output_circuit.bench", "w") as out_circuit:


    # out_circuit.write("module {} ({},{});\n".format(vcode_name,', '.join(input_main), ', '.join(out_main)))
    for inputs in input_main:
        out_circuit.write("INPUT({})\n".format(inputs))

    out_circuit.write("\n")

    for outs in out_main:
        out_circuit.write("OUTPUT({})\n".format(outs))

    out_circuit.write("\n\n")

    i=0
    for gate_type in node_names:
        out_circuit.write("{} = {}({})\n".format(get_net[i][-1], gate_type, ', '.join(get_net[i][0:-1])))
        i+=1

    out_circuit.write("\n")
########################################################################################################################
# Intersection:
net_all = list(set(get_net1_flat + get_net2_flat))
inter_main = list(set(get_net1_flat).intersection(get_net2_flat))
net_all1 = [item for item in get_net1_flat if item not in inter_main]
input_part1 = list(set(net_all1).intersection(allin1))
output_part1 = list(set(net_all1).intersection(allout1))
wires_part1 = list(set(net_all1).intersection(allwires))

net_all2 = [item for item in get_net2_flat if item not in inter_main]
input_part2 = list(set(net_all2).intersection(allin1))
output_part2 = list(set(net_all2).intersection(allout1))
wires_part2 = list(set(net_all2).intersection(allwires))

