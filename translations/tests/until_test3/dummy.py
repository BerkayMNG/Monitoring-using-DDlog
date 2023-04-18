import re

def compare(fileDDlog, FileLMonPoly):
    DataDDlog = []
    with open(fileDDlog, "r") as f:
        for line in f:
            if("Satisfied:" in line):
                continue

            tuple_temp = re.findall(r'\d+', line)[0:3]
            tuple = [int(x) for x in tuple_temp]
            DataDDlog.append(tuple)

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
            
    #Sort both by ts & id
    DataDDlog.sort(key=lambda x: (x[0],x[2]))
    DataMonPoly.sort(key=lambda x: (x[0],x[2]))
    for elem in DataDDlog:
        if not(elem in DataMonPoly):
            print(elem)

    #for elem in DataMonPoly:
        #if not(elem in  DataDDlog):
            #print(elem)
    print()
    #print(DataDDlog)
    #print()
    #print(DataMonPoly)
    bool = (DataMonPoly == DataDDlog)
    return bool

compare("outputDDlog.txt", "outputMonPoly.txt")