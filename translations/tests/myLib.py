import re
import os

def gen_tests(Data,nameDat, nameLog, batchSize, min:int, max:int):

    Data.sort(key=lambda x: x[2])
    size = len(Data)
    fileLog = open(nameLog, "w")
    fileDat = open(nameDat, "w")
    fileDat.write("start;\n")
    fileDat.write("insert Intervall(" + str(abs(min)) + "," + str(max)  + ");\n")
    fileDat.write("commit dump_changes;\n")


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

    fileLog.close()
    fileDat.close()

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
            tuple_temp = re.findall(r'\d+', line)[0:3]
            tuple = []
            tuple.append(int(tuple_temp[1]))
            tuple.append(int(tuple_temp[0]))
            tuple.append(int(tuple_temp[2]))
            DataMonPoly.append(tuple)
    
    bool = (DataMonPoly == DataDDlog)
    return bool

#This 
def runTest_since(Data, datFile, logFile, min, max):
    for batchsize in range(1,18,4):
        gen_tests(Data, datFile,logFile, batchsize, min, max)
        logFile_prefix = logFile[:-4]

        os.system("/home/berkay/Monitoring-using-DDlog/translations/since/since_ddlog/target/release/since_cli < " + datFile + " > outputDDlog.txt")
        os.system("monpoly -sig " + logFile_prefix+ ".sig -formula " + logFile_prefix + ".mfotl -log " + logFile_prefix+ ".log > outputMonPoly.txt")

        passed_this_batchsize = compare(fileDDlog="outputDDlog.txt", FileLMonPoly="outputMonPoly.txt")
        if(not passed_this_batchsize):
            print('\x1b[6;30;41m'+'failed with batchsize: ' + str(batchsize) + ' \x1b[0m')
            exit()

        else:
            print('\x1b[6;30;42m'+'passed with batchsize: ' + str(batchsize) + ' \x1b[0m')

        #don't need the output files anymore
        os.system("rm outputDDlog.txt")
        os.system("rm outputMonPoly.txt")