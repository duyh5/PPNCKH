import numpy as np
import pandas as pd
import time
import os
import webbrowser
import plotly.graph_objects as go
from scipy.spatial import distance_matrix

# 1. Các thiết lập cơ bản
sizes = [13, 16, 20, 32, 64, 128, 256]
dataset_dir = r"C:\test-prj\TSP_update\tsp_datasets"
output_dir = r"C:\test-prj\TSP_update\MPTN"
os.makedirs(output_dir, exist_ok=True)

# 2. Khai báo 3 thuật toán (Phiên bản tối ưu tốc độ để đo lường)

def nearest_neighbor_fast(dist_matrix, start_node=0):
    n = len(dist_matrix)
    unvisited = set(range(n))
    tour = [start_node]
    unvisited.remove(start_node)
    current = start_node
    
    while unvisited:
        next_node = min(unvisited, key=lambda x: dist_matrix[current][x])
        tour.append(next_node)
        unvisited.remove(next_node)
        current = next_node
        
    tour.append(start_node)
    return tour

def farthest_insertion_fast(dist_matrix, start_node=0):
    n = len(dist_matrix)
    unvisited = set(range(n))
    farthest_from_start = max(unvisited, key=lambda v: dist_matrix[start_node][v])
    tour = [start_node, farthest_from_start, start_node]
    unvisited.remove(start_node)
    unvisited.remove(farthest_from_start)
    
    while unvisited:
        dist_to_tour = {v: min(dist_matrix[v][node] for node in tour[:-1]) for v in unvisited}
        k = max(dist_to_tour, key=dist_to_tour.get)
        best_increase = float('inf')
        best_pos = -1
        for i in range(len(tour) - 1):
            u, v = tour[i], tour[i+1]
            increase = dist_matrix[u][k] + dist_matrix[k][v] - dist_matrix[u][v]
            if increase < best_increase:
                best_increase = increase
                best_pos = i + 1
        tour.insert(best_pos, k)
        unvisited.remove(k)
    return tour

def clarke_wright_fast(dist_matrix, depot=0):
    n = len(dist_matrix)
    savings = []
    for i in range(n):
        if i == depot: continue
        for j in range(i + 1, n):
            if j == depot: continue
            s = dist_matrix[depot][i] + dist_matrix[depot][j] - dist_matrix[i][j]
            savings.append(((i, j), s))
            
    savings.sort(key=lambda x: x[1], reverse=True)
    paths = {i: [i] for i in range(n) if i != depot}
    
    for (i, j), s in savings:
        path_i, path_j = paths[i], paths[j]
        if path_i is path_j: continue
        
        is_i_endpoint = (i == path_i[0] or i == path_i[-1])
        is_j_endpoint = (j == path_j[0] or j == path_j[-1])
        
        if is_i_endpoint and is_j_endpoint:
            if i == path_i[0]: path_i.reverse()
            if j == path_j[-1]: path_j.reverse()
            new_path = path_i + path_j
            for node in new_path: paths[node] = new_path
        if len(paths[i]) == n - 1: break
            
    core_path = next(iter(paths.values()))
    return [depot] + core_path + [depot]

# 3. Quá trình chạy thực nghiệm và đo thời gian
results = {"N": [], "NN_Time": [], "FI_Time": [], "CW_Time": []}

print("Đang tiến hành đo lường thời gian thực thi...\n" + "-"*50)

for n in sizes:
    file_path = os.path.join(dataset_dir, f"cities_{n}_Uniform.csv")
    try:
        df = pd.read_csv(file_path)
        points = df[['X', 'Y']].values if 'X' in df.columns else df.iloc[:, -2:].values
    except FileNotFoundError:
        print(f"Bỏ qua N={n} (Không tìm thấy file).")
        continue

    dist_matrix = distance_matrix(points, points)
    results["N"].append(n)
    print(f"Đang chạy N = {n}...")

    # Đo thời gian Tham lam (Nearest Neighbor)
    start = time.perf_counter()
    nearest_neighbor_fast(dist_matrix)
    results["NN_Time"].append((time.perf_counter() - start) * 1000)

    # Đo thời gian Chèn xa nhất (Farthest Insertion)
    start = time.perf_counter()
    farthest_insertion_fast(dist_matrix)
    results["FI_Time"].append((time.perf_counter() - start) * 1000)

    # Đo thời gian Clarke-Wright
    start = time.perf_counter()
    clarke_wright_fast(dist_matrix)
    results["CW_Time"].append((time.perf_counter() - start) * 1000)

print("-" * 50 + "\nHoàn tất đo lường! Đang xuất biểu đồ...")

# 4. Vẽ biểu đồ đường cong thời gian
fig = go.Figure()

# Đường cho Tham lam
fig.add_trace(go.Scatter(x=results["N"], y=results["NN_Time"], mode='lines+markers',
                         name='Tham lam (Nearest Neighbor)', line=dict(color='blue', width=2), marker=dict(size=8)))

# Đường cho Clarke-Wright
fig.add_trace(go.Scatter(x=results["N"], y=results["CW_Time"], mode='lines+markers',
                         name='Clarke-Wright', line=dict(color='orange', width=2), marker=dict(size=8)))

# Đường cho Chèn xa nhất
fig.add_trace(go.Scatter(x=results["N"], y=results["FI_Time"], mode='lines+markers',
                         name='Chèn xa nhất (Farthest Insertion)', line=dict(color='red', width=2), marker=dict(size=8)))

# Cấu hình giao diện biểu đồ
fig.update_layout(
    title="Đánh giá Tính mở rộng (Scalability) - Thời gian thực thi theo kích thước dữ liệu",
    title_x=0.5,
    xaxis_title="Số lượng đỉnh (N)",
    yaxis_title="Thời gian thực thi (mili-giây)",
    plot_bgcolor='white',
    hovermode="x unified",
    width=1000, height=600,
    legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, bgcolor="rgba(255, 255, 255, 0.8)")
)

fig.update_xaxes(showline=True, linecolor='black', gridcolor='whitesmoke', tickvals=sizes)
fig.update_yaxes(showline=True, linecolor='black', gridcolor='whitesmoke')

# 5. Lưu và hiển thị
output_filename = os.path.join(output_dir, "danh_gia_thoi_gian_thuc_thi.html")
fig.write_html(output_filename)

print(f"Đã xuất biểu đồ tại: {output_filename}")
webbrowser.open('file://' + os.path.realpath(output_filename))