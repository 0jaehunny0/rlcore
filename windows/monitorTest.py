import os
import psutil
import subprocess
import numpy as np
import time

print(1)


def get_top_5_cpu_processes():
    # 모든 프로세스의 정보를 가져옴
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
        try:
            processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    # CPU 사용량 기준으로 정렬하고 상위 5개 선택
    top_5 = sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)[:10]
    return top_5


def get_cpu_affinity(pid):
    p = psutil.Process(pid)
    current_affinity = p.cpu_affinity()
    print(f"현재 프로세스({pid})의 CPU affinity: {current_affinity}")

    return current_affinity

def set_cpu_affinity(pid, cpu_list):
    p = psutil.Process(pid)
    current_affinity = p.cpu_affinity()
    p.cpu_affinity(cpu_list)
    return current_affinity

def print_cpu_utilization_per_core():
    # 각 코어별 CPU 사용률 (퍼센트로 반환)
    core_utilizations = psutil.cpu_percent(interval=1, percpu=True)
    
    print("CPU Utilization per Core:")
    for i, utilization in enumerate(core_utilizations):
        print(f"Core {i}: {utilization}%")

def monitor_process_affinity():
    for proc in psutil.process_iter(attrs=['pid', 'name']):
        try:
            pid = proc.info['pid']
            name = proc.info['name']
            affinity = proc.cpu_affinity()  # 프로세스가 실행 가능한 CPU 코어 리스트
            print(f"PID: {pid}, Name: {name}, Affinity: {affinity}")
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

TARGET_PROCESS_NAME = "HandBrake.Worker.exe"
def set_cpu_affinity_for_handbrake(CPU_CORES):
    first = False
    while True:
        # 현재 실행 중인 모든 프로세스 확인
        for proc in psutil.process_iter(['pid', 'name']):
            # 프로세스 이름이 HandBrake.Worker.exe인 경우
            if proc.info['name'] == TARGET_PROCESS_NAME:
                if first == False:
                    first = True
                    prevPid = proc.info['pid']
                    print(f"[PID: {prevPid}] {TARGET_PROCESS_NAME} 확인")
                    break
                if proc.info['pid'] == prevPid:
                    break
                try:
                    p = psutil.Process(proc.info['pid'])
                    # CPU Affinity 설정
                    p.cpu_affinity(CPU_CORES)
                    print(f"[PID: {p.pid}] {TARGET_PROCESS_NAME} CPU Affinity가 {CPU_CORES}로 설정되었습니다.")
                    return
                except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                    print(f"프로세스에 접근할 수 없습니다: {e}")
                    return
        # 프로세스가 아직 생성되지 않았다면 대기
        time.sleep(0.05)


TARGET_PROCESS_NAME = "HandBrake.Worker.exe"
def set_cpu_affinity_for_handbrake(CPU_CORES):
    while True:
        # 현재 실행 중인 모든 프로세스 확인
        for proc in psutil.process_iter(['pid', 'name']):
            # 프로세스 이름이 HandBrake.Worker.exe인 경우
            if proc.info['name'] == TARGET_PROCESS_NAME:
                try:
                    p = psutil.Process(proc.info['pid'])
                    # CPU Affinity 설정
                    # p.cpu_affinity(CPU_CORES)
                    nums = len(set_cpu_affinity(proc.info['pid'], CPU_CORES))
                    print(f"[PID: {p.pid}] {TARGET_PROCESS_NAME} CPU Affinity가 {CPU_CORES}로 설정되었습니다.")
                    return nums
                except Exception  as e:
                    print(f"프로세스에 접근할 수 없습니다: {e}")
                    return
        # 프로세스가 아직 생성되지 않았다면 대기
        time.sleep(0.05)




# initialize
get_top_5_cpu_processes()

top_5 = get_top_5_cpu_processes()

full_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23] # full

pid = 0
if "System Idle" in top_5[0]["name"]:
    pid = top_5[1]["pid"]
else:
    pid = top_5[0]["pid"]

get_cpu_affinity(pid)

"""
0 1 
2 3 4 5
6 7 8 9
10 11
12 13 
14 15 16 17
18 19 20 21
22 23
"""

# cpu_list = [0,2,4,6,8,10,12,14]
# cpu_list = list(np.array(np.arange(0,16)).tolist())
# cpu_list = list(np.array(np.arange(0,32)).tolist())
# cpu_list = list(np.array(np.arange(16,32)).tolist())

full_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23] # full

obs = 24124
pmon = 5140

set_cpu_affinity(obs, [2, 3, 4, 5, 6, 7, 8, 9, 14, 15, 16, 17, 18, 19, 20, 21])
set_cpu_affinity(pmon, [2, 3, 4, 5, 6, 7, 8, 9, 14, 15, 16, 17, 18, 19, 20, 21])


set_cpu_affinity(obs, full_list)
set_cpu_affinity(pmon, full_list)



set_cpu_affinity(27500, full_list)
for i in range(50):
    set_cpu_affinity_for_handbrake(full_list)
    time.sleep(0.5)


set_cpu_affinity(16180, [0,1,10,11,12,13,22,23])
for i in range(50):
    set_cpu_affinity_for_handbrake([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22])
    time.sleep(0.5)


set_cpu_affinity(7368, [0,1,2,3,4,5,6,7,8,9,11,12,13,14,15,16,17,18,19,20,21,22])


set_cpu_affinity(26012, [2,3,4,5,6,7,8,9, 14,15,16,17,18,19,20,21])
set_cpu_affinity(31976, [20, 21])
set_cpu_affinity(9012, [18, 19])

set_cpu_affinity(33884, [2,3,4,5,6,7,8,9, 14,15,16,17,18,19,20,21])
set_cpu_affinity(6688, [2,3,4,5,6,7,8,9, 14,15,16,17,18,19,20,21])
set_cpu_affinity(14168, [2,3,4,5,6,7,8,9, 14,15,16,17,18,19,20,21])




set_cpu_affinity(26312, full_list)
set_cpu_affinity(31976, full_list)
set_cpu_affinity(9012, full_list)

set_cpu_affinity(26312, full_list)

cpu_list = [0,2,3,4,5,10,12,14,15,16,17,22] # left
cpu_list = list(np.array(np.arange(10,24)).tolist())

cpu_list = [0,1,2,3,4,5,6,7,8,9,14,15,16,17,18,19,20,21]



cpu_list = list(np.array(np.arange(10,24)).tolist())
cpu_list = list(np.array(np.arange(0,24)).tolist())
cpu_list = list(np.array(np.arange(0,24)).tolist())
cpu_list = [0, 2,3,4,5, 6,7,8,9, 14,15,16,17,18,19, 20,21] # 1P 16E

cpu_list = list(np.array(np.arange(10,24)).tolist())






set_cpu_affinity(12252, [12, 13, 14, 15, 16, 17 ])
set_cpu_affinity(28004, [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, ])
set_cpu_affinity(24752, [0, 1, 22, 23, 18, 19, 20, 21])


set_cpu_affinity(12252, [12, 13, 14, 15, 16, 17 ])
set_cpu_affinity(28004, [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, ])
set_cpu_affinity(24752, [0, 1, 22, 23, 18, 19, 20, 21])

set_cpu_affinity(12252, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, ])
set_cpu_affinity(28004, [10, 11, 12, 13, 14])
set_cpu_affinity(24752, [15, 16, 17, 18, 19, 20, 21, 22, 23])


set_cpu_affinity(12252, full_list)
set_cpu_affinity(28004, full_list)
set_cpu_affinity(24752, full_list)\




set_cpu_affinity(12296, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, ])
set_cpu_affinity(24760, [10, 11, 12, 13, 14])
set_cpu_affinity(7352, [15, 16, 17, 18, 19, 20, 21, 22, 23])
set_cpu_affinity(5424, full_list)
set_cpu_affinity(4, [10, 11, 12, 13, 14])



set_cpu_affinity(12296, full_list)
set_cpu_affinity(24760, full_list)
set_cpu_affinity(7352, full_list)



set_cpu_affinity(pid, full_list)


set_cpu_affinity(29940, [0, 1, 10, 11, 12, 13, 22, 23, 2,3,4,5])
set_cpu_affinity(4060, [6,7,8,9])
set_cpu_affinity(33704, [14,15,16,17])
set_cpu_affinity(5424, [18, 19, 20, 21])


set_cpu_affinity(29940, [0,1,2,3,4,5,6,7,8,9,10,11])
set_cpu_affinity(4060, [12,13,14,15,16,17])
set_cpu_affinity(33704, [18, 19, 20, 21, 22, 23])
set_cpu_affinity(5424, full_list)


set_cpu_affinity(29940, full_list)
set_cpu_affinity(4060, full_list)
set_cpu_affinity(33704, full_list)
set_cpu_affinity(5424, full_list)

set_cpu_affinity(21648,full_list)
set_cpu_affinity(2236, full_list)
set_cpu_affinity(5140, full_list)