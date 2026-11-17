import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px

# Sayfa Ayarları
st.set_page_config(page_title="ASHB Çağrı Paneli", layout="wide")
st.title("📞 ASHB Çağrı Merkezi Kalite Paneli")
st.markdown("Bu panel, çağrı kalite verilerini interaktif olarak analiz etmek için oluşturulmuştur.")

# Veriyi DuckDB ile oku (Hız için cache kullanıyoruz)
@st.cache_data
def veri_yukle():
    df = duckdb.query("SELECT * FROM 'cagri_kalite_2026_kasim.csv'").df()
    df['Tarih'] = pd.to_datetime(df['Çağrı Tarihi']).dt.date
    return df

try:
    df = veri_yukle()
except Exception as e:
    st.error(f"Veri yüklenirken hata oluştu: {e}")
    st.stop()

# --- SOL MENÜ (FİLTRELER) ---
st.sidebar.header("🔍 Filtreler")

# Tarih Filtresi
min_tarih = df['Tarih'].min()
max_tarih = df['Tarih'].max()
tarih_araligi = st.sidebar.date_input("Tarih Aralığı Seçin", [min_tarih, max_tarih])

# Takım Lideri Filtresi
takim_liderleri = ["Tümü"] + list(df['Takım Lideri'].dropna().unique())
secili_tl = st.sidebar.selectbox("Takım Lideri Seçin", takim_liderleri)

# Filtreleri Uygula
if len(tarih_araligi) == 2:
    baslangic, bitis = tarih_araligi
    filtrelenmis_df = df[(df['Tarih'] >= baslangic) & (df['Tarih'] <= bitis)]
else:
    filtrelenmis_df = df

if secili_tl != "Tümü":
    filtrelenmis_df = filtrelenmis_df[filtrelenmis_df['Takım Lideri'] == secili_tl]

# --- ÜST KISIM (KPI KARTLARI) ---
st.markdown("---")
col1, col2, col3 = st.columns(3)
col1.metric("Toplam Dinlenen Çağrı", len(filtrelenmis_df))
col2.metric("Ortalama Kalite Skoru", round(filtrelenmis_df['Skor'].mean(), 1) if not filtrelenmis_df.empty else 0)
col3.metric("Değerlendirici Sayısı", filtrelenmis_df['Değerlendiren'].nunique())

# --- GRAFİKLER ---
st.markdown("---")
col_graph1, col_graph2 = st.columns(2)

with col_graph1:
    st.subheader("Takım Lideri Performansı")
    if not filtrelenmis_df.empty:
        df_tl = filtrelenmis_df.groupby("Takım Lideri").agg(
            Dinlenen=("Temsilci", "count"),
            Ortalama_Skor=("Skor", "mean")
        ).reset_index().sort_values(by="Dinlenen", ascending=False)
        fig_tl = px.bar(df_tl, x="Takım Lideri", y="Dinlenen", text="Ortalama_Skor", color="Ortalama_Skor")
        fig_tl.update_traces(texttemplate='Ort: %{text:.1f}', textposition='outside')
        st.plotly_chart(fig_tl, use_container_width=True)
    else:
        st.warning("Seçilen filtrelerde veri yok.")

with col_graph2:
    st.subheader("Form Bazlı Dağılım")
    if not filtrelenmis_df.empty:
        df_form = filtrelenmis_df.groupby("Form Adı").agg(Toplam=("Temsilci", "count")).reset_index()
        fig_form = px.pie(df_form, values="Toplam", names="Form Adı", hole=0.4)
        st.plotly_chart(fig_form, use_container_width=True)
    else:
         st.warning("Seçilen filtrelerde veri yok.")

# Alt Kısım: Eğilimler
st.markdown("---")
st.subheader("Değerlendirici Not Eğilimleri")
if not filtrelenmis_df.empty:
    df_notlar = filtrelenmis_df[filtrelenmis_df["Değerlendirme Notu"].notna()]
    
    def not_ara(df, kelime):
        return df["Değerlendirme Notu"].str.contains(kelime, case=False).sum()

    egilimler = {
        "Hitap Eksikliği": not_ara(df_notlar, "hitap"),
        "Bekletme Sorunu": not_ara(df_notlar, "bekletme"),
        "Diksiyon/Ses Tonu": not_ara(df_notlar, "diksiyon") + not_ara(df_notlar, "ses tonu"),
        "Kayıt Hatası": not_ara(df_notlar, "kayıt") + not_ara(df_notlar, "kayit")
    }
    fig_egilim = px.bar(x=list(egilimler.keys()), y=list(egilimler.values()), color=list(egilimler.keys()))
    st.plotly_chart(fig_egilim, use_container_width=True)
