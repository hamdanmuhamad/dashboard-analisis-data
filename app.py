import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Konfigurasi Halaman Dashboard
st.set_page_config(page_title="Dashboard Analisis Data Otomatis", layout="wide")

st.title("📊 Dashboard Analisis Data & Visualisasi")
st.write("Unggah file CSV atau Excel Anda untuk melihat ringkasan data dan grafik interaktif secara instan!")

# 2. Fitur Unggah File (Uploader)
uploaded_file = st.file_uploader("Pilih file data (Format: .csv, .xlsx)", type=["csv", "xlsx"])

if uploaded_file is not None:
    # Membaca file berdasarkan formatnya
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.success("File berhasil diunggah!")
        
        # =========================================================
        # sideBAR & FILTER DINAMIS
        # =========================================================
        st.sidebar.header("🔍 Filter Data")
        
        # Filter 1: Wilayah
        if 'Wilayah' in df.columns:
            opsi_wilayah = ["Semua Wilayah"] + df['Wilayah'].unique().tolist()
            wilayah_terpilih = st.sidebar.selectbox("Pilih Wilayah:", opsi_wilayah)
            if wilayah_terpilih != "Semua Wilayah":
                df = df[df['Wilayah'] == wilayah_terpilih]
                
        # Filter 2: Kategori
        if 'Kategori' in df.columns:
            opsi_kategori = ["Semua Kategori"] + df['Kategori'].unique().tolist()
            kategori_terpilih = st.sidebar.selectbox("Pilih Kategori Produk:", opsi_kategori)
            if kategori_terpilih != "Semua Kategori":
                df = df[df['Kategori'] == kategori_terpilih]
        # =========================================================
        
        # 🔥 FITUR BARU: KARTU INFORMASI UTAMA (KPI CARDS)
        # =========================================================
        st.subheader("💰 Ringkasan Finansial & Operasional")
        kpi1, kpi2, kpi3 = st.columns(3)
        
        # Hitung total penjualan jika kolomnya ada di data sampel
        if 'Total_Penjualan' in df.columns:
            total_omset = df['Total_Penjualan'].sum()
            # Format ke mata uang Rupiah yang rapi
            kpi1.metric("Total Pendapatan (Omset)", f"Rp {total_omset:,.0f}".replace(",", "."))
        else:
            kpi1.metric("Total Pendapatan", "Kolom tidak ditemukan")
            
        # Hitung total unit barang yang terjual
        if 'Jumlah_Terjual' in df.columns:
            total_barang = df['Jumlah_Terjual'].sum()
            kpi2.metric("Total Produk Terjual", f"{total_barang:,} Unit".replace(",", "."))
        else:
            kpi2.metric("Total Produk Terjual", "Kolom tidak ditemukan")
            
        # Hitung rata-rata nilai transaksi
        if 'Total_Penjualan' in df.columns:
            rata_rata_transaksi = df['Total_Penjualan'].mean()
            kpi3.metric("Rata-rata Per Transaksi", f"Rp {rata_rata_transaksi:,.0f}".replace(",", "."))
        else:
            kpi3.metric("Rata-rata Transaksi", "Kolom tidak ditemukan")
        # =========================================================
        
        # 3. Menampilkan Ringkasan Struktur Data
        st.subheader("🧐 Struktur & Pratinjau Data")
        jumlah_duplikat = int(df.duplicated().sum()) if hasattr(df.duplicated(), 'sum') else 0
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Baris Data", f"{df.shape[0]}")
        col2.metric("Total Kolom", f"{df.shape[1]}")
        col3.metric("Kolom Duplikat", f"{jumlah_duplikat}")
        
        # Menampilkan 5 data pertama
        st.write("**Pratinjau Data (5 Baris Pertama):**")
        st.dataframe(df.head())
        
        # 4. Membuat Grafik Otomatis
        st.subheader("📈 Visualisasi Interaktif")
        
        kolom_numerik = df.select_dtypes(include=['number']).columns.tolist()
        kolom_kategori = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        if len(kolom_numerik) >= 1:
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                st.write("**Opsi Grafik 1 (Grid / Tren / Perbandingan)**")
                sumbu_x = st.selectbox("Pilih Sumbu X (Horizontal):", df.columns.tolist(), index=0)
                sumbu_y = st.selectbox("Pilih Sumbu Y (Vertikal):", kolom_numerik, index=0)
                jenis_grafik = st.radio("Pilih Jenis Grafik:", ["Garis (Line)", "Batang (Bar)", "Sebar (Scatter)"])
                
                if jenis_grafik == "Garis (Line)":
                    fig1 = px.line(df, x=sumbu_x, y=sumbu_y, title=f"Trends {sumbu_y} berdasarkan {sumbu_x}")
                elif jenis_grafik == "Batang (Bar)":
                    fig1 = px.bar(df, x=sumbu_x, y=sumbu_y, title=f"Perbandingan {sumbu_y} berdasarkan {sumbu_x}")
                else:
                    fig1 = px.scatter(df, x=sumbu_x, y=sumbu_y, title=f"Sebaran data {sumbu_y} vs {sumbu_x}")
                
                st.plotly_chart(fig1, use_container_width=True)
                
            with col_chart2:
                st.write("**Opsi Grafik 2 (Distribusi / Komposisi)**")
                if len(kolom_kategori) > 0:
                    kolom_pie = st.selectbox("Pilih Kolom Kategori (untuk Diagram Lingkaran):", kolom_kategori)
                    
                    df_pie = df[kolom_pie].value_counts().reset_index()
                    df_pie.columns = ['Kategori', 'Jumlah']
                    
                    fig2 = px.pie(df_pie, values='Jumlah', names='Kategori', title=f"Komposisi data pada {kolom_pie}")
                    st.plotly_chart(fig2, use_container_width=True)
                else:
                    st.warning("Tidak ditemukan kolom kategori (teks) untuk membuat Diagram Lingkaran.")
                    
        else:
            st.error("Data Anda tidak memiliki kolom angka (numerik) untuk divisualisasikan.")
            
    except Exception as e:
        st.error(f"Terjadi kesalahan saat membaca file: {e}")
else:
    st.info("💡 Menunggu file diunggah. Silakan unggah file data Anda pada kotak di atas.")
