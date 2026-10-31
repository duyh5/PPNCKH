import numpy as np
import pandas as pd
import plotly.graph_objects as go
import os
import webbrowser
from scipy.spatial import distance_matrix

# 1. Đọc dữ liệu từ file cities_8_DepotCentric.csv
file_path = r"C:\test-prj\TSP_update\tsp_datasets\cities_8_DepotCentric.csv"

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

# 3. Hàm chạy thuật toán Clarke-Wright (Tiết kiệm)
def clarke_wright_step_by_step(dist_matrix, depot=0):
    n = len(dist_matrix)
    
    # Lập ma trận tiết kiệm S(i, j)
    savings = []
    for i in range(1, n):
        for j in range(i + 1, n):
            s = dist_matrix[depot][i] + dist_matrix[depot][j] - dist_matrix[i][j]
            savings.append(((i, j), s))
            
    # Sắp xếp các cặp theo giá trị tiết kiệm giảm dần
    savings.sort(key=lambda x: x[1], reverse=True)
    
    # Khởi tạo mỗi đỉnh là một lộ trình riêng biệt
    paths = {i: [i] for i in range(1, n)}
    
    # Duyệt danh sách tiết kiệm để ghép các đỉnh
    for (i, j), s in savings:
        path_i = paths[i]
        path_j = paths[j]
        
        if path_i is path_j:
            continue
            
        is_i_endpoint = (i == path_i[0] or i == path_i[-1])
        is_j_endpoint = (j == path_j[0] or j == path_j[-1])
        
        if is_i_endpoint and is_j_endpoint:
            if i == path_i[0]:
                path_i.reverse()
            if j == path_j[-1]:
                path_j.reverse()
                
            new_path = path_i + path_j
            
            for node in new_path:
                paths[node] = new_path
                
        if len(paths[1]) == n - 1:
            break
            
    # Nối hai đầu của chuỗi kết quả với Depot để khép vòng
    final_tour = [depot] + paths[1] + [depot]
    
    return final_tour

# Lấy lộ trình
tour = clarke_wright_step_by_step(dist_matrix, depot=0)
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
fig1.update_layout(**layout_styling, title_text="Mô hình 8 thành phố (DepotCentric)")


# ==========================================
# 6. TẠO BIỂU ĐỒ 2: KẾT QUẢ LỘ TRÌNH CLARKE-WRIGHT
# ==========================================
fig2 = go.Figure()
fig2.add_trace(
    go.Scatter(
        x=tour_points[:, 0], y=tour_points[:, 1],
        mode='lines+markers+text',
        line=dict(color='forestgreen', width=1.5),
        marker=dict(color='red', size=8),
        text=[str(node) for node in tour],
        textposition="top right"
    )
)

fig2.update_xaxes(**axis_styling)
fig2.update_yaxes(**axis_styling)
fig2.update_layout(**layout_styling, title_text="Clarke-Wright - Lộ trình")


# ==========================================
# 7. XUẤT RA 2 FILE HTML RIÊNG BIỆT VÀ TỰ ĐỘNG MỞ
# ==========================================
output_dir = r"C:\test-prj\TSP_update\CSLT"
os.makedirs(output_dir, exist_ok=True) 

# Đường dẫn 2 file
file_diem = os.path.join(output_dir, "mo_hinh_thanh_pho_depotcentric.html")
file_ket_qua = os.path.join(output_dir, "lo_trinh_clarke_wright_ket_qua.html")

# Ghi file
fig1.write_html(file_diem)
fig2.write_html(file_ket_qua)

print(f"Đã xuất 2 file thành công:")
print(f"1. {file_diem}")
print(f"2. {file_ket_qua}")

# Tự động mở file HTML trên trình duyệt mặc định ngay khi code chạy xong
webbrowser.open('file://' + os.path.realpath(file_diem))
webbrowser.open('file://' + os.path.realpath(file_ket_qua))