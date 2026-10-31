import plotly.graph_objects as go
import os
import webbrowser

# 1. Dữ liệu tổng hợp từ kết quả thực nghiệm (N=128 và N=256)
datasets = [
    'Uniform 128', 'Uniform 256', 
    'Clustered 128', 'Clustered 256', 
    'DepotCentric 128', 'DepotCentric 256'
]

# Dữ liệu Tổng chi phí (Total Cost)
nn_cost = [10286.9, 15029.3, 5288.1, 9369.1, 8548.2, 11062.0]
fi_cost = [9133.4, 13294.3, 4694.7, 8542.4, 7382.7, 10155.8]
cw_cost = [8862.7, 13209.5, 4741.0, 8693.6, 7328.6, 9841.0]

# Dữ liệu Độ lệch phần trăm (% Gap)
nn_gap = [16.07, 13.78, 12.64, 9.68, 16.64, 12.41]
fi_gap = [3.05, 0.64, 0.00, 0.00, 0.74, 3.20]
cw_gap = [0.00, 0.00, 0.99, 1.77, 0.00, 0.00]

# Thư mục xuất file
output_dir = r"C:\test-prj\TSP_update\MPTN"
os.makedirs(output_dir, exist_ok=True)

# Cấu hình viền chung
axis_styling = dict(showline=True, linewidth=1.5, linecolor='black', gridcolor='whitesmoke')


# =====================================================================
# BIỂU ĐỒ 1: TỔNG CHI PHÍ (COST)
# =====================================================================
fig_cost = go.Figure()

fig_cost.add_trace(go.Bar(
    x=datasets, y=nn_cost, name='Tham lam (NN)',
    marker_color='royalblue', text=[f"{val:,.0f}" for val in nn_cost], textposition='auto'
))
fig_cost.add_trace(go.Bar(
    x=datasets, y=fi_cost, name='Chèn xa nhất (FI)',
    marker_color='indianred', text=[f"{val:,.0f}" for val in fi_cost], textposition='auto'
))
fig_cost.add_trace(go.Bar(
    x=datasets, y=cw_cost, name='Clarke-Wright (CW)',
    marker_color='mediumseagreen', text=[f"{val:,.0f}" for val in cw_cost], textposition='auto'
))

fig_cost.update_layout(
    title_text="So sánh Tổng chi phí Lộ trình (Cost)",
    title_x=0.5, plot_bgcolor='white', barmode='group',
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
    width=900, height=600
)
fig_cost.update_xaxes(**axis_styling)
fig_cost.update_yaxes(title_text="Tổng quãng đường (Cost)", **axis_styling)

cost_filename = os.path.join(output_dir, "bieu_do_1_tong_chi_phi.html")
fig_cost.write_html(cost_filename)


# =====================================================================
# BIỂU ĐỒ 2: ĐỘ LỆCH PHẦN TRĂM (% GAP)
# =====================================================================
fig_gap = go.Figure()

fig_gap.add_trace(go.Bar(
    x=datasets, y=nn_gap, name='Tham lam (NN)',
    marker_color='royalblue', text=[f"{val}%" for val in nn_gap], textposition='auto'
))
fig_gap.add_trace(go.Bar(
    x=datasets, y=fi_gap, name='Chèn xa nhất (FI)',
    marker_color='indianred', text=[f"{val}%" if val > 0 else "Best" for val in fi_gap], textposition='auto'
))
fig_gap.add_trace(go.Bar(
    x=datasets, y=cw_gap, name='Clarke-Wright (CW)',
    marker_color='mediumseagreen', text=[f"{val}%" if val > 0 else "Best" for val in cw_gap], textposition='auto'
))

fig_gap.update_layout(
    title_text="Đánh giá Độ lệch phần trăm (% Gap) so với nghiệm tốt nhất",
    title_x=0.5, plot_bgcolor='white', barmode='group',
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
    width=900, height=600
)
fig_gap.update_xaxes(**axis_styling)
fig_gap.update_yaxes(title_text="Độ lệch % (Gap)", **axis_styling)

gap_filename = os.path.join(output_dir, "bieu_do_2_do_lech_gap.html")
fig_gap.write_html(gap_filename)


# =====================================================================
# TỰ ĐỘNG MỞ 2 BIỂU ĐỒ
# =====================================================================
print(f"Đã xuất biểu đồ Cost tại: {cost_filename}")
print(f"Đã xuất biểu đồ Gap tại: {gap_filename}")

webbrowser.open('file://' + os.path.realpath(cost_filename))
webbrowser.open('file://' + os.path.realpath(gap_filename))