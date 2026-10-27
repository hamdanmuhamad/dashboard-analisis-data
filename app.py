import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Konfigurasi Halaman Dashboard
st.set_page_config(page_title="Dashboard Analisis Data Otomatis", layout="wide")

st.title("📊 Dashboard Analisis Data & Visualisasi")
st.write("Unggah file CSV atau Excel Anda untuk melihat ringkasan data dan grafik interaktif secara instan!")

# 2. Fitur Unggah File (Uploader)
uploaded_file = st.file_uploader("data_sampel.csv", type=["csv", "xlsx"])

if uploaded_file is not None:
    # Membaca file berdasarkan formatnya
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.success("File berhasil diunggah!")
        
        # 3. Menampilkan Ringkasan Data (Metrik)
        st.subheader("🧐 Ringkasan Data")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Baris Data", df.shape[0])
        col2.metric("Total Kolom", df.shape[1])
        col3.metric("Kolom Duplikat", int(df.duplicated().sum()))
        
        # Menampilkan 5 data pertama
        st.write("**Pratinjau Data (5 Baris Pertama):**")
        st.dataframe(df.head())
        
        # 4. Membuat Grafik Otomatis
        st.subheader("📈 Visualisasi Interaktif")
        
        # Memisahkan kolom teks (kategori) dan kolom angka (numerik)
        kolom_numerik = df.select_dtypes(include=['number']).columns.tolist()
        kolom_kategori = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        if len(kolom_numerik) >= 1:
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                st.write("**Opsi Grafik 1 (Grid / Tren / Perbandingan)**")
                sumbu_x = st.selectbox("Pilih Sumbu X (Horizontal):", df.columns.tolist(), index=0)
                sumbu_y = st.selectbox("Pilih Sumbu Y (Vertikal):", kolom_numerik, index=0)
                jenis_grafik = st.radio("Pilih Jenis Grafik:", ["Garis (Line)", "Batang (Bar)", "Sebar (Scatter)"])
                
                # Render grafik berdasarkan pilihan
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
                    # Menghitung jumlah data per kategori
                    df_pie = df[kolom_pie].value_counts().reset_index()
                    df_pie.columns = [kolom_pie, 'Jumlah']
                    
                    fig2 = px.pie(df_pie, values='Jumlah', names=kolom_pie, title=f"Komposisi data pada {kolom_pie}")
                    st.plotly_chart(fig2, use_container_width=True)
                else:
                    st.warning("Tidak ditemukan kolom kategori (teks) untuk membuat Diagram Lingkaran.")
                    
        else:
            st.error("Data Anda tidak memiliki kolom angka (numerik) untuk divisualisasikan.")
            
    except Exception as e:
        st.error(f"Terjadi kesalahan saat membaca file: {e}")
else:
    st.info("💡 Menunggu file diunggah. Silakan unggah file data Anda pada kotak di atas.")
