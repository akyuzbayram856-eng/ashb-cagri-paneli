import streamlit as st

# Sayfa Ayarları
st.set_page_config(page_title="ASHB Çağrı Yönetim Merkezi", layout="wide", initial_sidebar_state="expanded")

# ==========================================
# 🎨 ÖZEL TASARIM (CSS) - GÖRSELDEKİ GİBİ
# ==========================================
st.markdown("""
<style>
    /* Genel Arka Plan */
    .stApp {
        background-color: #F8FAFC;
    }
    
    /* Sol Menü (Sidebar) Arka Planı ve Genişliği */
    [data-testid="stSidebar"] {
        background-color: #0F172A; /* Koyu Lacivert */
        min-width: 280px;
        max-width: 280px;
    }
    
    /* Sol Menüdeki Yazı Rengi */
    [data-testid="stSidebar"] * {
        color: #E2E8F0;
    }

    /* Radyo Butonlarının Yuvarlak İşaretini Gizle */
    [data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child {
        display: none;
    }

    /* Menü Butonlarının Genel Tasarımı */
    [data-testid="stSidebar"] div[role="radiogroup"] > label {
        padding: 12px 15px;
        border-radius: 8px;
        margin-bottom: 5px;
        cursor: pointer;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        font-size: 16px;
        font-weight: 500;
        width: 100%;
    }

    /* Üzerine Gelince (Hover) */
    [data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
        background-color: #1E293B;
    }

    /* SEÇİLİ OLAN BUTONUN TASARIMI (Mavi Arka Plan) */
    [data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"] {
        background-color: #2563EB;
        color: white;
        font-weight: 600;
    }

    /* Sol Menü Başlıklarını Gizle */
    [data-testid="stSidebar"] .stRadio > label {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🏢 SOL MENÜ (LOGO VE BAŞLIKLAR)
# ==========================================
with st.sidebar:
    # Logo Alanı (HTML ile)
    st.markdown("""
        <div style="display: flex; align-items: center; margin-bottom: 30px; padding-top: 10px;">
            <div style="background: linear-gradient(135deg, #6366F1, #3B82F6); color: white; font-size: 24px; font-weight: bold; padding: 10px 20px; border-radius: 12px; margin-right: 15px;">
                A
            </div>
            <div>
                <h3 style="margin: 0; color: #FFFFFF; font-size: 20px; font-weight: 600;">ASHB</h3>
                <p style="margin: 0; color: #94A3B8; font-size: 12px;">Çağrı Yönetim Merkezi</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Menü Seçenekleri
    menu = st.radio(
        "Menü",
        ["🚀 Dashboard", "📅 Haftalık Sunum", "📞 Çağrı", "📝 ÇM"],
        label_visibility="collapsed"
    )

# ==========================================
# 📄 SAYFA İÇERİKLERİ
# ==========================================

if menu == "🚀 Dashboard":
    st.title("🚀 Genel Bakış (Dashboard)")
    st.info("Bu alanda genel özet metrikleri ve tüm operasyonu kapsayan grafikler yer alacak. İçerik beklentinizi belirttiğinizde burayı dolduracağız.")

elif menu == "📅 Haftalık Sunum":
    st.title("📅 Haftalık Sunum")
    st.success("Haftalık yönetici sunumları için hazırlanan özel tablolar ve özet grafikler burada olacak.")

elif menu == "📞 Çağrı":
    st.title("📞 Çağrı Operasyonları")
    st.warning("Çağrı süreleri, personel performansları ve SL metrikleri bu sayfada yer alacak.")

elif menu == "📝 ÇM":
    st.title("📝 ÇM (Çağrı Merkezi) Detayları")
    st.error("Konu kırılımları, kayıt detayları ve Köpük kayıtlar bu sayfada analiz edilecek.")
