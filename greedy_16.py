import requests
import folium
import os

def solve_tsp_greedy(matrix, start_node=0):
    num_nodes = len(matrix)
    visited = [False] * num_nodes
    tour = [start_node]
    visited[start_node] = True
    total_time = 0
    
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
        total_time += min_time
        current_node = next_node
        
    tour.append(start_node)
    total_time += matrix[current_node][start_node]
    return tour, total_time

def run_greedy_16_points():
    coords_str = [
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

    coord_joined = ";".join(coords_str)
    url = f"http://router.project-osrm.org/table/v1/driving/{coord_joined}?annotations=duration"
    
    print("Đang lấy ma trận thời gian từ OSRM (16 điểm)...")
    response = requests.get(url)
    data = response.json()
    
    if data.get("code") == "Ok":
        matrix = data["durations"]
        tour, total_time = solve_tsp_greedy(matrix, start_node=0)
        
        tour_display = [str(node + 1) for node in tour]
        print("\n--- KẾT QUẢ THUẬT TOÁN THAM LAM (16 ĐIỂM) ---")
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
            
            output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "caugiay_16_greedy_pure_map.html")
            m.save(output_path)
            print(f"Thành công! Mở file '{output_path}' để xem bản đồ.")
        else:
            print("Lỗi lấy dữ liệu chỉ đường từ OSRM.")
    else:
        print("Lỗi lấy dữ liệu từ OSRM!")

if __name__ == "__main__":
    run_greedy_16_points()