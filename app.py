import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import timedelta

# Sayfa Ayarları
st.set_page_config(page_title="ASHB Çağrı Yönetim Merkezi", layout="wide", initial_sidebar_state="expanded")

# ==========================================
# 🎨 ÖZEL TASARIM (CSS) 
# ==========================================
st.markdown("""
<style>
    .stApp { background-color: #F8FAFC; }
    [data-testid="stSidebar"] { background-color: #0F172A; min-width: 280px; max-width: 280px; }
    [data-testid="stSidebar"] * { color: #E2E8F0; }
    [data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child { display: none; }
    [data-testid="stSidebar"] div[role="radiogroup"] > label {
        padding: 12px 15px; border-radius: 8px; margin-bottom: 5px; cursor: pointer;
        transition: all 0.3s ease; display: flex; align-items: center; font-size: 16px; width: 100%;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] > label:hover { background-color: #1E293B; }
    [data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"] { background-color: #2563EB; color: white; font-weight: 600; }
    [data-testid="stSidebar"] .stRadio > label { display: none; }
    
    /* KPI Kartları */
    .kpi-card {
        background-color: #ffffff; padding: 20px; border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); text-align: center;
        border-top: 4px solid #3B82F6;
    }
    .kpi-card h4 { margin: 0; color: #64748B; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; }
    .kpi-card h2 { margin: 10px 0 0 0; color: #0F172A; font-size: 32px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🏢 SOL MENÜ
# ==========================================
with st.sidebar:
    st.markdown("""
        <div style="display: flex; align-items: center; margin-bottom: 30px; padding-top: 10px;">
            <div style="background: linear-gradient(135deg, #6366F1, #3B82F6); color: white; font-size: 24px; font-weight: bold; padding: 10px 20px; border-radius: 12px; margin-right: 15px;">A</div>
            <div><h3 style="margin: 0; color: #FFFFFF; font-size: 20px;">ASHB</h3><p style="margin: 0; color: #94A3B8; font-size: 12px;">Çağrı Yönetim Merkezi</p></div>
        </div>
    """, unsafe_allow_html=True)
    menu = st.radio("Menü", ["🚀 Dashboard", "📅 Haftalık Sunum", "📞 Çağrı", "📝 ÇM"], label_visibility="collapsed")

# ==========================================
# 📊 VERİ YÜKLEME FONKSİYONLARI
# ==========================================
@st.cache_data
def load_cagri_detay():
    df = duckdb.query("SELECT * FROM 'cagri_temsilcidetay_2026.csv'").df()
    df['Tarih'] = pd.to_datetime(df['Tarih'])
    return df

@st.cache_data
def load_cm_detay():
    df = duckdb.query("SELECT * FROM 'cm_detaykonular_2026_kasim.csv'").df()
    df['Tarih'] = pd.to_datetime(df['Tarih'])
    return df

@st.cache_data
def load_kopuk():
    df = duckdb.query("SELECT * FROM 'cm_kopukkayit_2024.csv'").df()
    return df

@st.cache_data
def load_kullanici():
    df = duckdb.query("SELECT * FROM 'cagri_kullanici.csv'").df()
    return df

# ==========================================
# 🚀 DASHBOARD SAYFASI
# ==========================================
if menu == "🚀 Dashboard":
    st.title("🚀 Genel Bakış ve Trendler")
    
    try:
        # Verileri Yükle
        df_cagri = load_cagri_detay()
        df_cm = load_cm_detay()
        df_kopuk = load_kopuk()
        
        # Son 1 Yıl Filtresi (Verideki en son tarihten geriye 365 gün)
        son_tarih = df_cagri['Tarih'].max()
        bir_yil_once = son_tarih - timedelta(days=365)
        df_cagri_yillik = df_cagri[df_cagri['Tarih'] >= bir_yil_once]
        df_cm_yillik = df_cm[df_cm['Tarih'] >= bir_yil_once]

        # --- 1. ÜST KPI KARTLARI ---
        # Not: Kaçan ve Cevaplanan verileri şu an Gelen Çağrı üzerinden varsayılmıştır. 
        # Gerçek sütun isimleri farklıysa buradaki değişkenleri güncelleyin.
        toplam_gelen = df_cagri_yillik['Gelen Çağrı'].sum()
        toplam_cevaplanan = toplam_gelen # Varsayım: Gelen = Cevaplanan
        toplam_kacan = 0 # Veri setinde yoksa 0
        kacan_yuzde = (toplam_kacan / toplam_gelen * 100) if toplam_gelen > 0 else 0
        
        toplam_cm = len(df_cm_yillik)
        toplam_kopuk = len(df_kopuk)

        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.markdown(f'<div class="kpi-card"><h4>Toplam Çağrı</h4><h2>{toplam_gelen:,.0f}</h2></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="kpi-card" style="border-top-color: #10B981;"><h4>Karşılanan</h4><h2>{toplam_cevaplanan:,.0f}</h2></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="kpi-card" style="border-top-color: #EF4444;"><h4>Kaçan Çağrı</h4><h2>{toplam_kacan:,.0f} <span style="font-size:16px; color:#EF4444;">(%{kacan_yuzde:.1f})</span></h2></div>', unsafe_allow_html=True)
        with col4:
            st.markdown(f'<div class="kpi-card" style="border-top-color: #8B5CF6;"><h4>ÇM Detay Kayıt</h4><h2>{toplam_cm:,.0f}</h2></div>', unsafe_allow_html=True)
        with col5:
            st.markdown(f'<div class="kpi-card" style="border-top-color: #F59E0B;"><h4>Köpük Kayıt</h4><h2>{toplam_kopuk:,.0f}</h2></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # --- 2. DİNAMİK FİLTRELEME ALANI ---
        st.markdown("### 📊 Detaylı Trend Analizi")
        
        # Ana Kategori Seçimi
        col_f1, col_f2, col_f3 = st.columns([1, 1, 2])
        with col_f1:
            ana_kategori = st.selectbox("Veri Kategorisi", ["Çağrı", "ÇM"])
            
        # Seçime Göre Alt Kırılımlar
        secilen_metrik = None
        secilen_personel = "Tümü"
        
        if ana_kategori == "Çağrı":
            with col_f2:
                # Çağrı metrikleri
                secilen_metrik = st.selectbox("Metrik Seçin", ["Gelen", "Cevaplanan", "Kaçan", "Operasyon", "IB", "OUT"])
            
            # Eğer Operasyon seçilirse Personel Filtresi Aç
            if secilen_metrik == "Operasyon":
                try:
                    df_kull = load_kullanici()
                    # Kullanıcı dosyasındaki isim sütununu tahmin ediyoruz, yoksa ilk sütunu alır
                    isim_sutunu = 'Ad Soyad' if 'Ad Soyad' in df_kull.columns else df_kull.columns[0]
                    personeller = ["Tümü"] + list(df_kull[isim_sutunu].dropna().unique())
                    with col_f3:
                        secilen_personel = st.selectbox("Personel Seçin", personeller)
                except:
                    st.warning("cagri_kullanici.csv yüklenemedi.")
                    
        elif ana_kategori == "ÇM":
            with col_f2:
                secilen_metrik = st.selectbox("Görünüm", ["Köpük", "Detay", "Özet"])

        # --- 3. VERİYİ HAZIRLA (Tablo ve Grafik İçin) ---
        # Seçilen filtreye göre aylık trend verisi oluşturuyoruz
        trend_df = pd.DataFrame()
        y_ekseni_basligi = ""
        
        if ana_kategori == "Çağrı":
            gecici_df = df_cagri_yillik.copy()
            
            # Personel filtresi uygula
            if secilen_metrik == "Operasyon" and secilen_personel != "Tümü":
                gecici_df = gecici_df[gecici_df['Müşteri Temsilcisi'] == secilen_personel]
            
            # Metriğe göre sütun seçimi (Sütun isimlerini kendi verinize göre güncelleyin)
            if secilen_metrik == "Gelen": sutun = "Gelen Çağrı"
            elif secilen_metrik == "Cevaplanan": sutun = "Gelen Çağrı" # Varsayım
            elif secilen_metrik == "Kaçan": sutun = "Gelen Çağrı" # Varsayım
            elif secilen_metrik == "Operasyon": sutun = "Gelen Çağrı"
            elif secilen_metrik == "IB": sutun = "IB ACH"
            elif secilen_metrik == "OUT": sutun = "OUT ACH"
            else: sutun = "Gelen Çağrı"
            
            gecici_df['Ay'] = gecici_df['Tarih'].dt.to_period('M').astype(str)
            trend_df = gecici_df.groupby('Ay')[sutun].sum().reset_index()
            trend_df.columns = ['Ay', 'Değer']
            y_ekseni_basligi = f"{secilen_metrik} Sayısı"
            
        elif ana_kategori == "ÇM":
            if secilen_metrik == "Detay":
                gecici_df = df_cm_yillik.copy()
                gecici_df['Ay'] = gecici_df['Tarih'].dt.to_period('M').astype(str)
                trend_df = gecici_df.groupby('Ay').size().reset_index(name='Değer')
                trend_df.columns = ['Ay', 'Değer']
                y_ekseni_basligi = "Detay Kayıt Sayısı"
            elif secilen_metrik == "Köpük":
                # Köpük kayıtlarında tarih sütunu yoksa genel toplam gösterelim
                trend_df = pd.DataFrame({'Ay': ['Toplam'], 'Değer': [toplam_kopuk]})
                y_ekseni_basligi = "Köpük Kayıt Sayısı"
            elif secilen_metrik == "Özet":
                trend_df = pd.DataFrame({'Ay': ['Toplam Çağrı', 'Toplam ÇM', 'Toplam Köpük'], 
                                         'Değer': [toplam_gelen, toplam_cm, toplam_kopuk]})
                y_ekseni_basligi = "Genel Özet"

        # --- 4. TABLO VE GRAFİK ÇİZİMİ ---
        if not trend_df.empty:
            # Tabloyu göster
            st.dataframe(trend_df, use_container_width=True, hide_index=True)
            
            # Grafiği çiz
            if len(trend_df) > 1 and trend_df['Ay'].iloc[0] != 'Toplam':
                # Zaman serisi (Çizgi Grafik)
                fig = px.area(trend_df, x='Ay', y='Değer', title=f"Son 1 Yıl {secilen_metrik} Trendi", markers=True)
            else:
                # Kategori karşılaştırma (Çubuk Grafik)
                fig = px.bar(trend_df, x='Ay', y='Değer', text='Değer', title=f"{secilen_metrik} Özeti")
                fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
            
            fig.update_layout(yaxis_title=y_ekseni_basligi, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=0, r=0, t=40, b=0))
            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Dashboard yüklenirken bir hata oluştu: {e}")

# ==========================================
# DİĞER SAYFALAR (İskelet)
# ==========================================
elif menu == "📅 Haftalık Sunum":
    st.title("📅 Haftalık Sunum")
    st.info("Burayı daha sonra dolduracağız.")

elif menu == "📞 Çağrı":
    st.title("📞 Çağrı Detayları")
    st.info("Burayı daha sonra dolduracağız.")

elif menu == "📝 ÇM":
    st.title("📝 ÇM Detayları")
    st.info("Burayı daha sonra dolduracağız.")
