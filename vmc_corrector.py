import pyliblo3
import json
import time
import sys
from collections import deque
import math

in_port = int(sys.argv[1]) if len(sys.argv) >= 2 else 39540
out_port = int(sys.argv[2]) if len(sys.argv) >= 3 else 39539
filter = float(sys.argv[3]) if len(sys.argv) >= 4 else None

#  (roll, pitch, yaw)
corrections = {
    "LeftHand":     [0, 0, 1],
    "RightHand":    [3, 3, 0],
    "LeftLowerArm": [0, 0, 0],
    "RightLowerArm":[0, 0, 0],

    "LeftLowerLeg": [3, 0, 3],
    "LeftFoot":     [0, 1, 0],
    "RightLowerLeg":[1, 0, 1],
    "RightFoot":    [0, 1, 2],

    "Chest":        [1, 0, 1],
    "Hips":         [1, 0, 1],
    "Head":         [0, 0, 0]
}

part_filter = [
    "LeftHand",
    "RightHand",
    "LeftLowerArm",
    "RightLowerArm",
    "Head",
    "LeftLowerLeg",
    "LeftFoot",
    "RightLowerLeg",
    "RightFoot",
    "Chest",
    "Hips",
]

result = {}

for i in corrections:
    corrections[i][0] *= math.pi/2
    corrections[i][1] *= math.pi/2
    corrections[i][2] *= math.pi/2

server = pyliblo3.Server(in_port)
addr = ("127.0.0.1", out_port)

data = deque

def toQuat(roll, pitch, yaw):
    cr = math.cos(roll * 0.5)
    sr = math.sin(roll * 0.5)
    cp = math.cos(pitch * 0.5)
    sp = math.sin(pitch * 0.5)
    cy = math.cos(yaw * 0.5)
    sy = math.sin(yaw * 0.5)

    q_w = cr * cp * cy + sr * sp * sy
    q_x = sr * cp * cy - cr * sp * sy
    q_y = cr * sp * cy + sr * cp * sy
    q_z = cr * cp * sy - sr * sp * cy

    return (q_x, q_y, q_z, q_w)

def toAng(q_x, q_y, q_z, q_w):
    # roll (x-axis rotation)
    sinr_cosp = 2 * (q_w * q_x + q_y * q_z)
    cosr_cosp = 1 - 2 * (q_x * q_x + q_y * q_y)
    roll = math.atan2(sinr_cosp, cosr_cosp)

    # pitch (y-axis rotation)
    sinp = math.sqrt(1 + 2 * (q_w * q_y - q_x * q_z))
    cosp = math.sqrt(1 - 2 * (q_w * q_y - q_x * q_z))
    pitch = 2 * math.atan2(sinp, cosp) - math.pi / 2

    # yaw (z-axis rotation)
    siny_cosp = 2 * (q_w * q_z + q_x * q_y)
    cosy_cosp = 1 - 2 * (q_y * q_y + q_z * q_z)
    yaw = math.atan2(siny_cosp, cosy_cosp)
    
    return (roll, pitch, yaw)

def getRot (q1, q2):
    return (
        q1[3] *  q2[0] + q1[0] *(-q2[3])+ q1[1] *  q2[2] - q1[2] *  q2[1] ,  # x
        q1[3] *  q2[1] - q1[0] *  q2[2] + q1[1] *(-q2[3])+ q1[2] *  q2[0] ,  # y
        q1[3] *  q2[2] + q1[0] *  q2[1] - q1[1] *  q2[0] + q1[2] *(-q2[3]),  # z
        q1[3] *(-q2[3])- q1[0] *  q2[0] - q1[1] *  q2[1] - q1[2] *  q2[2] ,  # w
    )

def quatMult (q1, q2):
    return (
        q1[3] *  q2[0] + q1[0] *  q2[3] + q1[1] *  q2[2] - q1[2] *  q2[1] ,  # x
        q1[3] *  q2[1] - q1[0] *  q2[2] + q1[1] *  q2[3] + q1[2] *  q2[0] ,  # y
        q1[3] *  q2[2] + q1[0] *  q2[1] - q1[1] *  q2[0] + q1[2] *  q2[3] ,  # z
        q1[3] *  q2[3] - q1[0] *  q2[0] - q1[1] *  q2[1] - q1[2] *  q2[2] ,  # w
    )

def corrector(path, args, types, src):
    try:
        if args[0] not in part_filter:
            return
        if (args[0] in corrections) and (
                (corrections[args[0]][0] != 0) or (
                    corrections[args[0]][1] != 0) or (
                    corrections[args[0]][2] != 0)):

            (roll, pitch, yaw) = toAng(*args[4:])

            if args[0] in corrections:
                roll += corrections[args[0]][0]
                pitch += corrections[args[0]][1]
                yaw += corrections[args[0]][2]

            quats = toQuat(roll, pitch, yaw)
            rot = getRot(quats, args[4:])
            print(args[0], rot)
            args[4:] = quatMult(args[4:], rot)
        args[6] *= -1
        args[7] *= -1
        
        pyliblo3.send(addr, path, *[(types[i], args[i]) for i in range(len(types))])
    except KeyboardInterrupt:
        exit(0)

server.add_method(filter, None, corrector)

print("Start")
try:
    while True:
        server.recv(100)
except KeyboardInterrupt:
    pass
