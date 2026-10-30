import requests
import folium
import os

def solve_tsp_farthest_insertion(matrix):
    num_nodes = len(matrix)
    unvisited = set(range(num_nodes))
    
    start_node = 0
    unvisited.remove(start_node)
    
    farthest_node = max(unvisited, key=lambda x: matrix[start_node][x] + matrix[x][start_node])
    unvisited.remove(farthest_node)
    
    tour = [start_node, farthest_node, start_node]
    
    while unvisited:
        best_k = None
        max_dist_to_tour = -1
        
        for k in unvisited:
            min_dist_to_tour = min(matrix[i][k] + matrix[k][i] for i in tour[:-1])
            if min_dist_to_tour > max_dist_to_tour:
                max_dist_to_tour = min_dist_to_tour
                best_k = k
                
        k = best_k
        best_i = -1
        min_insertion_cost = float('inf')
        
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

def generate_16_points_oropt_map():
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
    
    coord_joined = ";".join(coords_str)
    table_url = f"http://router.project-osrm.org/table/v1/driving/{coord_joined}?annotations=duration"
    
    print("Đang lấy ma trận thời gian cho 16 điểm...")
    table_response = requests.get(table_url).json()
    if table_response.get("code") != "Ok":
        print("Lỗi lấy ma trận OSRM.")
        return
        
    matrix = table_response["durations"]
    
    initial_tour = solve_tsp_farthest_insertion(matrix)
    initial_cost = calculate_cost(initial_tour, matrix)
    print("\n--- TRƯỚC CẢI TIẾN (16 ĐIỂM) ---")
    print(f"Lộ trình: {' -> '.join(str(n + 1) for n in initial_tour)}")
    print(f"Tổng thời gian: {round(initial_cost)} giây")

    optimized_tour = optimize_or_opt(initial_tour, matrix)
    optimized_cost = calculate_cost(optimized_tour, matrix)
    print("\n--- SAU CẢI TIẾN OR-OPT (16 ĐIỂM) ---")
    print(f"Lộ trình: {' -> '.join(str(n + 1) for n in optimized_tour)}")
    print(f"Tổng thời gian: {round(optimized_cost)} giây")
    print(f"-> Tiết kiệm: {round(initial_cost - optimized_cost)} giây\n")

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
        
        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "caugiay_16_farthest_oropt_map.html")
        m.save(output_path)
        print(f"Thành công! Mở file {output_path}")
    else:
        print("Lỗi lấy dữ liệu OSRM.")

if __name__ == "__main__":
    generate_16_points_oropt_map()