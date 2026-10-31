import numpy as np
import pandas as pd
import plotly.graph_objects as go
import os
import webbrowser
from scipy.spatial import distance_matrix

# 1. Đọc dữ liệu từ file cities_8_Uniform.csv
file_path = r"C:\test-prj\TSP_update\tsp_datasets\cities_8_Uniform.csv"

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

# 3. Hàm chạy thuật toán Chèn xa nhất (Farthest Insertion)
def farthest_insertion_step_by_step(dist_matrix, start_node=0):
    n = len(dist_matrix)
    unvisited = set(range(n))
    
    # Tìm đỉnh xa điểm xuất phát nhất
    farthest_from_start = max(unvisited, key=lambda v: dist_matrix[start_node][v])
    tour = [start_node, farthest_from_start, start_node]
    
    unvisited.remove(start_node)
    unvisited.remove(farthest_from_start)
    
    while unvisited:
        # Tìm đỉnh k chưa thăm có khoảng cách xa nhất tới lộ trình hiện tại
        dist_to_tour = {}
        for v in unvisited:
            min_dist = min(dist_matrix[v][node] for node in tour[:-1])
            dist_to_tour[v] = min_dist
            
        k = max(dist_to_tour, key=dist_to_tour.get)
        
        # Tìm vị trí chèn k vào lộ trình sao cho chi phí tăng thêm nhỏ nhất
        best_increase = float('inf')
        best_pos = -1
        
        for i in range(len(tour) - 1):
            u = tour[i]
            v = tour[i+1]
            increase = dist_matrix[u][k] + dist_matrix[k][v] - dist_matrix[u][v]
            
            if increase < best_increase:
                best_increase = increase
                best_pos = i + 1
                
        # Chèn k vào vị trí tốt nhất
        tour.insert(best_pos, k)
        unvisited.remove(k)
        
    return tour

# Chạy lấy lộ trình
tour = farthest_insertion_step_by_step(dist_matrix, start_node=0)
tour_points = points[tour] 

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
        mode='markers+text',
        marker=dict(color='red', size=8),
        text=[str(i) for i in range(len(points))],
        textposition="top right",
        hoverinfo="text"
    )
)

fig1.update_xaxes(**axis_styling)
fig1.update_yaxes(**axis_styling)
fig1.update_layout(**layout_styling, title_text="Mô hình 8 thành phố (Uniform)")

# ==========================================
# 6. TẠO BIỂU ĐỒ 2: KẾT QUẢ LỘ TRÌNH FARTHEST INSERTION
# ==========================================
fig2 = go.Figure()
fig2.add_trace(
    go.Scatter(
        x=tour_points[:, 0], y=tour_points[:, 1],
        mode='lines+markers+text',
        line=dict(color='forestgreen', width=1.5),
        marker=dict(color='red', size=8),
        text=[str(tour[i]) for i in range(len(tour))],
        textposition="top right"
    )
)

fig2.update_xaxes(**axis_styling)
fig2.update_yaxes(**axis_styling)
fig2.update_layout(**layout_styling, title_text="Farthest Insertion - Lộ trình")


# ==========================================
# 7. XUẤT RA 2 FILE HTML RIÊNG BIỆT VÀ TỰ ĐỘNG MỞ
# ==========================================
output_dir = r"C:\test-prj\TSP_update\CSLT"
os.makedirs(output_dir, exist_ok=True) 

# Đường dẫn 2 file
file_diem = os.path.join(output_dir, "mo_hinh_thanh_pho_chen_xa_nhat.html")
file_ket_qua = os.path.join(output_dir, "lo_trinh_chen_xa_nhat_ket_qua.html")

# Ghi file
fig1.write_html(file_diem)
fig2.write_html(file_ket_qua)

print(f"Đã xuất 2 file thành công:")
print(f"1. {file_diem}")
print(f"2. {file_ket_qua}")

# Tự động mở file HTML trên trình duyệt mặc định ngay khi code chạy xong
webbrowser.open('file://' + os.path.realpath(file_diem))
webbrowser.open('file://' + os.path.realpath(file_ket_qua))