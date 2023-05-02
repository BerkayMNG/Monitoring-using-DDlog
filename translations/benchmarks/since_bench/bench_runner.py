import sys
import os
sys.path.append("/home/berkay/Monitoring-using-DDlog/translations/benchmarks")
import bench_lib

#test1
runtime_ddlog = []
runtime_monPoly = []

memory_usage_ddlog = []
memory_usage_monpoly = []


bench_lib.since_bench(numts=8,evr=2,p=0.99,lower_bound=0,upper_bound=5,test_name="test1")
os.system("echo > ")
