import re

PATH = "./tests/or_2"

def process_file(file_path_read:str, file_path_write:str):
    
    pattern1 = r'@(\d+)'
    pattern2 = r'(\w+)\((.*?)\)'
    
    timestamps_nested = []
    events = []
    with open(file_path_read, 'r') as file:
        for line in file:
            timestamps_nested.append(re.findall(pattern1, line))
            events.append(re.findall(pattern2, line))

    timestamps = [int(item) for sublist in timestamps_nested for item in sublist]


    with open(file_path_write, 'w') as file:
        for tp in range(len(timestamps)):
            file.write('start;\n')
            file.write('insert Timestamp(' + str(tp) + "," + str(timestamps[tp]) + ");\n")
            for event, inpts in events[tp]:
                file.write('insert ' + event + "(" + str(tp) + "," + inpts + ");\n")
                

            file.write('commit dump_changes;\n \n')



file_path_read = PATH + "/input.log"
file_path_write = PATH + "/input.txt"
output = process_file(file_path_read,file_path_write)
