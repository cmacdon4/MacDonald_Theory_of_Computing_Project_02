#!/usr/bin/env python3

import csv
import sys
import os

class CTM:
    def __init__(self, name, nondeterministic, states, sigma, gamma, start, accept, reject, transitions):
        #File Data
        self.name = name
        self.nondeterministic = nondeterministic
        self.states = states
        self.sigma = sigma
        self.gamma = gamma
        self.start = start
        self.accept = accept
        self.reject = reject
        self.transitions = transitions

        #User Data 
        self.string = ""
        self.flag = 0

        #Simulation Data
        self.nsims = 0
        self.success = False

def usage(status):
    print("Usage Error:")
    print("\t ./traceTM_MacDonald.py $File $String $Termination_Flag\n")

    if (status == 1):
        print("Give a valid file")

    if (status == 2):
         print("Invalid String. Make sure the string has the appropriate chars given the file's sigma (line 3)\n")

    sys.exit(status)

def NTM_dump(TM):
    #helper function
    print(f"Name: {TM.name}")
    print(f"Nondeterministic?: {TM.nondeterministic}")
    print(f"States: {TM.states}")
    print(f"Sigma: {TM.sigma}")
    print(f"Gamma: {TM.gamma}")
    print(f"Accept: {TM.accept}")
    print(f"Reject: {TM.reject}")
    print("transitions:")
    for index, action in enumerate(TM.transitions):
        print(f'{index}) {action}')

    print(f"String: {TM.string}")


def parse_csv(file):
    with open(file, 'r') as file:
        name = file.readline().strip()
        if "Nondeterministic" in name:
            nondeterministic = True
        else:
            nondeterministic = False
        #getting things that arent interable
        states = file.readline().strip().split(",")
        sigma = file.readline().strip().split(",")
        gamma = file.readline().strip().split(",")
        start = file.readline().strip()
        accept = file.readline().strip()
        reject = file.readline().strip()

        transitions = []

        #iterable transitions
        for line in file:
            transitions.append(line.strip().split(","))

        TM = CTM(name, nondeterministic, states, sigma, gamma, start, accept, reject, transitions)

    return TM

def TM_walk(TM):
    curr = TM.start
    #each quad has the following format:
    #left_of_head, curr_state, right_of_head, prev_state
    frontier = [[('', curr, TM.string, None)]]
    tree = []

    #BFS tree transversal for valid transitions
    while frontier and TM.nsims < TM.flag:
        level = frontier.pop(0)
        tree.append(level)

        next_level = []
        for config in level:
            input_seen, curr_state, input_next, _ = config #dont care about previous state
            head_char = input_next[0]

            #getting mathcing transitions
            for transition in [transition for transition in TM.transitions if transition[0] == curr_state]:
                _, next_char, next_state, write_char, direction = transition
                #only valid if mathcing next chars
                if next_char == head_char:
                    #completed a simulation
                    TM.nsims += 1
                    if next_state == TM.accept:
                        #success
                        tree.append([(input_seen + write_char, next_state, "", curr_state)])
                        TM.success = True
                        return tree
                    if direction == "R":
                        #what the config looks like post transition for R
                        next_level.append((input_seen + write_char, next_state, input_next[1:], curr_state))
                    elif direction == "L":
                        #what the config looks like post transition for L
                        next_level.append((input_seen[:-1], next_state, input_seen[-1] + write_char + input_next[1:], curr_state))
              
        #make sure there is not empty levels
        if next_level: frontier.append(next_level)
    return tree

def backtrace(TM, tree):
    path = []
    #config is formatted in following format
    #input_seen, curr_state, input_next, _ = config

    #if it is deterministic then path is straight from the top
    if TM.nondeterministic == False:
        for level in tree:
            for config in level:
                input_seen, curr_state, input_next, _ = config
                path.append(config)
        return path
    else:
        #backtracing by mathcing the path
        path.append(tree[-1][0]) #the success node
        for index, level in enumerate(reversed(tree)):
            if index == 0:
                continue
            for config in level:
                _, curr_state, _, _ = config
                if curr_state == path[-1][3]: #path[-1][3] is the child's prev_state
                    path.append(config)
                    break

        return reversed(path)
    

def output(TM, tree, path):
    #calculate the determinism
    sum_configs = 0
    for level in tree:
        for config in level:
            sum_configs += 1

    nondeterminism =  sum_configs / len(tree)

    #output
    print(f"{"Name":<25}: {TM.name}")
    print(f"{"Nondeterministic?":<25}: {TM.nondeterministic}")
    print(f"{"String":<25}: {TM.string}")
    print(f"{"Transitions Simulated":<25}: {TM.nsims}")
    print(f"{"Degree of Nondeterminism":<25}: {nondeterminism:.3}")
    if TM.success == True:
        print(f"{"Path to accept":<25}: {len(tree) - 1} steps\n")
        print("Path:")
        for config in path:
            #unroll and print config
            input_seen, curr_state, input_next, _ = config
            print(f"{input_seen}{curr_state}{input_next}")

    #if ran out of simulations
    elif TM.nsims == TM.flag:
        print(f"{"Execution stopped after":<25}: {TM.nsims} simulation")

    #if just failed
    else:
        print(f"{"Path to reject":<25}: {len(tree) - 1} steps\n")

def main(args=sys.argv[1:]):
    if not args or len(args) < 3:
        usage(1)

    #getting file
    file = args[0]
    if not os.path.isfile(file):
        print("File does not exist")
        usage(1)


    TM = parse_csv(file)

    #getting string and making sure its valid
    string = args[1]
    for char in string:
        if char not in TM.sigma and not char == '_':
            usage(2)

    #adding an underscore if needed
    if "_" not in string:
        string += "_"
    TM.string = string

    TM.flag = int(args[2])

    #Walk Through the tree
    tree = TM_walk(TM)
    #backtrace to get proper path
    path = backtrace(TM, tree)

    #print results
    output(TM, tree, path)


if __name__ == "__main__":
    main()