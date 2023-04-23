import re
import os

#Each event at a 
def no_wrap(Data,nameDat, nameLog, batchSize):
        fileDat = open(nameDat, "a")
        fileLog = open(nameLog, "a")
        size = len(Data)
        i = 0
        tp = 0
        while i <= size:
            j = 0
            fileDat.write("start;\n")

            while (j < batchSize) & (tp + j < size):
                fileDat.write("insert Timestamp(" + str(tp+j) + "," + str(Data[tp+j][2]) + ");\n")
                if(Data[tp+j][0] == 1):
                    fileDat.write("insert P(" + str(tp+j) + "," + str(Data[tp+j][1]) + ");\n")
                    fileLog.write("@" + str(Data[tp+j][2]) + " p(" + str(Data[tp+j][1]) + ")\n")
                else:
                    fileDat.write("insert Q(" + str(tp+j) + "," + str(Data[tp+j][1]) + ");\n")
                    fileLog.write("@" + str(Data[tp+j][2]) + " q(" + str(Data[tp+j][1]) + ")\n")           
                j = j + 1

            tp = tp + j
            i = i + batchSize
            fileDat.write("commit dump_changes;\n")



def wrapper(Data,nameDat, nameLog, batchSize):

    fileDat = open(nameDat, "a")
    fileLog = open(nameLog, "a")

    Data.sort(key=lambda x: x[2])
    Data_new = []
    i = 0
    while i < len(Data):
        temp = []
        ts = Data[i][2]
        j = i
        while (j < len(Data)) & (ts == Data[j][2]):
            temp.append(Data[j])
            i = i+1
            j = j+1
            #python will otherwise evaluate loopcondition -> IndexError
            if j >= len(Data):
                    break         
        Data_new.append((ts,temp))


    i = 0
    tp = 0
    while i < len(Data_new):
        j = 0
        fileDat.write("\n \n")
        fileDat.write("start;\n")
        while (j < batchSize) & (tp + j < len(Data_new)):
            fileDat.write("insert Timestamp(" + str(tp+j) + "," + str(Data_new[tp+j][0]) + ");\n")
            fileLog.write("\n@" + str(Data_new[tp+j][0]) + " ")
            temp = Data_new[tp+j][1]
            k = 0
            while k < len(temp):
                if temp[k][0] == 1:
                    fileDat.write("insert P(" + str(tp+j) + "," + str(temp[k][1]) + ");\n")
                    fileLog.write("p(" + str(temp[k][1]) + ") ")
                else:
                    fileDat.write("insert Q(" + str(tp+j) + "," + str(temp[k][1]) + ");\n")
                    fileLog.write("q(" + str(temp[k][1]) + ") ")
                k = k + 1
            j = j + 1
        tp = tp + j
        i =  i + batchSize
        fileDat.write("commit dump_changes;\n")
        fileDat.write("\n \n")
    fileDat.close()   


def gen_tests(cat,Data,nameDat, nameLog, batchSize, min:int, max:int):

    Data.sort(key=lambda x: x[2])
    fileLog = open(nameLog, "w")
    fileDat = open(nameDat, "w")
    fileDat.write("start;\n")
    fileDat.write("insert Intervall(" + str(abs(min)) + "," + str(max)  + ");\n")
    fileDat.write("commit dump_changes;\n")

    fileLog.close()
    fileDat.close()

    if(cat == 0):
        no_wrap(Data,nameDat, nameLog, batchSize)

    elif(cat == 1):
        wrapper(Data,nameDat, nameLog, batchSize)


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
    bool = (DataMonPoly == DataDDlog)
    return bool


def runTest(cat,path,Data,datFile,logFile,min,max):
    for batchsize in [1,5,10]:
        gen_tests(cat,Data, datFile,logFile, batchsize, min, max)
        logFile_prefix = logFile[:-4]

        #We don't compile the programm for each intervall & testcase since this uses a lot of memory- instead just provide the intervall as input
        #in the original translation (/Monitoring-using-DDlog/translations) 
        os.system(path + " " + datFile + " > outputDDlog.txt")
        os.system("monpoly -sig " + logFile_prefix+ ".sig -formula " + logFile_prefix + ".mfotl -log " + logFile_prefix+ ".log  > outputMonPoly.txt")
        passed_this_batchsize = compare(fileDDlog="outputDDlog.txt", FileLMonPoly="outputMonPoly.txt")
        if(not passed_this_batchsize):
            
            print('\x1b[6;30;41m'+'failed with batchsize: ' + str(batchsize) + ' \x1b[0m')
            print("here")
            exit()

        else:
            print('\x1b[6;30;42m'+'passed with batchsize: ' + str(batchsize) + ' \x1b[0m')

        #don't need the output files anymore
        os.system("rm outputDDlog.txt")
        os.system("rm outputMonPoly.txt")

def runTest_since(cat,Data, datFile, logFile, min, max):
    path = "/home/berkay/Monitoring-using-DDlog/translations/since/since_ddlog/target/release/since_cli <"
    runTest(cat,path,Data,datFile,logFile,min,max)

def runTest_until(cat,Data, datFile, logFile, min, max):
    path = "/home/berkay/Monitoring-using-DDlog/translations/until/until_ddlog/target/release/until_cli <"
    runTest(cat,path,Data,datFile,logFile,min,max)