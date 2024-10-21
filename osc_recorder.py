import pyliblo3
import json
import time
import sys

out_path = sys.argv[1] if len(sys.argv) >= 2 else "dump.vmc"
in_port = int(sys.argv[2]) if len(sys.argv) >= 3 else 39540
duration = float(sys.argv[3]) if len(sys.argv) >= 4 else 6
filter = float(sys.argv[4]) if len(sys.argv) >= 5 else None

server = pyliblo3.Server(in_port)

data = []

def recorder(path, args, types, src):
    data.append(
        [
            time.time() - init_time, 
            path, 
            json.dumps(args), 
            types])

server.add_method(filter, None, recorder)

print("Start")
init_time = time.time()
try:
    while True:
        server.recv(100)
        if time.time() - init_time >= duration:
            break
except KeyboardInterrupt:
    pass

with open(out_path, "w") as f:
    for line in data:
        f.write("%f|%s|%s|%s\n" % tuple(line))