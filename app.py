import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Konfigurasi Halaman Dashboard
st.set_page_config(page_title="Dashboard Analisis Data Otomatis", layout="wide")

st.title("📊 Dashboard Analisis Data & Visualisasi")
st.write("Unggah file CSV atau Excel Anda. Dashboard ini akan otomatis menyesuaikan tampilan berdasarkan isi data Anda!")

# 2. Fitur Unggah File (Uploader)
uploaded_file = st.file_uploader("Pilih file data (Format: .csv, .xlsx)", type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        # DETEKSI & PILIH SHEET UNTUK EXCEL
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
            st.success("File CSV berhasil diunggah!")
        else:
            excel_file = pd.ExcelFile(uploaded_file)
            daftar_sheet = excel_file.sheet_names
            
            st.sidebar.header("📂 Pilih Lembar Kerja")
            sheet_terpilih = st.sidebar.selectbox("Pilih Sheet Excel:", daftar_sheet)
            df = pd.read_excel(uploaded_file, sheet_name=sheet_terpilih)
            st.success(f"File Excel Berhasil Dimuat! (Sheet: {sheet_terpilih})")
        
        # =========================================================
        # SIDEBAR & FILTER DATA DINAMIS
        # =========================================================
        st.sidebar.header("🔍 Filter Data")
        
        # Filter otomatis berdasarkan kolom yang tersedia di data
        for col_filter in ['Wilayah', 'Kategori', 'Lokasi_Gudang', 'Status_Stok']:
            if col_filter in df.columns:
                opsi = ["Semua"] + df[col_filter].dropna().unique().tolist()
                pilihan = st.sidebar.selectbox(f"Filter {col_filter}:", opsi)
                if pilihan != "Semua":
                    df = df[df[col_filter] == pilihan]
        
        # =========================================================
        # 🔥 FITUR BARU: LAYOUT METRIK ADAPTIF (MENYESUAIKAN ISI DATA)
        # =========================================================
        
        # Skenario A: Jika yang diunggah adalah DATA PENJUALAN
        if 'Total_Penjualan' in df.columns or 'Jumlah_Terjual' in df.columns:
            st.subheader("💰 Ringkasan Finansial & Operasional Penjualan")
            kpi1, kpi2, kpi3 = st.columns(3)
            
            if 'Total_Penjualan' in df.columns:
                total_omset = df['Total_Penjualan'].sum()
                kpi1.metric("Total Pendapatan (Omset)", f"Rp {total_omset:,.0f}".replace(",", "."))
                kpi3.metric("Rata-rata Per Transaksi", f"Rp {df['Total_Penjualan'].mean():,.0f}".replace(",", "."))
            else:
                kpi1.metric("Total Pendapatan", "Kolom tidak ditemukan")
                kpi3.metric("Rata-rata Transaksi", "Kolom tidak ditemukan")
                
            if 'Jumlah_Terjual' in df.columns:
                kpi2.metric("Total Produk Terjual", f"{df['Jumlah_Terjual'].sum():,} Unit".replace(",", "."))
            else:
                kpi2.metric("Total Produk Terjual", "Kolom tidak ditemukan")
                
        # Skenario B: Jika yang diunggah adalah DATA STOK / INVENTARIS BARANG
        elif 'Jumlah_Stok' in df.columns or 'Stok' in df.columns or 'Harga_Beli' in df.columns:
            st.subheader("📦 Ringkasan Manajemen Stok & Inventaris Gudang")
            kpi1, kpi2, kpi3 = st.columns(3)
            
            kolom_stok = 'Jumlah_Stok' if 'Jumlah_Stok' in df.columns else 'Stok'
            
            if kolom_stok in df.columns:
                kpi1.metric("Total Aset Barang di Gudang", f"{df[kolom_stok].sum():,} Unit".replace(",", "."))
                kpi2.metric("Rata-rata Stok per Item", f"{df[kolom_stok].mean():.1f} Unit")
            else:
                kpi1.metric("Total Aset Barang", "Kolom stok tidak ditemukan")
                kpi2.metric("Rata-rata Stok", "Kolom stok tidak ditemukan")
                
            # Menghitung perkiraan nilai aset jika ada kolom harga
            if 'Harga_Beli' in df.columns and kolom_stok in df.columns:
                nilai_aset = (df[kolom_stok] * df['Harga_Beli']).sum()
                kpi3.metric("Total Nilai Valuasi Aset", f"Rp {nilai_aset:,.0f}".replace(",", "."))
            elif 'Harga_Satuan' in df.columns and kolom_stok in df.columns:
                nilai_aset = (df[kolom_stok] * df['Harga_Satuan']).sum()
                kpi3.metric("Total Nilai Valuasi Aset (Est.)", f"Rp {nilai_aset:,.0f}".replace(",", "."))
            else:
                kpi3.metric("Total Nilai Aset", "Kolom harga tidak ditemukan")
                
        # Skenario C: Jika data umum / tidak dikenal kolomnya
        else:
            st.subheader("📊 Ringkasan Umum Data")
            kpi1, kpi2, kpi3 = st.columns(3)
            kpi1.metric("Total Baris Data", f"{df.shape[0]}")
            kpi2.metric("Total Kolom Data", f"{df.shape[1]}")
            kpi3.metric("Kolom Duplikat", f"{int(df.duplicated().sum())}")
            
        # =========================================================
        
        # 4. Menampilkan Struktur & Pratinjau Data
        st.subheader("🧐 Pratinjau Data")
        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Unduh Data Hasil Filter (.csv)",
            data=csv_data,
            file_name="data_hasil_filter.csv",
            mime="text/csv",
        )
        st.dataframe(df.head())
        
        # 5. Membuat Grafik Otomatis
        st.subheader("📈 Visualisasi Interaktif")
        kolom_numerik = df.select_dtypes(include=['number']).columns.tolist()
        kolom_kategori = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        if len(kolom_numerik) >= 1:
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                st.write("**Opsi Grafik 1 (Tren / Perbandingan)**")
                sumbu_x = st.selectbox("Pilih Sumbu X (Horizontal):", df.columns.tolist(), index=0)
                sumbu_y = st.selectbox("Pilih Sumbu Y (Vertikal):", kolom_numerik, index=0)
                jenis_grafik = st.radio("Pilih Jenis Grafik:", ["Garis (Line)", "Batang (Bar)", "Sebar (Scatter)"])
                
                if jenis_grafik == "Garis (Line)":
                    fig1 = px.line(df, x=sumbu_x, y=sumbu_y, title=f"Tren {sumbu_y} berdasarkan {sumbu_x}")
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
