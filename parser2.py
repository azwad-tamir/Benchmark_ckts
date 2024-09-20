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

wires_main = []
for net in wires1:
    wire2 = net.replace(' ', '')
    wire3 = wire2.split(",")
    wires_main.extend(wire3)



# Correcting input output and wire patterns:
allin1 = []
for net in allin:
    net = net.replace(' ','')
    if net.find('[') != -1:
        result = re.search('\[(.*):', net)
        for i in range(0,int(result.group(1))+1):
            allin1.append("{}[{}]".format(re.search('\](.*)', net).group(1), i))
    else:
        allin1.append(net)

allout1 = []
for net in allout:
    net = net.replace(' ','')
    if net.find('[') != -1:
        result = re.search('\[(.*):', net)
        for i in range(0,int(result.group(1))+1):
            allout1.append("{}[{}]".format(re.search('\](.*)', net).group(1), i))
    else:
        allout1.append(net)

allwires = []
for net in wires_main:
    net = net.replace(' ','')
    if net.find('[') != -1:
        result = re.search('\[(.*):', net)
        for i in range(0,int(result.group(1))+1):
            allwires.append("{}[{}]".format(re.search('\](.*)', net).group(1), i))
    else:
        allwires.append(net)


# part 1 object:
obj1 = vparser('Part1.v')
x1 = obj1.gethygraph()
#input_net1 = obj1.inputnets
#out_net1 = obj1.outputnets
get_net1 = obj1.getNets
get_net1_flat = [item for sublist in get_net1 for item in sublist]
get_net1_flat = list(set(get_net1_flat))
node_names1 = obj1.node_names
#allout1 = obj1.allOutputs
#allin1 = obj1.allIntputs
node_node1 = obj1.node_node
#wires1 = obj1.wires
in_master = []




# part 2 object:
obj2 = vparser('Part2.v')
x2 = obj2.gethygraph()
#input_net2 = obj2.inputnets
#out_net2 = obj2.outputnets
get_net2 = obj2.getNets
get_net2_flat = [item for sublist in get_net2 for item in sublist]
get_net2_flat = list(set(get_net2_flat))
node_names2 = obj2.node_names
#allout2 = obj2.allOutputs
#allin2 = obj2.allIntputs
node_node2 = obj2.node_node
#wires2 = obj2.wires

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

# cleaning wires:
allin1 = clean(allin1)
allout1 = clean(allout1)
allwires = clean(allwires)
node_names = clean(node_names)
node_node = clean(node_node)
i=0
for net in get_net:
    get_net[i] = clean(get_net[i])
    i+=1
node_node = clean2(node_node)

input_part1 = clean(input_part1)
output_part1 = clean(output_part1)
wires_part1 = clean(wires_part1)
inter_main = clean(inter_main)
node_names1 = clean(node_names1)
node_node1 = clean(node_node1)
i=0
for net in get_net1:
    get_net1[i] = clean(get_net1[i])
    i+=1
node_node1 = clean2(node_node1)

input_part2 = clean(input_part1)
output_part2 = clean(output_part1)
wires_part2 = clean(wires_part1)
node_names2 = clean(node_names2)
node_node2 = clean(node_node2)
i=0
for net in get_net2:
    get_net2[i] = clean(get_net2[i])
    i+=1
node_node2 = clean2(node_node2)

########################################################################################################################
# Writing to file:

# main file:
with open("output_circuit.v", "w") as out_circuit:
    out_circuit.write("module aes_cipher ({},{});\n".format(', '.join(allin1), ', '.join(allout1)))
    out_circuit.write("\n")
    out_circuit.write("input {};\n".format(', '.join(allin1)))
    out_circuit.write("\n")
    out_circuit.write("output {};\n".format(', '.join(allout1)))
    out_circuit.write("\n")
    out_circuit.write("wire {};\n".format(', '.join(allwires)))
    out_circuit.write("\n")
    # for i in wires1:
    #     out_circuit.write("wire {};\n".format(i))
    # out_circuit.write("wire {};\n".format(','.join(wire_out)))
    # out_circuit.write("\n")

    i=0
    for nodes in node_names:
        out_circuit.write("{} {} ({}, {});\n".format(nodes, node_node[i], get_net[i][(get_net[i].__len__()-1)], ', '.join(get_net[i][0:(get_net[i].__len__()-1)])))
        i+=1

# Part1 file:
with open("Part1_out.v", "w") as out_circuit:
    #out_circuit.write("module aes_cipher ({},{});\n".format(', '.join(input_net), ', '.join(out_net)))
    #out_circuit.write("\n")
    #out_circuit.write("input {};\n".format(', '.join(allin)))
    #out_circuit.write("\n")
    #out_circuit.write("output {};\n".format(', '.join(allout)))
    #out_circuit.write("\n")
    #for i in wires1:
        #out_circuit.write("wire {};\n".format(i))
    # out_circuit.write("wire {};\n".format(','.join(wire_out)))
    # out_circuit.write("\n")
    out_circuit.write("module aes_cipher ({},{});\n".format(', '.join(input_part1), ', '.join(output_part1)))
    out_circuit.write("\n")
    out_circuit.write("input {};\n".format(', '.join(input_part1)))
    out_circuit.write("\n")
    out_circuit.write("output {};\n".format(', '.join(output_part1)))
    out_circuit.write("\n")
    out_circuit.write("wire {};\n".format(', '.join(wires_part1)))
    out_circuit.write("\n")
    out_circuit.write("inout {};\n".format(', '.join(inter_main)))
    out_circuit.write("\n")
    i=0
    for nodes1 in node_names1:
        out_circuit.write("{} {} ({}, {});\n".format(nodes1, node_node1[i], get_net1[i][(get_net1[i].__len__()-1)], ', '.join(get_net1[i][0:(get_net1[i].__len__()-1)])))
        i+=1

# Part2 file:
with open("Part2_out.v", "w") as out_circuit:
    #out_circuit.write("module aes_cipher ({},{});\n".format(', '.join(input_net), ', '.join(out_net)))
    #out_circuit.write("\n")
    #out_circuit.write("input {};\n".format(', '.join(allin)))
    #ut_circuit.write("\n")
    #out_circuit.write("output {};\n".format(', '.join(allout)))
    #out_circuit.write("\n")
    #for i in wires1:
        #out_circuit.write("wire {};\n".format(i))
    # out_circuit.write("wire {};\n".format(','.join(wire_out)))
    # out_circuit.write("\n")
    out_circuit.write("module aes_cipher ({},{});\n".format(', '.join(input_part2), ', '.join(output_part2)))
    out_circuit.write("\n")
    out_circuit.write("input {};\n".format(', '.join(input_part2)))
    out_circuit.write("\n")
    out_circuit.write("output {};\n".format(', '.join(output_part2)))
    out_circuit.write("\n")
    out_circuit.write("wire {};\n".format(', '.join(wires_part2)))
    out_circuit.write("\n")
    out_circuit.write("inout {};\n".format(', '.join(inter_main)))
    out_circuit.write("\n")
    i=0
    for nodes2 in node_names2:
        out_circuit.write("{} {} ({}, {});\n".format(nodes2, node_node2[i], get_net2[i][(get_net2[i].__len__()-1)], ', '.join(get_net2[i][0:(get_net2[i].__len__()-1)])))
        i+=1