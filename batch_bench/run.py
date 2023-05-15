import random
import subprocess
import os
import matplotlib.pyplot as plt

# Parameters
REP = 5
TOTAL_EVENTS = [i*5000 for i in range(1,8,2)]
PROGRAMS = [ "batched"]
BATCH_SIZES = [100,1000, 5000]


Trace = list[tuple[int, list[tuple[str, int]]]]

def input_generator(total_events: int) -> Trace:
    num_ts = total_events
    events = []
    num_tp = 0
    for ts in range(num_ts):
        elem1 = random.randint(1,3)
        elem2 = random.randint(1,3)
        events.append((ts,[("Q", elem1),("P", elem2)]))
    return events

def file_generator(events: Trace, batch_size: int, filename: str):
    with open(filename, 'w') as file:
        for batch_start in range(0, len(events), batch_size):
            file.write("start;\n")
            for tp in range(batch_start, min(batch_start + batch_size, len(events))):
                ts, elems = events[tp]
                file.write("insert Timestamp(" + str(tp) + ", " + str(ts) + ");\n")
                for rel, elem in elems:
                    file.write("insert " + rel + "(" + str(tp) + ", " + str(elem) + ");\n")
            file.write("commit dump_changes;\n\n")

def measure(program: str, total_events: int, batch_size: int) -> float:
    print(f"{program}, batch size {batch_size}, {total_events} events")
    INPUT_FILE = 'input.txt'
    events = input_generator(total_events)
    file_generator(events, batch_size, INPUT_FILE)
    args = ["/usr/bin/time", "-f", "%e", f"./{program}_ddlog/target/release/{program}_cli"]
    acc = 0.0
    for _ in range(0, REP):
        with open(INPUT_FILE, 'rb') as input_file:
            proc = subprocess.run(args, stdin=input_file, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        proc.check_returncode()
        elapsed = float(proc.stderr)
        #print(f"{elapsed:.2f}")
        acc += elapsed
    avg = acc / REP
    print(f"{avg:.2f}")
    return avg

def measure_series(program: str, batch_size: int) -> list[float]:
    return [measure(program, x, batch_size) for x in TOTAL_EVENTS]

def monpoly_input_generator(total_events: int, filename:str):
    with open(filename, 'w') as file:
        for ts in range(total_events):
            id1 = random.randint(1,3)
            id2 = random.randint(1,3)
            file.write(f"@{ts} p({id1}) q({id2})\n")
    
def measure2 (program: str, total_events: int) -> float:
    INPUT_FILE = f"{program}.log"
    monpoly_input_generator(total_events,INPUT_FILE)
    args = ["/usr/bin/time", "-f", "%e", "monpoly", "-sig", "cnt.sig", "-formula", "cnt.mfotl", "-log", "cnt.log"]
    acc = 0.0
    for _ in range(0, REP):
        proc = subprocess.run(args, stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
        proc.check_returncode()
        elapsed = float(proc.stderr)
        #print(f"{elapsed:.2f}")
        acc += elapsed
    avg = acc / REP
    print(f"{avg:.2f}")
    return avg

def measure_monpoly(program: str) -> list[float]:
    return [measure2(program,x) for x in TOTAL_EVENTS]



def main():
    for program in PROGRAMS:
        bsz = [1] if program == "not_batched" else BATCH_SIZES
        for batch_size in bsz:
            label = f"{program}, batch size {batch_size}"
            plt.plot(TOTAL_EVENTS, measure_series(program, batch_size), label=label)

    label = "Monpoly"
    plt.plot(TOTAL_EVENTS,measure_monpoly("cnt"), label=label)
    plt.xlabel("number of matching pairs")
    plt.ylabel("runtime [s]")
    plt.figlegend()
    plt.savefig("comparison.png")

if __name__ == '__main__':
    main()
