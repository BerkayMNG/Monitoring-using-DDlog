import random
import subprocess
import matplotlib.pyplot as plt

# Parameters
SEED = 20230508
REP = 3
TOTAL_EVENTS = [2_000, 4_000, 6_000, 8_000]
TP_PER_TS = 10
EV_PER_TP = 2
MAX_VALUE = 1_000_000_000
PROGRAMS = ["no_batching", "batching", "batching_new"]
BATCH_SIZES = [1, 5]

random.seed(SEED)

Trace = list[tuple[int, list[tuple[str, int]]]]

def input_generator(total_events: int) -> Trace:
    num_ts = round(total_events / 2 / EV_PER_TP / TP_PER_TS)
    events = []
    cache = []
    count = 0
    num_tp = 0
    for ts in range(num_ts):
        for tp in range(TP_PER_TS):
            curr_events = [("Q", elem) for elem in cache]
            cache.clear()
            for _ in range(EV_PER_TP):
                elem = random.randint(0, MAX_VALUE)
                cache.append(elem)
                curr_events.append(("P", elem))
            events.append((ts, curr_events))
            count += len(curr_events)
            num_tp += 1
    print(f"generated {count} events across {num_ts} time-stamps, {num_tp} time-points")
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

def main():
    for program in PROGRAMS:
        bsz = [1] if program == "no_batching" else BATCH_SIZES
        for batch_size in bsz:
            label = f"{program}, batch size {batch_size}"
            plt.plot(TOTAL_EVENTS, measure_series(program, batch_size), label=label)
    plt.xlabel("tp/ts")
    plt.ylabel("runtime [s]")
    plt.figlegend()
    plt.savefig("comparison.png")

if __name__ == '__main__':
    main()
