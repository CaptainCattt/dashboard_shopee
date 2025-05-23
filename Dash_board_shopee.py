import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import io

st.set_page_config(page_title="Shopee Dashboard", layout="wide", page_icon="📊")

# ===== CSS tuỳ chỉnh =====
st.markdown(
    """
    <style>
        /* Tổng thể */
        html, body, [class*="css"] {
            font-family: 'Segoe UI', sans-serif;
        }
        h1, h3, h4 {
            color: #333333;
        }
        .centered {
            text-align: center;
        }
        .upload-box {
            border: 2px dashed #cccccc;
            padding: 20px;
            border-radius: 10px;
            background-color: #f9f9f9;
        }
    </style>
""",
    unsafe_allow_html=True,
)

# ===== HEADER =====
col_logo, col_title, col_empty = st.columns([1, 4, 1])
with col_logo:
    st.image(
        "https://raw.githubusercontent.com/CaptainCattt/Report_of_shopee/main/logo-lamvlog.png",
        width=120,
    )
with col_title:
    st.markdown(
        """
        <div style='display: flex; justify-content: center; align-items: center; gap: 10px;'>
            <img src='https://img.icons8.com/color/48/shopee.png' width='40'/>
            <h1 style='margin: 0;color: #f1582e'>DASHBOARD BÁO CÁO SHOPEE</h1>
        </div>
    """,
        unsafe_allow_html=True,
    )

st.markdown(
    "<hr style='margin-top: 10px; margin-bottom: 30px;'>", unsafe_allow_html=True
)

# ===== UPLOAD FILE =====
st.markdown("### 📤 Tải lên dữ liệu", unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    st.markdown(
        "<div class='upload-box'><h4 class='centered'>📁 File tất cả đơn hàng Shopee</h4>",
        unsafe_allow_html=True,
    )
    file_all = st.file_uploader("Chọn file Excel", type=["xlsx", "xls"], key="file_all")
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown(
        "<div class='upload-box'><h4 class='centered'>💰 File doanh thu Shopee</h4>",
        unsafe_allow_html=True,
    )
    file_income = st.file_uploader(
        "Chọn file Excel", type=["xlsx", "xls"], key="file_income"
    )
    st.markdown("</div>", unsafe_allow_html=True)

# ===== LỌC THEO NGÀY =====
st.markdown(
    """
    <br>
    <h4>📅 Chọn khoảng ngày cần phân tích <span style='font-weight: normal;'>(tuỳ chọn)</span></h4>
""",
    unsafe_allow_html=True,
)

col3, col4 = st.columns(2)
with col3:
    ngay_bat_dau = st.date_input("🔰 Ngày bắt đầu", value=datetime.now().date())
with col4:
    ngay_ket_thuc = st.date_input("🏁 Ngày kết thúc", value=datetime.now().date())

ngay_bat_dau = pd.to_datetime(ngay_bat_dau)
ngay_ket_thuc = pd.to_datetime(ngay_ket_thuc)


def read_file_shopee(df_all, df_income, ngay_bat_dau, ngay_ket_thuc):
    df_income.columns = df_income.columns.str.strip()
    df_all.columns = df_all.columns.str.strip()
    df_all["Actually type"] = df_all["Trạng Thái Đơn Hàng"]
    df_all["Actually type"] = df_all["Actually type"].apply(
        lambda x: (
            "Đơn hàng đã đến User"
            if isinstance(x, str) and "Người mua xác nhận đã nhận được hàng" in x
            else x
        )
    )
    df_all["SKU Category"] = df_all["SKU phân loại hàng"].copy()

    # Danh sách các mẫu thay thế
    replacements = {
        r"^(COMBO-SC-ANHDUC|COMBO-SC-NGOCTRINH|COMBO-SC-MIX|SC_COMBO_MIX|SC_COMBO_MIX_LIVESTREAM|COMBO-SC_LIVESTREAM)": "COMBO-SC",
        r"^(SC_X1)": "SC-450g",
        r"^(SC_X2)": "SC-x2-450g",
        r"^(SC_COMBO_X1|COMBO-CAYVUA-X1|SC_COMBO_X1_LIVESTREAM|COMBO-SCX1_LIVESTREAM)": "COMBO-SCX1",
        r"^(SC_COMBO_X2|COMBO-SIEUCAY-X2|SC_COMBO_X2_LIVESTREAM|COMBO-SCX2_LIVESTREAM)": "COMBO-SCX2",
        r"^(BTHP-Cay-200gr|BTHP_Cay)": "BTHP-CAY",
        r"^(BTHP-200gr|BTHP_KhongCay)": "BTHP-0CAY",
        r"^(BTHP_COMBO_MIX|BTHP003_combo_mix)": "BTHP-COMBO",
        r"^(BTHP_COMBO_KhongCay|BTHP003_combo_kocay)": "BTHP-COMBO-0CAY",
        r"^(BTHP_COMBO_Cay|BTHP003_combo_cay)": "BTHP-COMBO-CAY",
        r"^BTHP-COMBO\+SC_X1$": "COMBO_BTHP_SCx1",
        r"^BTHP-COMBO\+SC_X2$": "COMBO_BTHP_SCx2",
        r"^BTHP_COMBO_MIX\+SC_X1$": "COMBO_BTHP_SCx1",
        r"^BTHP_COMBO_MIX\+SC_X2$": "COMBO_BTHP_SCx2",
        r"^(BTHP-2Cay-2KhongCay)$": "COMBO_4BTHP",
        r"^(BTHP-4Hu-KhongCay)$": "4BTHP_0CAY",
        r"^(BTHP-4Hu-Cay)$": "4BTHP_CAY",
    }

    for pattern, replacement in replacements.items():
        df_all["SKU Category"] = df_all["SKU Category"].str.replace(
            pattern, replacement, regex=True
        )
    date_columns_shopee = [
        "Ngày đặt hàng",
        "Ngày giao hàng dự kiến",
        "Ngày gửi hàng",
        "Thời gian giao hàng",
    ]

    # Ép kiểu về datetime với định dạng đúng
    df_all[date_columns_shopee] = df_all[date_columns_shopee].apply(
        lambda col: pd.to_datetime(col, errors="coerce", format="%Y-%m-%d %H:%M")
    )

    # Loại bỏ giờ, giữ lại phần ngày
    for col in date_columns_shopee:
        df_all[col] = df_all[col].dt.normalize()

    # Kiểm tra xem cột còn tồn tại không

    df_merged = pd.merge(
        df_income,
        df_all,
        how="left",
        right_on="Mã đơn hàng",
        left_on="Mã đơn hàng",
    )

    df_merged["Ngày hoàn thành thanh toán"] = pd.to_datetime(
        df_merged["Ngày hoàn thành thanh toán"], errors="coerce"
    )

    df_main = df_merged[
        (df_merged["Ngày hoàn thành thanh toán"] >= ngay_bat_dau)
        & (df_merged["Ngày hoàn thành thanh toán"] <= ngay_ket_thuc)
    ]

    Don_hoan_thanh = df_main[df_main["Tổng tiền đã thanh toán"] > 0]

    Don_hoan_tra = df_main[
        (df_main["Trạng thái Trả hàng/Hoàn tiền"] == "Đã Chấp Thuận Yêu Cầu")
        | (df_main["Số lượng sản phẩm được hoàn trả"] != 0)
    ]

    Don_huy = df_all[
        (df_all["Trạng Thái Đơn Hàng"] == "Đã hủy")
        & (df_all["Ngày đặt hàng"] >= ngay_bat_dau)
        & (df_all["Ngày đặt hàng"] <= ngay_ket_thuc)
    ]

    return df_main, Don_hoan_thanh, Don_hoan_tra, Don_huy


if "processing" not in st.session_state:
    st.session_state.processing = False

# Nút xử lý
# Nút Xử lý dữ liệu
with st.container():
    st.markdown('<div class="center-button">', unsafe_allow_html=True)
    process_btn = st.button(
        "🔍 Xử lý dữ liệu",
        key="process_data",
        disabled=st.session_state.processing,
        use_container_width=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

if st.button("🔁 Reset", use_container_width=True):
    st.session_state.clear()
    st.rerun()

if process_btn:
    if file_all and file_income:
        with st.spinner("⏳ Đang xử lý dữ liệu, vui lòng chờ..."):
            # Đọc file
            df_all = pd.read_excel(
                file_all,
                dtype={"Mã đơn hàng": str, "Mã Kiện Hàng": str, "Mã vận đơn": str},
            )
            df_income = pd.read_excel(
                file_income,
                sheet_name="Income",  # tên sheet
                dtype={
                    "Mã đơn hàng": str,
                    "Mã Số Thuế": str,
                    "Mã yêu cầu hoàn tiền": str,
                },
            )

            # Gọi hàm xử lý chính
            df_main, Don_hoan_thanh, Don_hoan_tra, Don_huy = read_file_shopee(
                df_all, df_income, ngay_bat_dau, ngay_ket_thuc
            )
            st.session_state.update(
                {
                    "df_main": df_main,
                    "Don_hoan_thanh": Don_hoan_thanh,
                    "Don_hoan_tra": Don_hoan_tra,
                    "Don_huy": Don_huy,
                    "df_all": df_all,
                    "df_income": df_income,
                }
            )

            st.session_state.processing = True

import plotly.express as px
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns


if st.session_state.processing:
    st.markdown("## 🛒 BIỂU ĐỒ SHOPEE")

    df_shopee_main = st.session_state.get("df_main").copy()

    Don_ht = st.session_state.get("Don_hoan_thanh")
    Don_hoantra = st.session_state.get("Don_hoan_tra")
    Don_huy = st.session_state.get("Don_huy")
    df_all = st.session_state.get("df_all")
    df_income = st.session_state.get("df_income")

    Don_quyettoan = df_shopee_main.drop_duplicates(subset="Mã đơn hàng").copy()

    # Biểu đồ 1: Số lượng đơn hàng theo loại
    df_counts = pd.DataFrame(
        {
            "Loại đơn": ["Hoàn thành", "Hoàn trả", "Hủy"],
            "Số lượng": [
                Don_ht["Mã đơn hàng"].nunique(),
                Don_hoantra["Mã đơn hàng"].nunique(),
                Don_huy["Mã đơn hàng"].nunique(),
            ],
        }
    )
    fig1 = px.bar(
        df_counts,
        x="Loại đơn",
        y="Số lượng",
        color="Loại đơn",
        title="📦 Số lượng đơn theo loại (Shopee)",
    )
    st.plotly_chart(fig1, use_container_width=True)

    # Tổng doanh thu
    total_revenue = Don_quyettoan["Tổng tiền đã thanh toán"].sum()
    st.metric("💰 Tổng doanh thu", f"{total_revenue:,.0f} ₫")

    # Doanh thu theo ngày
    if "Ngày hoàn thành thanh toán" in Don_quyettoan.columns:
        Don_quyettoan = Don_quyettoan.copy()
        Don_quyettoan.loc[:, "Ngày hoàn thành thanh toán"] = pd.to_datetime(
            Don_quyettoan["Ngày hoàn thành thanh toán"]
        )
        Don_quyettoan.loc[:, "Ngày"] = Don_quyettoan[
            "Ngày hoàn thành thanh toán"
        ].dt.date

        df_rev_by_day = (
            Don_quyettoan.groupby("Ngày")["Tổng tiền đã thanh toán"].sum().reset_index()
        )
        fig2 = px.line(
            df_rev_by_day,
            x="Ngày",
            y="Tổng tiền đã thanh toán",
            title="📈 Doanh thu theo ngày",
            markers=True,
        )
        st.plotly_chart(fig2, use_container_width=True)

        df_count_by_day = (
            Don_quyettoan.groupby("Ngày")["Mã đơn hàng"].nunique().reset_index()
        )
        fig3 = px.bar(
            df_count_by_day, x="Ngày", y="Mã đơn hàng", title="📦 Số đơn theo ngày"
        )
        st.plotly_chart(fig3, use_container_width=True)

    # Doanh thu theo SKU
    if "SKU Category" in df_shopee_main.columns:
        df_sku = (
            df_shopee_main.groupby("SKU Category")["Tổng tiền đã thanh toán"]
            .sum()
            .reset_index()
        )
        fig4 = px.bar(
            df_sku,
            x="SKU Category",
            y="Tổng tiền đã thanh toán",
            title="🧺 Doanh thu theo SKU",
            color="Tổng tiền đã thanh toán",
        )
        st.plotly_chart(fig4, use_container_width=True)

    # Số lượng theo SKU
    if df_shopee_main is not None and not df_shopee_main.empty:
        fig5 = px.histogram(
            df_shopee_main,
            x="SKU Category",
            y="Số lượng",
            color="SKU Category",
            title="📊 Số lượng theo SKU",
        )
        st.plotly_chart(fig5, use_container_width=True)

    # Doanh thu theo tỉnh
    if "Tỉnh/Thành phố" in Don_quyettoan.columns:
        df_prov = (
            Don_quyettoan.groupby("Tỉnh/Thành phố")["Tổng tiền đã thanh toán"]
            .sum()
            .reset_index()
        )
        fig6 = px.bar(
            df_prov,
            x="Tỉnh/Thành phố",
            y="Tổng tiền đã thanh toán",
            title="📍 Doanh thu theo tỉnh",
            color="Tổng tiền đã thanh toán",
        )
        st.plotly_chart(fig6, use_container_width=True)

    # Top người mua
    if Don_ht is not None and not Don_ht.empty and "Người Mua_y" in Don_ht.columns:
        df_ht = Don_ht.copy()
        buyers = (
            df_ht.groupby("Người Mua_y")
            .agg(So_don=("Mã đơn hàng", "nunique"), Tong_sl=("Số lượng", "sum"))
            .reset_index()
        )

        col4, col5 = st.columns(2)

        with col4:
            top_don = buyers.sort_values("So_don", ascending=False).head(20)
            fig7 = px.bar(
                top_don,
                x="Người Mua_y",
                y="So_don",
                title="🏆 Top người mua theo số đơn",
                color_discrete_sequence=["#1f77b4"],
            )
            fig7.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig7, use_container_width=True)

        with col5:
            top_sl = buyers.sort_values("Tong_sl", ascending=False).head(20)
            fig8 = px.bar(
                top_sl,
                x="Người Mua_y",
                y="Tong_sl",
                title="🎁 Top người mua theo số lượng sản phẩm",
                color_discrete_sequence=["#FF7F0E"],
            )
            fig8.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig8, use_container_width=True)

    # Biểu đồ tròn phương thức thanh toán
    if "Phương thức thanh toán" in Don_quyettoan.columns:
        df_pie = Don_quyettoan["Phương thức thanh toán"].value_counts().reset_index()
        df_pie.columns = ["Phương thức", "Số lượng"]
        fig_pie = px.pie(
            df_pie,
            names="Phương thức",
            values="Số lượng",
            title="💳 Phương thức thanh toán",
        )
        st.plotly_chart(fig_pie, use_container_width=True)
