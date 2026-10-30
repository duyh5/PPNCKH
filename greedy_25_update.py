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
    cost = 0
    for i in range(len(tour) - 1):
        cost += matrix[tour[i]][tour[i+1]]
    return cost

def optimize_3opt(tour, matrix):
    base_tour = tour[:-1]
    n = len(base_tour)
    improved = True
    best_tour = base_tour
    
    def get_base_cost(t):
        c = sum(matrix[t[idx]][t[idx+1]] for idx in range(len(t) - 1))
        c += matrix[t[-1]][t[0]]
        return c

    best_cost = get_base_cost(best_tour)

    while improved:
        improved = False
        for i in range(n - 2):
            for j in range(i + 1, n - 1):
                for k in range(j + 1, n):
                    A = best_tour[:i+1]
                    B = best_tour[i+1:j+1]
                    C = best_tour[j+1:k+1]
                    D = best_tour[k+1:]

                    B_R = B[::-1]
                    C_R = C[::-1]

                    alternative_tours = [
                        A + B + C_R + D,
                        A + B_R + C + D,
                        A + C + B + D,
                        A + C + B_R + D,
                        A + C_R + B + D,
                        A + C_R + B_R + D,
                        A + B_R + C_R + D
                    ]

                    for new_t in alternative_tours:
                        new_cost = get_base_cost(new_t)
                        if new_cost < best_cost:
                            best_tour = new_t
                            best_cost = new_cost
                            improved = True
                            break
                    if improved: break
                if improved: break
                    
    return best_tour + [best_tour[0]]

def generate_25_points_map():
    coords_str = [
        # --- NHÓM 1: ĐIỂM BIÊN / NGOẠI LAI (Outliers / Hull Nodes - 6 điểm) ---
                   "105.790528,21.052114",  # 1. Bệnh viện E (Cực Bắc)
                   "105.793812,21.007536",  # 2. Big C Thăng Long / GO! (Cực Nam)
                   "105.774815,21.036941",  # 3. Đại học Thương mại (Cực Tây)
                   "105.803109,21.045812",  # 4. Học viện Quốc phòng (Cực Đông Bắc)
                   "105.803318,21.012537",  # 5. Đại học Lao động - Xã hội (Cực Đông Nam)
                   "105.775529,21.035218",  # 6. Công viên Hồ điều hòa Mai Dịch (Tân Tây)
               
                   # --- NHÓM 2: ĐIỂM CẦU NỐI / TRỤC GIAO THÔNG (Bridge Nodes - 8 điểm) ---
                   "105.789135,21.036142",  # 7. Học viện Báo chí và Tuyên truyền (Trục Xuân Thủy)
                   "105.782718,21.036815",  # 8. Đại học Quốc gia Hà Nội (Trục Xuân Thủy)
                   "105.783429,21.037311",  # 9. Trường Đại học Sư phạm Hà Nội
                   "105.782105,21.038144",  # 10. Trường Đại học Công nghệ - ĐHQGHN
                   "105.786911,21.023827",  # 11. Viện Huyết học - Truyền máu Trung ương
                   "105.784522,21.024538",  # 12. Tòa nhà PVI Tower (Khu Cầu Giấy mới)
                   "105.783016,21.029812",  # 13. Tòa nhà CMC Tower (Trục Duy Tân)
                   "105.792814,21.046833",  # 14. Học viện Kỹ thuật Quân sự (Trục Hoàng Quốc Việt)
               
                   # --- NHÓM 3: ĐIỂM CỤM ĐÔ THỊ / TRUNG TÂM (Cluster Nodes - 11 điểm) ---
                   "105.792412,21.025634",  # 15. Công viên Cầu Giấy (Trung tâm quận)
                   "105.798925,21.042118",  # 16. Công viên Nghĩa Đô
                   "105.798714,21.040622",  # 17. Bảo tàng Dân tộc học Việt Nam
                   "105.795233,21.042916",  # 18. Hồ Nghĩa Tân
                   "105.791826,21.044239",  # 19. Chợ Nghĩa Tân
                   "105.794217,21.033529",  # 20. Làng Quốc tế Thăng Long
                   "105.794635,21.035721",  # 21. Tòa nhà Discovery Complex
                   "105.782936,21.030925",  # 22. Tòa nhà FPT Cầu Giấy
                   "105.781824,21.017216",  # 23. Tòa nhà Vinaconex 9 (Trung Hòa)
                   "105.792541,21.015208",  # 24. Chợ Nam Trung Yên
                   "105.796631,21.009124"   # 25. Trường THPT Chuyên Hà Nội - Amsterdam
    ]
    
    coord_joined = ";".join(coords_str)
    table_url = f"http://router.project-osrm.org/table/v1/driving/{coord_joined}?annotations=duration"
    
    print("Đang lấy ma trận thời gian cho 25 điểm...")
    table_response = requests.get(table_url).json()
    if table_response.get("code") != "Ok":
        print("Lỗi lấy ma trận OSRM.")
        return
        
    matrix = table_response["durations"]
    
    greedy_tour = solve_tsp_greedy(matrix)
    greedy_cost = calculate_cost(greedy_tour, matrix)
    print("\n--- TRƯỚC CẢI TIẾN (25 ĐIỂM) ---")
    print(f"Lộ trình: {' -> '.join(str(n + 1) for n in greedy_tour)}")
    print(f"Tổng thời gian: {round(greedy_cost)} giây")

    optimized_tour = optimize_3opt(greedy_tour, matrix)
    optimized_cost = calculate_cost(optimized_tour, matrix)
    print("\n--- SAU CẢI TIẾN 3-OPT (25 ĐIỂM) ---")
    print(f"Lộ trình: {' -> '.join(str(n + 1) for n in optimized_tour)}")
    print(f"Tổng thời gian: {round(optimized_cost)} giây")
    print(f"-> Tiết kiệm: {round(greedy_cost - optimized_cost)} giây\n")

    ordered_coords_str = [coords_str[i] for i in optimized_tour]
    route_joined = ";".join(ordered_coords_str)
    
    route_url = f"http://router.project-osrm.org/route/v1/driving/{route_joined}?overview=full&geometries=geojson"
    print("Đang tải dữ liệu vẽ mạng lưới đường thực tế...")
    route_response = requests.get(route_url).json()
    
    if route_response.get("code") == "Ok":
        geometry = route_response["routes"][0]["geometry"]["coordinates"]
        detailed_path = [[lat, lon] for lon, lat in geometry]
        
        m = folium.Map(location=[21.0300, 105.7900], zoom_start=14, tiles='https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}', attr='Google Maps')
        
        coords_latlon = [[float(c.split(',')[1]), float(c.split(',')[0])] for c in coords_str]
        for i, (lat, lon) in enumerate(coords_latlon):
            bg_color = '#e74c3c' if i == 0 else '#3498db'
            icon_html = f'<div style="background-color: {bg_color}; color: white; border-radius: 50%; width: 24px; height: 24px; display: flex; justify-content: center; align-items: center; font-weight: bold; font-family: Arial, sans-serif; font-size: 11px; border: 2px solid white; box-shadow: 1px 1px 3px rgba(0,0,0,0.5);">{i+1}</div>'
            folium.Marker([lat, lon], popup=f"Tọa độ: {lat}, {lon}", tooltip=f"Điểm {i+1}", icon=folium.DivIcon(html=icon_html, icon_size=(24, 24), icon_anchor=(12, 12))).add_to(m)
            
        folium.PolyLine(detailed_path, weight=5, color='#800080', opacity=0.8).add_to(m)
        
        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "caugiay_25_greedy_3opt_map.html")
        m.save(output_path)
        print(f"Thành công! Mở file {output_path}")
    else:
        print("Lỗi lấy dữ liệu OSRM.")

if __name__ == "__main__":
    generate_25_points_map()