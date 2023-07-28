import subprocess
import os
import time
import re


#inputs for programms are of this form
Trace =  list[tuple[int, list[tuple[str, int]]]]


def input_ddlog_gen(events: Trace, filename: str, min:int, max:int):
    nr_tps = len(events)
    with open(filename, 'w') as file:
        file.write("start;\n")
        file.write(f'insert Intervall({min}, {max});\n')
        file.write("commit dump_changes;\n\n")
        for tp in range(nr_tps):
            file.write("start;\n")
            ts, elems = events[tp]
            file.write("insert Timestamp(" + str(tp) + ", " + str(ts) + ");\n")
            for rel, elem in elems:
                file.write("insert " + rel + "(" + str(tp) + ", " + str(elem) + ");\n")
            file.write("commit dump_changes;\n\n")


def input_MonPoly_gen(events: Trace, filename: str):
    with open(filename, 'w') as file:
        for ts,elems in events:
            file.write(f'@{ts} ')
            for rel,elem in elems:
                file.write(rel + f'({elem}) ')
            file.write('\n')


def compare_binary(fileDDlog:str, FileMonPoly:str):
    DataDDlog = []
    with open(fileDDlog, "r") as f:
        for line in f:
            if((line.find("Output{") == 0) or (line.find("Satisfied{") == 0)):
                tuples_temp = re.findall(r'\d+', line)[0:3]
                tuples = [int(x) for x in tuples_temp]
                DataDDlog.append(tuple(tuples))


    #Consider that several id's can be output in a single line (unlike in DDlog) 
    #if they have same timepoint and same timestamp
    DataMonPoly = []
    with open(FileMonPoly, "r") as f:
        for line in f:
            tuples_temp = re.findall(r'\d+', line)
            for id in tuples_temp[2:]:
                tuples = []
                tuples.append(int(tuples_temp[1]))
                tuples.append(int(tuples_temp[0]))
                tuples.append(int(id))
                DataMonPoly.append(tuple(tuples))
        
    
     
    #Uncomment below code if output is correct but is out of order
    #DataDDlog.sort(key=lambda x: (x[0],x[2]))
    #DataMonPoly.sort(key=lambda x: (x[0],x[2]))
    bool = (DataMonPoly == DataDDlog)

    if(False):

        print(DataMonPoly)
        print()
        print()
        setdiff1 = set(DataMonPoly)-set(DataDDlog)
        #print(setdiff1)
        print()
        print()
        print(DataDDlog)
        print()
        print()
        setdiff2 = set(DataDDlog) - set(DataMonPoly)
        #print(setdiff2)
    
    return bool


def runTest(events: Trace, min:int, max:int, ddlog_program:str, MonPoly_program:str, description:str):

    #run ddlog
    input_ddlog = 'input_ddlog.txt'
    input_ddlog_gen(events,input_ddlog,min,max)
    output_ddlog = 'output_ddlog.txt'
    args_ddlog = [ddlog_program]
    subprocess.run(args_ddlog, stdin=open(input_ddlog, "r"), stdout=open(output_ddlog, "w"), stderr=subprocess.PIPE)
    #run MonPoly
    input_MonPoly = 'input_MonPoly.txt'
    input_MonPoly_gen(events,input_MonPoly)
    output_MonPoly = 'output_MonPoly.txt'
    args_MonPoly = ["monpoly", "-sig", f"{MonPoly_program}.sig", "-formula", f"{MonPoly_program}.mfotl", "-log", input_MonPoly, "-nonewlastts"]
    subprocess.run(args_MonPoly, stdin=subprocess.PIPE, stdout=open(output_MonPoly, "w"), stderr=subprocess.PIPE)

    
    time.sleep(1)
    passed = compare_binary(fileDDlog=output_ddlog, FileMonPoly=output_MonPoly)



    print('\x1b[6;30;47m' + description + ' \x1b[0m')

    if(not passed):
        print('\x1b[6;30;41m'+'failed test! \x1b[0m')
        exit()
    else:
        print('\x1b[6;30;42m'+'passed test! \x1b[0m')
    

    #If tests are passed, delete input and output
    subprocess.run(["rm", input_ddlog])
    subprocess.run(["rm", output_ddlog])
    subprocess.run(["rm", input_MonPoly])
    subprocess.run(["rm", output_MonPoly])



"""
Function 'compare_unary' is used to compare outputs of a DDlog program and MonPoly program.

:param cat: "category output", e.g. If we have Formulas of the form NEXT[0,3] P(1), the output is different 
            as in NEXT[0,3] P(x). For cat == 0 there is no free variable in the formula, for cat == 1 the id 
            is a free variable (as shown in the later example)
:type cat:  int

:param fileDDlog: name of a txt file which stores output of a DDlog program
:type fileDDLog: str

:param fileMonPoly: name of a txt file which stores output of a MonPoly program
:type fileDDLog: str

:return: Nothing
:rtype: None
"""
def compare_unary(cat:int,fileDDlog:str, FileLMonPoly:str):
    DataDDlog = []

    if (cat == 0):
        with open(fileDDlog, "r") as f:
            for line in f:
                if("Satisfied:" in line):
                    continue
                elif("Violations:" in line):
                    continue

                tuples_temp = re.findall(r'\d+', line)[0:3]
                tuples = [int(x) for x in tuples_temp]
                DataDDlog.append(tuples)

        #Consider that several id's can be output in a single line (unlike in DDlog) 
        #if they have same timepoint and same timestamp
        DataMonPoly = []
        with open(FileLMonPoly, "r") as f:
            for line in f:
                tuples_temp = re.findall(r'\d+', line)
                
                
                for id in tuples_temp[2:]:

                    tuples = []
                    tuples.append(int(tuples_temp[1]))
                    tuples.append(int(tuples_temp[0]))
                    tuples.append(int(id))
                    DataMonPoly.append(tuples)
    elif(cat == 1):
            with open(fileDDlog, "r") as f:
                for line in f:
                    if("Satisfied:" in line):
                        continue
                    elif("Violations:" in line):
                        continue

                    tuples_temp = re.findall(r'\d+', line)[0:2]
                    if not tuples_temp: #empty
                        continue
                    tuples = [int(x) for x in tuples_temp]
                    DataDDlog.append(tuples)

            #Consider that several id's can be output in a single line (unlike in DDlog) 
            #if they have same timepoint and same timestamp
            DataMonPoly = []
            with open(FileLMonPoly, "r") as f:
                for line in f:
                    tuples_temp = re.findall(r'\d+', line)
                    tuples = []
                    tuples.append(int(tuples_temp[1]))
                    tuples.append(int(tuples_temp[0]))
                    DataMonPoly.append(tuples)

    else:
        raise Exception("Not valid output category.")
            
    #Uncomment below code if you want to check that output is correct but may be out of order

    bool = (DataMonPoly == DataDDlog)
    return bool

def runTest_unary(events: Trace, min:int, max:int, ddlog_program:str, MonPoly_program:str, description:str, cat:int, viol_or_sat:int,):

    #run ddlog
    input_ddlog = 'input_ddlog.txt'
    input_ddlog_gen(events,input_ddlog,min,max)
    output_ddlog = 'output_ddlog.txt'
    args_ddlog = [ddlog_program]
    subprocess.run(args_ddlog, stdin=open(input_ddlog, "r"), stdout=open(output_ddlog, "w"), stderr=subprocess.PIPE)

    #run MonPoly
    input_MonPoly = 'input_MonPoly.txt'
    input_MonPoly_gen(events,input_MonPoly)
    output_MonPoly = 'output_MonPoly.txt'

    args_MonPoly = []
    if(viol_or_sat == -1):
        args_MonPoly = ["monpoly", "-sig", f"{MonPoly_program}.sig", "-formula", f"{MonPoly_program}.mfotl", "-log", input_MonPoly, "-negate", "nonewlastts"]
    elif(viol_or_sat == 1):
        args_MonPoly = ["monpoly", "-sig", f"{MonPoly_program}.sig", "-formula", f"{MonPoly_program}.mfotl", "-log", input_MonPoly,  "nonewlastts"]
    else:
        raise Exception("Please provide correct value for val_or_sat.")
    
    subprocess.run(args_MonPoly, stdin=subprocess.PIPE, stdout=open(output_MonPoly, "w"), stderr=subprocess.PIPE)

    passed = compare_unary(cat=cat,fileDDlog=output_ddlog, FileLMonPoly=output_MonPoly)

    print('\x1b[6;30;47m' + description + ' \x1b[0m')
    if(not passed):
        print('\x1b[6;30;41m'+'failed test! \x1b[0m')
        exit()
    else:
        print('\x1b[6;30;42m'+'passed test! \x1b[0m')
    

    #If tests are passed, delete input and output
    subprocess.run(["rm", input_ddlog])
    subprocess.run(["rm", output_ddlog])
    subprocess.run(["rm", input_MonPoly])
    subprocess.run(["rm", output_MonPoly])
    subprocess.run(["rm",  f"{MonPoly_program}.mfotl"])