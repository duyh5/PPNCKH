import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import webbrowser
from scipy.spatial import distance_matrix

# 1. Khai báo danh sách các kích thước N và thư mục
sizes = [128, 256]
dataset_dir = r"C:\test-prj\TSP_update\tsp_datasets"
output_dir = r"C:\test-prj\TSP_update\MPTN"
os.makedirs(output_dir, exist_ok=True) 

# 2. Hàm chạy thuật toán Chèn xa nhất (Farthest Insertion)
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
            u = tour[i]
            v = tour[i+1]
            increase = dist_matrix[u][k] + dist_matrix[k][v] - dist_matrix[u][v]
            
            if increase < best_increase:
                best_increase = increase
                best_pos = i + 1
                
        tour.insert(best_pos, k)
        unvisited.remove(k)
        
    return tour

# 3. Chạy vòng lặp qua từng bộ dữ liệu
for n in sizes:
    file_path = os.path.join(dataset_dir, f"cities_{n}_DepotCentric.csv")
    print(f"{'-'*40}\nĐang xử lý dữ liệu với N = {n} đỉnh...")
    
    try:
        df = pd.read_csv(file_path)
        if 'X' in df.columns and 'Y' in df.columns:
            points = df[['X', 'Y']].values
        elif 'x' in df.columns and 'y' in df.columns:
            points = df[['x', 'y']].values
        else:
            points = df.iloc[:, -2:].values
    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file {file_path}. Bỏ qua bộ dữ liệu này.")
        continue

    # Tính ma trận khoảng cách
    dist_matrix = distance_matrix(points, points)

    # Chạy lấy lộ trình
    tour = farthest_insertion_fast(dist_matrix, start_node=0)
    tour_points = points[tour] 

    # Tính tổng chi phí
    total_cost = sum(dist_matrix[tour[i]][tour[i+1]] for i in range(len(tour)-1))
    print(f"Chạy xong! Tổng quãng đường: {total_cost:.2f}")

    # 4. Vẽ đồ thị trực quan (1 hàng, 2 cột)
    fig = make_subplots(rows=1, cols=2, 
                        subplot_titles=(f"Mô hình {n} thành phố (DepotCentric)", f"Farthest Insertion - Cost: {total_cost:.2f}"))

    # Biểu đồ trái
    fig.add_trace(
        go.Scatter(
            x=points[:, 0], y=points[:, 1],
            mode='markers',
            marker=dict(color='red', size=6),
            hoverinfo="text",
            hovertext=[f"Đỉnh {i}" for i in range(len(points))]
        ),
        row=1, col=1
    )

    # Biểu đồ phải
    fig.add_trace(
        go.Scatter(
            x=tour_points[:, 0], y=tour_points[:, 1],
            mode='lines+markers',
            line=dict(color='forestgreen', width=1),
            marker=dict(color='red', size=6),
            hoverinfo="text",
            hovertext=[f"Đỉnh {node}" for node in tour]
        ),
        row=1, col=2
    )

    # Căn chỉnh giao diện
    axis_styling = dict(showline=True, linewidth=1.5, linecolor='black', gridcolor='whitesmoke', zeroline=False)
    fig.update_xaxes(**axis_styling, row=1, col=1)
    fig.update_yaxes(**axis_styling, row=1, col=1)
    fig.update_xaxes(**axis_styling, row=1, col=2)
    fig.update_yaxes(**axis_styling, row=1, col=2)

    fig.update_layout(plot_bgcolor='white', showlegend=False, width=1100, height=500, title_x=0.5)

    # 5. Xuất file HTML và tự động mở
    output_filename = os.path.join(output_dir, f"lo_trinh_chen_xa_nhat_DepotCentric{n}.html")
    fig.write_html(output_filename)

    print(f"Đã xuất file lộ trình tại: {output_filename}")
    webbrowser.open('file://' + os.path.realpath(output_filename))