# 🛒 Olist E-Commerce Analytics Dashboard

Dashboard analisis data interaktif berbasis Streamlit menggunakan **Brazilian E-Commerce Public Dataset (Olist)**.

## 📋 Deskripsi Proyek

Proyek ini merupakan proyek akhir dari kelas **Belajar Fundamental Analisis Data** di Dicoding. Analisis mencakup:

- **Segmentasi pelanggan** menggunakan RFM Analysis (Recency, Frequency, Monetary)
- **Analisis distribusi geografis** pesanan di seluruh wilayah Brasil
- **Clustering** pelanggan berdasarkan Spending Tier (Manual Binning)
- **Geospatial Analysis** dengan peta interaktif menggunakan Folium

## 📁 Struktur Direktori

```
submission/
├── dashboard/
│   ├── main_data.csv       ← Data utama hasil preprocessing
│   └── dashboard.py        ← Aplikasi Streamlit
├── data/
│   ├── olist_orders_dataset.csv
│   ├── olist_order_items_dataset.csv
│   ├── olist_customers_dataset.csv
│   ├── olist_order_payments_dataset.csv
│   ├── olist_order_reviews_dataset.csv
│   ├── olist_products_dataset.csv
│   ├── olist_sellers_dataset.csv
│   ├── olist_geolocation_dataset.csv
│   └── product_category_name_translation.csv
├── notebook.ipynb           ← Notebook analisis lengkap
├── README.md
├── requirements.txt
└── url.txt                  ← URL dashboard yang sudah di-deploy
```

## 🚀 Cara Menjalankan Dashboard

### 1. Clone / Download Proyek

```bash
git clone <repo-url>
cd submission
```

### 2. Install Dependencies

Disarankan menggunakan virtual environment:

```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

pip install -r requirements.txt
```

### 3. Siapkan Data

Pastikan folder `data/` berisi seluruh file CSV dataset Olist.

Kemudian jalankan notebook `notebook.ipynb` hingga selesai agar file `dashboard/main_data.csv` terbuat secara otomatis.

Atau tambahkan cell berikut di akhir notebook:

```python
cols = ['order_id','customer_unique_id','customer_state','customer_city',
        'customer_zip_code_prefix','order_purchase_timestamp',
        'order_status','total_payment','payment_type',
        'review_score','customer_lat','customer_lng',
        'order_year','order_month']

main_df[[c for c in cols if c in main_df.columns]].to_csv('dashboard/main_data.csv', index=False)
print("✅ main_data.csv tersimpan!")
```

### 4. Jalankan Dashboard

```bash
streamlit run dashboard/dashboard.py
```

Buka browser dan akses: **http://localhost:8501**

## 📊 Fitur Dashboard

| Fitur | Deskripsi |
|-------|-----------|
| 🔍 **Filter Interaktif** | Filter berdasarkan rentang tanggal dan negara bagian |
| 📈 **KPI Metrics** | Total orders, revenue, customers, AOV, review score |
| 📅 **Tren Waktu** | Grafik dual-axis volume & revenue bulanan |
| 🗺️ **Peta Interaktif** | HeatMap + CircleMarker distribusi pesanan |
| 👥 **RFM Segmentasi** | Bar chart, bubble chart, dan tabel segmen |
| 📦 **Analisis Produk** | Review score, spending tier, metode pembayaran |

## 🛠️ Library yang Digunakan

- `pandas` — manipulasi data
- `numpy` — komputasi numerik
- `matplotlib` & `seaborn` — visualisasi statis
- `folium` & `streamlit-folium` — peta interaktif
- `streamlit` — framework dashboard

## 👤 Author

- **Nama:** [Nama Anda]
- **Email:** [Email Anda]
- **ID Dicoding:** [Username Dicoding Anda]
