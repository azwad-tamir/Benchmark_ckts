import networkx as nx
import re
import os
import io
#from halp.undirected_hypergraph import UndirectedHypergraph
import copy
import matplotlib.pyplot as plt

from itertools import *

class Gate(object):
    """Simulate logic gates.

    Keyword arguments:
    id    -- Block ID
    name  -- Block name
    type  -- Logic gate type
    input -- List of input names
    """
    def __init__(self, name, type, input):
        #self.id = id
        self.name = name.upper()
        self.type = type.upper()
        self.input = input
        #self.score = score
        #self.sorting = sorting

    def logic_output(self, input):
        """Evaluate the output of the current gate based on its type.

        Keyword arguments:
        input -- Input value; could be a list (all) or a single int (NOT gate)
        """
        if (self.type == "INVX1") | (self.type == "INVX2") | (self.type == "INVX4") | (self.type == "INVX8"):
            return self.__not(input)
        elif (self.type == "BUF") | (self.type == "BUFX2") | (self.type == "BUFX4") | (self.type == "CLKBUF1") | (self.type == "CLKBUF2") | (self.type == "CLKBUF3"):
            return self.__buf(input)
        elif (self.type == "OR") | (self.type == "OR2X1") | (self.type == "OR2X2"):
            return self.__or(input)
        elif self.type == "AND":
            return self.__and(input)
        elif (self.type == "AND2X1") | (self.type == "AND2X2"):
            return self.__and(input)
        elif self.type == "AND3":
            return self.__and3(input)
        elif self.type == "XOR":
            return self.__xor(input)
        elif self.type == "NAND":
            return self.__not(self.__and(input))
        elif (self.type == "NAND2X1") | (self.type == "NAND3X1"):
            return self.__not(self.__and(input))
        elif (self.type == "NOR") | (self.type == "NOR3X1"):
            return self.__not(self.__or(input))
        elif self.type == "XNOR2X1":
            return self.__not(self.__xor(input))
        elif self.type == "NAND3":
            return self.__not(self.__and3(input))
        elif (self.type == "DFFPOSX1") | (self.type == "DFFNEGX1") | (self.type == "LATCH"):
            return self.__dffpos(input)
        elif self.type == "NOR3X1":
            return self.__not(self.__or_probability(input))
        elif self.type == "OAI21X1":
            return self.__oai(input)
        elif self.type == "OAI22X1":
            return self.__oai22(input)
        elif self.type == "FAX1":
            return self.__fax1(input)
        else:
            print("ERROR:: Invalid gate type (type = \"" + self.type + "\")")
            print("        Use a valid gate type (NOT, OR, AND, XOR, NAND, NOR, or XNOR).")
            return 0

    def output_probability(self, input):
        """Evaluate the output probability of the current gate based on its type.

        Keyword arguments:
        input -- Input value; could be a list (all) or a single int (NOT gate)

        Note:
        The probabilities are inteneded as the probabilities of the input being one
        """
        print(self.name)
        print(input)
        print("\n")
        if (self.type == "INVX1") | (self.type == "INVX2") | (self.type == "INVX4") | (self.type == "INVX8"):
            probab = self.__not_probability(input)
            # print("DEBUG:: probability: " + str(probab))
            return probab
        elif(self.type == "BUF") | (self.type == "BUFX2") | (self.type == "BUFX4") | (self.type == "CLKBUF1") | (self.type == "CLKBUF2") | (self.type == "CLKBUF3"):
            probab = self.__buf_probability(input)
            # print("DEBUG:: probability: " + str(probab))
            return probab
        elif (self.type == "OR2X1") | (self.type == "OR") | (self.type == "OR2X2"):
            probab = self.__or_probability(input)
            # print("DEBUG:: probability: " + str(probab))
            return probab
        elif self.type == "AND":
            probab = self.__and_probability(input)
            # print("DEBUG:: probability: " + str(probab))
            return probab
        elif (self.type == "AND2X1") | (self.type == "AND2X2"):
            probab = self.__and_probability(input)
            # print("DEBUG:: probability: " + str(probab))
            return probab
        elif self.type == "AND3":
            probab = self.__and3_probability(input)
            return probab
        elif self.type == "XOR":
            probab = self.__xor_probability(input)
            # print("DEBUG:: probability: " + str(probab))
            return probab
        elif self.type == "NAND":
            probab = self.__not_probability(self.__and_probability(input))
            # print("DEBUG:: probability: " + str(probab))
            return probab
        elif self.type == "NAND2X1":
            probab = self.__not_probability(self.__and_probability(input))
            # print("DEBUG:: probability: " + str(probab))
            return probab
        elif self.type == "NAND3X1":
            probab = self.__not_probability(self.__and_probability(input))
            # print("DEBUG:: probability: " + str(probab))
            return probab
        elif self.type == "NAND3":
            probab = self.__not_probability(self.__and3_probability(input))
            return probab
        elif (self.type == "NOR") | (self.type == "NOR3X1"):
            probab = self.__not_probability(self.__or_probability(input))
            # print("DEBUG:: probability: " + str(probab))
            return probab
        elif self.type == "NOR3X1":
            probab = self.__not_probability(self.__or_probability(input))
            # print("DEBUG:: probability: " + str(probab))
            return probab
        elif self.type == "XNOR2X1":
            probab =  self.__not_probability(self.__xor_probability(input))
            # print("DEBUG:: probability: " + str(probab))
            return probab
        elif (self.type == "DFFPOSX1") | (self.type == "DFFNEGX1") | (self.type == "LATCH"):
            probab = self.__dffpos_probability(input)
            return probab
        elif self.type == "OAI21X1":
            probab = self.__oai_probability(input)
            return probab
        elif self.type == "OAI22X1":
            probab = self.__oai22_probability(input)
            return probab
        elif self.type == "FAX1":
            probab = self.__fax1_probability(input)
            return probab
        else:
            print("ERROR:: Invalid gate type (type = \"" + self.type + "\")")
            print("        Use a valid gate type (NOT, OR, AND, XOR, NAND, NOR, or XNOR).")
            return 0

    # def truth_table(self, bit_size):
    #     """Print out the truth table of the logic gate.
    #
    #     This is designed primarily for verifygateclass.py and debugging
    #     purposes to verify each logic implementation.
    #
    #     Keyword arguments:
    #     bit_size -- Maximum number of bits to test
    #     """
    #
    #     # If the gate is a NOT gate, then simply do a basic inverter test for
    #     # 2 inputs.
    #     if self.type == "NOT":
    #         print("I0 OUT")
    #         for i in range(2):
    #             print(str(i).rjust(2) + " ", end="")
    #             print(str(self.logic_output(i)).rjust(2))
    #
    #     # Otherwise, generate a truth table with the specified bit size.
    #     else:
    #         # Create the table headers (I for input and OUT for output).
    #         for i in range(bit_size):
    #             print("I" + str(i) + " ", end="")
    #         print("OUT")
    #
    #         # Generate 2^n bit combinations.
    #         combinations = list(product([0, 1], repeat=bit_size))
    #
    #         # Generate the output for each bit combination.
    #         for combination in combinations:
    #             for bit in combination:
    #                 print(str(bit).rjust(2) + " ", end="")
    #             print(str(self.logic_output(combination)).rjust(2))
    #
    # def print_info(self):
    #     """Print the stored gate information.
    #
    #     This is designed primarily for verifygateclass.py and debugging
    #     purposes to verify the accuracy of each logic implementation.
    #
    #     Keyword arguments:
    #     <None>
    #     """
    #     print("Gate " + str(self.id))
    #     print("    * Name   : " + self.name)
    #     print("    * Type   : " + self.type)
    #     print("    * Inputs : " + str(self.input))

    def __not(self, input):
        """Perform a logic NOT on the input value.

        Keyword arguments:
        input -- Input value
        """
        final_input = None

        # If the input is a list, then take the first element.
        if type(input) is list:
            if (len(input) > 1 ):
                raise Exception('not_prob input > 1 not supported')
            final_input = input[0]

        # Otherwise, take the input as is.
        else:
            final_input = input

        # If the input was still not assigned, then display an error.
        if final_input is None:
            print("ERROR:: Invalid input to NOT gate (input = \"" + input + "\"")

        # Otherwise, evaluate the NOT logic.
        else:
            # If input is logic 1, then return a logic 0.
            if final_input is 1:
                return 0

            # Otherwise, return a logic 1.
            else:
                return 1

    def __not_probability(self, input):
        """Calculate the probability of a logic NOT on the input value.

        Keyword arguments:
        input -- Input value
        """
        final_input = None

        # If the input is a list, then take the first element.
        if type(input) is list:
            if (len(input) > 1 ):
                raise Exception('not_prob input > 1 not supported')
            final_input = input[0]

        # Otherwise, take the input as is.
        else:
            final_input = input

        # If the input was still not assigned, then display an error.
        if final_input is None:
            print("ERROR:: Invalid input to NOT gate (input = \"" + input + "\"")

        # The probabilty of logic not is the same of the input
        else:
            return 1-final_input;

    def __buf(self, input):
        """Perform a logic BUF on the input value.

        Keyword arguments:
        input -- Input value
        """
        final_input = None

        # If the input is a list, then take the first element.
        if type(input) is list:
            if (len(input) > 1 ):
                raise Exception('not_prob input > 1 not supported')
            final_input = input[0]

        # Otherwise, take the input as is.
        else:
            final_input = input

        # If the input was still not assigned, then display an error.
        if final_input is None:
            print("ERROR:: Invalid input to NOT gate (input = \"" + input + "\"")

        # Otherwise, evaluate the NOT logic.
        else:
            return final_input

    def __buf_probability(self, input):
        """Calculate the probability of a logic BUF on the input value.

        Keyword arguments:
        input -- Input value
        """
        final_input = None

        # If the input is a list, then take the first element.
        if type(input) is list:
            if (len(input) > 1 ):
                raise Exception('not_prob input > 1 not supported')
            final_input = input[0]

        # Otherwise, take the input as is.
        else:
            final_input = input

        # If the input was still not assigned, then display an error.
        if final_input is None:
            print("ERROR:: Invalid input to NOT gate (input = \"" + input + "\"")

        # The probabilty of logic not is the same of the input
        else:
            return final_input

    def __dffpos(self, input):
        """Perform a logic BUF on the input value.

        Keyword arguments:
        input -- Input value
        """
        final_input = None

        # If the input is a list, then take the first element.
        if type(input) is list:
            #if (len(input) > 1 ):
            #    raise Exception('not_prob input > 1 not supported')
            final_input = input[0]

        # Otherwise, take the input as is.
        else:
            final_input = input

        # If the input was still not assigned, then display an error.
        if final_input is None:
            print("ERROR:: Invalid input to NOT gate (input = \"" + input + "\"")

        # Otherwise, evaluate the NOT logic.
        else:
            return final_input

    def __dffpos_probability(self, input):
        """Calculate the probability of a logic BUF on the input value.

        Keyword arguments:
        input -- Input value
        """
        final_input = None

        # If the input is a list, then take the first element.
        if type(input) is list:
            #if (len(input) > 1 ):
                #raise Exception('not_prob input > 1 not supported')
            final_input = input[0]

        # Otherwise, take the input as is.
        else:
            final_input = input

        # If the input was still not assigned, then display an error.
        if final_input is None:
            print("ERROR:: Invalid input to NOT gate (input = \"" + input + "\"")

        # The probabilty of logic not is the same of the input
        else:
            return final_input

    def __and(self, input):
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

    def __and_probability(self, input):
        """Calculate the probability of a logic AND on all the input values.

        Keyword arguments:
        input -- List of input values
        """
        # if (len(input) > 2 ):
        #     raise Exception('and input > 2 not supported')

        final_value = 1

        # The probaility of logic and is the multiplication of the input
        # probabilties of being one (e.g. 0.5 * 0.5 = 0.25)
        for value in input:
            final_value *= float(value);

        return final_value

    def __or(self, input):
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

    def __or_probability(self, input):
        """Calculate the probbility of a logic OR on all the input values.

        Keyword arguments:
        input -- List of input values
        """

        # multiple inputs are supported!
        # if (len(input) > 2 ):
        #     print("DEBUG:: probability input: " + str(input))
        #     raise Exception('or_prob input > 2 not supported')

        # The probaility of logic or is the multiplication of the input
        # probabilties of being 0 (1 - prob_of_being_1) (e.g. (1-0.5) * (1-0.5) = 0.25)
        temp_value = 1

        for value in input:
            temp_value *= (1 - float(value))

        return 1 - temp_value

    def __xor(self, input):
        """Perform a logic XOR on all the input values.

        Keyword arguments:
        input -- List of input values
        """
        value = input[0]
        for i in range(1, len(input)):
            # If the stored value is the same as the current input, then set the
            # value to logic 0.
            if value is input[i]:
                value = 0

            # Otherwise, set the value to logic 1.
            else:
                value = 1

        # Return the calculated logic value.
        return value

    def __xor_probability(self, input):
        """Calculate the probability a logic XOR on all the input values.

        Keyword arguments:
        input -- List of input values
        """

        if (len(input) > 2 ):
            raise Exception('xor_prob input > 2 not supported')

        temp_value = 1
        final_value = 0
        for i in input:
            final_value += float(i)
            temp_value *= float(i)

        return final_value - 2 * temp_value

    def __and3(self, input):
        """Perform a logic AND3 on all the input values.

        Keyword arguments:
        input -- List of input values
        """
        # If there is a logic 0 at any moment, then simply return a logic 0.
        for value in input:
            if value is 0:
                return 0

        # Otherwise, return 1 if no logic 0 is found.
        return 1

    def __and3_probability(self, input):
        """Calculate the probability of a logic AND on all the input values.

        Keyword arguments:
        input -- List of input values
        """
        # if (len(input) > 2 ):
        #     raise Exception('and input > 2 not supported')

        final_value = 1

        # The probaility of logic and is the multiplication of the input
        # probabilties of being one (e.g. 0.5 * 0.5 = 0.25)
        for value in input:
            final_value *= float(value);

        return final_value

    def __oai(self, input):
        """Perform a logic OR on all the input values.
        Keyword arguments:
        input -- List of input values
        """
        if input.__len__() != 3:
            print("fetal error")
        # If there is a logic 1 at any moment, then simply return a logic 1.
        input1 = input[0:2]
        x=0
        for value in input1:
            if value is 1:
                x = 1

        y=1
        input2 = [x, input[2]]
        # If there is a logic 0 at any moment, then simply return a logic 0.
        for value in input2:
            if value is 0:
                y = 0

        result = 2
        if y ==1:
            result = 0
        else:
            result = 1

        return result

    def __oai_probability(self, input):
        """Calculate the probbility of a logic OR on all the input values.

        Keyword arguments:
        input -- List of input values
        """

        # multiple inputs are supported!
        # if (len(input) > 2 ):
        #     print("DEBUG:: probability input: " + str(input))
        #     raise Exception('or_prob input > 2 not supported')

        # The probaility of logic or is the multiplication of the input
        # probabilties of being 0 (1 - prob_of_being_1) (e.g. (1-0.5) * (1-0.5) = 0.25)
        temp_value = 1
        input1 = input[0:2]
        for value in input1:
            temp_value *= (1 - float(value))

        x = 1 - temp_value

        input2 = [x, input[2]]
        final_value = 1
        # The probaility of logic and is the multiplication of the input
        # probabilties of being one (e.g. 0.5 * 0.5 = 0.25)
        for value in input2:
            final_value *= float(value);

        x1 = final_value

        return 1-final_value

    def __oai22(self, input):
        """Perform a logic OR on all the input values.
        Keyword arguments:
        input -- List of input values
        """
        if input.__len__() != 4:
            raise Exception("oai22!=4 not supported")
        # If there is a logic 1 at any moment, then simply return a logic 1.
        input1 = input[0:2]
        x=0
        for value in input1:
            if value is 1:
                x = 1

        input2 = input[2:4]
        x1=0
        for value in input2:
            if value is 1:
                x1 = 1

        y=1
        input3 = [x, x1]
        # If there is a logic 0 at any moment, then simply return a logic 0.
        for value in input3:
            if value is 0:
                y = 0

        result = 2
        if y ==1:
            result = 0
        else:
            result = 1

        return result

    def __oai22_probability(self, input):
        """Calculate the probbility of a logic OR on all the input values.

        Keyword arguments:
        input -- List of input values
        """

        # multiple inputs are supported!
        # if (len(input) > 2 ):
        #     print("DEBUG:: probability input: " + str(input))
        #     raise Exception('or_prob input > 2 not supported')

        # The probaility of logic or is the multiplication of the input
        # probabilties of being 0 (1 - prob_of_being_1) (e.g. (1-0.5) * (1-0.5) = 0.25)
        temp_value = 1
        input1 = input[0:2]
        for value in input1:
            temp_value *= (1 - float(value))

        x = 1 - temp_value

        temp_value = 1
        input1 = input[2:4]
        for value in input1:
            temp_value *= (1 - float(value))

        x1 = 1 - temp_value


        input2 = [x, x1]
        final_value = 1
        # The probaility of logic and is the multiplication of the input
        # probabilties of being one (e.g. 0.5 * 0.5 = 0.25)
        for value in input2:
            final_value *= float(value);

        return 1-final_value

    def __fax1(self, input):
        """Perform a logic XOR on all the input values.

        Keyword arguments:
        input -- List of input values
        """
        value = input[0]
        if value == input[1]:
            value = 0
        # Otherwise, set the value to logic 1.
        else:
            value = 1

        # Return the calculated logic value.
        x = value

        value = x
        if value == input[2]:
            value = 0
        # Otherwise, set the value to logic 1.
        else:
            value = 1

        # Return the calculated logic value.
        return value



    def __fax1_probability(self, input):
        """Calculate the probability a logic XOR on all the input values.

        Keyword arguments:
        input -- List of input values
        """

        if (len(input) != 3 ):
            raise Exception('fax1 != 3 not supported')

        temp_value = 1
        final_value = 0
        for i in input[0:2]:
            final_value += float(i)
            temp_value *= float(i)

        x = final_value - 2 * temp_value

        temp_value = 1
        final_value = 0
        for i in [x, input[2]]:
            final_value += float(i)
            temp_value *= float(i)

        return final_value - 2 * temp_value


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
for gate in allin1:
    G.add_node(gate, type='input', prob=0.5, prob_has = 1)

#adding output nodes:
for gate in allout1:
    G.add_node(gate, type='output', prob=0, prob_has = 1)

# adding gate nodes:
i=0
for gate in node_node:
    G.add_node(gate, type=node_names[i], prob=0, prob_has = 0)
    i+=1

# adding wire nodes:
for gate in allwires:
    G.add_node(gate, type='wire', prob=0, prob_has=2)

# adding edges to the graph:
i=0
for net in get_net:
    G.add_edge(node_node[i], net[net.__len__()-1])
    #print(node_node[i] + ' -->  ' + net[net.__len__()-1])
    for net_in in net[0:net.__len__()-1]:
        G.add_edge(net_in,node_node[i])
        #print(net_in, ' --> ', node_node[i])
    i+=1

# Removing empty wires:
for net in allwires:
    if((list(G.predecessors(net)).__len__()==0) | (list(G.successors(net)).__len__()==0)):
        G.remove_node(net)
        #print(net)

    #print(list(G.successors(net)).__len__())
# for net in allwires:
#     if G.has_node(net):
#         for net1 in list(G.predecessors(net)) + list(G.successors(net)):
#             if G.nodes[net1]['type'] == 'wire':
#                 print(net1)

# Removing wires from the graph:
for net in allwires:
    if G.has_node(net):
        if (list(G.predecessors(net)).__len__()) != 1:
            print("Fetal Error: Check wire predecessor")

for net in allwires:
    if G.has_node(net):
        for net1 in list(G.successors(net)):
            G.add_edge(list(G.predecessors(net))[0], net1)
            print(list(G.predecessors(net)),' --> ', net1)
        G.remove_node(net)

# calling Gate class:
I = nx.DiGraph()
I.add_nodes_from(['N1','N2','N3','N6','N7'],type='input', prob=0.5, prob_has = 1)
I.add_nodes_from(['NAND2_1','NAND2_2','NAND2_3','NAND2_4','NAND2_5','NAND2_6'],type='NAND2X1', prob=0, prob_has = 0)
I.add_nodes_from(['N22','N23'],type='output', prob=0, prob_has=1)
I.add_edge('N1','NAND2_1')
I.add_edge('N3','NAND2_1')
I.add_edge('N3','NAND2_2')
I.add_edge('N6','NAND2_2')
I.add_edge('N2','NAND2_3')
I.add_edge('NAND2_2','NAND2_3')
I.add_edge('N7','NAND2_4')
I.add_edge('NAND2_2','NAND2_4')
I.add_edge('NAND2_1','NAND2_5')
I.add_edge('NAND2_3','NAND2_5')
I.add_edge('NAND2_3','NAND2_6')
I.add_edge('NAND2_4','NAND2_6')
I.add_edge('NAND2_5','N22')
I.add_edge('NAND2_6','N23')

def calculate_prob(I, net):
    input = []
    for pred_net in list(I.predecessors(net)):
        if I.nodes[pred_net]['prob_has'] == 0:
            I = calculate_prob(I, pred_net)
        else:
            input.append(I.nodes[pred_net]['prob'])

    A = Gate(net, I.nodes[net]['type'], input)
    I.nodes[net]['prob'] = A.output_probability(input)
    I.nodes[net]['prob_has'] = 1
    return I

net_net = ['NAND2_1','NAND2_2','NAND2_3','NAND2_4','NAND2_5','NAND2_6']
for net in node_node:
    if G.nodes[net]['prob_has'] == 0:
        G = calculate_prob(G,net)

for i in range(0,1000):
    for net in node_node:
        input = []
        if G.nodes[net]['prob_has'] == 0:
            pred_list = list(G.predecessors(net))
            j=0
            for pred in pred_list:
                if G.nodes[pred]['prob_has'] == 0:
                    j=1
                else:
                    input.append(G.nodes[pred]['prob'])
            if j == 0:
                A = Gate(net, G.nodes[net]['type'], input)
                G.nodes[net]['prob'] = A.output_probability(input)
                G.nodes[net]['prob_has'] = 1
                print(net)

# Fining simple cycles:
cycles = list(nx.simple_cycles(G))
nets = list(nx.find_cycle(G, orientation='original'))

#deleting nodes with cycles
num=0
cycles = []
for i in range(0,10000):
    nets = list(nx.find_cycle(G, orientation='original'))
    print(nets)
    G.remove_node(nets[0][0])


print(I.nodes(data='prob'))



list(G.nodes(data=True))[0]
G.add_node(1, time='5pm')
list(G.nodes(data= 'time'))[0][1]




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

