"""
İK Karar Destek Sistemi — Ana Sayfa
- Kullanıcı tipi seçimi (İK / Aday)
- Dinamik sayfa menüsü (st.navigation)
"""

import streamlit as st
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "scripts"))

from database import veritabani_olustur

st.set_page_config(
    page_title="İK Karar Destek Sistemi",
    page_icon="🤖",
    layout="wide",
)

veritabani_olustur()

# =====================================================================
# SESSION STATE
# =====================================================================
if "kullanici_tipi" not in st.session_state:
    st.session_state.kullanici_tipi = None
if "aday_id" not in st.session_state:
    st.session_state.aday_id = None


# =====================================================================
# GİRİŞ YAPILMAMIŞSA — GİRİŞ SAYFASI
# =====================================================================
if st.session_state.kullanici_tipi is None:
    # Sidebar'ı temizle
    st.sidebar.empty()
    
    # Ana içerik
    st.title("🤖 İK Karar Destek Sistemi")
    st.caption("Yapay Zeka Destekli İşe Alım Platformu")
    
    st.markdown("---")
    
    # Ortalanmış giriş
    col_bos1, col_orta, col_bos2 = st.columns([1, 2, 1])
    
    with col_orta:
        st.markdown("### 👋 Hoş Geldiniz!")
        st.markdown("Lütfen **giriş yapmak istediğiniz** alanı seçin:")
        st.markdown("")
        
        # İK Uzmanı Girişi
        with st.container(border=True):
            st.markdown("#### 👔 İnsan Kaynakları Girişi")
            st.caption("CV havuzu, pozisyon tanımlama, eşleştirme")
            if st.button("🔐 İK Uzmanı Girişi", use_container_width=True,
                          type="primary", key="ik_giris"):
                st.session_state.kullanici_tipi = "ik"
                st.rerun()
        
        st.markdown("")
        
        # Aday Girişi
        with st.container(border=True):
            st.markdown("#### 👤 Aday Girişi")
            st.caption("Profil oluşturma, CV yükleme, başvuru takibi")
            if st.button("👤 Aday Girişi", use_container_width=True,
                          key="aday_giris"):
                st.session_state.kullanici_tipi = "aday"
                st.rerun()
    
    st.markdown("---")
    st.caption("🔒 Hibrit Karar Destek Yaklaşımı — Nihai karar her zaman insana aittir.")
    
    st.stop()


# =====================================================================
# İK UZMANI GİRİŞİ YAPILDIYSA
# =====================================================================
if st.session_state.kullanici_tipi == "ik":
    # Sayfaları tanımla (sadece İK sayfaları)
    ik_sayfalari = [
        st.Page("pages/1_📥_CV_Havuzu.py", title="CV Havuzu", icon="📥"),
        st.Page("pages/2_🎯_Pozisyonlar.py", title="Pozisyonlar", icon="🎯"),
        st.Page("pages/3_🔍_Eşleştirme.py", title="Eşleştirme", icon="🔍"),
    ]
    
    # Navigasyon
    pg = st.navigation(ik_sayfalari, position="sidebar")
    
    # Sidebar'a çıkış butonu ekle
    with st.sidebar:
        st.markdown("---")
        if st.button("🚪 Çıkış Yap", use_container_width=True, key="ik_cikis"):
            st.session_state.kullanici_tipi = None
            st.rerun()
    
    # Aktif sayfayı çalıştır
    pg.run()


# =====================================================================
# ADAY GİRİŞİ YAPILDIYSA
# =====================================================================
elif st.session_state.kullanici_tipi == "aday":
    # Sidebar'a çıkış butonu ekle
    with st.sidebar:
        if st.session_state.aday_id:
            st.success(f"👤 Aday ID: {st.session_state.aday_id}")
        st.markdown("---")
        if st.button("🚪 Çıkış Yap", use_container_width=True, key="aday_cikis"):
            st.session_state.kullanici_tipi = None
            st.session_state.aday_id = None
            st.rerun()
    
    # Aday girişi yapılmamışsa — Kayıt/Giriş
    if st.session_state.aday_id is None:
        st.title("👤 Aday Portalı")
        st.caption("Profilinizi oluşturun ve CV'nizi yönetin.")
        
        st.markdown("---")
        
        from database import aday_ekle, adaylari_listele
        
        tab1, tab2 = st.tabs(["🆕 Yeni Kayıt", "🔐 Giriş Yap"])
        
        with tab1:
            with st.form("aday_kayit"):
                st.markdown("**Kişisel Bilgiler**")
                
                col1, col2 = st.columns(2)
                with col1:
                    ad_soyad = st.text_input("Ad Soyad *")
                    email = st.text_input("Email *")
                with col2:
                    telefon = st.text_input("Telefon")
                    sehir = st.text_input("Şehir")
                
                if st.form_submit_button("✅ Kayıt Ol", type="primary",
                                          use_container_width=True):
                    if ad_soyad and email:
                        aday_id = aday_ekle(
                            isim=ad_soyad,
                            email=email,
                            telefon=telefon,
                            cv_metni="",
                            kategori="belirsiz",
                            beceriler=[],
                            kaynak="aday_portali",
                        )
                        st.session_state.aday_id = aday_id
                        st.success(f"✅ Kayıt başarılı! ID: {aday_id}")
                        st.rerun()
                    else:
                        st.error("❌ Ad Soyad ve Email zorunlu!")
        
        with tab2:
            with st.form("aday_giris"):
                giris_email = st.text_input("Email")
                
                if st.form_submit_button("🔐 Giriş Yap", use_container_width=True):
                    if giris_email:
                        tum_adaylar = adaylari_listele(limit=10000)
                        bulunan = [a for a in tum_adaylar if a["email"] == giris_email]
                        
                        if bulunan:
                            st.session_state.aday_id = bulunan[0]["id"]
                            st.success("✅ Giriş başarılı!")
                            st.rerun()
                        else:
                            st.error("❌ Bu email ile kayıt bulunamadı.")
        
        st.stop()
    
    # Aday giriş yapmışsa — Sayfalar
    aday_sayfalari = [
        st.Page("pages/4_👤_Aday_Profili.py", title="Profilim", icon="👤"),
        st.Page("pages/5_📄_Aday_CV.py", title="CV'm", icon="📄"),
    ]
    
    pg = st.navigation(aday_sayfalari, position="sidebar")
    pg.run()