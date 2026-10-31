import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from scipy.spatial import distance_matrix

# 1. Đọc dữ liệu từ file
file_path = r"C:\test-prj\TSP_update\tsp_datasets\cities_16_Uniform.csv"

try:
    df = pd.read_csv(file_path)
    if 'X' in df.columns and 'Y' in df.columns:
        points = df[['X', 'Y']].values
    elif 'x' in df.columns and 'y' in df.columns:
        points = df[['x', 'y']].values
    else:
        points = df.iloc[:, -2:].values
except FileNotFoundError:
    print(f"Lỗi: Không tìm thấy file {file_path}. Đảm bảo file nằm cùng thư mục.")
    exit()

# 2. Tính ma trận khoảng cách Euclid
dist_matrix = distance_matrix(points, points)

# 3. Hàm chạy thuật toán Tham lam (Nearest Neighbor)
def nearest_neighbor_step_by_step(dist_matrix, start_node=0):
    n = len(dist_matrix)
    unvisited = set(range(n))
    tour = [start_node]
    unvisited.remove(start_node)
    current_node = start_node
    
    while unvisited:
        distances_to_unvisited = {v: dist_matrix[current_node][v] for v in unvisited}
        next_node = min(distances_to_unvisited, key=distances_to_unvisited.get)
        tour.append(next_node)
        unvisited.remove(next_node)
        current_node = next_node
        
    # Quay về điểm xuất phát
    tour.append(start_node)
    return tour

# Lấy lộ trình
tour = nearest_neighbor_step_by_step(dist_matrix, start_node=0)
tour_points = points[tour] # Lấy mảng tọa độ theo đúng thứ tự lộ trình

# 4. Vẽ đồ thị giống hình mẫu bằng subplots (1 hàng, 2 cột)
fig = make_subplots(rows=1, cols=2, 
                    subplot_titles=("Mô hình 8 thành phố", "Thuật toán Tham lam - Lộ trình"))

# Biểu đồ bên trái: Chỉ vẽ các điểm thành phố màu đỏ
fig.add_trace(
    go.Scatter(
        x=points[:, 0], y=points[:, 1],
        mode='markers',
        marker=dict(color='red', size=8),
        hoverinfo="text",
        hovertext=[f"Đỉnh {i}" for i in range(len(points))]
    ),
    row=1, col=1
)

# Biểu đồ bên phải: Vẽ các điểm đỏ và nối bằng đường màu xanh lá
fig.add_trace(
    go.Scatter(
        x=tour_points[:, 0], y=tour_points[:, 1],
        mode='lines+markers',
        line=dict(color='forestgreen', width=1.5),
        marker=dict(color='red', size=8)
    ),
    row=1, col=2
)

# 5. Căn chỉnh màu sắc, viền, phông nền giống hệt mẫu
axis_styling = dict(
    showline=True,           # Hiện đường kẻ trục
    linewidth=1.5,           # Độ dày viền trục
    linecolor='black',       # Màu viền trục
    gridcolor='whitesmoke',  # Màu lưới nền nhạt
    zeroline=False           # Tắt đường kẻ số 0 mặc định
)

# Áp dụng giao diện cho cả 2 biểu đồ
fig.update_xaxes(**axis_styling, row=1, col=1)
fig.update_yaxes(**axis_styling, row=1, col=1)
fig.update_xaxes(**axis_styling, row=1, col=2)
fig.update_yaxes(**axis_styling, row=1, col=2)

fig.update_layout(
    plot_bgcolor='white',    # Nền trắng
    showlegend=False,        # Ẩn chú thích
    width=1100,              # Chiều rộng khung hình
    height=500,              # Chiều cao khung hình
    title_x=0.5              # Căn giữa tiêu đề (nếu có)
)

# 6. Xuất ra file HTML trong thư mục CSDL
output_dir = r"C:\\test-prj\\TSP_update\\MPTN"
os.makedirs(output_dir, exist_ok=True) 

output_filename = os.path.join(output_dir, "lo_trinh_tham_lam_16_uniform.html")
fig.write_html(output_filename)

print(f"Đã xuất file giao diện mới tại: {output_filename}")