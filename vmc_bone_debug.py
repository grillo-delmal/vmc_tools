import pyliblo3 as liblo
import json
import time

parts = {}
freq = 1 # secs

server = liblo.Server(39540)
def test_handler(path, args, types, src):
    if types != 'sfffffff':
        print("what!", types)
        return
    parts[args[0]] = [
            "pos %.2f %.2f %.2f" % tuple(args[1:4]), 
            "rot %.2f %.2f %.2f %.2f" % tuple(args[4:])]
    
server.add_method('/VMC/Ext/Bone/Pos', None, test_handler)

next_t = time.time()
while True:
    server.recv(100)
    cur_t = time.time()
    if cur_t > next_t:
        print("=== Received ===")
        print(json.dumps(parts, sort_keys=True, indent=4))
        next_t = cur_t + freq
