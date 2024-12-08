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
        self.nlevels = 0
        self.tree = []
        self.avg_determinism = 0
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

def condition_dump(TM, pre_transition, transition, post_transition):
    print("Level: TM.Level")
    print(f"Sim: {TM.nsims}")
    print(f'{"Curr_State":<10} {pre_transition[0]}')
    print(f'{"prev_state":<10} {pre_transition[1]}')
    print(f'{"left_of_head":<10} {pre_transition[2]}')
    print(f'{"tape":<10} {pre_transition[3]}')
    print(f'{"head_index":<10} {pre_transition[4]}')
    print(f'{"head_char":<10} {pre_transition[5]}')

    print(transition)
    print(f"{post_transition}\n")


def parse_csv(file):
    with open(file, 'r') as file:
        name = file.readline().strip()
        if "Nondeterministic" in name:
            nondeterministic = True
        else:
            nondeterministic = False
        states = file.readline().strip().split(",")
        sigma = file.readline().strip().split(",")
        gamma = file.readline().strip().split(",")
        start = file.readline().strip()
        accept = file.readline().strip()
        reject = file.readline().strip()

        transitions = []

        for line in file:
            transitions.append(line.strip().split(","))

        TM = CTM(name, nondeterministic, states, sigma, gamma, start, accept, reject, transitions)

    return TM

def TM_walk(TM):
    curr_state = TM.start
    prev_state = "N/A"
    left_of_head = ""
    tape = TM.string
    head_index = 0
    head_char = tape[head_index]
    
    #each transition can be shown in a list with the following format
        #[previous state, current state, tape, left_of_head, head_index, head_char]
    frontier = []
    frontier.append([prev_state, curr_state, tape, left_of_head, head_index, head_char])
    TM.tree.append([prev_state, curr_state, tape, left_of_head, head_index, head_char])

    while TM.nsims < TM.flag and frontier:
        pre_transition = frontier.pop(0)
        prev_state, curr_state, tape, left_of_head, head_index, head_char = pre_transition

        post_transitions = []

        if curr_state == TM.reject:
            continue
        
        if curr_state == TM.accept:
            TM.success = True
            break

        #Transition is formatted as follows:
            # [curr_state, head_char, new_state, new_head_char, Head_Movement]

        transitions = [transition for transition in TM.transitions if (transition[0] == curr_state and transition[1] == head_char)]

        if not transitions:
            post_transitions.append([curr_state, TM.reject, tape, left_of_head, head_index, head_char])

        for transition in transitions:
            #updating config based on transition
            #getting states
            prev_state = curr_state
            next_state = transition[2]

            if head_index + 2 <= len(tape):
                #update tape
                new_tape = tape[:head_index] + transition[3] + tape[head_index + 1:] 

                #update head index
                if transition[4] == "R":
                    new_head_index = head_index + 1
                elif transition[4] == "L":
                    new_head_index = head_index - 1

                #update left of head
                new_left_of_head = new_tape[:new_head_index]

                #update head_char
                new_head_char = new_tape[new_head_index]

                post_transition = [prev_state, next_state, new_tape, new_left_of_head, new_head_index, new_head_char]
            else:
                #update tape
                new_tape = tape[:head_index] + transition[3] + tape[head_index + 1:]
                left_of_head = new_tape
                head_char = "N/A"
                #index, leftofhead, and stays same

                post_transition = [prev_state, next_state, new_tape, left_of_head, head_index, head_char]

            #update frontier
            frontier.append(post_transition)
            post_transitions.append(post_transition)

        if len(post_transitions) > 0:
            TM.tree.append(post_transitions)
            TM.nsims += 1
    return

def output(TM):
    #calculate the determinism
    sum = 0
    levels = 0
    ntransitions = 0

    for level in TM.tree:
        levels += 1
        print(level)
        for option in level:
            sum += 1
    avg_determinism = sum / levels

    # #printing results
    # if TM.success == True:
    #     #backtrace
        

    #     #print results
    #     print(f'String accepted in {ntransitions}')
    # else:
    


def main(args=sys.argv[1:]):
    if not args or len(args) < 3:
        usage(1)

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

    #NTM_dump(TM)

    #Walk Through the tree
    TM_walk(TM)

    #print results
    output(TM)


if __name__ == "__main__":
    main()