import numpy as np
import win32api
import win32process
import win32con

import psutil
import time

def get_top_5_mem_processes():
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


def get_top_5_mem_processes():
    # 모든 프로세스의 정보를 가져옴
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
        try:
            if proc.info['memory_info'] is not None:
                processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    # 메모리 사용량(RSS) 기준으로 정렬하고 상위 5개 선택
    top_5 = sorted(processes, key=lambda x: x['memory_info'].rss, reverse=True)[:5]
    return top_5

def get_threads_cpu_utilization(pid, interval=1):
    """
    특정 프로세스(PID)의 각 스레드별 CPU 사용률을 반환합니다.

    :param pid: 프로세스 ID
    :return: 스레드별 CPU 사용률 리스트 [(thread_id, cpu_percent)] (높은 순으로 정렬)
    """
    process = psutil.Process(pid)

    # 프로세스의 스레드 정보 가져오기
    threads_info = process.threads()

    # CPU 사용량 측정 전 대기 (psutil에서 CPU 퍼센트를 계산하기 위해 필요)
    time.sleep(1)

    cpu_percentages = []
    for thread in threads_info:
        # 스레드 ID 가져오기
        thread_id = thread.id

        # 각 스레드의 CPU 사용량 추적
        cpu_percent = process.cpu_percent(interval)  # 프로세스 CPU 사용률
        cpu_percentages.append((thread_id, cpu_percent))

    # CPU 사용률 높은 순으로 정렬
    cpu_percentages.sort(key=lambda x: x[1], reverse=True)

    return cpu_percentages



def get_thread_ids(pid):
    """
    특정 프로세스(PID)의 모든 스레드 ID를 반환합니다.

    :param pid: 프로세스 ID
    :return: 스레드 ID 리스트 [thread_id1, thread_id2, ...]
    """

    process = psutil.Process(pid)

    # 프로세스의 스레드 정보 가져오기
    threads_info = process.threads()

    # 각 스레드의 ID만 추출
    thread_ids = [thread.id for thread in threads_info]

    return thread_ids



def set_thread_affinity(pid, thread_id, affinity_mask):
    try:
        # 프로세스 핸들 가져오기
        process_handle = win32api.OpenProcess(
            win32process.PROCESS_ALL_ACCESS, False, pid)
        
        # 스레드 핸들 가져오기
        thread_handle = win32api.OpenThread(
            win32process.THREAD_SET_INFORMATION | win32process.THREAD_QUERY_INFORMATION, 
            False, 
            thread_id
        )
        
        # CPU affinity 설정
        win32process.SetThreadAffinityMask(thread_handle, affinity_mask)
        print(f"Set thread {thread_id} affinity to mask: {affinity_mask:#010b}")
        
        # 핸들 닫기
        win32api.CloseHandle(thread_handle)
        win32api.CloseHandle(process_handle)
    except Exception as e:
        print(f"Failed to set thread affinity: {e}")


def set_thread_affinity2(pid, cpus):
    """
    지정된 PID의 모든 스레드에 대해 CPU affinity를 설정합니다.
    
    :param pid: 프로세스 ID
    :param cpus: CPU affinity로 설정할 CPU 코어 비트마스크 (예: [0, 1])
    """
    try:
        # CPU 코어를 비트마스크로 변환
        affinity_mask = sum(1 << cpu for cpu in cpus)
        
        # 프로세스 핸들 열기
        process_handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, False, pid)
        
        # 프로세스의 스레드 ID 가져오기
        threads = win32process.EnumThreads(pid)
        
        for thread_id in threads:
            try:
                # 스레드 핸들 열기
                thread_handle = win32api.OpenThread(
                    win32con.THREAD_SET_INFORMATION | win32con.THREAD_QUERY_INFORMATION,
                    False,
                    thread_id
                )
                
                # 스레드 CPU affinity 설정
                win32process.SetThreadAffinityMask(thread_handle, affinity_mask)
                print(f"Thread ID {thread_id}: CPU affinity 설정 완료 -> {cpus}")
                
                # 스레드 핸들 닫기
                win32api.CloseHandle(thread_handle)
            except Exception as thread_error:
                print(f"Thread ID {thread_id}: CPU affinity 설정 실패 - {thread_error}")
        
        # 프로세스 핸들 닫기
        win32api.CloseHandle(process_handle)

    except Exception as e:
        print(f"PID {pid}: 에러 발생 - {e}")


def get_thread_cpu_usage(pid, interval=1.0):
    """
    주어진 PID에 대해 interval(초) 동안의 스레드별 CPU 사용률(%)을 측정 후,
    사용률이 큰 순서로 정렬된 리스트[(TID, 사용률), ...]를 반환합니다.

    - psutil.Process(pid).threads()는 스레드별 (user_time, system_time)을 초 단위로 제공
    - Δ(사용한 CPU 시간) / (interval * 코어 수) * 100 => CPU 사용률(퍼센트)
    """
    try:
        proc = psutil.Process(pid)
    except psutil.NoSuchProcess:
        print(f"PID {pid} 프로세스를 찾을 수 없습니다.")
        return []

    # 측정 시작 시점(t1)에서 스레드별 CPU 시간 기록
    threads_t1 = proc.threads()
    t1_times = {t.id: t.user_time + t.system_time for t in threads_t1}

    # interval만큼 대기
    time.sleep(interval)

    # 측정 종료 시점(t2)에서 스레드별 CPU 시간 기록
    threads_t2 = proc.threads()
    t2_times = {t.id: t.user_time + t.system_time for t in threads_t2}

    # CPU 코어 수
    cpu_count = psutil.cpu_count(logical=True)

    usage_result = {}
    for tid, start_time in t1_times.items():
        end_time = t2_times.get(tid, None)
        # interval 중 스레드가 종료되었을 수도 있음
        if end_time is None:
            continue

        # t2 - t1 = 해당 스레드가 interval 동안 사용한 CPU 시간(초)
        delta_time = end_time - start_time
        # CPU 사용률(%) = (ΔCPU시간 / (interval * 코어 수)) * 100
        usage_percent = (delta_time / (interval * cpu_count)) * 100
        usage_result[tid] = usage_percent

    # usage_result를 사용률이 큰 순서대로 정렬
    # 정렬 결과를 [(tid, usage_percent), ...] 형태의 리스트로 반환
    sorted_usage_list = sorted(
        usage_result.items(),
        key=lambda x: x[1],
        reverse=True
    )

    return sorted_usage_list

def set_thread_affinity(tid, affinity_mask):
    """
    주어진 TID(Thread ID)의 CPU Affinity를 affinity_mask로 설정한다.
    - affinity_mask 예시:
      * 0x1 -> CPU0만
      * 0x2 -> CPU1만
      * 0x3 -> CPU0 + CPU1
      * 0xF -> CPU0 + CPU1 + CPU2 + CPU3 (4코어 시스템 예시)
    - 성공하면 이전(old) Affinity Mask를 반환한다.
    - 실패 시 예외 발생.
    """
    # 스레드 핸들을 연다.
    # 필요한 접근 권한: THREAD_SET_INFORMATION, THREAD_QUERY_INFORMATION
    desired_access = win32con.THREAD_SET_INFORMATION | win32con.THREAD_QUERY_INFORMATION
    hThread = win32api.OpenThread(desired_access, False, tid)
    if not hThread:
        raise OSError(f"OpenThread failed for TID={tid}")

    try:
        # SetThreadAffinityMask를 통해 스레드 Affinity 설정
        old_mask = win32process.SetThreadAffinityMask(hThread, affinity_mask)
        if old_mask == 0:
            raise OSError(f"SetThreadAffinityMask failed for TID={tid}")
    finally:
        # 핸들 닫기
        win32api.CloseHandle(hThread)

    return old_mask


def cpus_to_affinity_mask(cpu_list):
    """
    주어진 CPU 인덱스 리스트를 CPU Affinity 마스크(정수)로 변환한다.
    
    예:
      cpu_list = [0, 2, 3]
      => 이진수   : 1101 (역순: CPU0=LSB)
      => 10진수   : 13
      => 16진수   : 0xd
    """
    mask = 0
    for cpu_index in cpu_list:
        mask |= (1 << cpu_index)
    return int(mask)


def mask_to_cpus_list(mask):
    mask_str = mask

    # 1) 정수값으로 변환
    mask_value = int(mask_str, 2)

    # 2) 0비트부터 순서대로 확인하면서 set(1)인 비트를 찾아 리스트화
    cpu_list = []
    bit_index = 0
    while mask_value > 0:
        if mask_value & 1:  # 현재 비트가 1이면
            cpu_list.append(bit_index)
        mask_value >>= 1
        bit_index += 1

    print(cpu_list)  # [5, 8, 11, 12, 14]
    return cpu_list

def set_thread_affinity_for_top_threads_li(top_threads, li, num_threads=24):

    top_threads = top_threads[:24]

    # 코어 수 확인
    cpu_count = psutil.cpu_count(logical=True)
    if num_threads > cpu_count:
        print(f"Error: Number of threads ({num_threads}) exceeds available CPU cores ({cpu_count}).")
        return

    for idx, (thread_id, usage) in enumerate(top_threads):
        try:
            # 각 스레드를 각각의 코어에 배정
            affinity_mask = cpus_to_affinity_mask(li[idx])
            old_mask = set_thread_affinity(thread_id, affinity_mask)
            print(f"Thread ID {thread_id}: CPU affinity set to Core {idx} (Old Mask: {old_mask:#010b})")
        except Exception as e:
            print(f"Failed to set affinity for Thread ID {thread_id}: {e}")

def set_thread_affinity_for_top_threads(top_threads, num_threads=24):

    top_threads = top_threads[:24]

    # 코어 수 확인
    cpu_count = psutil.cpu_count(logical=True)
    if num_threads > cpu_count:
        print(f"Error: Number of threads ({num_threads}) exceeds available CPU cores ({cpu_count}).")
        return

    for idx, (thread_id, usage) in enumerate(top_threads):
        try:
            # 각 스레드를 각각의 코어에 배정
            affinity_mask = 1 << idx  # 각 코어에 대해 1 << 코어 인덱스를 사용해 마스크 생성
            old_mask = set_thread_affinity(thread_id, affinity_mask)
            print(f"Thread ID {thread_id}: CPU affinity set to Core {idx} (Old Mask: {old_mask:#010b})")
        except Exception as e:
            print(f"Failed to set affinity for Thread ID {thread_id}: {e}")
    
    idx, (thread_id, usage) = 0, top_threads[0]
    affinity_mask = cpus_to_affinity_mask(np.arange(0,23))
    old_mask = set_thread_affinity(thread_id, affinity_mask)
    print(f"Thread ID {thread_id}: CPU affinity set to Core {idx} (Old Mask: {old_mask:#010b})")

    # idx, (thread_id, usage) = 0, top_threads[23]
    # affinity_mask = cpus_to_affinity_mask([0])
    # old_mask = set_thread_affinity(thread_id, affinity_mask)
    # print(f"Thread ID {thread_id}: CPU affinity set to Core {idx} (Old Mask: {old_mask:#010b})")



def set_affinity_all_threads_of_pid_to_all_cores(pid):
    """
    주어진 PID의 모든 스레드에 대해 CPU affinity를 모든 코어를 사용하도록 설정합니다.

    :param pid: 프로세스 ID
    """
    cpu_count = psutil.cpu_count(logical=True)
    affinity_mask = (1 << cpu_count) - 1  # 모든 코어를 사용하는 비트마스크

    try:
        # psutil을 사용하여 프로세스 스레드 정보 가져오기
        process = psutil.Process(pid)
        threads = process.threads()  # 스레드 정보 가져오기

        for thread in threads:
            thread_id = thread.id
            try:
                # 스레드 핸들 열기
                thread_handle = win32api.OpenThread(
                    win32con.THREAD_SET_INFORMATION | win32con.THREAD_QUERY_INFORMATION,
                    False,
                    thread_id
                )

                # CPU affinity 설정
                win32process.SetThreadAffinityMask(thread_handle, affinity_mask)
                print(f"Thread ID {thread_id} of PID {pid}: Affinity set to all cores.")

                # 핸들 닫기
                win32api.CloseHandle(thread_handle)
            except Exception as thread_error:
                print(f"Failed to set affinity for Thread ID {thread_id} of PID {pid}: {thread_error}")

    except Exception as process_error:
        print(f"Failed to process PID {pid}: {process_error}")

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

top5 = get_top_5_mem_processes()
if top5[0]["name"] != "msedge.exe":
    pid = top5[0]["pid"]
else:
    pid = top5[0]["pid"]


a = get_thread_ids(pid)
time.sleep(2)
b = get_thread_ids(pid)
print(set(a) == set(b))



def set_cpu_affinity(pid, cpu_list):
    p = psutil.Process(pid)
    current_affinity = p.cpu_affinity()
    p.cpu_affinity(cpu_list)
    return current_affinity

cpu_list = list(np.array(np.arange(10,24)).tolist())

set_cpu_affinity(pid, cpu_list)



top_threads = get_thread_cpu_usage(pid, 5)
set_thread_affinity_for_top_threads(top_threads, 24)

li = [
    list(np.arange(0,2)),
    list(np.arange(2,6)),
    list(np.arange(10,24)),
    list(np.arange(10,24)),
    list(np.arange(10,24)),
    list(np.arange(10,24)),
    list(np.arange(10,24)),
    list(np.arange(10,24)),
    list(np.arange(10,24)),
    list(np.arange(10,24)),
    list(np.arange(10,24)),
    list(np.arange(10,24)),
    list(np.arange(10,24)),
    list(np.arange(10,24)),
    list(np.arange(10,24)),
    list(np.arange(10,24)),
    list(np.arange(10,24)),
    list(np.arange(10,24)),
    list(np.arange(10,24)),
    list(np.arange(10,24)),
    list(np.arange(10,24)),
    list(np.arange(10,24)),
    list(np.arange(10,24)),
    list(np.arange(10,24)),
    list(np.arange(10,24)),
    list(np.arange(10,24)),
    list(np.arange(10,24)),
    list(np.arange(10,24)),
    list(np.arange(10,24)),
    list(np.arange(10,24)),
    list(np.arange(10,24)),
    list(np.arange(10,24))
]
set_thread_affinity_for_top_threads_li(top_threads, li, 24)

li = [
    [10],
    [22],
    [0],
    [11],
    [1],
    [23],
    [12],
    [13],
    list(np.arange(2,6)),
    list(np.arange(2,6)),
    list(np.arange(6,10)),
    list(np.arange(6,10)),
    list(np.arange(14,18)),
    list(np.arange(14,18)),
    list(np.arange(18,22)),
    list(np.arange(18,22)),
    list(np.arange(0,24)),
    list(np.arange(0,24)),
    list(np.arange(0,24)),
    list(np.arange(0,24)),
    list(np.arange(0,24)),
    list(np.arange(0,24)),
    list(np.arange(0,24)),
    list(np.arange(0,24))
]
set_thread_affinity_for_top_threads_li(top_threads, li, 24)


li = [
    [10],
    [11],
    [12],
    [13],
    [0],
    [1],
    [22],
    [23],
    list(np.arange(2,6)),
    list(np.arange(2,6)),
    list(np.arange(2,6)),
    list(np.arange(2,6)),
    list(np.arange(6,10)),
    list(np.arange(6,10)),
    list(np.arange(6,10)),
    list(np.arange(6,10)),
    list(np.arange(14,18)),
    list(np.arange(14,18)),
    list(np.arange(14,18)),
    list(np.arange(14,18)),
    list(np.arange(18,22)),
    list(np.arange(18,22)),
    list(np.arange(18,22)),
    list(np.arange(18,22)),
]
set_thread_affinity_for_top_threads_li(top_threads, li, 24)

li = [
    list(np.arange(0,24)),
    list(np.arange(0,24)),
    list(np.arange(0,24)),
    list(np.arange(0,24)),
    list(np.arange(0,24)),
    list(np.arange(0,24)),
    list(np.arange(0,24)),
    list(np.arange(0,24)),
    list(np.arange(0,24)),
    list(np.arange(0,24)),
    list(np.arange(0,24)),
    list(np.arange(0,24)),
    list(np.arange(0,24)),
    list(np.arange(0,24)),
    list(np.arange(0,24)),
    list(np.arange(0,24)),
    list(np.arange(0,24)),
    list(np.arange(0,24)),
    list(np.arange(0,24)),
    list(np.arange(0,24)),
    list(np.arange(0,24)),
    list(np.arange(0,24)),
    list(np.arange(0,24)),
    list(np.arange(0,24))
]
set_thread_affinity_for_top_threads_li(top_threads, li, 24)



li = [
    [2,3,4,5],
    [2,3,4,5],
    [2,3,4,5],
    [2,3,4,5],
    [6,7,8,9],
    [6,7,8,9],
    [6,7,8,9],
    [6,7,8,9], 
    [14,15,16,17],
    [14,15,16,17],
    [14,15,16,17],
    [14,15,16,17],
    [18,19,20,21],
    [18,19,20,21],
    [18,19,20,21],
    [18,19,20,21],
    list(np.arange(6,24)),
    list(np.arange(6,24)),
    list(np.arange(6,24)),
    list(np.arange(6,24)),
    list(np.arange(6,24)),
    list(np.arange(6,24)),
    list(np.arange(6,24)),
    list(np.arange(6,24)),
    list(np.arange(6,24)),
    list(np.arange(6,24)),
    list(np.arange(6,24)),
    list(np.arange(6,24)),
    list(np.arange(6,24)),
    list(np.arange(6,24)),
    list(np.arange(6,24))
]

li = [
[0],
[1],
[10],
[11],
[12],
[13],
[22],
[23],
[2,3,4,5],
[2,3,4,5],
[2,3,4,5],
[2,3,4,5],
[6,7,8,9],
[6,7,8,9],
[6,7,8,9],
[6,7,8,9],    
[14,15,16,17],
[14,15,16,17],
[14,15,16,17],
[14,15,16,17],
[18,19,20,21],
[18,19,20,21],
[18,19,20,21],
[18,19,20,21]
]
set_thread_affinity_for_top_threads_li(top_threads, li, 24)

li = [
list(np.arange(0,24)),
[0, 2,3,4,5],
[1, 2,3,4,5],
[10, 2,3,4,5],
[11, 2,3,4,5],
[12, 6,7,8,9],
[13, 6,7,8,9],
[22, 6,7,8,9],
[23, 6,7,8,9],    
[14,15,16,17],
[14,15,16,17],
[14,15,16,17],
[14,15,16,17],
[18,19,20,21],
[18,19,20,21],
[18,19,20,21],
[18,19,20,21],
[2,3,4,5],
[2,3,4,5],
[2,3,4,5],
[2,3,4,5],
[6,7,8,9],
[6,7,8,9],
[6,7,8,9],
# [6,7,8,9],
]
# cpus = [0, 1]  # CPU 코어 리스트
# set_thread_affinity(pid, cpus)

xx = cpus_to_affinity_mask([10, 11, 12, 13])
set_thread_affinity(9768, xx)



xx = cpus_to_affinity_mask([10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21])
set_thread_affinity(2500, xx)

xx = cpus_to_affinity_mask([0, 1])
set_thread_affinity(10396, xx)


xx = cpus_to_affinity_mask([10, 11])
set_thread_affinity(23012, xx)


xx = cpus_to_affinity_mask([12, 13])
set_thread_affinity(13256, xx)

xx = cpus_to_affinity_mask([22, 23])
set_thread_affinity(13324, xx)

xx = cpus_to_affinity_mask([2, 3, 4, 5])
set_thread_affinity(26352, xx)

xx = cpus_to_affinity_mask([2, 3, 4, 5])
set_thread_affinity(10056, xx)


xx = cpus_to_affinity_mask([6, 7, 8, 9])
set_thread_affinity(5368, xx)

xx = cpus_to_affinity_mask([6, 7, 8, 9])
set_thread_affinity(2448, xx)
