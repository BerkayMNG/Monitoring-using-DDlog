import re
import os
import random




"""
(Used for binary operators such as SINCE and UNTIL)

format_generator_binary will generate/return a new list 'Data_new', which is of the format [(timestamp, [class,identifier, timestamp])]. See below for 
more information. To keep it short: given the list 'Data', we need to get it into the format explained before before generating the concrete .log and .dat files 
which will be fed into the corresponding programs as input. Since it is desirable to choose how to handle events happening at the same timestamp (put it into same timepoint
(I call this "wrapping"), only single events at a timepoint, varying), this function will take care of it given paraneters 'wrapSize', 'vary'.


:param Data:    2D list, where each elemen is of the form [class,identifier,timestamp]. if class = 1 use P(identifier), if class == 2 Q(identifier).
                So timestamp tells when the event occured.
:type Data: list (2D list consisting of integers)

:param wrapSize:       maximal amount of events at a timepoint. If we have e.g. 10 events at a certain timestamp ts, we will divide it into "batches" (nothing to do with batchSize)
                       of Size wrapSize. If events = 4 the 10 events occur at 3 timepoints (4-4-2). WrapSize = -1 means no upperbound. If vary=True, wrapSize will be chosen
                       will be chosen for each timestamp randomly and is between 1 and the initial wrapSize. Do not use vary = True and wrapSize = -1 simultaneously
:type wrapSize:        int

:param vary:    default vary=False, if vary=True the wrapSize will be randomly chosen for each timestamp of the values [1,2,...,wrapSize], where wrapSize in the list is the initial wrapSize.
                Do not use vary = True and wrapSize = -1 simultaneously
:type vary:     bool

:return Data_new:    format is [(timestamp, [[class,identifier, timestamp]])]. For each element the timestamp of the first element of the tuple matches (or should match) with the timestamp of the array of 
                     the second tuple-element
:trype list
"""
def format_generator_binary(Data:list, wrapSize:int, vary=False):

    wrapSize_original = wrapSize
    if not (wrapSize == -1 or wrapSize > 0):
        raise Exception("wrapSize must be eqal -1 or a positive integer.")
    elif(wrapSize == -1 & vary == True):
        raise Exception("Use valid upper bound for wrapSize when using vary.")

    Data.sort(key=lambda x: x[2])
    Data_new = []
    i = 0

    while i < len(Data):
        temp = []
        ts = Data[i][2]
        j = i
        count = 0
        if vary:
            wrapSize = random.randint(1,wrapSize_original)

        while (j < len(Data)) & (ts == Data[j][2]) & (count < wrapSize or wrapSize == -1): #wrapSize == -1 means no restriction in wrapSize
            temp.append(Data[j])
            i = i+1
            j = j+1
            count = count+1
            #python will otherwise evaluate loopcondition -> IndexError
            if j >= len(Data):
                break         
        Data_new.append((ts,temp))
    return Data_new



"""
'logFile_generator_binary' generates the corresponding .log file with name 'nameLog' given the input description in form of a list ('Data'). 
For description of the format of 'Data' see documentation of the function 'format_generator_binary'.

:param Data:    inputs which need to be written in correct form to the .log file
:type Data:     list

:param nameLog: name of the file where Data should be written to.
:type nameLog:  str

:param action:  action perfomed to nameLog, by default "w" (see open() function for other options)
:type action:   string

:return Nothing
:trype None

"""
def logFile_generator_binary(Data:list, nameLog:str, action="w"):

    fileLog = open(nameLog, action)
    length_Data = len(Data)
    i = 0
    while i < length_Data:
        fileLog.write("@" + str(Data[i][0]) + " ")
        temp = Data[i][1]
        length_temp = len(temp)
        k = 0
        while k < length_temp:
            if temp[k][0] == 1:
                fileLog.write("p(" + str(temp[k][1]) + ") ")
            else:
                fileLog.write("q(" + str(temp[k][1]) + ") ")
            k = k + 1
        i = i + 1
        fileLog.write("\n")
    fileLog.close()


"""
'datFile_generator_binary' generates the corresponding .dat file with name 'nameDat' given the input description in form of a list ('Data'). 
For description of the format of 'Data' see documentation of the function 'format_generator_binary'.

:param Data:    inputs which need to be written in correct form to the .dat file
:type Data:     list

:param batchSize:   the used batchSize for the DDlog input
:param batchSize:   int

:param nameLog: name of the file where Data should be written to.
:type nameLog:  str

:param action:  action perfomed to nameLog, by default "w" (see open() function for other options)
:type action:   string

:return Nothing
:trype None
"""
def datFile_generator_binary(Data:list, nameDat:str, batchSize:int, action:str):

    fileDat = open(nameDat, action)
    i = 0
    tp = 0
    while i < len(Data):
        j = 0
        fileDat.write("\n \n")
        fileDat.write("start;\n")
        while (j < batchSize) & (tp + j < len(Data)):
            fileDat.write("insert Timestamp(" + str(tp+j) + "," + str(Data[tp+j][0]) + ");\n")
            temp = Data[tp+j][1]
            k = 0
            while k < len(temp):
                if temp[k][0] == 1:
                    fileDat.write("insert P(" + str(tp+j) + "," + str(temp[k][1]) + ");\n")

                else:
                    fileDat.write("insert Q(" + str(tp+j) + "," + str(temp[k][1]) + ");\n")
                k = k + 1
            j = j + 1
        tp = tp + j
        i =  i + batchSize
        fileDat.write("commit dump_changes;\n")
        fileDat.write("\n \n")
    fileDat.close()
    

"""
Function 'compare_binary' is used to compare outputs of a DDlog program and MonPoly program.

:param fileDDlog: name of a txt file which stores output of a DDlog program
:type fileDDLog: str

:param fileMonPoly: name of a txt file which stores output of a MonPoly program
:type fileDDLog: str

:return: Nothing
:rtype: None
"""
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
            
    #Uncomment below code if you want to check that output is correct but may be out of order

    #DataDDlog.sort(key=lambda x: (x[0],x[2]))
    #DataMonPoly.sort(key=lambda x: (x[0],x[2]))
    bool = (DataMonPoly == DataDDlog)
    return bool


"""
'gen_tests_binary' builds .log and .dat files needed as input for testing/comparing binary operators (UNTIL and SINCE). 'Data' only contains the events and their 
timestamp (e.g. P(2) occured at timestamp 4 -> [1,2,4] is in Data) which need to be translated into concrete input files for ddlog and MonPoly. batchSize, maximum number of events 
at a timepoint etc. are choices which can be specified by using batchSize, wrapSize, vary. Since we only look at formulas containing only either SINCE[min,max] or UNTIL[min,max],
we also need to specify the intervall.

Parameters are self-explanatory and are already described in the documentation of the functions which are called in 'gen_tests_binary'
"""
def gen_tests_binary(Data:str,nameDat:str, nameLog:str, batchSize:int, min:int, max:int, wrapSize=2,vary=False):

    Data.sort(key=lambda x: x[2])
    fileDat = open(nameDat, "w")
    fileDat.write("start;\n")
    fileDat.write("insert Intervall(" + str(abs(min)) + "," + str(max)  + ");\n")
    fileDat.write("commit dump_changes;\n")
    fileDat.close()


    Data = format_generator_binary(Data,wrapSize,vary)
    logFile_generator_binary(Data,nameLog,"w")
    datFile_generator_binary(Data,nameDat,batchSize,"a")

"""

"""
def runTest_binary(path:str, Data:list, datFile:str, logFile:str, min:int, max:int, wrapSize:int, vary:bool):
    for batchsize in [1]: #changed batchsize to one since we don't batch anymore
        gen_tests_binary(Data, datFile,logFile, batchsize, min, max,wrapSize, vary)
        logFile_prefix = logFile[:-4]

        #We don't compile the programm for each intervall & testcase since this uses a lot of memory- instead just provide the intervall as input
        #in the original translation (/Monitoring-using-DDlog/translations) 
        os.system(path + " " + datFile + " > outputDDlog.txt")
        os.system("monpoly -sig " + logFile_prefix+ ".sig -formula " + logFile_prefix + ".mfotl -log " + logFile_prefix+ ".log -nonewlastts  > outputMonPoly.txt")
        passed_this_batchsize = compare_binary(fileDDlog="outputDDlog.txt", FileLMonPoly="outputMonPoly.txt")
        if(not passed_this_batchsize):
            
            print('\x1b[6;30;41m'+'failed with batchsize: ' + str(batchsize) + ' \x1b[0m')
            exit()

        else:
            print('\x1b[6;30;42m'+'passed with batchsize: ' + str(batchsize) + ' \x1b[0m')

        #don't need the output files anymore
        os.system("rm outputDDlog.txt")
        os.system("rm outputMonPoly.txt")


def test_binary(path:str, test_description:str, Data:list, datFile:str, logFile:str, I_min:int, I_max:int, wrapSize:int,vary:bool):
    print('\x1b[6;30;47m' + test_description + ' \x1b[0m')
    runTest_binary(path,Data, datFile, logFile, I_min,I_max,wrapSize,vary)



"""
(Used for unary operators such as NEXT and PREV, similar to function 'format_generator_binary')

format_generator_unary will generate/return a new list 'Data_new', which is of the format [(timestamp, [identifier, timestamp])]. See below for 
more information. To keep it short: given the list 'Data', we need to get it into the format explained before, before generating the concrete .log and .dat files,
which will be fed into the corresponding programs as input. Since it is desirable to choose how to handle events happening at the same timestamp (put it into same timepoint, 
which I call "wrapping", or to have only single events at a timepoint or a random variation), this function will take care of it given paraneters 'wrapSize', 'vary'.


:param Data:    2D list, where each element is of the form [identifier,timestamp]. E.g. [2,5] means P(2) occured at timestamp 5
:type Data:     list (2D list consisting of integers)

:param wrapSize:       maximal amount of events at a timepoint. If we have e.g. 10 events at a certain timestamp ts, we will divide it into "batches" (nothing to do with batchSize)
                       of Size wrapSize. If events = 4 the 10 events occur at 3 timepoints (4-4-2). WrapSize = -1 means no upperbound. If vary=True, wrapSize will be chosen
                       will be chosen for each timestamp randomly and is between 1 and the initial wrapSize. Do not use vary = True and wrapSize = -1 simultaneously
:type wrapSize:        int

:param vary:    default vary=False, if vary=True the wrapSize will be randomly chosen for each timestamp of the values [1,2,...,wrapSize], where wrapSize in the list is the initial wrapSize.
                Do not use vary = True and wrapSize = -1 simultaneously
:type vary:     bool

:return Data_new:    format is [(timestamp, [identifier, timestamp])]. For each element the timestamp of the first element of the tuple matches (or should match) with the timestamp of the array of 
                     the second tuple-element
:trype               list
"""
def format_generator_unary(Data:list, wrapSize:int, vary=False):

    wrapSize_original = wrapSize
    if not (wrapSize == -1 or wrapSize > 0):
        raise Exception("wrapSize must be eqal -1 or a positive integer.")
    elif(wrapSize == -1 & vary == True):
        raise Exception("Use valid upper bound for wrapSize when using vary.")

    Data.sort(key=lambda x: x[1])
    Data_new = []
    i = 0

    while i < len(Data):
        temp = []
        ts = Data[i][1]
        j = i
        count = 0
        if vary:
            wrapSize = random.randint(1,wrapSize_original)

        while (j < len(Data)) & (ts == Data[j][1]) & (count < wrapSize or wrapSize == -1): #wrapSize == -1 means no restriction in wrapSize
            temp.append(Data[j])
            i = i+1
            j = j+1
            count = count+1
            #python will otherwise evaluate loopcondition -> IndexError
            if j >= len(Data):
                break         
        Data_new.append((ts,temp))
    return Data_new


"""
'logFile_generator_unary' generates the corresponding .log file with name 'nameLog' given the input description in form of a list ('Data'). 
For description of the format of 'Data' see documentation of the function 'format_generator_unary'.

:param Data:    inputs which need to be written in correct form to the .log file
:type Data:     list

:param nameLog: name of the file where Data should be written to.
:type nameLog:  str

:param action:  action perfomed to nameLog, by default "w" (see open() function for other options)
:type action:   string

:return Nothing
:trype None

"""
def logFile_generator_unary(Data:list, nameLog:str, action="w"):
    fileLog = open(nameLog, action)
    length_Data = len(Data)
    i = 0
    while i < length_Data:
        fileLog.write("@" + str(Data[i][0]) + " ")
        temp = Data[i][1]
        length_temp = len(temp)

        k = 0
        while k < length_temp:
            fileLog.write("p(" + str(temp[k][0]) + ") ")
            k = k + 1

        i = i + 1
        fileLog.write("\n")
    fileLog.close()


"""
'datFile_generator_unary' generates the corresponding .dat file with name 'nameDat' given the input description in form of a list ('Data'). 
For description of the format of 'Data' see documentation of the function 'format_generator_unary'.

:param Data:    inputs which need to be written in correct form to the .dat file
:type Data:     list

:param batchSize:   the used batchSize for the DDlog input
:param batchSize:   int

:param nameLog: name of the file where Data should be written to.
:type nameLog:  str

:param action:  action perfomed to nameLog, by default "w" (see open() function for other options)
:type action:   string

:return Nothing
:trype None
"""
def datFile_generator_unary(Data:list, nameDat:str, batchSize:int, action:str):

    fileDat = open(nameDat, action)
    i = 0
    tp = 0
    while i < len(Data):
        j = 0
        fileDat.write("start;\n")
        while (j < batchSize) & (tp + j < len(Data)):
            fileDat.write("insert Timestamp(" + str(tp+j) + "," + str(Data[tp+j][0]) + ");\n")
            temp = Data[tp+j][1]
            k = 0
            while k < len(temp):
                fileDat.write("insert P(" + str(tp+j) + "," + str(temp[k][0]) + ");\n")
                k = k + 1

            j = j + 1
        tp = tp + j
        i =  i + batchSize
        fileDat.write("commit dump_changes;\n")
        fileDat.write("\n")
    fileDat.close()


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
    elif(cat == 1):
            with open(fileDDlog, "r") as f:
                for line in f:
                    if("Satisfied:" in line):
                        continue
                    elif("Violations:" in line):
                        continue

                    tuple_temp = re.findall(r'\d+', line)[0:2]
                    if not tuple_temp: #empty
                        continue
                    tuple = [int(x) for x in tuple_temp]
                    DataDDlog.append(tuple)

            #Consider that several id's can be output in a single line (unlike in DDlog) 
            #if they have same timepoint and same timestamp
            DataMonPoly = []
            with open(FileLMonPoly, "r") as f:
                for line in f:
                    tuple_temp = re.findall(r'\d+', line)
                    tuple = []
                    tuple.append(int(tuple_temp[1]))
                    tuple.append(int(tuple_temp[0]))
                    DataMonPoly.append(tuple)

    else:
        raise Exception("Not valid output category.")
            
    #Uncomment below code if you want to check that output is correct but may be out of order

    bool = (DataMonPoly == DataDDlog)
    return bool


"""
'gen_tests_unary' builds .log and .dat files needed as input for testing/comparing unary operators (NEXT and PREV). 'Data' only contains the events and their 
timestamp (e.g. P(2) occured at timestamp 4 -> [2,4] is in Data) which need to be translated into concrete input files for ddlog and MonPoly. batchSize, maximum number of events 
at a timepoint etc. are choices which can be specified by using batchSize, wrapSize, vary. Since we only look at formulas containing only either SINCE[min,max] or UNTIL[min,max],
we also need to specify the intervall.

Most parameters are self-explanatory and are already described in the documentation of the functions which are called in 'gen_tests_unary'. Except viol_or_sat:

:param viol_or_sat: viol_or_sat == -1 we are analysing violations, viol_or_sat == 1 we are analysing satisfactions
:type viol_or_sat:  int

:param id:  identifier if cat == 0, i.e. We are analysing the unary operator with a concrete id (not free variable)
:type id:   int

"""
def gen_tests_unary(cat:int, viol_or_sat:int, Data:str,nameDat:str, nameLog:str, batchSize:int, min:int, max:int, id:int, wrapSize=2,vary=False):
    Data.sort(key=lambda x: x[1])
    fileDat = open(nameDat, "w")
    fileDat.write("start;\n")
    fileDat.write("insert Intervall(" + str(min) + "," + str(max)  + ");\n")
    if (cat == 1):
        fileDat.write("insert Value(" + str(id) + ");\n")
        fileDat.write("insert Viol_or_sat(" + str(viol_or_sat) + ");\n")
    fileDat.write("commit;\n")
    fileDat.close()


    Data = format_generator_unary(Data,wrapSize,vary)
    logFile_generator_unary(Data,nameLog,"w")
    datFile_generator_unary(Data,nameDat,batchSize,"a")


def runTest_unary(path:str,cat:str, viol_or_sat:int, Data:list, datFile:str, logFile:str, min:int, max:int, id:int, wrapSize:int, vary:bool):
    for batchsize in [1]:
        gen_tests_unary(cat, viol_or_sat, Data, datFile,logFile, batchsize, min, max, id, wrapSize, vary)
        logFile_prefix = logFile[:-4]

        #We don't compile the programm for each intervall & testcase since this uses a lot of memory- instead just provide the intervall as input
        #in the original translation (/Monitoring-using-DDlog/translations) 
        os.system(path + " " + datFile + " > outputDDlog.txt")
        
        if(viol_or_sat == -1):
            os.system("monpoly -sig " + logFile_prefix+ ".sig -formula " + logFile_prefix + ".mfotl -log " + logFile_prefix+ ".log -negate -nonewlastts  > outputMonPoly.txt")
        elif(viol_or_sat == 1):
            os.system("monpoly -sig " + logFile_prefix+ ".sig -formula " + logFile_prefix + ".mfotl -log " + logFile_prefix+ ".log -nonewlastts  > outputMonPoly.txt")
        else:
            raise Exception("Please provide correct value for val_or_sat.")
        
        passed_this_batchsize = compare_unary(cat=cat,fileDDlog="outputDDlog.txt", FileLMonPoly="outputMonPoly.txt")
        if(not passed_this_batchsize):
            
            print('\x1b[6;30;41m'+'failed with batchsize: ' + str(batchsize) + ' \x1b[0m')
            exit()

        else:
            print('\x1b[6;30;42m'+'passed with batchsize: ' + str(batchsize) + ' \x1b[0m')

        #don't need the output files anymore
        os.system("rm outputDDlog.txt")
        os.system("rm outputMonPoly.txt")


def test_unary(path:str, test_description:str, cat:int, viol_or_sat:int, Data:list, datFile:str, logFile:str, I_min:int,I_max:int, id:int, wrapSize:int,vary:bool):
    print('\x1b[6;30;47m' + test_description + ' \x1b[0m')
    runTest_unary(path,cat,viol_or_sat,Data, datFile, logFile, I_min,I_max,id,wrapSize,vary)
