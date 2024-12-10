import time
import threading
import psutil
import platform
import sys
import itertools
import matplotlib.pyplot as plt
import seaborn as sns
import os
import math

# OS별 affinity 설정
IS_WINDOWS = (platform.system().lower() == 'windows')
IS_LINUX = (platform.system().lower() == 'linux')
IS_MACOS = (platform.system().lower() == 'darwin')

if IS_WINDOWS:
    import ctypes
    kernel32 = ctypes.windll.kernel32
    THREAD_QUERY_INFORMATION = 0x0040
    THREAD_SET_INFORMATION = 0x0020

    def get_current_thread_handle():
        pseudo_handle = kernel32.GetCurrentThread()
        desired_access = THREAD_QUERY_INFORMATION | THREAD_SET_INFORMATION
        return kernel32.OpenThread(desired_access, False, kernel32.GetCurrentThreadId())

    def set_thread_affinity(thread_handle, core_id):
        mask = 1 << core_id
        res = kernel32.SetThreadAffinityMask(thread_handle, mask)
        if res == 0:
            raise OSError("SetThreadAffinityMask failed")

elif IS_LINUX:
    def get_current_thread_handle():
        return None

    def set_thread_affinity(thread_handle, core_id):
        os.sched_setaffinity(0, {core_id})
else:
    # macOS나 기타 OS에서는 thread affinity 설정 불가(여기서는 무시)
    def get_current_thread_handle():
        return None

    def set_thread_affinity(thread_handle, core_id):
        pass

class CoreToCoreLatencyTester:
    def __init__(self, sender_core, receiver_core):
        self.sender_core = sender_core
        self.receiver_core = receiver_core
        self.start_event = threading.Event()
        self.response_event = threading.Event()
        self.stop_flag = False
        self.round_trip_times = []

    def receiver_thread_func(self):
        thread_handle = get_current_thread_handle()
        set_thread_affinity(thread_handle, self.receiver_core)

        while not self.stop_flag:
            if self.start_event.wait(timeout=1.0):
                self.response_event.set()
                self.start_event.clear()

    def run_test(self, iterations=1000):
        receiver_thread = threading.Thread(target=self.receiver_thread_func)
        receiver_thread.start()

        sender_thread_handle = get_current_thread_handle()
        set_thread_affinity(sender_thread_handle, self.sender_core)

        for _ in range(iterations):
            start = time.perf_counter()
            self.start_event.set()
            if self.response_event.wait(timeout=1.0):
                end = time.perf_counter()
                rtt = (end - start) * 1e6
                self.round_trip_times.append(rtt)
                self.response_event.clear()

        self.stop_flag = True
        self.start_event.set()
        receiver_thread.join()

    def get_statistics(self):
        if not self.round_trip_times:
            return None
        avg = sum(self.round_trip_times) / len(self.round_trip_times)
        return {
            'average_us': avg,
            'min_us': min(self.round_trip_times),
            'max_us': max(self.round_trip_times),
            'count': len(self.round_trip_times)
        }

if __name__ == "__main__":
    cpu_count = psutil.cpu_count(logical=True)
    if cpu_count is None:
        print("Unable to determine CPU count.")
        sys.exit(1)

    # 모든 코어 쌍 (i, j) i != j
    core_pairs = [(i, j) for i in range(cpu_count) for j in range(cpu_count) if i != j]

    iterations = 500

    # NxN 매트릭스 만들기. i->j 평균 레이턴시 저장
    # 초기값은 None (측정 안된 경우)
    latency_matrix = [[math.nan for _ in range(cpu_count)] for _ in range(cpu_count)]

    for (sender_core, receiver_core) in core_pairs:
        tester = CoreToCoreLatencyTester(sender_core, receiver_core)
        tester.run_test(iterations=iterations)
        stats = tester.get_statistics()
        if stats:
            latency_matrix[sender_core][receiver_core] = stats['average_us']
            print(f"Core {sender_core} -> {receiver_core}: "
                  f"Avg={stats['average_us']:.2f} us, "
                  f"Min={stats['min_us']:.2f} us, "
                  f"Max={stats['max_us']:.2f} us")

    # heatmap 그리기
    plt.figure(figsize=(10, 8))
    sns.heatmap(latency_matrix, annot=True, fmt=".2f", cmap='coolwarm', 
                xticklabels=[f"Core {i}" for i in range(cpu_count)],
                yticklabels=[f"Core {i}" for i in range(cpu_count)],
                cbar_kws={'label': 'Latency (µs)'},
                linewidths=0.5, linecolor='gray')
    plt.title("Core-to-Core Latency Heatmap")
    plt.xlabel("Receiver Core")
    plt.ylabel("Sender Core")
    plt.tight_layout()
    plt.show()
