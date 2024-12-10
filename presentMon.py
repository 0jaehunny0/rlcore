import subprocess
import threading
import csv
import io

from torch.utils.tensorboard import SummaryWriter
import time
from time import sleep
import argparse


# parser.add_argument("--total_timesteps", type=int, default = 1001,
#                     help="total timesteps of the experiments")
# parser.add_argument("--experiment", type=int, default = 1,
#                     help="the type of experiment")
# parser.add_argument("--temperature", type=int, default = 20,
#                     help="the ouside temperature")
# parser.add_argument("--initSleep", type=int, default = 3,
#                     help="initial sleep time")
# parser.add_argument("--loadModel", type=str, default = "no",
#                     help="initial sleep time")
# parser.add_argument("--timeOut", type=int, default = 60*30,
#                     help="end time")
# parser.add_argument("--qos", default="fps", choices=['fps', 'byte', 'packet'],
#                     help="Quality of Service")
# parser.add_argument("--tempSet", type = float, default=-1.0,
# 					help="initial temperature")
# parser.add_argument("--coreOff", type = str, default="big mid ",
# 					help="initial temperature")


def monitor_fps(process_id):
    # PresentMon 명령어 설정
    cmd = ['PresentMon-2.2.0-x64.exe', '--process_id', str(process_id), '--output_stdout', '--stop_existing_session']
    
    # PresentMon 프로세스 시작 (text=True로 stdout, stderr를 텍스트 모드로 받음)
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    def read_output(pipe):
        reader = csv.reader(pipe)
        headers = next(reader, None)
        if headers is None:
            return
        for row in reader:
            if not row:
                continue
            data = dict(zip(headers, row))
            try:
                # msBetweenPresents 사용
                ms_between_presents = float(data.get('FrameTime', 0))
                if ms_between_presents > 0:
                    fps = 1000.0 / ms_between_presents
                    print(f'현재 FPS: {fps:.2f}')
            except ValueError:
                # 변환 오류 시 다음 라인으로 넘어감
                continue

    def read_stderr(pipe):
        for line in pipe:
            print("ERR:", line.strip())

    # 표준 출력 및 에러를 별도의 스레드에서 읽기
    stdout_thread = threading.Thread(target=read_output, args=(proc.stdout,))
    stderr_thread = threading.Thread(target=read_stderr, args=(proc.stderr,))

    stdout_thread.start()
    # stderr_thread.start()
    try:
        proc.wait()
    except KeyboardInterrupt:
        proc.kill()
    finally:
        stdout_thread.join()
        # stderr_thread.join()

if __name__ == "__main__":
    # 모니터링할 게임의 실행 파일 이름을 입력하세요 (예: 'Game.exe')
    parser = argparse.ArgumentParser()
    parser.add_argument("--pid", type=int, default = 22740, help="PID of the process to monitor")
    args = parser.parse_args()

    print(args)

    # qos_type = args.qos
    monitor_fps(22740)
