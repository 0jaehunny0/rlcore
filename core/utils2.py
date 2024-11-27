import subprocess
import numpy as np

from time import sleep
import time
import random

from typing import Optional
from utils import *

target_fps=30
target_temp=65
beta=2

little_available_frequencies = [300000, 574000, 738000, 930000, 1098000, 1197000, 1328000, 1401000, 1598000, 1704000, 1803000]
mid_available_frequencies = [400000, 553000, 696000, 799000, 910000, 1024000, 1197000, 1328000, 1491000, 1663000, 1836000, 1999000, 2130000, 2253000]
big_available_frequencies = [500000, 851000, 984000, 1106000, 1277000, 1426000, 1582000, 1745000, 1826000, 2048000, 2188000, 2252000, 2401000, 2507000, 2630000, 2704000, 2802000]
gpu_available_frequencies = [151000, 202000, 251000, 302000, 351000, 400000, 471000, 510000, 572000, 701000, 762000, 848000]

little_len = 11
mid_len = 14
big_len = 17
gpu_len = 12

little_min_freq = 300000
mid_min_freq = 400000
big_min_freq = 500000
gpu_min_freq = 151000

little_max_freq = 1803000
mid_max_freq = 2253000
big_max_freq = 2802000 
gpu_max_freq = 848000

def set_frequency_and_get_energy(little_min, little_max, mid_min, mid_max, big_min, big_max, gpu_min, gpu_max):

    msg = 'adb shell "echo '+str(big_min)+' > /sys/devices/system/cpu/cpufreq/policy6/scaling_min_freq'
    msg += ' && echo '+str(big_max)+' > /sys/devices/system/cpu/cpufreq/policy6/scaling_max_freq'

    msg += ' && echo '+str(little_min)+' > /sys/devices/system/cpu/cpufreq/policy0/scaling_min_freq'
    msg += ' && echo '+str(little_max)+' > /sys/devices/system/cpu/cpufreq/policy0/scaling_max_freq'

    msg += ' && echo '+str(mid_min)+' > /sys/devices/system/cpu/cpufreq/policy4/scaling_min_freq'
    msg += ' && echo '+str(mid_max)+' > /sys/devices/system/cpu/cpufreq/policy4/scaling_max_freq'


    msg += ' && echo '+str(gpu_min)+' > /sys/class/misc/mali0/device/scaling_min_freq'
    msg += ' &&  echo '+str(gpu_max)+' > /sys/class/misc/mali0/device/scaling_max_freq'

    msg += ' && cat /sys/bus/iio/devices/iio:device0/energy_value'
    msg += ' && cat /sys/bus/iio/devices/iio:device1/energy_value'
    msg += ' && cat /proc/stat'
	
    msg += '"'

    result = subprocess.Popen(msg, shell=True, stdout=subprocess.PIPE).stdout.read()
    result = result.decode('utf-8')
    result = result.split("\n")

    t1 = int(result[0][2:])
    big = int(result[4].split()[1])
    mid = int(result[5].split()[1])
    little = int(result[6].split()[1])

    t2 = int(result[9][2:])
    gpu = int(result[16].split()[1])

    li = []
    for i in result[18:26]:
        temp = np.array(i.split()[1:], dtype=np.int32)
        li.append([temp[0:7].sum(), temp[3]])

    return t1, t2, little, mid, big, gpu, np.array(li)

def set_frequency_and_get_energy2(little_max, mid_max, big_max, gpu_max, up, down, gpu_rate):

    msg = 'adb shell "echo '+str(big_max)+' > /sys/devices/system/cpu/cpufreq/policy6/scaling_max_freq'    
    msg += ' && echo '+str(little_max)+' > /sys/devices/system/cpu/cpufreq/policy0/scaling_max_freq'
    msg += ' && echo '+str(mid_max)+' > /sys/devices/system/cpu/cpufreq/policy4/scaling_max_freq'
    msg += ' && echo '+str(gpu_max)+' > /sys/class/misc/mali0/device/scaling_max_freq'
    msg += ' && echo '+str(up)+' > /sys/devices/system/cpu/cpufreq/policy0/sched_pixel/up_rate_limit_us'
    msg += ' && echo '+str(up)+' > /sys/devices/system/cpu/cpufreq/policy4/sched_pixel/up_rate_limit_us'
    msg += ' && echo '+str(up)+' > /sys/devices/system/cpu/cpufreq/policy6/sched_pixel/up_rate_limit_us'
    msg += ' && echo '+str(down)+' > /sys/devices/system/cpu/cpufreq/policy0/sched_pixel/down_rate_limit_us'
    msg += ' && echo '+str(down)+' > /sys/devices/system/cpu/cpufreq/policy4/sched_pixel/down_rate_limit_us'
    msg += ' && echo '+str(down)+' > /sys/devices/system/cpu/cpufreq/policy6/sched_pixel/down_rate_limit_us'
    msg += ' && echo '+str(gpu_rate)+' > /sys/class/misc/mali0/device/dvfs_period'

    msg += ' && cat /sys/bus/iio/devices/iio:device0/energy_value'
    msg += ' && cat /sys/bus/iio/devices/iio:device1/energy_value'
    msg += ' && cat /proc/stat'
	
    msg += '"'

    result = subprocess.Popen(msg, shell=True, stdout=subprocess.PIPE).stdout.read()
    result = result.decode('utf-8')
    result = result.split("\n")

    t1 = int(result[0][2:])
    big = int(result[4].split()[1])
    mid = int(result[5].split()[1])
    little = int(result[6].split()[1])

    t2 = int(result[9][2:])
    gpu = int(result[16].split()[1])

    li = []
    for i in result[18:26]:
        temp = np.array(i.split()[1:], dtype=np.int32)
        li.append([temp[0:7].sum(), temp[3]])

    return t1, t2, little, mid, big, gpu, np.array(li)

def set_frequency_and_no_get_energy(little_max, mid_max, big_max, gpu_max, up, down, gpu_rate):

    msg = 'adb shell "echo '+str(big_max)+' > /sys/devices/system/cpu/cpufreq/policy6/scaling_max_freq'    
    msg += ' && echo '+str(little_max)+' > /sys/devices/system/cpu/cpufreq/policy0/scaling_max_freq'
    msg += ' && echo '+str(mid_max)+' > /sys/devices/system/cpu/cpufreq/policy4/scaling_max_freq'
    msg += ' && echo '+str(gpu_max)+' > /sys/class/misc/mali0/device/scaling_max_freq'
    msg += ' && echo '+str(up)+' > /sys/devices/system/cpu/cpufreq/policy0/sched_pixel/up_rate_limit_us'
    msg += ' && echo '+str(up)+' > /sys/devices/system/cpu/cpufreq/policy4/sched_pixel/up_rate_limit_us'
    msg += ' && echo '+str(up)+' > /sys/devices/system/cpu/cpufreq/policy6/sched_pixel/up_rate_limit_us'
    msg += ' && echo '+str(down)+' > /sys/devices/system/cpu/cpufreq/policy0/sched_pixel/down_rate_limit_us'
    msg += ' && echo '+str(down)+' > /sys/devices/system/cpu/cpufreq/policy4/sched_pixel/down_rate_limit_us'
    msg += ' && echo '+str(down)+' > /sys/devices/system/cpu/cpufreq/policy6/sched_pixel/down_rate_limit_us'
    msg += ' && echo '+str(gpu_rate)+' > /sys/class/misc/mali0/device/dvfs_period'
	
    msg += '"'

    subprocess.Popen(msg, shell=True, stdout=subprocess.PIPE).stdout.read()


def get_states(window):
    
    """ temps """
    msg = 'adb shell "'
    msg += ' cat /dev/thermal/tz-by-name/BIG/temp /dev/thermal/tz-by-name/MID/temp /dev/thermal/tz-by-name/LITTLE/temp /dev/thermal/tz-by-name/G3D/temp /dev/thermal/tz-by-name/qi_therm/temp /dev/thermal/tz-by-name/battery/temp'
    msg += ' && cat /dev/thermal/cdev-by-name/thermal-cpufreq-0/cur_state /dev/thermal/cdev-by-name/thermal-cpufreq-1/cur_state /dev/thermal/cdev-by-name/thermal-cpufreq-2/cur_state /dev/thermal/cdev-by-name/thermal-gpufreq-0/cur_state'
    msg += ' && cat /sys/bus/iio/devices/iio:device0/energy_value'
    msg += ' && cat /sys/bus/iio/devices/iio:device1/energy_value'
    msg += '&& cat /proc/stat'
    msg += '&& cat /sys/devices/platform/1c500000.mali/utilization'
    msg += '&& dumpsys SurfaceFlinger --latency ' + '\'' + window + '\''
    msg += '"'


    result = subprocess.Popen(msg, shell=True, stdout=subprocess.PIPE).stdout.read()
    result = result.decode('utf-8')

    result = result.split("\n")
    big_temp = int(result[0])
    mid_temp = int(result[1])
    little_temp = int(result[2])
    gpu_temp = int(result[3])
    qi_temp = int(result[4])
    battery_temp = int(result[5])

    little_cdev = int(result[6])
    mid_cdev = int(result[7])
    big_cdev = int(result[8])
    gpu_cdev = int(result[9])

    t1 = int(result[10][2:])
    big_e = int(result[14].split()[1])
    mid_e = int(result[15].split()[1])
    little_e = int(result[16].split()[1])

    t2 = int(result[19][2:])
    gpu_e = int(result[26].split()[1])

    li = []
    for i in result[28:36]:
        temp = np.array(i.split()[1:], dtype=np.int32)
        li.append([temp[0:7].sum(), temp[3]])

    gpu_util = [int(result[44])/100]

    startTime = int(result[-23].split("\t")[0])
    lastTime = int(result[-3].split("\t")[-1])  
    twentyFrameTime = (lastTime - startTime) / 1000000000
    fps = 20 / twentyFrameTime

    c_states = [little_cdev, mid_cdev, big_cdev, gpu_cdev]

    temps = [little_temp/1000, mid_temp/1000, big_temp/1000, gpu_temp/1000, qi_temp/1000, battery_temp/1000]
    return c_states, temps, fps, t1, t2, little_e, mid_e, big_e, gpu_e, np.array(li), gpu_util


def get_states2(window, qos_type: str, qos_time_prev: float, byte_prev: Optional[int], packet_prev: Optional[int]):
    """ temps """
    msg = 'adb shell "'
    msg += ' cat /dev/thermal/tz-by-name/BIG/temp /dev/thermal/tz-by-name/MID/temp /dev/thermal/tz-by-name/LITTLE/temp /dev/thermal/tz-by-name/G3D/temp /dev/thermal/tz-by-name/qi_therm/temp /dev/thermal/tz-by-name/battery/temp'
    msg += ' && cat /dev/thermal/cdev-by-name/thermal-cpufreq-0/cur_state /dev/thermal/cdev-by-name/thermal-cpufreq-1/cur_state /dev/thermal/cdev-by-name/thermal-cpufreq-2/cur_state /dev/thermal/cdev-by-name/thermal-gpufreq-0/cur_state'
    msg += ' && cat /sys/bus/iio/devices/iio:device0/energy_value'
    msg += ' && cat /sys/bus/iio/devices/iio:device1/energy_value'
    msg += '&& cat /proc/stat'
    msg += '&& cat /sys/devices/platform/1c500000.mali/utilization'
    msg += '&& cat /sys/devices/system/cpu/cpufreq/policy0/scaling_cur_freq /sys/devices/system/cpu/cpufreq/policy4/scaling_cur_freq /sys/devices/system/cpu/cpufreq/policy6/scaling_cur_freq /sys/class/misc/mali0/device/cur_freq'
    msg += '&& dumpsys SurfaceFlinger --latency ' + '\'' + window + '\''
    msg += '"'

    result = subprocess.Popen(msg, shell=True, stdout=subprocess.PIPE).stdout.read()
    result = result.decode('utf-8')

    result = result.split("\n")
    big_temp = int(result[0])
    mid_temp = int(result[1])
    little_temp = int(result[2])
    gpu_temp = int(result[3])
    qi_temp = int(result[4])
    battery_temp = int(result[5])

    little_cdev = int(result[6])
    mid_cdev = int(result[7])
    big_cdev = int(result[8])
    gpu_cdev = int(result[9])

    t1 = int(result[10][2:])
    big_e = int(result[14].split()[1])
    mid_e = int(result[15].split()[1])
    little_e = int(result[16].split()[1])

    t2 = int(result[19][2:])
    gpu_e = int(result[26].split()[1])

    li = []
    for i in result[29:37]:
        temp = np.array(i.split()[1:], dtype=np.int32)
        li.append([temp[0:7].sum(), temp[3]])

    gpu_util = [int(result[44])/100]

    little = int(result[45])
    mid = int(result[46])
    big = int(result[47])
    gpu = int(result[48])

    freqs = np.array([little, mid, big, gpu])

    byte_cur = None
    packet_cur = None
    qos_time_cur = None
    match qos_type:
        case "fps":              
            startTime = int(result[-33].split("\t")[0])
            lastTime = int(result[-3].split("\t")[-1])  
            twentyFrameTime = (lastTime - startTime) / 1000000000
            qos = 30 / twentyFrameTime
        case "byte":
            byte_cur = get_packet_info(window, qos_type)
            qos_time_cur = time.time()
            qos = cal_packet((byte_prev, byte_cur), (qos_time_prev, qos_time_cur))
            print(byte_cur[1] - byte_prev[1], byte_cur[0] - byte_prev[0], qos_time_cur - qos_time_prev, qos)
        case "packet":
            packet_cur = get_packet_info(window, qos_type)
            qos_time_cur = time.time()
            qos = cal_packet((packet_prev, packet_cur), (qos_time_prev, qos_time_cur))

    c_states = [little_cdev, mid_cdev, big_cdev, gpu_cdev]

    temps = [little_temp/1000, mid_temp/1000, big_temp/1000, gpu_temp/1000, qi_temp/1000, battery_temp/1000]


    return c_states, temps, qos, t1, t2, little_e, mid_e, big_e, gpu_e, np.array(li), gpu_util, freqs, qos_time_cur, byte_cur, packet_cur

def get_core_util():
	msg = 'adb shell cat /proc/stat'
	result = subprocess.run(msg.split(), stdout=subprocess.PIPE)
	result = result.stdout.decode('utf-8')
	result = result.split("\n")

	li = []
	for i in result[1:9]:
		temp = np.array(i.split()[1:], dtype=np.int32)
		li.append([temp[0:7].sum(), temp[3]])

	return np.array(li)

def cal_core_util(b, a):
	x = b - a
	return (1 - x[:, 1] / x[:, 0]) 

def get_cpu_util():
	msg = 'adb shell top -n 1'
	result = subprocess.run(msg.split(), stdout=subprocess.PIPE)
	result = result.stdout.decode('utf-8')
	result = result.split("\n")
	cpu_util = [int(result[3].split("%idle")[0].split(" ")[-1])/800*100]
	return cpu_util

def get_gpu_util():
	msg = 'adb shell cat /sys/devices/platform/1c500000.mali/utilization'
	result = subprocess.run(msg.split(), stdout=subprocess.PIPE)
	result = result.stdout.decode('utf-8')
	result = result.split("\n")
	gpu_util = [int(result[0])/100]
	return gpu_util

def get_frequency():
	msg = 'adb shell cat /sys/devices/system/cpu/cpufreq/policy0/scaling_cur_freq /sys/devices/system/cpu/cpufreq/policy4/scaling_cur_freq /sys/devices/system/cpu/cpufreq/policy6/scaling_cur_freq /sys/class/misc/mali0/device/cur_freq'
	result = subprocess.run(msg.split(), stdout=subprocess.PIPE)
	result = result.stdout.decode('utf-8')
	result = result.split("\n")
	little = int(result[0])
	mid = int(result[1])
	big = int(result[2])
	gpu = int(result[3])

	return little, mid, big, gpu

def get_window2(window):
    window = r'SurfaceView[com.pubg.krmobile/com.epicgames.ue4.GameActivity]\(BLAST\)#0"'
    msg = r'adb shell "dumpsys SurfaceFlinger --latency ' + window
    result = subprocess.Popen(msg, shell=True, stdout=subprocess.PIPE).stdout.read()
    result = result.decode('utf-8')
    result = result.split("\n")

    startTime = int(result[-23].split("\t")[0])
    lastTime = int(result[-3].split("\t")[-1])  
    twentyFrameTime = (lastTime - startTime) / 1000000000
    fps = 20 / twentyFrameTime

def get_window():
    msg = 'adb shell dumpsys SurfaceFlinger'
    result = subprocess.run(msg.split(), stdout=subprocess.PIPE)
    result = result.stdout.decode('utf-8')
    result = result.split("\n")
    ans = "asdf"
    for i in range(len(result)):
        if "Fingerprint" in result[i]:
            if "Letterbox" in result[i+3]: continue
            print(result[i+3])
            ans = result[i+3]
            break
    ans = ans.split("Layer ")[-1][1:-1]
    
    window = ans
    return ans


def get_fps(window):
    msg = 'adb shell dumpsys SurfaceFlinger --latency ' + '"' + window + '"'
    result = subprocess.run(msg.split(), stdout=subprocess.PIPE)
    result = result.stdout.decode('utf-8')
    result = result.split("\n")

    startTime = int(result[-23].split("\t")[0])
    lastTime = int(result[-3].split("\t")[-1])  
    twentyFrameTime = (lastTime - startTime) / 1000000000
    fps = 20 / twentyFrameTime

    return fps

def get_energy():
    msg = 'adb shell cat /sys/bus/iio/devices/iio:device0/energy_value'
    msg2 = 'adb shell cat /sys/bus/iio/devices/iio:device1/energy_value'
    result = subprocess.run(msg.split(), stdout=subprocess.PIPE)
    result2 = subprocess.run(msg2.split(), stdout=subprocess.PIPE)

    result = result.stdout.decode('utf-8')
    result = result.split("\n")
    t1 = int(result[0][2:])
    big = int(result[4].split()[1])
    mid = int(result[5].split()[1])
    little = int(result[6].split()[1])
    
    result2 = result2.stdout.decode('utf-8')
    result2 = result2.split("\n")
    t2 = int(result2[0][2:])
    gpu = int(result2[7].split()[1])
    
    return t1, t2, little, mid, big, gpu

def get_battery_power():
    msg = 'adb shell cat /sys/class/power_supply/battery/current_now'
    result = subprocess.run(msg.split(), stdout=subprocess.PIPE)
    current = int(result.stdout.decode('utf-8'))
    msg = 'adb shell cat /sys/class/power_supply/battery/voltage_now'
    result = subprocess.run(msg.split(), stdout=subprocess.PIPE)
    voltage = int(result.stdout.decode('utf-8'))
    current = current * 1.0 / 1e3
    voltage = voltage * 1.0 / 1e6
    return [float(abs(current)*abs(voltage))] # mW

def get_temperatures():

    msg = 'adb shell cat /dev/thermal/tz-by-name/BIG/temp /dev/thermal/tz-by-name/MID/temp /dev/thermal/tz-by-name/LITTLE/temp /dev/thermal/tz-by-name/G3D/temp /dev/thermal/tz-by-name/qi_therm/temp /dev/thermal/tz-by-name/battery/temp'
    result = subprocess.run(msg.split(), stdout=subprocess.PIPE)
    result = result.stdout.decode('utf-8')
    result = result.split("\n")
    big = int(result[0])
    mid = int(result[1])
    little = int(result[2])
    gpu = int(result[3])
    qi = int(result[4])
    battery = int(result[5])

    return little/1000, mid/1000, big/1000, gpu/1000, qi/1000, battery/1000

def set_rate_limit_us(rate_limit_us, dvfs_period): # us / ms
    msg = 'adb shell "echo '+str(rate_limit_us)+' > /sys/devices/system/cpu/cpufreq/policy0/sched_pixel/down_rate_limit_us"'
    subprocess.Popen(msg, shell=True, stdout=subprocess.PIPE).stdout.read()
    msg = 'adb shell "echo '+str(rate_limit_us)+' > /sys/devices/system/cpu/cpufreq/policy4/sched_pixel/down_rate_limit_us"'
    subprocess.Popen(msg, shell=True, stdout=subprocess.PIPE).stdout.read()
    msg = 'adb shell "echo '+str(rate_limit_us)+' > /sys/devices/system/cpu/cpufreq/policy6/sched_pixel/down_rate_limit_us"'
    subprocess.Popen(msg, shell=True, stdout=subprocess.PIPE).stdout.read()
    msg = 'adb shell "echo '+str(rate_limit_us)+' > /sys/devices/system/cpu/cpufreq/policy0/sched_pixel/up_rate_limit_us"'
    subprocess.Popen(msg, shell=True, stdout=subprocess.PIPE).stdout.read()
    msg = 'adb shell "echo '+str(rate_limit_us)+' > /sys/devices/system/cpu/cpufreq/policy4/sched_pixel/up_rate_limit_us"'
    subprocess.Popen(msg, shell=True, stdout=subprocess.PIPE).stdout.read()
    msg = 'adb shell "echo '+str(rate_limit_us)+' > /sys/devices/system/cpu/cpufreq/policy6/sched_pixel/up_rate_limit_us"'
    subprocess.Popen(msg, shell=True, stdout=subprocess.PIPE).stdout.read()

    msg = 'adb shell "echo '+str(dvfs_period)+' > /sys/class/misc/mali0/device/dvfs_period"'
    subprocess.Popen(msg, shell=True, stdout=subprocess.PIPE).stdout.read()     


def set_rate_limit_us2(up, down, dvfs_period): # us / ms
    msg = 'adb shell "echo '+str(down)+' > /sys/devices/system/cpu/cpufreq/policy0/sched_pixel/down_rate_limit_us"'
    subprocess.Popen(msg, shell=True, stdout=subprocess.PIPE).stdout.read()
    msg = 'adb shell "echo '+str(down)+' > /sys/devices/system/cpu/cpufreq/policy4/sched_pixel/down_rate_limit_us"'
    subprocess.Popen(msg, shell=True, stdout=subprocess.PIPE).stdout.read()
    msg = 'adb shell "echo '+str(down)+' > /sys/devices/system/cpu/cpufreq/policy6/sched_pixel/down_rate_limit_us"'
    subprocess.Popen(msg, shell=True, stdout=subprocess.PIPE).stdout.read()
    msg = 'adb shell "echo '+str(up)+' > /sys/devices/system/cpu/cpufreq/policy0/sched_pixel/up_rate_limit_us"'
    subprocess.Popen(msg, shell=True, stdout=subprocess.PIPE).stdout.read()
    msg = 'adb shell "echo '+str(up)+' > /sys/devices/system/cpu/cpufreq/policy4/sched_pixel/up_rate_limit_us"'
    subprocess.Popen(msg, shell=True, stdout=subprocess.PIPE).stdout.read()
    msg = 'adb shell "echo '+str(up)+' > /sys/devices/system/cpu/cpufreq/policy6/sched_pixel/up_rate_limit_us"'
    subprocess.Popen(msg, shell=True, stdout=subprocess.PIPE).stdout.read()

    msg = 'adb shell "echo '+str(dvfs_period)+' > /sys/class/misc/mali0/device/dvfs_period"'
    subprocess.Popen(msg, shell=True, stdout=subprocess.PIPE).stdout.read()     


def unset_rate_limit_us():
    msg = 'adb shell "echo '+"5000"+' > /sys/devices/system/cpu/cpufreq/policy0/sched_pixel/down_rate_limit_us"'
    subprocess.Popen(msg, shell=True, stdout=subprocess.PIPE).stdout.read()
    msg = 'adb shell "echo '+"20000"+' > /sys/devices/system/cpu/cpufreq/policy4/sched_pixel/down_rate_limit_us"'
    subprocess.Popen(msg, shell=True, stdout=subprocess.PIPE).stdout.read()
    msg = 'adb shell "echo '+"20000"+' > /sys/devices/system/cpu/cpufreq/policy6/sched_pixel/down_rate_limit_us"'
    subprocess.Popen(msg, shell=True, stdout=subprocess.PIPE).stdout.read()
    msg = 'adb shell "echo '+"500"+' > /sys/devices/system/cpu/cpufreq/policy0/sched_pixel/up_rate_limit_us"'
    subprocess.Popen(msg, shell=True, stdout=subprocess.PIPE).stdout.read()
    msg = 'adb shell "echo '+"500"+' > /sys/devices/system/cpu/cpufreq/policy4/sched_pixel/up_rate_limit_us"'
    subprocess.Popen(msg, shell=True, stdout=subprocess.PIPE).stdout.read()
    msg = 'adb shell "echo '+"500"+' > /sys/devices/system/cpu/cpufreq/policy6/sched_pixel/up_rate_limit_us"'
    subprocess.Popen(msg, shell=True, stdout=subprocess.PIPE).stdout.read()

    msg = 'adb shell "echo '+"20"+' > /sys/class/misc/mali0/device/dvfs_period"'
    subprocess.Popen(msg, shell=True, stdout=subprocess.PIPE).stdout.read()     


def set_frequency(little_min, little_max, mid_min, mid_max, big_min, big_max, gpu_min, gpu_max):

    msg = 'adb shell "echo '+str(big_min)+' > /sys/devices/system/cpu/cpufreq/policy6/scaling_min_freq'
    msg += ' && echo '+str(big_max)+' > /sys/devices/system/cpu/cpufreq/policy6/scaling_max_freq'

    msg += ' && echo '+str(little_min)+' > /sys/devices/system/cpu/cpufreq/policy0/scaling_min_freq'
    msg += ' && echo '+str(little_max)+' > /sys/devices/system/cpu/cpufreq/policy0/scaling_max_freq'

    msg += ' && echo '+str(mid_min)+' > /sys/devices/system/cpu/cpufreq/policy4/scaling_min_freq'
    msg += ' && echo '+str(mid_max)+' > /sys/devices/system/cpu/cpufreq/policy4/scaling_max_freq'


    msg += ' && echo '+str(gpu_min)+' > /sys/class/misc/mali0/device/scaling_min_freq'
    msg += ' &&  echo '+str(gpu_max)+' > /sys/class/misc/mali0/device/scaling_max_freq'

    msg += '"'

    subprocess.Popen(msg, shell=True, stdout=subprocess.PIPE).stdout.read()


def unset_frequency():
    msg = 'adb shell "echo '+str(big_min_freq)+' > /sys/devices/system/cpu/cpufreq/policy6/scaling_min_freq'
    msg += ' && echo '+str(big_max_freq)+' > /sys/devices/system/cpu/cpufreq/policy6/scaling_max_freq'

    msg += ' && echo '+str(little_min_freq)+' > /sys/devices/system/cpu/cpufreq/policy0/scaling_min_freq'
    msg += ' && echo '+str(little_max_freq)+' > /sys/devices/system/cpu/cpufreq/policy0/scaling_max_freq'

    msg += ' && echo '+str(mid_min_freq)+' > /sys/devices/system/cpu/cpufreq/policy4/scaling_min_freq'
    msg += ' && echo '+str(mid_max_freq)+' > /sys/devices/system/cpu/cpufreq/policy4/scaling_max_freq'


    msg += ' && echo '+str(gpu_min_freq)+' > /sys/class/misc/mali0/device/scaling_min_freq'
    msg += ' &&  echo '+str(gpu_max_freq)+' > /sys/class/misc/mali0/device/scaling_max_freq'

    msg += '"'

    subprocess.Popen(msg, shell=True, stdout=subprocess.PIPE).stdout.read()

def set_root(): 
    msg = 'adb root'
    subprocess.run(msg.split(), stdout=subprocess.PIPE)
    msg = 'adb shell setenforce 0'
    subprocess.run(msg.split(), stdout=subprocess.PIPE)


def set_brightness(level):
    msg = 'adb shell settings put system screen_brightness '+str(level)
    subprocess.run(msg.split(), stdout=subprocess.PIPE)

def turn_on_screen():
    """ check screen and unlock screen """
    msg = 'adb shell dumpsys input_method | grep mInteractive=true'
    result = subprocess.run(msg.split(), stdout=subprocess.PIPE).stdout.decode('utf-8')
    if len(result) < 1:
        """ unlock screen """
        msg = 'adb shell input keyevent 82'
        subprocess.run(msg.split(), stdout=subprocess.PIPE)
        sleep(0.5)
    a,b = 500+random.randint(0,50), 1200+random.randint(0,100)
    c,d = 500+random.randint(0,50), 400+random.randint(0,100)
    msg = 'adb shell input touchscreen swipe '+str(a)+' '+str(b)+' '+str(c)+' '+str(d)
    subprocess.run(msg.split(), stdout=subprocess.PIPE)
    msg = 'adb shell input touchscreen swipe '+str(a)+' '+str(b)+' '+str(c)+' '+str(d)
    subprocess.run(msg.split(), stdout=subprocess.PIPE)

def turn_off_screen():
    """ check screen and lock screen """
    msg = 'adb shell dumpsys input_method | grep mInteractive=true'
    result = subprocess.run(msg.split(), stdout=subprocess.PIPE).stdout.decode('utf-8')
    if len(result) > 1:
        """ lock screen """
        msg = 'adb shell input keyevent 26'
        subprocess.run(msg.split(), stdout=subprocess.PIPE)
        sleep(0.5)


def turn_off_usb_charging():
    # msg = 'adb shell dumpsys battery set usb 0'
    msg = 'adb shell dumpsys battery unplug'
    subprocess.run(msg.split(), stdout=subprocess.PIPE)

def turn_on_usb_charging():
    # msg = 'adb shell dumpsys battery set usb 1'
    msg = 'adb shell dumpsys battery reset'
    subprocess.run(msg.split(), stdout=subprocess.PIPE)

def get_cooling_state():
    msg = 'adb shell cat /dev/thermal/cdev-by-name/thermal-cpufreq-0/cur_state /dev/thermal/cdev-by-name/thermal-cpufreq-1/cur_state /dev/thermal/cdev-by-name/thermal-cpufreq-2/cur_state /dev/thermal/cdev-by-name/thermal-gpufreq-0/cur_state'
    result = subprocess.run(msg.split(), stdout=subprocess.PIPE)
    result = result.stdout.decode('utf-8')
    result = result.split("\n")
    little = int(result[0])
    mid = int(result[1])
    big = int(result[2])
    gpu = int(result[3])
    return little, mid, big, gpu