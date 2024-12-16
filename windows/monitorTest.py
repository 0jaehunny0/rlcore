import os
import psutil
import subprocess
import numpy as np

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
    top_5 = sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)[:5]
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



# initialize
get_top_5_cpu_processes()

top_5 = get_top_5_cpu_processes()

pid = 0
if "System Idle" in top_5[0]["name"]:
    pid = top_5[1]["pid"]
else:
    pid = top_5[0]["pid"]

get_cpu_affinity(pid)

cpu_list = [0,2,4,6,8,10,12,14]
cpu_list = list(np.array(np.arange(0,16)).tolist())
cpu_list = list(np.array(np.arange(0,32)).tolist())
cpu_list = list(np.array(np.arange(16,32)).tolist())
set_cpu_affinity(pid, cpu_list)