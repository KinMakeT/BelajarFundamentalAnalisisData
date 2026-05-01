import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import folium
from streamlit_folium import st_folium
import warnings
from pathlib import Path
warnings.filterwarnings('ignore')

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Prabha E-Commerce Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem 1.5rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .metric-card h2 { margin: 0; font-size: 1.8rem; }
    .metric-card p  { margin: 0; font-size: 0.85rem; opacity: 0.85; }
    .section-header {
        font-size: 1.3rem; font-weight: 700;
        border-left: 4px solid #667eea;
        padding-left: 10px; margin: 1rem 0 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ─── Load Data ───────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    base_dir = Path(__file__).resolve().parent
    csv_path = base_dir / 'main_data.csv'
    try:
        df = pd.read_csv(csv_path, parse_dates=['order_purchase_timestamp'])
    except FileNotFoundError:
        st.error(f"⚠️ File `main_data.csv` tidak ditemukan di `{csv_path}`. Pastikan Anda sudah menjalankan notebook terlebih dahulu dan menyimpan main_df ke CSV.")
        st.stop()
    return df

@st.cache_data
def compute_rfm(df):
    ref_date = df['order_purchase_timestamp'].max() + pd.Timedelta(days=1)
    rfm = df.groupby('customer_unique_id').agg(
        Recency   = ('order_purchase_timestamp', lambda x: (ref_date - x.max()).days),
        Frequency = ('order_id', 'count'),
        Monetary  = ('total_payment', 'sum')
    ).reset_index()
    rfm['R_Score'] = pd.qcut(rfm['Recency'],   q=5, labels=[5,4,3,2,1]).astype(int)
    rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), q=5, labels=[1,2,3,4,5]).astype(int)
    rfm['M_Score'] = pd.qcut(rfm['Monetary'],  q=5, labels=[1,2,3,4,5]).astype(int)
    rfm['RFM_Total'] = rfm[['R_Score','F_Score','M_Score']].sum(axis=1)

    def segment(row):
        r, f, m = row['R_Score'], row['F_Score'], row['M_Score']
        if r >= 4 and f >= 4 and m >= 4: return 'Champions'
        elif r >= 3 and f >= 3:           return 'Loyal Customers'
        elif r >= 4 and f <= 2:           return 'New Customers'
        elif r >= 3 and f <= 2 and m >= 3:return 'Potential Loyalists'
        elif r <= 2 and f >= 4:           return 'At Risk'
        elif r <= 2 and f <= 2 and m >= 3:return 'Cant Lose Them'
        elif r == 1 and f == 1:           return 'Lost'
        else:                             return 'Hibernating'

    rfm['Segment'] = rfm.apply(segment, axis=1)
    return rfm

main_df = load_data()

# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/f/f1/Olist_logo.png/320px-Olist_logo.png", width=150)
    st.markdown("## 🔍 Filter Data")

    min_date = main_df['order_purchase_timestamp'].min().date()
    max_date = main_df['order_purchase_timestamp'].max().date()

    start_date, end_date = st.date_input(
        "Rentang Tanggal",
        value=[min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )

    states = ['Semua'] + sorted(main_df['customer_state'].dropna().unique().tolist())
    selected_state = st.selectbox("Negara Bagian", states)

    st.markdown("---")
    st.markdown("**📊 Dataset:** Brazilian E-Commerce (Olist)")
    st.markdown("**📅 Periode:** Sep 2016 – Sep 2018")
    st.markdown("**👤 Dibuat oleh:** I Putu Prabha Nugraha ")

# ─── Filter Logic ────────────────────────────────────────────────────────────
mask = (
    (main_df['order_purchase_timestamp'].dt.date >= start_date) &
    (main_df['order_purchase_timestamp'].dt.date <= end_date)
)
if selected_state != 'Semua':
    mask &= (main_df['customer_state'] == selected_state)

filtered = main_df[mask].copy()

# ─── Header ──────────────────────────────────────────────────────────────────
st.title("🛒 Olist E-Commerce Analytics Dashboard")
st.markdown("**Analisis komprehensif transaksi e-commerce Brasil | Proyek Akhir Analisis Data**")
st.markdown("---")

# ─── KPI Metrics ─────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">📈 Key Performance Indicators</div>', unsafe_allow_html=True)

col1, col2, col3, col4, col5 = st.columns(5)
total_orders   = len(filtered)
total_revenue  = filtered['total_payment'].sum()
total_customers= filtered['customer_unique_id'].nunique()
avg_aov        = filtered['total_payment'].mean()
avg_score      = filtered['review_score'].mean() if 'review_score' in filtered.columns else 0

with col1:
    st.metric("📦 Total Orders",    f"{total_orders:,}")
with col2:
    st.metric("💰 Total Revenue",   f"R$ {total_revenue:,.0f}")
with col3:
    st.metric("👥 Unique Customers",f"{total_customers:,}")
with col4:
    st.metric("🛍️ Avg Order Value", f"R$ {avg_aov:.2f}")
with col5:
    st.metric("⭐ Avg Review Score",f"{avg_score:.2f}")

st.markdown("---")

# ─── Tab Layout ──────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📅 Tren Waktu",
    "🗺️ Geospatial",
    "👥 Segmentasi RFM",
    "📦 Produk & Kategori"
])

# ════════════════════════════════════════════════════════════
# TAB 1 — Tren Waktu
# ════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-header">📅 Tren Volume Pesanan & Revenue Bulanan</div>', unsafe_allow_html=True)

    monthly = filtered.copy()
    monthly['ym'] = monthly['order_purchase_timestamp'].dt.to_period('M').astype(str)
    monthly_agg = monthly.groupby('ym').agg(
        total_orders  = ('order_id', 'count'),
        total_revenue = ('total_payment', 'sum'),
        avg_aov       = ('total_payment', 'mean')
    ).reset_index()

    fig, ax1 = plt.subplots(figsize=(13, 5))
    ax2 = ax1.twinx()
    ax1.bar(monthly_agg['ym'], monthly_agg['total_orders'], color='#667eea', alpha=0.7, label='Jumlah Order')
    ax2.plot(monthly_agg['ym'], monthly_agg['total_revenue'], color='#e74c3c', lw=2.5, marker='o', ms=4, label='Revenue')
    ax1.set_xlabel('Bulan'); ax1.set_ylabel('Jumlah Order', color='#667eea')
    ax2.set_ylabel('Total Revenue (BRL)', color='#e74c3c')
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'R${x/1e6:.1f}M'))
    plt.xticks(rotation=45, ha='right', fontsize=8)
    ax1.set_title('Tren Bulanan: Volume Pesanan & Revenue', fontweight='bold', fontsize=13)
    lines1, lbl1 = ax1.get_legend_handles_labels()
    lines2, lbl2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, lbl1 + lbl2, loc='upper left')
    ax1.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig); plt.close()

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**📊 Statistik Bulanan**")
        st.dataframe(monthly_agg.describe().round(2), use_container_width=True)
    with col_b:
        st.markdown("**🔝 Top 5 Bulan Terbaik (Revenue)**")
        top5 = monthly_agg.nlargest(5, 'total_revenue')[['ym','total_orders','total_revenue','avg_aov']]
        top5.columns = ['Bulan','Orders','Revenue (BRL)','AOV (BRL)']
        top5['Revenue (BRL)'] = top5['Revenue (BRL)'].apply(lambda x: f'R${x:,.0f}')
        top5['AOV (BRL)']     = top5['AOV (BRL)'].apply(lambda x: f'R${x:.2f}')
        st.dataframe(top5, use_container_width=True, hide_index=True)

# ════════════════════════════════════════════════════════════
# TAB 2 — Geospatial
# ════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-header">🗺️ Distribusi Geografis Pesanan di Brasil</div>', unsafe_allow_html=True)

    col_l, col_r = st.columns([2, 1])

    with col_l:
        if 'customer_lat' in filtered.columns and filtered['customer_lat'].notna().sum() > 10:
            from folium.plugins import HeatMap
            m = folium.Map(location=[-15.0, -50.0], zoom_start=4, tiles='CartoDB positron')
            city_geo = filtered.dropna(subset=['customer_lat','customer_lng']).groupby(
                ['customer_city','customer_state']
            ).agg(
                orders  = ('order_id', 'count'),
                lat     = ('customer_lat', 'mean'),
                lng     = ('customer_lng', 'mean'),
                revenue = ('total_payment', 'sum')
            ).reset_index()

            heat_data = city_geo[['lat','lng','orders']].values.tolist()
            HeatMap(heat_data, radius=12, blur=10, min_opacity=0.4).add_to(m)

            for _, r in city_geo.nlargest(15, 'orders').iterrows():
                folium.CircleMarker(
                    location=[r['lat'], r['lng']],
                    radius=min(r['orders']/400, 18),
                    color='#e74c3c', fill=True, fill_opacity=0.75,
                    popup=folium.Popup(
                        f"<b>{r['customer_city'].title()}, {r['customer_state']}</b><br>"
                        f"Orders: {r['orders']:,}<br>Revenue: R${r['revenue']:,.0f}",
                        max_width=200
                    )
                ).add_to(m)

            st_folium(m, width=700, height=420)
        else:
            st.info("ℹ️ Data koordinat tidak tersedia. Pastikan kolom `customer_lat` dan `customer_lng` ada di main_data.csv")

    with col_r:
        st.markdown("**Top 10 Negara Bagian**")
        state_df = filtered.groupby('customer_state').agg(
            Orders  = ('order_id', 'count'),
            Revenue = ('total_payment', 'sum'),
            AOV     = ('total_payment', 'mean')
        ).sort_values('Orders', ascending=False).head(10).round(2)
        state_df['Revenue'] = state_df['Revenue'].apply(lambda x: f'R${x:,.0f}')
        state_df['AOV']     = state_df['AOV'].apply(lambda x: f'R${x:.2f}')
        st.dataframe(state_df, use_container_width=True)

        st.markdown("**Top 10 AOV Tertinggi**")
        aov_df = filtered.groupby('customer_state').agg(
            AOV    = ('total_payment', 'mean'),
            Orders = ('order_id', 'count')
        ).nlargest(10, 'AOV').round(2)
        aov_df['AOV'] = aov_df['AOV'].apply(lambda x: f'R${x:.2f}')
        st.dataframe(aov_df, use_container_width=True)

# ════════════════════════════════════════════════════════════
# TAB 3 — RFM Segmentasi
# ════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-header">👥 Segmentasi Pelanggan — Analisis RFM</div>', unsafe_allow_html=True)
    st.markdown("Analisis RFM mengelompokkan pelanggan berdasarkan **Recency** (seberapa baru), **Frequency** (seberapa sering), dan **Monetary** (seberapa besar pengeluaran).")

    rfm = compute_rfm(filtered)

    COLORS = {
        'Champions': '#2ecc71', 'Loyal Customers': '#27ae60',
        'New Customers': '#3498db', 'Potential Loyalists': '#9b59b6',
        'At Risk': '#e67e22', 'Cant Lose Them': '#e74c3c',
        'Lost': '#95a5a6', 'Hibernating': '#bdc3c7'
    }

    seg_count = rfm['Segment'].value_counts().reset_index()
    seg_count.columns = ['Segment', 'Count']
    seg_rev   = rfm.groupby('Segment')['Monetary'].sum().reset_index()
    seg_rev.columns = ['Segment', 'Revenue']

    col_r1, col_r2 = st.columns(2)

    with col_r1:
        fig, ax = plt.subplots(figsize=(7, 5))
        colors1 = [COLORS.get(s, '#aaa') for s in seg_count['Segment']]
        bars = ax.barh(seg_count['Segment'], seg_count['Count'], color=colors1, edgecolor='white')
        for bar, val in zip(bars, seg_count['Count']):
            ax.text(bar.get_width() + 50, bar.get_y() + bar.get_height()/2,
                    f'{val:,}', va='center', fontsize=8)
        ax.set_title('Jumlah Pelanggan per Segmen', fontweight='bold')
        ax.set_xlabel('Jumlah Pelanggan')
        ax.set_xlim(0, seg_count['Count'].max() * 1.2)
        ax.invert_yaxis(); ax.grid(axis='x', alpha=0.3)
        plt.tight_layout(); st.pyplot(fig); plt.close()

    with col_r2:
        fig, ax = plt.subplots(figsize=(7, 5))
        seg_rev_s = seg_rev.sort_values('Revenue', ascending=True)
        colors2 = [COLORS.get(s, '#aaa') for s in seg_rev_s['Segment']]
        bars = ax.barh(seg_rev_s['Segment'], seg_rev_s['Revenue'], color=colors2, edgecolor='white')
        for bar, val in zip(bars, seg_rev_s['Revenue']):
            ax.text(bar.get_width() * 1.01, bar.get_y() + bar.get_height()/2,
                    f'R${val/1e6:.2f}M', va='center', fontsize=8)
        ax.set_title('Total Revenue per Segmen', fontweight='bold')
        ax.set_xlabel('Total Revenue (BRL)')
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'R${x/1e6:.1f}M'))
        ax.set_xlim(0, seg_rev_s['Revenue'].max() * 1.25)
        ax.grid(axis='x', alpha=0.3)
        plt.tight_layout(); st.pyplot(fig); plt.close()

    # Bubble Chart
    st.markdown("**RFM Bubble Chart — Posisi Segmen**")
    rfm_agg = rfm.groupby('Segment').agg(
        avg_r = ('Recency','mean'), avg_f = ('Frequency','mean'),
        total_m = ('Monetary','sum'), count = ('customer_unique_id','count')
    ).reset_index()
    fig, ax = plt.subplots(figsize=(12, 5))
    scatter_colors = [COLORS.get(s, '#aaa') for s in rfm_agg['Segment']]
    ax.scatter(rfm_agg['avg_r'], rfm_agg['avg_f'],
               s=rfm_agg['total_m']/200, c=scatter_colors, alpha=0.8, edgecolors='white', lw=1.5)
    for _, row in rfm_agg.iterrows():
        ax.annotate(f"{row['Segment']}\n({row['count']:,})",
                    (row['avg_r'], row['avg_f']), xytext=(8,4),
                    textcoords='offset points', fontsize=8, fontweight='bold')
    ax.set_xlabel('Rata-rata Recency (hari) — semakin kiri semakin baru')
    ax.set_ylabel('Rata-rata Frequency (transaksi)')
    ax.set_title('RFM Bubble Chart (Ukuran = Total Revenue)', fontweight='bold')
    ax.invert_xaxis(); ax.grid(alpha=0.3)
    plt.tight_layout(); st.pyplot(fig); plt.close()

    # Tabel Ringkasan
    st.markdown("**📋 Ringkasan Statistik per Segmen**")
    seg_table = rfm.groupby('Segment').agg(
        Pelanggan      = ('customer_unique_id', 'count'),
        Avg_Recency    = ('Recency', 'mean'),
        Avg_Frequency  = ('Frequency', 'mean'),
        Total_Revenue  = ('Monetary', 'sum'),
        Avg_Revenue    = ('Monetary', 'mean')
    ).round(2).sort_values('Pelanggan', ascending=False)
    seg_table['Total_Revenue'] = seg_table['Total_Revenue'].apply(lambda x: f'R${x:,.0f}')
    seg_table['Avg_Revenue']   = seg_table['Avg_Revenue'].apply(lambda x: f'R${x:.2f}')
    st.dataframe(seg_table, use_container_width=True)

# ════════════════════════════════════════════════════════════
# TAB 4 — Produk & Kategori
# ════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-header">📦 Analisis Produk & Spending Tier</div>', unsafe_allow_html=True)

    col_p1, col_p2 = st.columns(2)

    with col_p1:
        # Review Score Distribution
        st.markdown("**⭐ Distribusi Review Score**")
        if 'review_score' in filtered.columns:
            review_counts = filtered['review_score'].value_counts().sort_index()
            fig, ax = plt.subplots(figsize=(6, 4))
            colors_rev = ['#e74c3c','#e67e22','#f1c40f','#2ecc71','#27ae60']
            bars = ax.bar(review_counts.index, review_counts.values, color=colors_rev, edgecolor='white')
            for bar, val in zip(bars, review_counts.values):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50,
                        f'{val:,}', ha='center', fontsize=9, fontweight='bold')
            ax.set_xlabel('Review Score'); ax.set_ylabel('Jumlah')
            ax.set_title('Distribusi Review Score', fontweight='bold')
            ax.grid(axis='y', alpha=0.3)
            plt.tight_layout(); st.pyplot(fig); plt.close()

    with col_p2:
        # Spending Tier
        st.markdown("**💎 Clustering Spending Tier**")
        customer_spending = filtered.groupby('customer_unique_id').agg(
            total_spend = ('total_payment', 'sum')
        ).reset_index()
        bins   = [0, 100, 300, 700, 1500, float('inf')]
        labels = ['Bronze\n<R$100', 'Silver\nR$100-300', 'Gold\nR$300-700',
                  'Platinum\nR$700-1.5K', 'Diamond\n>R$1.5K']
        customer_spending['Tier'] = pd.cut(customer_spending['total_spend'], bins=bins, labels=labels)
        tier_cnt = customer_spending['Tier'].value_counts().sort_index()
        fig, ax = plt.subplots(figsize=(6, 4))
        tier_colors = ['#cd7f32','#c0c0c0','#ffd700','#e5e4e2','#b9f2ff']
        bars = ax.bar(tier_cnt.index, tier_cnt.values, color=tier_colors, edgecolor='white')
        for bar, val in zip(bars, tier_cnt.values):
            pct = val / tier_cnt.sum() * 100
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 20,
                    f'{val:,}\n({pct:.1f}%)', ha='center', fontsize=8)
        ax.set_xlabel('Spending Tier'); ax.set_ylabel('Jumlah Pelanggan')
        ax.set_title('Distribusi Pelanggan per Spending Tier', fontweight='bold')
        ax.grid(axis='y', alpha=0.3)
        plt.tight_layout(); st.pyplot(fig); plt.close()

    # Payment Type
    st.markdown("**💳 Metode Pembayaran**")
    if 'payment_type' in filtered.columns:
        pay_cnt = filtered['payment_type'].value_counts()
        fig, axes = plt.subplots(1, 2, figsize=(12, 4))
        axes[0].pie(pay_cnt.values, labels=pay_cnt.index, autopct='%1.1f%%',
                    startangle=90, colors=sns.color_palette('Set2', len(pay_cnt)))
        axes[0].set_title('Proporsi Metode Pembayaran', fontweight='bold')

        pay_rev = filtered.groupby('payment_type')['total_payment'].mean().sort_values(ascending=False)
        axes[1].bar(pay_rev.index, pay_rev.values,
                    color=sns.color_palette('Set2', len(pay_rev)), edgecolor='white')
        for i, val in enumerate(pay_rev.values):
            axes[1].text(i, val + 1, f'R${val:.0f}', ha='center', fontsize=9)
        axes[1].set_title('Rata-rata Nilai per Metode Pembayaran', fontweight='bold')
        axes[1].set_xlabel('Metode Pembayaran')
        axes[1].set_ylabel('Rata-rata (BRL)')
        axes[1].grid(axis='y', alpha=0.3)
        plt.tight_layout(); st.pyplot(fig); plt.close()

# ─── Footer ──────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#888; font-size:0.85rem;'>"
    "🛒 Prabha E-Commerce Analytics Dashboard"
    "</div>",
    unsafe_allow_html=True
)
