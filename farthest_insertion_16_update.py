import requests
import folium
import os

# --- 1. CÁC HÀM THUẬT TOÁN ---

def solve_tsp_farthest_insertion(matrix):
    num_nodes = len(matrix)
    unvisited = set(range(num_nodes))
    
    start_node = 0
    unvisited.remove(start_node)
    
    # Tìm điểm cách xa điểm 0 nhất để tạo khung bao ban đầu
    farthest_node = max(unvisited, key=lambda x: matrix[start_node][x] + matrix[x][start_node])
    unvisited.remove(farthest_node)
    
    tour = [start_node, farthest_node, start_node]
    
    while unvisited:
        best_k = None
        max_dist_to_tour = -1
        
        # BƯỚC A: Tìm điểm k ở xa lộ trình hiện tại nhất
        for k in unvisited:
            min_dist_to_tour = min(matrix[i][k] + matrix[k][i] for i in tour[:-1])
            if min_dist_to_tour > max_dist_to_tour:
                max_dist_to_tour = min_dist_to_tour
                best_k = k
                
        k = best_k
        best_i = -1
        min_insertion_cost = float('inf')
        
        # BƯỚC B: Tìm vị trí chèn k ít tốn chi phí (thời gian) nhất
        for i in range(len(tour) - 1):
            u = tour[i]
            v = tour[i+1]
            cost = matrix[u][k] + matrix[k][v] - matrix[u][v]
            
            if cost < min_insertion_cost:
                min_insertion_cost = cost
                best_i = i
                
        tour.insert(best_i + 1, k)
        unvisited.remove(k)
        
    return tour

def calculate_cost(tour, matrix):
    cost = 0
    for i in range(len(tour) - 1):
        cost += matrix[tour[i]][tour[i+1]]
    return cost

def optimize_or_opt(tour, matrix):
    base_tour = tour[:-1]
    n = len(base_tour)
    improved = True
    best_tour = base_tour[:]
    
    def get_base_cost(t):
        c = sum(matrix[t[idx]][t[idx+1]] for idx in range(len(t) - 1))
        c += matrix[t[-1]][t[0]]
        return c

    best_cost = get_base_cost(best_tour)

    while improved:
        improved = False
        # Thử nhấc chuỗi 3, 2, 1 điểm
        for segment_length in [3, 2, 1]:
            if improved: break
            
            for i in range(n):
                if improved: break
                if i + segment_length > n:
                    continue
                
                segment = best_tour[i:i+segment_length]
                rest = best_tour[:i] + best_tour[i+segment_length:]
                
                for j in range(len(rest) + 1):
                    if j == i: continue
                    
                    new_tour = rest[:j] + segment + rest[j:]
                    new_cost = get_base_cost(new_tour)
                    
                    if new_cost < best_cost:
                        best_cost = new_cost
                        best_tour = new_tour
                        improved = True
                        break
                        
    return best_tour + [best_tour[0]]

# --- 2. HÀM TẠO BẢN ĐỒ VÀ IN KẾT QUẢ ---

def generate_farthest_oropt_map(coords_str, output_filename, dataset_name=""):
    print(f"\n{'='*45}")
    print(f"BẮT ĐẦU XỬ LÝ DỮ LIỆU: {dataset_name.upper()} ({len(coords_str)} ĐIỂM)")
    print(f"{'='*45}")
    
    coord_joined = ";".join(coords_str)
    table_url = f"http://router.project-osrm.org/table/v1/driving/{coord_joined}?annotations=duration"
    
    print("Đang lấy ma trận thời gian...")
    table_response = requests.get(table_url).json()
    if table_response.get("code") != "Ok":
        print("Lỗi lấy ma trận OSRM.")
        return
        
    matrix = table_response["durations"]
    
    # 1. Chạy Chèn xa nhất thuần
    initial_tour = solve_tsp_farthest_insertion(matrix)
    initial_cost = calculate_cost(initial_tour, matrix)
    print("\n[1] TRƯỚC CẢI TIẾN (CHÈN XA NHẤT THUẦN)")
    print(f"Lộ trình: {' -> '.join(str(n + 1) for n in initial_tour)}")
    print(f"Tổng thời gian: {round(initial_cost)} giây")

    # 2. Chạy cải tiến Or-opt
    optimized_tour = optimize_or_opt(initial_tour, matrix)
    optimized_cost = calculate_cost(optimized_tour, matrix)
    print("\n[2] SAU CẢI TIẾN (CHÈN XA NHẤT + OR-OPT)")
    print(f"Lộ trình: {' -> '.join(str(n + 1) for n in optimized_tour)}")
    print(f"Tổng thời gian: {round(optimized_cost)} giây")
    
    savings = round(initial_cost - optimized_cost)
    percent = round((savings / initial_cost) * 100, 2) if initial_cost > 0 else 0
    print(f"-> Tiết kiệm được: {savings} giây ({percent}%)\n")

    # 3. Gọi Route API vẽ đường thực tế
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
            font_size = '11px' if len(coords_str) > 10 else '12px'
            
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
                    font-size: {font_size};
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
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(current_dir, output_filename)
        m.save(output_path)
        
        print(f"Thành công! Mở file '{output_filename}' để xem kết quả.")
    else:
        print("Lỗi lấy dữ liệu chỉ đường từ OSRM.")


# --- 3. DỮ LIỆU ĐẦU VÀO VÀ THỰC THI ---

if __name__ == "__main__":
    coords_16 = [
        # --- NHÓM 1: ĐIỂM BIÊN / NGOẠI LAI (Outliers / Hull Nodes - 4 điểm) ---
            "105.790528,21.052114",  # 1. Bệnh viện E (Cực Bắc)
            "105.793812,21.007536",  # 2. Big C Thăng Long / GO! (Cực Nam)
            "105.774815,21.036941",  # 3. Đại học Thương mại (Cực Tây)
            "105.803109,21.045812",  # 4. Học viện Quốc phòng (Cực Đông Bắc)
        
            # --- NHÓM 2: ĐIỂM CẦU NỐI / TRỤC GIAO THÔNG (Bridge Nodes - 4 điểm) ---
            "105.789135,21.036142",  # 5. Học viện Báo chí và Tuyên truyền (Trục Xuân Thủy)
            "105.782718,21.036815",  # 6. Đại học Quốc gia Hà Nội (Trục Xuân Thủy)
            "105.786911,21.023827",  # 7. Viện Huyết học - Truyền máu Trung ương (Trục Dương Đình Nghệ)
            "105.792814,21.046833",  # 8. Học viện Kỹ thuật Quân sự (Trục Hoàng Quốc Việt)
        
            # --- NHÓM 3: ĐIỂM CỤM ĐÔ THỊ / TRUNG TÂM (Cluster Nodes - 8 điểm) ---
            "105.792412,21.025634",  # 9. Công viên Cầu Giấy (Trung tâm quận)
            "105.798925,21.042118",  # 10. Công viên Nghĩa Đô
            "105.798714,21.040622",  # 11. Bảo tàng Dân tộc học Việt Nam
            "105.795233,21.042916",  # 12. Hồ Nghĩa Tân
            "105.794217,21.033529",  # 13. Làng Quốc tế Thăng Long
            "105.782936,21.030925",  # 14. Tòa nhà FPT Cầu Giấy
            "105.792541,21.015208",  # 15. Chợ Nam Trung Yên
            "105.796631,21.009124"   # 16. Trường THPT Chuyên Hà Nội - Amsterdam
    ]
    
    coords_25 = coords_16 + [
        "105.784500,21.032100", "105.796300,21.021400", "105.803200,21.031100",
        "105.775600,21.034500", "105.789900,21.042300", "105.792100,21.026700",
        "105.786700,21.023400", "105.781900,21.039800", "105.795500,21.038800"
    ]

    # Chạy cho tập 16 điểm
    generate_farthest_oropt_map(coords_16, "caugiay_16_farthest_oropt_map.html", "caugiay_16")
    
    # Chạy cho tập 25 điểm
    generate_farthest_oropt_map(coords_25, "caugiay_25_farthest_oropt_map.html", "caugiay_25")