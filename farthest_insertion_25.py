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
        
    total_time = sum(matrix[tour[i]][tour[i+1]] for i in range(len(tour)-1))
    
    return tour, total_time

def run_farthest_insertion_25_points():
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
    url = f"http://router.project-osrm.org/table/v1/driving/{coord_joined}?annotations=duration"
    
    print("Đang lấy ma trận thời gian từ OSRM (25 điểm)...")
    response = requests.get(url)
    data = response.json()
    
    if data.get("code") == "Ok":
        matrix = data["durations"]
        tour, total_time = solve_tsp_farthest_insertion(matrix)
        
        tour_display = [str(node + 1) for node in tour]
        print("\n--- KẾT QUẢ THUẬT TOÁN CHÈN XA NHẤT (25 ĐIỂM) ---")
        print(f"Lộ trình: {' -> '.join(tour_display)}")
        print(f"Tổng thời gian: {round(total_time)} giây (~{round(total_time/60, 2)} phút)")
        
        ordered_coords_str = [coords_str[i] for i in tour]
        route_joined = ";".join(ordered_coords_str)
        route_url = f"http://router.project-osrm.org/route/v1/driving/{route_joined}?overview=full&geometries=geojson"
        
        print("\nĐang tải dữ liệu vẽ mạng lưới đường thực tế...")
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
            
            output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "caugiay_25_farthest_insertion_map.html")
            m.save(output_path)
            print(f"Thành công! Mở file '{output_path}' để xem bản đồ.")
        else:
            print("Lỗi lấy dữ liệu chỉ đường từ OSRM.")
    else:
        print("Lỗi lấy dữ liệu từ OSRM!")

if __name__ == "__main__":
    run_farthest_insertion_25_points()