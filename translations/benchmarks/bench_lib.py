import random
import os
import sys
sys.path.append("/home/berkay/Monitoring-using-DDlog/translations/tests")
import myLib


def since_Data_generator(numts:int, evr:int, p:float, 
                          lower_bound:int, upper_bound:int,
                          ts_min_dist:int,ts_max_dist:int,
                          id_min:int, id_max:int):
    timestamps = []
    current_timestamp = 0
    for it in range(numts):
        current_timestamp = current_timestamp + random.randint(ts_min_dist,ts_max_dist)
        timestamps.append(current_timestamp)

    

    Q_events = []
    P_events=[]
    for it1 in range(numts):    
        Q_events_curr = []

        for it2 in range(evr):
            event = random.randint(id_min,id_max)
            Q_events_curr.append(event)

        Q_events.append(Q_events_curr)
        P_events.append([]) #will be filled later


    
    for it1 in range(numts):
        current_timestamp = timestamps[it1]
        Q_events_curr = Q_events[it1]
        it2 = it1 + 1
        if (random.random() < p):
            while it2 < numts:
                future_timestamp = timestamps[it2]
                if(future_timestamp  - current_timestamp > upper_bound):
                    break

                P_events_future = []
                for id in Q_events_curr:
                    P_events_future.append(id)
                
                P_events[it2] = P_events_future
                it2 = it2 + 1
        else:
            continue

    return timestamps,Q_events,P_events


def since_input_transform(timestamp:list,Q_events:list,P_events:list):
    
    if not ((len(timestamp)==len(Q_events)) & (len(Q_events)==len(P_events))):
        raise Exception("All lists need to be of the same size")
    
    size = len(timestamp)
    Data = []
    for it in range(size):
        ts = timestamp[it]
        P_curr_ts = P_events[it]
        Q_curr_ts = Q_events[it]

        all_events = []
        for elem in P_curr_ts:
            all_events.append([1,elem,ts])

        for elem in Q_curr_ts:
            all_events.append([2,elem,ts])
        
        Data.append((ts,all_events))
    
    return Data
    
def since_bench(numts:int, evr:int, p:float, lower_bound:int, upper_bound:int, test_name:str,
                batch_size= 1,ts_min_dist= 0,ts_max_dist= 3, id_min=0, id_max=100):
    
    timestamps, Q_events, P_events = since_Data_generator(numts,evr,p,lower_bound,upper_bound,ts_min_dist,ts_max_dist,id_min,id_max)
    Data = since_input_transform(timestamps, Q_events, P_events)
    myLib.logFile_generator_binary(Data,test_name+".log")

    fileDat = open(test_name+".dat", "w")
    fileDat.write("start;\n")
    fileDat.write("insert Intervall(" + str(abs(lower_bound)) + "," + str(upper_bound)  + ");\n")
    fileDat.write("commit dump_changes;\n")
    fileDat.close()
    myLib.datFile_generator_binary(Data,test_name+".dat",batch_size,"a")





    

    
        

    






    

