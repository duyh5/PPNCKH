import networkx as nx
import matplotlib.pyplot as plt
import requests
import folium
import os

def solve_tsp_greedy(matrix, start_node=0):
    num_nodes = len(matrix)
    visited = [False] * num_nodes
    tour = [start_node]
    visited[start_node] = True
    
    current_node = start_node
    for _ in range(num_nodes - 1):
        next_node = -1
        min_time = float('inf')
        for j in range(num_nodes):
            if not visited[j] and matrix[current_node][j] < min_time:
                min_time = matrix[current_node][j]
                next_node = j
                
        tour.append(next_node)
        visited[next_node] = True
        current_node = next_node
        
    tour.append(start_node)
    return tour

def calculate_cost(tour, matrix):
    """Tính tổng thời gian di chuyển của một chu trình"""
    cost = 0
    # tour chứa sẵn điểm đầu ở cuối mảng (VD: 0 -> 4 -> ... -> 0)
    for i in range(len(tour) - 1):
        cost += matrix[tour[i]][tour[i+1]]
    return cost

def optimize_3opt(tour, matrix):
    """Cải tiến lộ trình bằng thuật toán 3-opt Local Search"""
    # Loại bỏ điểm cuối (điểm xuất phát lặp lại) để thuận tiện hoán vị
    base_tour = tour[:-1]
    n = len(base_tour)
    improved = True
    best_tour = base_tour
    
    # Tính chi phí mảng base_tour (cần cộng thêm cạnh nối điểm cuối về điểm đầu)
    def get_base_cost(t):
        c = sum(matrix[t[idx]][t[idx+1]] for idx in range(len(t) - 1))
        c += matrix[t[-1]][t[0]]
        return c

    best_cost = get_base_cost(best_tour)

    while improved:
        improved = False
        # Cắt chu trình tại 3 vị trí i, j, k
        for i in range(n - 2):
            for j in range(i + 1, n - 1):
                for k in range(j + 1, n):
                    # Chia lộ trình thành 4 phân đoạn
                    A = best_tour[:i+1]
                    B = best_tour[i+1:j+1]
                    C = best_tour[j+1:k+1]
                    D = best_tour[k+1:]

                    # Sinh ra các đoạn đảo ngược (Vì là đồ thị có hướng/Bất đối xứng)
                    B_R = B[::-1]
                    C_R = C[::-1]

                    # 7 cách nối lại 3 đoạn vừa cắt (Bao gồm cả các hoán vị của 2-opt và 3-opt)
                    alternative_tours = [
                        A + B + C_R + D,     # Đảo ngược đoạn C
                        A + B_R + C + D,     # Đảo ngược đoạn B
                        A + C + B + D,       # Đổi chỗ B và C
                        A + C + B_R + D,     # Đổi chỗ và đảo ngược B
                        A + C_R + B + D,     # Đổi chỗ và đảo ngược C
                        A + C_R + B_R + D,   # Đảo ngược cả B và C
                        A + B_R + C_R + D    # Hoán vị chéo
                    ]

                    # Thử nghiệm xem có cách nối nào giảm thời gian không
                    for new_t in alternative_tours:
                        new_cost = get_base_cost(new_t)
                        if new_cost < best_cost:
                            best_tour = new_t
                            best_cost = new_cost
                            improved = True
                            break # Thoát vòng lặp để bắt đầu rà soát lại từ đầu với lộ trình mới
                    if improved:
                        break
                if improved:
                    break
                    
    # Trả về lộ trình khép kín
    return best_tour + [best_tour[0]]

def generate_3opt_google_map():
    # Danh sách 10 tọa độ dữ liệu Cầu Giấy
    coords_str = [
       # --- NHÓM 1: ĐIỂM BIÊN / NGOẠI LAI (Outliers / Hull Nodes - ~20% = 8 điểm) ---
           # Đóng vai trò khung bao lồi, ép các thuật toán xây dựng biên giới vòng quanh quận
           "105.790528,21.052114",  # 1. Bệnh viện E (Cực Bắc)
           "105.793812,21.007536",  # 2. Big C Thăng Long / GO! (Cực Nam)
           "105.774815,21.036941",  # 3. Đại học Thương mại (Cực Tây)
           "105.803109,21.045812",  # 4. Học viện Quốc phòng (Cực Đông Bắc)
           "105.803318,21.012537",  # 5. Đại học Lao động - Xã hội (Cực Đông Nam)
           "105.775529,21.035218",  # 6. Công viên Hồ điều hòa Mai Dịch (Tân Tây)
           "105.803241,21.030517",  # 7. Chợ Cầu Giấy / Đê Tô Hoàng (Cực Đông)
           "105.797219,21.007834",  # 8. Tòa nhà Charmvit Tower (Rìa Nam - Trần Duy Hưng)
       
           # --- NHÓM 2: ĐIỂM CẦU NỐI / TRỤC GIAO THÔNG (Bridge Nodes - ~30% = 12 điểm) ---
           # Nằm dọc các tuyến đường huyết mạch (Xuân Thủy, Cầu Giấy, Nguyễn Khang, Trần Thái Tông)
           "105.789135,21.036142",  # 9. Học viện Báo chí và Tuyên truyền (Trục Xuân Thủy)
           "105.782718,21.036815",  # 10. Đại học Quốc gia Hà Nội (Trục Xuân Thủy)
           "105.783429,21.037311",  # 11. Trường Đại học Sư phạm Hà Nội
           "105.782105,21.038144",  # 12. Trường Đại học Công nghệ - ĐHQGHN
           "105.785219,21.038431",  # 13. Chợ Nhà Xanh (Phan Văn Trường)
           "105.786911,21.023827",  # 14. Viện Huyết học - Truyền máu Trung ương (Trục Dương Đình Nghệ)
           "105.784522,21.024538",  # 15. Tòa nhà PVI Tower (Khu Cầu Giấy mới)
           "105.783016,21.029812",  # 16. Tòa nhà CMC Tower (Trục Duy Tân)
           "105.784839,21.028115",  # 17. Bộ Nội vụ (Đường Tôn Thất Thuyết)
           "105.782327,21.026743",  # 18. Bộ Tài nguyên và Môi trường
           "105.792814,21.046833",  # 19. Học viện Kỹ thuật Quân sự (Trục Hoàng Quốc Việt)
           "105.783622,21.041908",  # 20. Trường Đại học Ngoại ngữ - ĐHQGHN
       
           # --- NHÓM 3: ĐIỂM CỤM ĐÔ THỊ / TRUNG TÂM (Cluster Nodes - ~50% = 20 điểm) ---
           # Tạo mật độ dày đặc tại các khu vực nội quận (Nghĩa Đô, Nghĩa Tân, Trung Hòa, Dịch Vọng)
           "105.792412,21.025634",  # 21. Công viên Cầu Giấy (Trung tâm quận)
           "105.798925,21.042118",  # 22. Công viên Nghĩa Đô
           "105.798714,21.040622",  # 23. Bảo tàng Dân tộc học Việt Nam
           "105.795233,21.042916",  # 24. Hồ Nghĩa Tân
           "105.791826,21.044239",  # 25. Chợ Nghĩa Tân
           "105.794217,21.033529",  # 26. Làng Quốc tế Thăng Long
           "105.794635,21.035721",  # 27. Tòa nhà Discovery Complex
           "105.796811,21.033845",  # 28. Nhà văn hóa Quận Cầu Giấy
           "105.782142,21.036619",  # 29. Indochina Plaza Hanoi (IPH)
           "105.782936,21.030925",  # 30. Tòa nhà FPT Cầu Giấy
           "105.786514,21.025109",  # 31. Cục Hàng hải Việt Nam
           "105.781824,21.017216",  # 32. Tòa nhà Vinaconex 9 (Trung Hòa)
           "105.792541,21.015208",  # 33. Chợ Nam Trung Yên
           "105.800512,21.015528",  # 34. Tòa nhà Trung Yên Plaza
           "105.798215,21.021804",  # 35. Chợ Yên Hòa
           "105.796631,21.009124",  # 36. Trường THPT Chuyên Hà Nội - Amsterdam
           "105.778842,21.033519",  # 37. Bệnh viện 19-8 Bộ Công an (Mai Dịch)
           "105.782511,21.039826",  # 38. Bệnh viện Đa khoa Y học Cổ truyền Hà Nội
           "105.776533,21.040211",  # 39. Chợ Đồng Xa
           "105.788534,21.006822"   # 40. Trung tâm Hội nghị Quốc gia (Cổng Phạm Hùng)
    ]
    
    # 1. Lấy ma trận thời gian từ OSRM
    coord_joined = ";".join(coords_str)
    table_url = f"http://router.project-osrm.org/table/v1/driving/{coord_joined}?annotations=duration"
    
    print("Đang lấy ma trận thời gian...")
    table_response = requests.get(table_url).json()
    if table_response.get("code") != "Ok":
        print("Lỗi lấy ma trận OSRM.")
        return
        
    matrix = table_response["durations"]
    
    # 2. Khởi tạo bằng Tham lam và in kết quả
    greedy_tour = solve_tsp_greedy(matrix)
    greedy_cost = calculate_cost(greedy_tour, matrix)
    print("\n--- TRƯỚC CẢI TIẾN (THAM LAM THUẦN) ---")
    print(f"Lộ trình: {' -> '.join(str(n + 1) for n in greedy_tour)}")
    print(f"Tổng thời gian: {round(greedy_cost)} giây")

    # 3. Tối ưu hóa bằng 3-opt và in kết quả
    optimized_tour = optimize_3opt(greedy_tour, matrix)
    optimized_cost = calculate_cost(optimized_tour, matrix)
    print("\n--- SAU CẢI TIẾN (THAM LAM + 3-OPT) ---")
    print(f"Lộ trình: {' -> '.join(str(n + 1) for n in optimized_tour)}")
    print(f"Tổng thời gian: {round(optimized_cost)} giây")
    print(f"-> Tiết kiệm được: {round(greedy_cost - optimized_cost)} giây so với thuật toán gốc\n")

    # 4. Vẽ bản đồ cho lộ trình đã cải tiến
    ordered_coords_str = [coords_str[i] for i in optimized_tour]
    route_joined = ";".join(ordered_coords_str)
    
    route_url = f"http://router.project-osrm.org/route/v1/driving/{route_joined}?overview=full&geometries=geojson"
    print("Đang tải dữ liệu vẽ mạng lưới đường thực tế từ OSRM...")
    route_response = requests.get(route_url).json()
    
    if route_response.get("code") == "Ok":
        geometry = route_response["routes"][0]["geometry"]["coordinates"]
        detailed_path = [[lat, lon] for lon, lat in geometry]
        
        m = folium.Map(
            location=[21.0280, 105.7900], 
            zoom_start=14, 
            tiles='https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',
            attr='Google Maps'
        )
        
        coords_latlon = [[float(c.split(',')[1]), float(c.split(',')[0])] for c in coords_str]
        for i, (lat, lon) in enumerate(coords_latlon):
            bg_color = '#e74c3c' if i == 0 else '#3498db'
            
            icon_html = f'''
                <div style="
                    background-color: {bg_color};
                    color: white;
                    border-radius: 50%;
                    width: 24px;
                    height: 24px;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    font-weight: bold;
                    font-family: Arial, sans-serif;
                    font-size: 12px;
                    border: 2px solid white;
                    box-shadow: 1px 1px 3px rgba(0,0,0,0.5);
                ">{i+1}</div>
            '''
            
            folium.Marker(
                location=[lat, lon],
                popup=f"Tọa độ: {lat}, {lon}",
                tooltip=f"Điểm {i+1}", 
                icon=folium.DivIcon(html=icon_html, icon_size=(24, 24), icon_anchor=(12, 12))
            ).add_to(m)
            
        folium.PolyLine(
            detailed_path,
            weight=5,
            color='#800080',
            opacity=0.8
        ).add_to(m)
        
       # Lưu thẳng vào thư mục làm việc hiện tại (Current Working Directory)
        output_path = "caugiay_10_greedy_3opt_map.html"
        m.save(output_path)

    # In ra đường dẫn tuyệt đối để bạn copy và dán vào thanh địa chỉ trình duyệt
        full_path = os.path.abspath(output_path)
        print(f"Thành công! File được lưu tại:\n{full_path}")
    else:
        print("Lỗi lấy dữ liệu chỉ đường từ OSRM.")

def plot_styled_network(tour, coords_str, title="Sau cải tiến"):
    G = nx.DiGraph() # Đồ thị có hướng
    
    # 1. Trích xuất tọa độ (Longitude -> X, Latitude -> Y)
    pos = {}
    for i, coord in enumerate(coords_str):
        lon, lat = map(float, coord.split(','))
        # Phóng to hệ tọa độ một chút để giãn cách các điểm
        pos[i] = (lon * 10000, lat * 10000) 

    # 2. Tạo danh sách các cạnh từ mảng lộ trình (tour)
    edges = [(tour[i], tour[i+1]) for i in range(len(tour)-1)]
    G.add_edges_from(edges)

    # 3. Cấu hình khung hình và nền (Màu nền xám nhạt #f4f5f9 giống ảnh)
    plt.figure(figsize=(10, 12))
    ax = plt.gca()
    ax.set_facecolor('#f4f5f9') 
    plt.title(title, fontsize=28, fontweight='bold', pad=20, fontname='sans-serif')

    # 4. Vẽ các cạnh (Màu xanh xám #5b84b1, nét dày)
    nx.draw_networkx_edges(
        G, pos, 
        width=2.5, 
        edge_color='#5b84b1', 
        arrows=False, # Tắt mũi tên để giống ảnh nguyên bản
        ax=ax
    )

    # 5. Vẽ Node nguồn (Điểm đầu tiên - màu đỏ #c0392b)
    start_node = tour[0]
    nx.draw_networkx_nodes(
        G, pos, 
        nodelist=[start_node], 
        node_size=600, 
        node_color='#c0392b', 
        ax=ax
    )
    
    # 6. Vẽ các Node còn lại (Màu xanh dương đậm #2c5282)
    other_nodes = [n for n in G.nodes() if n != start_node]
    nx.draw_networkx_nodes(
        G, pos, 
        nodelist=other_nodes, 
        node_size=500, 
        node_color='#2c5282', 
        ax=ax
    )

    # 7. Vẽ số thứ tự bên trong Node (Màu trắng)
    labels = {n: str(n + 1) for n in G.nodes()} # Cộng 1 để bắt đầu từ 1
    nx.draw_networkx_labels(
        G, pos, 
        labels=labels, 
        font_color='white', 
        font_size=10, 
        ax=ax
    )

    # 8. Hoàn thiện và hiển thị
    plt.axis('off') # Ẩn viền và trục tọa độ
    plt.tight_layout()
    plt.show() # Lệnh này sẽ bung cửa sổ ảnh ra màn hình