import os
import time
import json
pid = os.getpid()


trace = {"args": {},
         "name": "",
         "cat": "cc2",
         "ph": "",
         "pid": pid,
         "tid": 1,
         "ts": 0.0}

counter = {"counter": 0}
logging = []


def func_start(func_name, cnt=None):
    """
    Method to register start of function for tracing.

    :params func_name: function name as string.
    :params cnt: optional count value.
    """
    trace["name"] = func_name
    trace["ph"] = "B"
    trace["ts"] = time.perf_counter()
    if (cnt is not None):
        counter["counter"] = cnt
        trace["args"] = counter.copy()
    logging.append(trace.copy())


def func_end(func_name):
    """
    Method to register end of function for tracing.

    :params func_name: function name as string.
    """
    trace["name"] = func_name
    trace["ph"] = "E"
    trace["ts"] = time.perf_counter()
    logging.append(trace.copy())


def dump_trace(json_file):
    """
    Method to dump registered tracing information.

    :params json_file: json file name where data needs to be written.
    """
    for i in range(len(logging)):
        logging[i]["ts"] = 1000000*logging[i]["ts"]
    out_file = open(json_file, "w")
    json.dump(logging, out_file, indent=4)
    out_file.close()
