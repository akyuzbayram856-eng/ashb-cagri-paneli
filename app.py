import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px

# Sayfa Ayarları
st.set_page_config(page_title="ASHB Çağrı Merkezi Paneli", layout="wide")
st.title("📞 ASHB Çağrı Merkezi Yönetim Paneli")

# --- SOL MENÜ (MODÜL SEÇİMİ) ---
st.sidebar.header("📌 Analiz Modülü")
modul = st.sidebar.radio(
    "Görüntülemek istediğiniz veriyi seçin:",
    ("Kalite Değerlendirmeleri", "Çağrı & SL Süreleri", "ÇM Konu Detayları", "Köpük Kayıtlar")
)

st.sidebar.markdown("---")

# ==========================================
# 1. MODÜL: KALİTE DEĞERLENDİRMELERİ
# ==========================================
if modul == "Kalite Değerlendirmeleri":
    st.header("📝 Çağrı Kalite Değerlendirmeleri")
    
    @st.cache_data
    def kalite_yukle():
        df = duckdb.query("SELECT * FROM 'cagri_kalite_2026_kasim.csv'").df()
        df['Tarih'] = pd.to_datetime(df['Çağrı Tarihi']).dt.date
        return df
    
    try:
        df_kalite = kalite_yukle()
        
        # Filtreler
        min_tarih = df_kalite['Tarih'].min()
        max_tarih = df_kalite['Tarih'].max()
        tarih_araligi = st.sidebar.date_input("Tarih Aralığı", [min_tarih, max_tarih])
        
        takim_liderleri = ["Tümü"] + list(df_kalite['Takım Lideri'].dropna().unique())
        secili_tl = st.sidebar.selectbox("Takım Lideri Seçin", takim_liderleri)
        
        # Filtreleme
        if len(tarih_araligi) == 2:
            df_kalite = df_kalite[(df_kalite['Tarih'] >= tarih_araligi[0]) & (df_kalite['Tarih'] <= tarih_araligi[1])]
        if secili_tl != "Tümü":
            df_kalite = df_kalite[df_kalite['Takım Lideri'] == secili_tl]
            
        # KPI'lar
        col1, col2, col3 = st.columns(3)
        col1.metric("Toplam Dinlenen Çağrı", len(df_kalite))
        col2.metric("Ortalama Skor", round(df_kalite['Skor'].mean(), 1) if not df_kalite.empty else 0)
        col3.metric("Değerlendirici Sayısı", df_kalite['Değerlendiren'].nunique())
        
        # Grafikler
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            if not df_kalite.empty:
                df_tl = df_kalite.groupby("Takım Lideri").agg(Dinlenen=("Temsilci", "count"), Skor=("Skor", "mean")).reset_index().sort_values(by="Dinlenen", ascending=False)
                fig_tl = px.bar(df_tl, x="Takım Lideri", y="Dinlenen", text="Skor", color="Skor")
                fig_tl.update_traces(texttemplate='Ort: %{text:.1f}', textposition='outside')
                st.plotly_chart(fig_tl, use_container_width=True)
        with col_g2:
            if not df_kalite.empty:
                df_form = df_kalite.groupby("Form Adı").agg(Toplam=("Temsilci", "count")).reset_index()
                fig_form = px.pie(df_form, values="Toplam", names="Form Adı", hole=0.4)
                st.plotly_chart(fig_form, use_container_width=True)
                
        # Eğilimler
        st.markdown("---")
        st.subheader("Değerlendirici Not Eğilimleri")
        if not df_kalite.empty:
            df_notlar = df_kalite[df_kalite["Değerlendirme Notu"].notna()]
            def not_ara(df, kelime): return df["Değerlendirme Notu"].str.contains(kelime, case=False).sum()
            egilimler = {
                "Hitap Eksikliği": not_ara(df_notlar, "hitap"),
                "Bekletme Sorunu": not_ara(df_notlar, "bekletme"),
                "Diksiyon/Ses Tonu": not_ara(df_notlar, "diksiyon") + not_ara(df_notlar, "ses tonu"),
                "Kayıt Hatası": not_ara(df_notlar, "kayıt") + not_ara(df_notlar, "kayit")
            }
            fig_egilim = px.bar(x=list(egilimler.keys()), y=list(egilimler.values()), color=list(egilimler.keys()))
            st.plotly_chart(fig_egilim, use_container_width=True)
            
    except Exception as e:
        st.error(f"Kalite verisi yüklenemedi: {e}")


# ==========================================
# 2. MODÜL: ÇAĞRI & SL SÜRELERİ
# ==========================================
elif modul == "Çağrı & SL Süreleri":
    st.header("⏱️ Çağrı ve Görüşme (SL) Süreleri")
    
    @st.cache_data
    def cagri_yukle():
        df = duckdb.query("SELECT * FROM 'cagri_temsilcidetay_2026.csv'").df()
        df['Tarih'] = pd.to_datetime(df['Tarih']).dt.date
        return df

    try:
        df_cagri = cagri_yukle()
        
        # Filtreler
        min_tarih = df_cagri['Tarih'].min()
        max_tarih = df_cagri['Tarih'].max()
        tarih_araligi = st.sidebar.date_input("Tarih Aralığı", [min_tarih, max_tarih])
        
        if len(tarih_araligi) == 2:
            df_cagri = df_cagri[(df_cagri['Tarih'] >= tarih_araligi[0]) & (df_cagri['Tarih'] <= tarih_araligi[1])]
            
        # KPI'lar
        toplam_cagri = df_cagri['Gelen Çağrı'].sum()
        toplam_sure = df_cagri['Gelen Çağrı Süresi'].sum()
        ort_sl = (toplam_sure / toplam_cagri) if toplam_cagri > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Toplam Gelen Çağrı", f"{toplam_cagri:,.0f}")
        col2.metric("Toplam Görüşme Süresi", f"{toplam_sure/3600:,.1f} Saat")
        col3.metric("Ortalama SL Süresi", f"{ort_sl:.1f} Saniye")
        
        st.markdown("---")
        st.subheader("Personel Bazlı Çağrı Sayısı ve Ortalama Süre")
        
        if not df_cagri.empty:
            # Personel bazlı özet
            df_personel = df_cagri.groupby("Müşteri Temsilcisi").agg(
                Cagri=("Gelen Çağrı", "sum"),
                Sure=("Gelen Çağrı Süresi", "sum")
            ).reset_index()
            df_personel['Ortalama_SL'] = df_personel['Sure'] / df_personel['Cagri']
            df_personel = df_personel.sort_values(by="Cagri", ascending=False).head(20) # İlk 20 kişi
            
            fig_cagri = px.bar(df_personel, x="Müşteri Temsilcisi", y="Cagri", text="Ortalama_SL",
                               title="En Çok Çağrı Alan 20 Personel (Ortalama SL Saniye)",
                               color="Ortalama_SL", color_continuous_scale="Bluered")
            fig_cagri.update_traces(texttemplate='%{text:.0f} sn', textposition='outside')
            st.plotly_chart(fig_cagri, use_container_width=True)
            
    except Exception as e:
        st.error(f"Çağrı verisi yüklenemedi: {e}")


# ==========================================
# 3. MODÜL: ÇM KONU DETAYLARI
# ==========================================
elif modul == "ÇM Konu Detayları":
    st.header("📊 ÇM Konu ve Kayıt Detayları")
    
    @st.cache_data
    def cm_yukle():
        df = duckdb.query("SELECT * FROM 'cm_detaykonular_2026_kasim.csv'").df()
        df['Tarih'] = pd.to_datetime(df['Tarih']).dt.date
        return df

    try:
        df_cm = cm_yukle()
        
        # Filtreler
        min_tarih = df_cm['Tarih'].min()
        max_tarih = df_cm['Tarih'].max()
        tarih_araligi = st.sidebar.date_input("Tarih Aralığı", [min_tarih, max_tarih])
        
        if len(tarih_araligi) == 2:
            df_cm = df_cm[(df_cm['Tarih'] >= tarih_araligi[0]) & (df_cm['Tarih'] <= tarih_araligi[1])]
            
        col1, col2 = st.columns(2)
        col1.metric("Toplam Kayıt Sayısı", f"{len(df_cm):,.0f}")
        col2.metric("İşlem Yapan Personel", df_cm['Adı Soyadı'].nunique())
        
        st.markdown("---")
        
        if not df_cm.empty:
            col_g1, col_g2 = st.columns(2)
            with col_g1:
                # En çok konuşulan 15 konu
                df_konu = df_cm.groupby("Kırılım").size().reset_index(name="Kayit_Sayisi").sort_values(by="Kayit_Sayisi", ascending=False).head(15)
                fig_konu = px.bar(df_konu, x="Kayit_Sayisi", y="Kırılım", orientation='h', title="En Çok Kayıt Yapılan 15 Konu")
                fig_konu.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_konu, use_container_width=True)
                
            with col_g2:
                # En çok kayıt yapan 15 personel
                df_pers = df_cm.groupby("Adı Soyadı").size().reset_index(name="Kayit_Sayisi").sort_values(by="Kayit_Sayisi", ascending=False).head(15)
                fig_pers = px.bar(df_pers, x="Adı Soyadı", y="Kayit_Sayisi", title="En Çok Kayıt Yapan 15 Personel", color="Kayit_Sayisi")
                st.plotly_chart(fig_pers, use_container_width=True)
                
    except Exception as e:
        st.error(f"ÇM verisi yüklenemedi: {e}")


# ==========================================
# 4. MODÜL: KÖPÜK KAYITLAR
# ==========================================
elif modul == "Köpük Kayıtlar":
    st.header("🚨 Köpük Kayıt Analizi")
    
    @st.cache_data
    def kopuk_yukle():
        # Dosya adını GitHub'a yüklediğiniz isimle değiştirin
        df = duckdb.query("SELECT * FROM 'cm_kopukkayit_2024.csv'").df()
        return df

    try:
        df_kopuk = kopuk_yukle()
        
        st.metric("Toplam Köpük Kayıt Sayısı", f"{len(df_kopuk):,.0f}")
        st.markdown("---")
        
        st.write("Veri Önizlemesi (İlk 100 Satır):")
        st.dataframe(df_kopuk.head(100), use_container_width=True)
                
    except Exception as e:
        st.error(f"Köpük kayıt verisi yüklenemedi. Dosya adını kontrol edin. Hata: {e}")
