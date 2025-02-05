import os
import glob
import pandas as pd
import numpy as np

def compute_gpu_percent_mean(file_path, column_name="FrameTime", percent=0.01):
    """
    주어진 파일에서 column_name 컬럼의 하위 percent(기본: 1%)에 해당하는 값들의 평균을 계산.
    """
    try:
        df = pd.read_excel(file_path, usecols=[column_name],)
    except Exception as e:
        print(f"파일 {file_path} 읽기 실패: {e}")
        return None

    # 컬럼이 존재하는지 확인
    if column_name not in df.columns:
        print(f"파일 {file_path}에 '{column_name}' 컬럼이 없습니다.")
        return None

    # 결측치 제거 후 데이터 선택
    values = df[column_name].dropna()

    if len(values) == 0:
        print(f"파일 {file_path}의 '{column_name}' 컬럼에 데이터가 없습니다.")
        return None

    mean_frame = values.mean()


    # 데이터를 오름차순으로 정렬한 후, 하위 percent(예: 1%)에 해당하는 개수 계산
    sorted_values = values.sort_values()
    n_bottom = int(np.ceil(len(sorted_values) * percent))
    # 최소 1개의 값은 선택하도록 합니다.
    n_bottom = max(n_bottom, 1)

    bottom_values = sorted_values.iloc[:n_bottom]
    mean_val = bottom_values.mean()

    return [mean_val, mean_frame]

def compute_bottom_percent_mean(file_path, column_name="FrameTime", percent=0.01):
    """
    주어진 파일에서 column_name 컬럼의 하위 percent(기본: 1%)에 해당하는 값들의 평균을 계산.
    """
    try:
        df = pd.read_excel(file_path, usecols=[column_name],)
    except Exception as e:
        print(f"파일 {file_path} 읽기 실패: {e}")
        return None

    # 컬럼이 존재하는지 확인
    if column_name not in df.columns:
        print(f"파일 {file_path}에 '{column_name}' 컬럼이 없습니다.")
        return None

    # 결측치 제거 후 데이터 선택
    values = (1 / df[column_name].dropna()) * 1000

    if len(values) == 0:
        print(f"파일 {file_path}의 '{column_name}' 컬럼에 데이터가 없습니다.")
        return None

    mean_frame = values.mean()


    # 데이터를 오름차순으로 정렬한 후, 하위 percent(예: 1%)에 해당하는 개수 계산
    sorted_values = values.sort_values()
    n_bottom = int(np.ceil(len(sorted_values) * percent))
    # 최소 1개의 값은 선택하도록 합니다.
    n_bottom = max(n_bottom, 1)

    bottom_values = sorted_values.iloc[:n_bottom]
    mean_val = bottom_values.mean()

    return [mean_val, mean_frame]

# 분석할 폴더 경로 (원하는 폴더 경로로 변경하세요)
folder_path = r"result/PresentMon/cs2"  # 예: r"C:\Data\ExcelFiles"
folder_path = r"result/PresentMon/Cyberpunk"  # 예: r"C:\Data\ExcelFiles"
folder_path = r"result/PresentMon/SOTTR"  # 예: r"C:\Data\ExcelFiles"

# 폴더 내의 모든 .xls 파일 리스트 생성
xls_files = glob.glob(os.path.join(folder_path, "*.xls"))

# if not xls_files:
#     print("해당 폴더에 .xls 파일이 없습니다.")
# else:
#     for file in xls_files:
#         mean_bottom = compute_bottom_percent_mean(file, column_name="FrameTime", percent=0.01)
#         if mean_bottom is not None:
#             print(f"파일: {os.path.basename(file)}  ->  하위 1% FrameTime 평균: {mean_bottom[0]} 전체 FrameTime 평균: {mean_bottom[1]}")



if not xls_files:
    print("해당 폴더에 .xls 파일이 없습니다.")
else:
    for file in xls_files:
        mean_bottom = compute_gpu_percent_mean(file, column_name="GPUUtilization", percent=0.01)
        if mean_bottom is not None:
            print(f"파일: {os.path.basename(file)}  ->  하위 1% GPUUtilization 평균: {mean_bottom[0]} 전체 GPUUtilization 평균: {mean_bottom[1]}")
