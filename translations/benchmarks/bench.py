import random
import subprocess
import matplotlib.pyplot as plt

REP = 3
MAX_VALUE = 1_000_000_000
MIN_VALUE = 200
PATH = "../since/"
PROGAMS = ["since1", "since2", "since3"]
Trace = list[tuple[int, list[tuple[str, int]]]]
Window = list[tuple[int,list[int]]]


def filter_window(ts_new:int, max:int, cache:Window) -> Window:
    i = 0
    while i < len(cache):
        ts, _ = cache[i]
        if (ts_new - ts > max):
            cache.pop(i)
        else:
            i += 1
        
    return cache

def filter_with_probability(probability:float) -> bool:
    return random.random() < probability

def event_generator_1(num_ts:int, evr:int, p:float,intervall_max:int) -> Trace:
    events = []
    cache = []
    for ts in range(num_ts):
        cache = filter_window(ts,intervall_max,cache)
        curr_events = [("P", elem) for _,elem in cache if filter_with_probability(p)]
        for _ in range(evr):
            elem = random.randint(0, MAX_VALUE)
            cache.append((ts,elem))
            curr_events.append(("Q", elem))
        events.append((ts, curr_events))
    return events

def event_generator_2(num_ts:int, evr:int, p:float,intervall_max:int) -> Trace:
    events = []
    cache = []
    for ts in range(num_ts):
        curr_events = [("P", elem) for elem in cache if filter_with_probability(p)]
        for _ in range(evr):
            elem = random.randint(0, MAX_VALUE)
            if elem not in cache:
                cache.append(elem)
            curr_events.append(("Q", elem))

        events.append((ts, curr_events))
    return events

def event_generator_3(num_ts:int, evr:int, p:float,intervall_max:int) -> Trace:
    events = []
    cache = []
    for ts in range(num_ts):
        curr_events = [("P", elem) for elem in cache if filter_with_probability(p)]
        for elem in range(evr):
            cache.append(elem)
            curr_events.append(("Q", elem))
        events.append((ts, curr_events))
    return events

def event_generator_4(num_ts:int, evr:int, p:float,intervall_max:int) -> Trace:
    #id pool consists of [1,2,3,..200]
    events = []

    for ts in range(num_ts):
        curr_events = [("P", elem) for elem in [i for i in range(1,601,1)]]

        if(ts%2==0):
            for elem in range(1,301,1): #evr is kind of half of id pool
                curr_events.append(("Q", elem))
        else:
            for elem in range(301,601,1): 
                curr_events.append(("Q", elem))
        events.append((ts, curr_events))
    return events


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

def measure_ddlog(func, numt_ts:int, evr:int, p:float, intervall_min:int,intervall_max:int, args:list[str]) -> float:


    input_file = "input.dat"
    events = event_generator(func,numt_ts,evr,p,intervall_max)
    input_ddlog_gen(events,input_file,intervall_min,intervall_max)

    acc = 0.0
    for _ in range(0, REP):
        with open(input_file, 'rb') as input:
            proc = subprocess.run(args, stdin=input, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        proc.check_returncode()
        elapsed = float(proc.stderr)
        acc += elapsed
    avg = acc / REP
    print(f"{avg:.2f}")

    subprocess.run(["rm", input_file])
    return avg

def event_generator(func, num_ts:int, evr:int, p:float,intervall_max:int) -> Trace:
    return func(num_ts,evr,p,intervall_max)


def measure_MonPoly(func,numt_ts:int, evr:int, p:float, intervall_min:int,intervall_max:int) -> float:
    
    mftol_file = "mply.mfotl"
    sig_file = "mply.sig"
    log_file = "mply.log"

    with open(mftol_file,'w') as file:
        file.write(f'P(x) SINCE[{intervall_min},{intervall_max}] Q(x)')

    with open(sig_file,'w') as file:
        file.write('P(x:int) \n')
        file.write('Q(x:int) \n')
    

    events = func(numt_ts,evr,p,intervall_max)
    input_MonPoly_gen(events,log_file)

    args = ["/usr/bin/time", "-f", "%e", "monpoly", "-sig", sig_file, "-formula", mftol_file, "-log", log_file]

    acc = 0.0
    for _ in range(0, REP):
        proc = subprocess.run(args,stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
        proc.check_returncode()
        elapsed = float(proc.stderr)
        acc += elapsed
    avg = acc / REP
    print(f"{avg:.2f}")

    subprocess.run(["rm", mftol_file])
    subprocess.run(["rm", log_file])
    subprocess.run(["rm", sig_file])
    
    return avg


def plot(program:str, x:list[int], y:list[int], description:str = ""):
    plt.plot(x,y,label=program + ", "+ description)
    plt.legend(loc='best')



"""
For each id occured as Q(id) within the window, prob. p decides wheter id follows in next ts as
P(id). Since Q(id) (with same id) are not likely to occur repeatedly, since1 should be at least slightly
faster, because it uses the simplest logic whereas the other two involve more rules/aggregation.
"""
def bench1():
    #parameters for bench
    distinct_ts = [500, 1_000, 1_500, 2_000, 2_500]
    evr = 2

    intervall_min = 2
    intervall_max = 4

    x = [i//evr for i in distinct_ts]
    exp = 1
    for p in [0.01, 0.5, 0.99]:
        for program in PROGAMS:
            print(f'program: {program}, prob. = {p}')
            args_ddlog = ["/usr/bin/time", "-f", "%e", f"{PATH}{program}_ddlog/target/release/{program}_cli"]
            y_ddlog = [measure_ddlog(event_generator_1,ts,evr,p,intervall_min,intervall_max,args_ddlog) for ts in x]
            plot(program,x,y_ddlog)

        plt.xlabel("number Q events")
        plt.ylabel("runtime[s]")
        #plt.title(f"p={p}")
        plt.savefig(f"./since_plots/bench1/exp{exp}",dpi=500)
        plt.close()
        exp +=1
    #plot("monpoly", total_events, [measure_MonPoly(event_generator_1,ts,evr,p,intervall_min, intervall_max) for ts in total_events], f'prob. = {p}')


"""
Assumption/idea: since1 will keep a lot of outdated tuples because "chains" never stop and 
new id's enter frequently. Since2 and Since3 should perform much better due to "garbage collecting"
"""
def bench2():
    total_events = [i*200 for i in range(1,11,1)]
    evr = 2

    intervall_min = 2
    intervall_max = 4

    x = [i//evr for i in total_events]
    exp = 1
    for p in [0.01]:
        for program in PROGAMS:
            print(f'program: {program}, prob. = {p}')
            args_ddlog = ["/usr/bin/time", "-f", "%e", f"{PATH}{program}_ddlog/target/release/{program}_cli"]
            y_ddlog = [measure_ddlog(event_generator_2,ts,evr,p,intervall_min,intervall_max,args_ddlog) for ts in x]
            plot(program,x,y_ddlog)

        plt.xlabel("number Q events")
        plt.ylabel("runtime[s]")
        plt.title(f"p={p}")
        plt.savefig(f"./since_plots/bench2/exp{exp}",dpi=500)
        plt.close()
        exp +=1

"""
don't know, i was tired and tried new stuff
But does increase eventrate and keeps numt_ts constant- since we observe every Q once,
we should (maybe) be faster with since2.dl and/or since3.dl when p is really high (filters out irrelevant
tuples)
"""
def bench3():
    num_ts = 2000
    p = 0.99

    intervall_min = 3
    intervall_max = 20
    x = [10,20,30,40,50,60,70,80,90,100]

    exp = 1
    for program in PROGAMS:
        print(f'program: {program}, prob. = {p}')
        args_ddlog = ["/usr/bin/time", "-f", "%e", f"{PATH}{program}_ddlog/target/release/{program}_cli"]
        y_ddlog = [measure_ddlog(event_generator_3,round(num_ts/evr),evr,p,intervall_min,intervall_max,args_ddlog) for evr in x]
        plot(program,x,y_ddlog)

    plt.xlabel("evr")
    plt.ylabel("runtime[s]")
    plt.title(f"Constant number of distinct ts (={num_ts})")
    plt.savefig(f"./since_plots/bench3/exp{exp}",dpi=500)
    plt.close()


"""
Pool of "ids"- p(id) always occurs, whereas Q(id) occurs for each id 2 tp later again.
Thus, since3 does much more work than the other 2 versions due to the group_by.
since2 should be worse than since1, because it does more work but obtains the same result.
probability is not used here. 
"""
def bench4():
    total_events = [i*50 for i in range(1,8,1)]
    evr = 2

    intervall_min = 2
    intervall_max = 25

    x = [i for i in total_events]
    exp = 3
    for p in [0.99]:
        for program in PROGAMS:
            print(f'program: {program}, prob. = {p}')
            args_ddlog = ["/usr/bin/time", "-f", "%e", f"{PATH}{program}_ddlog/target/release/{program}_cli"]
            y_ddlog = [measure_ddlog(event_generator_4,ts,evr,p,intervall_min,intervall_max,args_ddlog) for ts in x]
            plot(program,x,y_ddlog)

        plt.xlabel("number timepoints")
        plt.ylabel("runtime[s]")
        #plt.title("id-Pool- P alway occurs for each id, Q with gaps")
        plt.savefig(f"./since_plots/bench4/exp{exp}",dpi=500)
        plt.close()
        exp +=1


if __name__ == '__main__':
    #bench1()
    #bench2()
    #bench3()
    bench4()
    