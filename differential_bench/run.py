import random
import subprocess
import matplotlib.pyplot as plt

# Parameters
SEED = 20230508
REP = 1
IV_LO = 0
IV_HI = 10
TOTAL_EVENTS = 10_000
TP_PER_TS = [10, 20, 30, 40, 50, 60]
EV_PER_TP = 10
MAX_VALUE = 1_000_000_000
PROGRAMS = ["no_batching", "batching", "batching_new"]
BATCH_SIZES = [1, 5]

random.seed(SEED)

Trace = list[tuple[int, list[int]]]

def input_generator(tp_per_ts: int) -> Trace:
    num_ts = round(TOTAL_EVENTS / EV_PER_TP / tp_per_ts)
    events = []
    count = 0
    num_tp = 0
    for ts in range(num_ts):
        for tp in range(tp_per_ts):
            curr_events = []
            for _ in range(EV_PER_TP):
                curr_events.append(random.randint(0, MAX_VALUE))
                count += 1
            events.append((ts, curr_events))
            num_tp += 1
    print(f"generated {count} events across {num_ts} time-stamps, {num_tp} time-points")
    return events

def file_generator(events: Trace, batch_size: int, filename: str):
    with open(filename, 'w') as file:
        file.write("start;\n")
        file.write(f"insert Intervall({IV_LO}, {IV_HI});\n")
        file.write("commit dump_changes;\n\n")

        for batch_start in range(0, len(events), batch_size):
            file.write("start;\n")
            for tp in range(batch_start, min(batch_start + batch_size, len(events))):
                ts, elems = events[tp]
                file.write("insert Timestamp(" + str(tp) + ", " + str(ts) + ");\n")
                for elem in elems:
                    file.write("insert P(" + str(tp) + ", " + str(elem) + ");\n")
            file.write("commit dump_changes;\n\n")

def measure(program: str, tp_per_ts: int, batch_size: int) -> float:
    print(f"{program}, batch size {batch_size}, {tp_per_ts} tp/ts")
    INPUT_FILE = 'input.txt'
    events = input_generator(tp_per_ts)
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
    return [measure(program, rate, batch_size) for rate in TP_PER_TS]

def main():
    for program in PROGRAMS:
        bsz = [1] if program == "no_batching" else BATCH_SIZES
        for batch_size in bsz:
            label = f"{program}, batch size {batch_size}"
            plt.plot(TP_PER_TS, measure_series(program, batch_size), label=label)
    plt.xlabel("tp/ts")
    plt.ylabel("runtime [s]")
    plt.figlegend()
    plt.savefig("comparison.png")

if __name__ == '__main__':
    main()
