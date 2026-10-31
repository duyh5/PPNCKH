import numpy as np
import pandas as pd
import plotly.graph_objects as go
import os
from scipy.spatial import distance_matrix

# 1. Đọc dữ liệu từ file
file_path = r"C:\test-prj\TSP_update\tsp_datasets\cities_8_Clustered.csv"

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

# 4. Định dạng chung cho biểu đồ
axis_styling = dict(
    showline=True,           # Hiện đường kẻ trục
    linewidth=1.5,           # Độ dày viền trục
    linecolor='black',       # Màu viền trục
    gridcolor='whitesmoke',  # Màu lưới nền nhạt
    zeroline=False           # Tắt đường kẻ số 0 mặc định
)

layout_styling = dict(
    plot_bgcolor='white',    # Nền trắng
    showlegend=False,        # Ẩn chú thích
    width=600,               # Chiều rộng khung hình
    height=500,              # Chiều cao khung hình
    title_x=0.5              # Căn giữa tiêu đề
)

# ==========================================
# 5. TẠO BIỂU ĐỒ 1: CHỈ CÁC ĐIỂM THÀNH PHỐ
# ==========================================
fig1 = go.Figure()
fig1.add_trace(
    go.Scatter(
        x=points[:, 0], y=points[:, 1],
        mode='markers',
        marker=dict(color='red', size=8),
        hoverinfo="text",
        hovertext=[f"Đỉnh {i}" for i in range(len(points))]
    )
)

fig1.update_xaxes(**axis_styling)
fig1.update_yaxes(**axis_styling)
fig1.update_layout(**layout_styling, title_text="Mô hình 8 thành phố")


# ==========================================
# 6. TẠO BIỂU ĐỒ 2: KẾT QUẢ LỘ TRÌNH THAM LAM
# ==========================================
fig2 = go.Figure()
fig2.add_trace(
    go.Scatter(
        x=tour_points[:, 0], y=tour_points[:, 1],
        mode='lines+markers',
        line=dict(color='forestgreen', width=1.5),
        marker=dict(color='red', size=8)
    )
)

fig2.update_xaxes(**axis_styling)
fig2.update_yaxes(**axis_styling)
fig2.update_layout(**layout_styling, title_text="Thuật toán Tham lam - Lộ trình")


# ==========================================
# 7. XUẤT RA 2 FILE HTML RIÊNG BIỆT
# ==========================================
output_dir = r"C:\test-prj\TSP_update\CSLT"
os.makedirs(output_dir, exist_ok=True) 

# Đường dẫn 2 file
file_diem = os.path.join(output_dir, "mo_hinh_thanh_pho_tham_lam.html")
file_ket_qua = os.path.join(output_dir, "lo_trinh_tham_lam_ket_qua.html")

# Ghi file
fig1.write_html(file_diem)
fig2.write_html(file_ket_qua)

print(f"Đã xuất 2 file thành công:")
print(f"1. {file_diem}")
print(f"2. {file_ket_qua}")