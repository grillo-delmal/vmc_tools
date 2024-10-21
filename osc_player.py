import pyliblo3
import json
import time
import sys

in_path = sys.argv[1] if len(sys.argv) >= 2 else "dump.vmc"
out_port = int(sys.argv[2]) if len(sys.argv) >= 3 else 39539

data = []

# Load file
print("Loading file")
with open(in_path, "r") as f:
    for line in f:
        (tstamp, path, args, types) = line.rstrip().split('|')
        args = tuple(json.loads(args))
        data.append(
            (
                float(tstamp), 
                path, 
                [(types[i], args[i]) for i in range(len(types))]))

i = 0
cur_reg = data[i]
addr = ("127.0.0.1", out_port)

print("Start")
init_time = time.time()
try:
    while True:
        if time.time() - init_time >= cur_reg[0]:
            pyliblo3.send(addr, cur_reg[1], *cur_reg[2])
            i += 1
            if i >= len(data):
                print("loop")
                i = 0
                init_time = time.time()
            cur_reg = data[i]
            continue
except KeyboardInterrupt:
    pass