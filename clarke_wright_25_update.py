import requests
import folium
import os

def solve_tsp_clarke_wright(matrix):
    num_nodes = len(matrix)
    savings = []
    for i in range(1, num_nodes):
        for j in range(1, num_nodes):
            if i != j:
                savings.append((matrix[i][0] + matrix[0][j] - matrix[i][j], i, j))
                
    savings.sort(key=lambda x: x[0], reverse=True)
    
    parent = {i: i for i in range(1, num_nodes)}
    def find(i):
        if parent[i] == i: return i
        parent[i] = find(parent[i])
        return parent[i]
        
    def union(i, j):
        root_i = find(i)
        root_j = find(j)
        if root_i != root_j:
            parent[root_i] = root_j
            return True
        return False

    adj = {i: [] for i in range(1, num_nodes)}
    edges = 0
    for s, i, j in savings:
        if len(adj[i]) < 2 and len(adj[j]) < 2 and find(i) != find(j):
            adj[i].append(j)
            adj[j].append(i)
            union(i, j)
            edges += 1
            if edges == num_nodes - 2: break
                    
    endpoints = [i for i in range(1, num_nodes) if len(adj[i]) == 1]
    curr, prev = endpoints[0], 0
    tour = [0, curr]
    
    while len(tour) < num_nodes:
        neighbors = adj[curr]
        next_node = neighbors[0] if neighbors[0] != prev else neighbors[1]
        tour.append(next_node)
        prev, curr = curr, next_node
    tour.append(0)
    
    c_fwd = sum(matrix[tour[i]][tour[i+1]] for i in range(num_nodes))
    t_rev = tour[::-1]
    c_rev = sum(matrix[t_rev[i]][t_rev[i+1]] for i in range(num_nodes))
    
    return t_rev if c_rev < c_fwd else tour

def optimize_vnd(tour, matrix):
    base_tour = tour[:-1]
    n = len(base_tour)
    
    def get_cost(t):
        return sum(matrix[t[idx]][t[idx+1]] for idx in range(n - 1)) + matrix[t[-1]][t[0]]
        
    best_tour = base_tour[:]
    best_cost = get_cost(best_tour)
    
    k = 0
    while k < 3:
        improved = False
        
        if k == 0:
            for i in range(1, n - 1):
                for j in range(i + 1, n):
                    new_t = best_tour[:i] + best_tour[i:j+1][::-1] + best_tour[j+1:]
                    new_c = get_cost(new_t)
                    if new_c < best_cost:
                        best_tour, best_cost, improved = new_t, new_c, True
                        break
                if improved: break
                
        elif k == 1:
            for length in [3, 2, 1]:
                if improved: break
                for i in range(1, n - length + 1):
                    if improved: break
                    segment = best_tour[i:i+length]
                    rest = best_tour[:i] + best_tour[i+length:]
                    for j in range(1, len(rest) + 1):
                        if j == i: continue
                        new_t = rest[:j] + segment + rest[j:]
                        new_c = get_cost(new_t)
                        if new_c < best_cost:
                            best_tour, best_cost, improved = new_t, new_c, True
                            break
                            
        elif k == 2:
            for i in range(1, n - 1):
                for j in range(i + 1, n):
                    new_t = best_tour[:]
                    new_t[i], new_t[j] = new_t[j], new_t[i]
                    new_c = get_cost(new_t)
                    if new_c < best_cost:
                        best_tour, best_cost, improved = new_t, new_c, True
                        break
                if improved: break
        
        if improved: k = 0
        else: k += 1
            
    return best_tour + [best_tour[0]], best_cost

def run_cw_vnd_25_points():
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
    response = requests.get(url).json()
    if response.get("code") == "Ok":
        matrix = response["durations"]
        
        initial_tour = solve_tsp_clarke_wright(matrix)
        initial_cost = sum(matrix[initial_tour[i]][initial_tour[i+1]] for i in range(len(initial_tour)-1))
        
        print("\n[1] TRƯỚC CẢI TIẾN (CLARKE-WRIGHT)")
        print(f"Lộ trình: {' -> '.join(str(n + 1) for n in initial_tour)}")
        print(f"Tổng thời gian: {round(initial_cost)} giây")

        final_tour, final_cost = optimize_vnd(initial_tour, matrix)
        print("\n[2] SAU CẢI TIẾN (VND: 2-opt -> Or-opt -> Swap)")
        print(f"Lộ trình: {' -> '.join(str(n + 1) for n in final_tour)}")
        print(f"Tổng thời gian: {round(final_cost)} giây")
        print(f"-> Tiết kiệm: {round(initial_cost - final_cost)} giây\n")

        ordered_coords = [coords_str[i] for i in final_tour]
        route_url = f"http://router.project-osrm.org/route/v1/driving/{';'.join(ordered_coords)}?overview=full&geometries=geojson"
        
        print("Đang tải dữ liệu vẽ mạng lưới đường thực tế...")
        r_resp = requests.get(route_url).json()
        if r_resp.get("code") == "Ok":
            geometry = r_resp["routes"][0]["geometry"]["coordinates"]
            detailed_path = [[lat, lon] for lon, lat in geometry]
            
            m = folium.Map(location=[21.0300, 105.7900], zoom_start=14, tiles='https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}', attr='Google Maps')
            
            coords_latlon = [[float(c.split(',')[1]), float(c.split(',')[0])] for c in coords_str]
            for i, (lat, lon) in enumerate(coords_latlon):
                bg_color = '#e74c3c' if i == 0 else '#3498db'
                font_size = '11px'
                icon_html = f'<div style="background-color: {bg_color}; color: white; border-radius: 50%; width: 24px; height: 24px; display: flex; justify-content: center; align-items: center; font-weight: bold; font-family: Arial, sans-serif; font-size: {font_size}; border: 2px solid white; box-shadow: 1px 1px 3px rgba(0,0,0,0.5);">{i+1}</div>'
                folium.Marker([lat, lon], popup=f"Tọa độ: {lat}, {lon}", tooltip=f"Điểm {i+1}", icon=folium.DivIcon(html=icon_html, icon_size=(24, 24), icon_anchor=(12, 12))).add_to(m)
                
            folium.PolyLine(detailed_path, weight=5, color='#800080', opacity=0.8).add_to(m)
            
            output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "caugiay_25_cw_vnd_map.html")
            m.save(output_path)
            print(f"Thành công! Mở file '{output_path}'.")

if __name__ == "__main__":
    run_cw_vnd_25_points()