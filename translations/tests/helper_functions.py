import subprocess
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


def compare_binary(fileDDlog:str, FileLMonPoly:str):
    DataDDlog = []
    with open(fileDDlog, "r") as f:
        for line in f:
            if("Output:" in line):
                continue

            tuple_temp = re.findall(r'\d+', line)[0:3]
            tuple = [int(x) for x in tuple_temp]
            DataDDlog.append(tuple)

    #Consider that several id's can be output in a single line (unlike in DDlog) 
    #if they have same timepoint and same timestamp
    DataMonPoly = []
    with open(FileLMonPoly, "r") as f:
        for line in f:
            tuple_temp = re.findall(r'\d+', line)
            for id in tuple_temp[2:]:
                tuple = []
                tuple.append(int(tuple_temp[1]))
                tuple.append(int(tuple_temp[0]))
                tuple.append(int(id))
                DataMonPoly.append(tuple)    
     
    #Uncomment below code if output is correct but is out of order
    #DataDDlog.sort(key=lambda x: (x[0],x[2]))
    #DataMonPoly.sort(key=lambda x: (x[0],x[2]))
    bool = (DataMonPoly == DataDDlog)

    if(not bool):
        print(DataDDlog)
        print()
        print(DataMonPoly)
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
    args_MonPoly = ["monpoly", "-sig", f"{MonPoly_program}.sig", "-formula", f"{MonPoly_program}.mfotl", "-log", input_MonPoly, "-verified"]
    subprocess.run(args_MonPoly, stdin=subprocess.PIPE, stdout=open(output_MonPoly, "w"), stderr=subprocess.PIPE)

    passed = compare_binary(fileDDlog=output_ddlog, FileLMonPoly=output_MonPoly)

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

