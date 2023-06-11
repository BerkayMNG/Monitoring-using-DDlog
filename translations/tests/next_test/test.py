import random
import sys
sys.path.append("/home/berkay/Monitoring-using-DDlog/translations/tests")
from helper_functions import runTest


SIZE = 50
EVR = 3
MAX_VALUE = 1_000_000_000
PROBABILITY = 0.8

INTERVALL_MIN = 0
INTERVALL_MAX= 3
USED_IDS = [1,2]
PATH = "/home/berkay/Monitoring-using-DDlog/translations/next/next_formula1_ddlog/target/release/next_formula1_cli"
MONPOLY_PROGRAM = "next_test"

Window = list[tuple[int,list[int]]]