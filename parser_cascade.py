import networkx as nx
import re
import os
import io
from halp.undirected_hypergraph import UndirectedHypergraph

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

obj = vparser('aes_cipher.v')
x = obj.gethygraph()
input_net = obj.inputnets
out_net = obj.outputnets
get_net = obj.getNets
node_names = obj.node_names
allout = obj.allOutputs
allin = obj.allIntputs
node_node = obj.node_node
wires = obj.wires
wires_new = [item for sublist in wires for item in sublist]
# get_net_all = list(set(get_net_all))
# out_out = input_net
wires1 = []
for i in wires_new:
    temp = str(i).replace(' ','')
    wires1.append(temp.replace(',',', '))
with open("output_circuit.v", "w") as out_circuit:


    out_circuit.write("module aes_cipher ({},{});\n".format(', '.join(input_net), ', '.join(out_net)))
    out_circuit.write("\n")
    out_circuit.write("input {};\n".format(', '.join(allin)))
    out_circuit.write("\n")
    out_circuit.write("output {};\n".format(', '.join(allout)))
    out_circuit.write("\n")
    for i in wires1:
        out_circuit.write("wire {};\n".format(i))
    # out_circuit.write("wire {};\n".format(','.join(wire_out)))
    # out_circuit.write("\n")

    i=0
    for nodes in node_names:
        out_circuit.write("{} {} ({}, {});\n".format(nodes, node_node[i], get_net[i][(get_net[i].__len__()-1)], ', '.join(get_net[i][0:(get_net[i].__len__()-1)])))
        i+=1
