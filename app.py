import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
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
# (Yıldız (*) işareti ile o dosya grubundaki tüm yılları okur)
# ==========================================
@st.cache_data
def load_cagri_kuyruk():
    # Tüm cagri_kuyruk_2023, 2024, 2025, 2026 dosyalarını tek tabloda birleştirir
    df = duckdb.query("SELECT * FROM 'cagri_kuyruk_*.csv'").df()
    # Tarih sütununu bul ve formatla (Sütun adının 'Tarih' olduğunu varsayıyoruz)
    if 'Tarih' in df.columns:
        df['Tarih'] = pd.to_datetime(df['Tarih'])
    return df

@st.cache_data
def load_cm_detay():
    df = duckdb.query("SELECT * FROM 'cm_detaykonular_*.csv'").df()
    if 'Tarih' in df.columns:
        df['Tarih'] = pd.to_datetime(df['Tarih'])
    return df

@st.cache_data
def load_kopuk():
    df = duckdb.query("SELECT * FROM 'cm_kopukkayit*.csv'").df()
    return df

@st.cache_data
def load_operasyon():
    try:
        df_in = duckdb.query("SELECT * FROM 'cagri_operasyoninbound_2026.csv'").df()
    except:
        df_in = pd.DataFrame()
    try:
        df_out = duckdb.query("SELECT * FROM 'cagri_operasyonoutbound_2026.csv'").df()
    except:
        df_out = pd.DataFrame()
    
    # İki dosyayı alt alta birleştir (Eğer sütunlar uyuşmuyorsa hata verebilir, o yüzden dikkatli birleştiriyoruz)
    df_op = pd.concat([df_in, df_out], ignore_index=True)
    if not df_op.empty and 'Tarih' in df_op.columns:
        df_op['Tarih'] = pd.to_datetime(df_op['Tarih'])
    return df_op

# ==========================================
# 🚀 DASHBOARD SAYFASI
# ==========================================
if menu == "🚀 Dashboard":
    st.title("🚀 Genel Bakış ve Trendler")
    
    try:
        # 1. VERİLERİ YÜKLE
        df_kuyruk = load_cagri_kuyruk()
        df_cm = load_cm_detay()
        df_kopuk = load_kopuk()
        
        # Son 1 Yıl Filtresi (Kuyruk verisinin en son tarihini baz alıyoruz)
        if not df_kuyruk.empty and 'Tarih' in df_kuyruk.columns:
            son_tarih = df_kuyruk['Tarih'].max()
            bir_yil_once = son_tarih - timedelta(days=365)
            
            df_kuyruk_yillik = df_kuyruk[df_kuyruk['Tarih'] >= bir_yil_once]
            df_cm_yillik = df_cm[df_cm['Tarih'] >= bir_yil_once] if not df_cm.empty and 'Tarih' in df_cm.columns else df_cm
        else:
            df_kuyruk_yillik = df_kuyruk
            df_cm_yillik = df_cm

        # --- 2. ÜST KPI KARTLARI (CAGRİ KUYRUK DOSYASINDAN) ---
        # NOT: Aşağıdaki sütun isimleri (Gelen_Cagri, Cevaplanan_Cagri, Kacan_Cagri) 
        # sizin dosyanızdaki başlıklarla birebir aynı olmalıdır. Farklıysa buradan değiştirin.
        
        sutun_gelen = 'Gelen_Cagri' if 'Gelen_Cagri' in df_kuyruk_yillik.columns else df_kuyruk_yillik.columns[0] 
        sutun_cevaplanan = 'Cevaplanan_Cagri' if 'Cevaplanan_Cagri' in df_kuyruk_yillik.columns else sutun_gelen
        sutun_kacan = 'Kacan_Cagri' if 'Kacan_Cagri' in df_kuyruk_yillik.columns else sutun_gelen

        toplam_gelen = df_kuyruk_yillik[sutun_gelen].sum()
        toplam_cevaplanan = df_kuyruk_yillik[sutun_cevaplanan].sum()
        toplam_kacan = df_kuyruk_yillik[sutun_kacan].sum()
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

        # --- 3. DİNAMİK FİLTRELEME ALANI ---
        st.markdown("### 📊 Detaylı Trend Analizi")
        
        col_f1, col_f2, col_f3 = st.columns([1, 1, 2])
        with col_f1:
            ana_kategori = st.selectbox("Veri Kategorisi", ["Çağrı", "ÇM"])
            
        secilen_metrik = None
        secilen_il = "Tümü"
        
        if ana_kategori == "Çağrı":
            with col_f2:
                secilen_metrik = st.selectbox("Metrik Seçin", ["Gelen", "Cevaplanan", "Kaçan", "Operasyon", "IB", "OUT"])
            
            # Eğer Operasyon seçilirse İl Filtresi Aç
            if secilen_metrik == "Operasyon":
                df_op = load_operasyon()
                if not df_op.empty:
                    # 'Il' veya 'İl' sütununu bul
                    il_sutunu = 'Il' if 'Il' in df_op.columns else ('İl' if 'İl' in df_op.columns else df_op.columns[1])
                    iller = ["Tümü"] + list(df_op[il_sutunu].dropna().unique())
                    with col_f3:
                        secilen_il = st.selectbox("Operasyon İli Seçin", iller)
                else:
                    st.warning("Operasyon dosyaları okunamadı.")
                    
        elif ana_kategori == "ÇM":
            with col_f2:
                secilen_metrik = st.selectbox("Görünüm", ["Köpük", "Detay", "Özet"])

        # --- 4. VERİYİ HAZIRLA (Tablo ve Grafik İçin) ---
        trend_df = pd.DataFrame()
        y_ekseni_basligi = ""
        
        if ana_kategori == "Çağrı":
            gecici_df = df_kuyruk_yillik.copy()
            
            # Metriğe göre ilgili sütunu seç
            if secilen_metrik == "Gelen": sutun = sutun_gelen
            elif secilen_metrik == "Cevaplanan": sutun = sutun_cevaplanan
            elif secilen_metrik == "Kaçan": sutun = sutun_kacan
            elif secilen_metrik == "IB": sutun = 'IB' if 'IB' in gecici_df.columns else df_kuyruk.columns[0] # Sütun adını kontrol edin
            elif secilen_metrik == "OUT": sutun = 'OUT' if 'OUT' in gecici_df.columns else df_kuyruk.columns[0]
            elif secilen_metrik == "Operasyon":
                # Operasyon verisini yükle ve İl filtresini uygula
                gecici_op = load_operasyon()
                if not gecici_op.empty and secilen_il != "Tümü":
                    gecici_op = gecici_op[gecici_op[il_sutunu] == secilen_il]
                
                if not gecici_op.empty and 'Tarih' in gecici_op.columns:
                    gecici_op['Ay'] = gecici_op['Tarih'].dt.to_period('M').astype(str)
                    # Operasyon sayısı için satır sayısını (len) sayıyoruz, eğer sayısal bir sütun varsa onu sumlayabilirsiniz.
                    trend_df = gecici_op.groupby('Ay').size().reset_index(name='Değer')
                    trend_df.columns = ['Ay', 'Değer']
                    y_ekseni_basligi = "Operasyon Çağrı Sayısı"
                else:
                    st.warning("Seçilen operasyon için veri bulunamadı.")
            
            # Eğer Operasyon seçilmediyse Kuyruk verisinden normal grupla
            if secilen_metrik != "Operasyon":
                gecici_df['Ay'] = gecici_df['Tarih'].dt.to_period('M').astype(str)
                trend_df = gecici_df.groupby('Ay')[sutun].sum().reset_index()
                trend_df.columns = ['Ay', 'Değer']
                y_ekseni_basligi = f"{secilen_metrik} Sayısı"
            
        elif ana_kategori == "ÇM":
            if secilen_metrik == "Detay":
                gecici_df = df_cm_yillik.copy()
                if not gecici_df.empty and 'Tarih' in gecici_df.columns:
                    gecici_df['Ay'] = gecici_df['Tarih'].dt.to_period('M').astype(str)
                    trend_df = gecici_df.groupby('Ay').size().reset_index(name='Değer')
                    y_ekseni_basligi = "Detay Kayıt Sayısı"
            elif secilen_metrik == "Köpük":
                # Köpük kayıtlarında tarih sütunu yoksa genel toplam gösterelim
                trend_df = pd.DataFrame({'Ay': ['Toplam (Son 1 Yıl)'], 'Değer': [toplam_kopuk]})
                y_ekseni_basligi = "Köpük Kayıt Sayısı"
            elif secilen_metrik == "Özet":
                trend_df = pd.DataFrame({'Ay': ['Toplam Çağrı', 'Toplam CM Detay', 'Toplam Köpük'], 
                                         'Değer': [toplam_gelen, toplam_cm, toplam_kopuk]})
                y_ekseni_basligi = "Genel Özet"

        # --- 5. TABLO VE GRAFİK ÇİZİMİ ---
        if not trend_df.empty:
            # Tabloyu göster
            st.dataframe(trend_df, use_container_width=True, hide_index=True)
            
            # Grafiği çiz
            if len(trend_df) > 1 and "Toplam" not in trend_df['Ay'].iloc[0]:
                # Zaman serisi (Alan Grafik)
                fig = px.area(trend_df, x='Ay', y='Değer', title=f"Son 1 Yıl {secilen_metrik} Trendi", markers=True)
            else:
                # Kategori karşılaştırma (Çubuk Grafik)
                fig = px.bar(trend_df, x='Ay', y='Değer', text='Değer', title=f"{secilen_metrik} Özeti")
                fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
            
            fig.update_layout(yaxis_title=y_ekseni_basligi, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=0, r=0, t=40, b=0))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Seçilen kriterlere uygun veri bulunamadı.")

    except Exception as e:
        st.error(f"Dashboard yüklenirken bir hata oluştu: {e}")

# Diğer Sayfalar (İskelet)
elif menu == "📅 Haftalık Sunum":
    st.title("📅 Haftalık Sunum")
elif menu == "📞 Çağrı":
    st.title("📞 Çağrı Detayları")
elif menu == "📝 ÇM":
    st.title("📝 ÇM Detayları")
