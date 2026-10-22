"""
Sentetik CV Üretici (Genişletilmiş — 12 CV)
Türkçe karakterlerin (İ, Ş, Ğ, Ü, Ö, Ç) doğru gömülmesi için Arial fontu kullanılır.

Gerekli paket: reportlab
Kurulum: python -m pip install reportlab
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# --- Font Kaydı (Türkçe Karakter Desteği) ---
def font_kaydet():
    """Windows'ta hazır gelen Arial fontunu kaydeder."""
    adaylar = [
        ("C:/Windows/Fonts/arial.ttf", "Arial"),
        ("C:/Windows/Fonts/calibri.ttf", "Calibri"),
        ("C:/Windows/Fonts/segoeui.ttf", "SegoeUI"),
    ]
    for yol, ad in adaylar:
        if os.path.exists(yol):
            try:
                pdfmetrics.registerFont(TTFont(ad, yol))
                print(f"✅ Font yüklendi: {ad} ({yol})")
                return ad
            except Exception as e:
                print(f"⚠️ Font yüklenemedi ({ad}): {e}")
    print("⚠️ Sistem fontu bulunamadı, Helvetica kullanılacak.")
    return "Helvetica"

FONT_ADI = font_kaydet()

# --- Çıktı Klasörü ---
OUTPUT_DIR = "test_cvs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Stiller ---
styles = getSampleStyleSheet()

baslik_stil = ParagraphStyle(
    "Baslik", parent=styles["Heading1"], fontSize=18,
    fontName=FONT_ADI, textColor="#1a1a1a", spaceAfter=6, alignment=TA_LEFT
)
alt_baslik_stil = ParagraphStyle(
    "AltBaslik", parent=styles["Heading2"], fontSize=12,
    fontName=FONT_ADI, textColor="#003366", spaceBefore=10, spaceAfter=4
)
normal_stil = ParagraphStyle(
    "Normal", parent=styles["Normal"], fontSize=10,
    fontName=FONT_ADI, leading=14, spaceAfter=4
)


def cv_olustur(dosya_adi, ad_soyad, iletisim, ozet, deneyimler, egitim, beceriler):
    yol = os.path.join(OUTPUT_DIR, dosya_adi)
    doc = SimpleDocTemplate(
        yol, pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=1.5 * cm, bottomMargin=1.5 * cm
    )
    icerik = []
    icerik.append(Paragraph(ad_soyad, baslik_stil))
    icerik.append(Paragraph(iletisim, normal_stil))
    icerik.append(Spacer(1, 0.4 * cm))
    icerik.append(Paragraph("PROFESYONEL ÖZET", alt_baslik_stil))
    icerik.append(Paragraph(ozet, normal_stil))
    icerik.append(Paragraph("İŞ DENEYİMİ", alt_baslik_stil))
    for d in deneyimler:
        baslik = f"<b>{d['pozisyon']}</b> — {d['sirket']} ({d['tarih']})"
        icerik.append(Paragraph(baslik, normal_stil))
        for gorev in d['gorevler']:
            icerik.append(Paragraph(f"• {gorev}", normal_stil))
    icerik.append(Paragraph("EĞİTİM", alt_baslik_stil))
    icerik.append(Paragraph(egitim, normal_stil))
    icerik.append(Paragraph("BECERİLER", alt_baslik_stil))
    icerik.append(Paragraph(", ".join(beceriler), normal_stil))
    doc.build(icerik)
    print(f"✅ {yol}")


# =====================================================================
# CV 1: Güçlü Junior Python Developer
# =====================================================================
cv_olustur(
    "01_junior_python.pdf",
    "Ahmet Yılmaz",
    "ahmet.yilmaz@email.com | 0532 111 22 33 | İstanbul",
    "3 yıllık Python geliştirme deneyimine sahip, veri analizi ve web geliştirme "
    "konusunda tutkulu bir yazılım geliştiricisiyim. Takım çalışmasına yatkın, "
    "öğrenmeye açık ve problem çözme odaklıyım.",
    [
        {"pozisyon": "Python Developer", "sirket": "TechSoft A.Ş.",
         "tarih": "2022 - 2025",
         "gorevler": [
             "Django ve Flask ile 8+ web uygulaması geliştirdim",
             "PostgreSQL ve MongoDB ile veritabanı tasarımı",
             "RESTful API geliştirme ve entegrasyon",
             "Pandas ve NumPy ile veri analizi projeleri"
         ]},
        {"pozisyon": "Junior Developer", "sirket": "StartUpX",
         "tarih": "2021 - 2022",
         "gorevler": [
             "Python ile otomasyon scriptleri yazdım",
             "Git ve Agile metodolojiler ile takım çalışması"
         ]},
    ],
    "Lisans — Bilgisayar Mühendisliği, İstanbul Teknik Üniversitesi (2017-2021)",
    ["Python", "Django", "Flask", "SQL", "PostgreSQL", "MongoDB",
     "Pandas", "NumPy", "Git", "Agile", "REST API", "Docker"]
)

# =====================================================================
# CV 2: Deneyimli Senior Developer
# =====================================================================
cv_olustur(
    "02_senior_dev.pdf",
    "Zeynep Kaya",
    "zeynep.kaya@email.com | 0533 222 33 44 | Ankara",
    "10 yıllık yazılım geliştirme deneyimine sahip, takım liderliği ve mimari "
    "tasarım konusunda uzmanlaşmış bir kıdemli yazılım mühendisiyim. Büyük ölçekli "
    "projelerde liderlik yapmış, ekipleri yönetmiş ve mentorluk yapmış bir profesyonelim.",
    [
        {"pozisyon": "Senior Software Engineer / Tech Lead", "sirket": "BüyükTeknoloji A.Ş.",
         "tarih": "2018 - 2025",
         "gorevler": [
             "15 kişilik yazılım ekibine liderlik ettim",
             "Mikroservis mimarisi tasarımı (Python, Java)",
             "Yıllık 10M+ kullanıcıya hizmet veren sistemler geliştirdim",
             "CI/CD pipeline kurulumu ve DevOps süreçleri",
             "Junior geliştiricilere mentorluk"
         ]},
        {"pozisyon": "Software Developer", "sirket": "OrtaTeknoloji",
         "tarih": "2015 - 2018",
         "gorevler": [
             "Python ve Java ile kurumsal yazılım geliştirme",
             "Veritabanı optimizasyonu ve analiz"
         ]},
    ],
    "Yüksek Lisans — Yazılım Mühendisliği, ODTÜ (2013-2015)<br/>"
    "Lisans — Bilgisayar Mühendisliği, Bilkent Üniversitesi (2009-2013)",
    ["Python", "Java", "Docker", "Kubernetes", "AWS", "Mikroservis",
     "Liderlik", "Proje Yönetimi", "SQL", "MongoDB", "CI/CD", "Agile"]
)

# =====================================================================
# CV 3: Kariyer Değiştiren (Muhasebe → Yazılım)
# =====================================================================
cv_olustur(
    "03_kariyer_degisimi.pdf",
    "Mehmet Demir",
    "mehmet.demir@email.com | 0534 333 44 55 | İzmir",
    "12 yıllık muhasebe deneyiminden sonra yazılım geliştirmeye geçiş yapıyorum. "
    "Son 1 yıldır Python ve veri analizi öğreniyorum. Analitik düşünme ve problem "
    "çözme becerilerim güçlüdür.",
    [
        {"pozisyon": "Muhasebe Müdürü", "sirket": "Finans A.Ş.",
         "tarih": "2015 - 2024",
         "gorevler": [
             "10 kişilik muhasebe ekibini yönettim",
             "Excel ve SQL ile finansal raporlama",
             "Bütçe analizi ve süreç iyileştirme"
         ]},
        {"pozisyon": "Serbest Yazılım Öğrencisi", "sirket": "Online Kurslar",
         "tarih": "2024 - 2025",
         "gorevler": [
             "Python ile küçük projeler geliştirdim",
             "Pandas ve Matplotlib ile veri analizi",
             "SQL temelleri"
         ]},
    ],
    "Lisans — İşletme, Dokuz Eylül Üniversitesi (2005-2009)",
    ["Python", "Pandas", "SQL", "Excel", "Analiz", "Muhasebe"]
)

# =====================================================================
# CV 4: Yeni Mezun (Düşük Deneyim)
# =====================================================================
cv_olustur(
    "04_yeni_mezun.pdf",
    "Ayşe Şahin",
    "ayse.sahin@email.com | 0535 444 55 66 | Bursa",
    "Bilgisayar mühendisliği yeni mezunu. Staj deneyimim ve kişisel projelerim ile "
    "yazılım geliştirmeye hazırım. Hızlı öğreniyor, takım çalışmasına yatkınım.",
    [
        {"pozisyon": "Stajyer", "sirket": "Yazılım Ltd.",
         "tarih": "2024 (3 ay)",
         "gorevler": [
             "Python ile temel web uygulaması geliştirdim",
             "Kod inceleme ve test süreçlerine katıldım"
         ]},
    ],
    "Lisans — Bilgisayar Mühendisliği, Uludağ Üniversitesi (2020-2024)",
    ["Python", "HTML", "CSS", "JavaScript", "Git"]
)

# =====================================================================
# CV 5: Pazarlama / Satış Uzmanı
# =====================================================================
cv_olustur(
    "05_pazarlama.pdf",
    "Can Öztürk",
    "can.ozturk@email.com | 0536 555 66 77 | İstanbul",
    "5 yıllık dijital pazarlama ve satış deneyimine sahip. Müşteri ilişkileri, "
    "kampanya yönetimi ve veri odaklı pazarlama konularında uzmanım. İletişim "
    "becerilerim güçlüdür.",
    [
        {"pozisyon": "Dijital Pazarlama Uzmanı", "sirket": "Pazarlama Ajansı",
         "tarih": "2020 - 2025",
         "gorevler": [
             "Google Ads ve Meta Ads kampanyaları yönettim",
             "Aylık 100K+ TL reklam bütçesi yönettim",
             "Müşteri ilişkileri ve satış süreçleri",
             "Google Analytics ile raporlama ve analiz"
         ]},
        {"pozisyon": "Satış Temsilcisi", "sirket": "Ticaret A.Ş.",
         "tarih": "2019 - 2020",
         "gorevler": [
             "B2B satış ve müşteri portföyü yönetimi",
             "Aylık satış hedeflerini %120 oranında aştım"
         ]},
    ],
    "Lisans — İşletme, Marmara Üniversitesi (2015-2019)",
    ["Pazarlama", "Satış", "Google Ads", "SEO", "İletişim", "Analiz", "Müşteri İlişkileri"]
)

# =====================================================================
# CV 6: UI/UX Tasarımcı
# =====================================================================
cv_olustur(
    "06_ui_ux_tasarimci.pdf",
    "Elif Arslan",
    "elif.arslan@email.com | 0537 666 77 88 | İstanbul",
    "6 yıllık UI/UX tasarım deneyimine sahip. Kullanıcı odaklı tasarım, "
    "prototipleme ve tasarım sistemi oluşturma konularında uzmanım. "
    "Figma ve Adobe XD ile profesyonel düzeyde çalışıyorum.",
    [
        {"pozisyon": "Senior UI/UX Designer", "sirket": "Dijital Ajans",
         "tarih": "2021 - 2025",
         "gorevler": [
             "30+ mobil ve web uygulaması için UI/UX tasarımı yaptım",
             "Figma ile tasarım sistemi kurdum",
             "Kullanıcı araştırması ve usability testleri yürüttüm",
             "5 kişilik tasarım ekibine mentorluk yaptım"
         ]},
        {"pozisyon": "UI Designer", "sirket": "Startup A.Ş.",
         "tarih": "2019 - 2021",
         "gorevler": [
             "Web ve mobil arayüz tasarımı",
             "Prototipleme ve wireframe çalışmaları",
             "Geliştirici ekibiyle işbirliği"
         ]},
    ],
    "Lisans — Görsel İletişim Tasarımı, Mimar Sinan Üniversitesi (2015-2019)",
    ["UI", "UX", "Figma", "Sketch", "Adobe XD", "Wireframe", "Prototype",
     "Kullanıcı Deneyimi", "Kullanılabilirlik", "Tasarım Sistemi",
     "Photoshop", "Illustrator", "Responsive Design"]
)

# =====================================================================
# CV 7: Finans / Muhasebe Uzmanı
# =====================================================================
cv_olustur(
    "07_finans_uzmani.pdf",
    "Burak Yıldız",
    "burak.yildiz@email.com | 0538 777 88 99 | Ankara",
    "8 yıllık finans ve muhasebe deneyimine sahip. Finansal analiz, bütçeleme "
    "ve vergi mevzuatı konularında uzmanım. SAP FI/CO modülleri ile "
    "profesyonel düzeyde çalışıyorum. SMMM belgesine sahibim.",
    [
        {"pozisyon": "Finans Müdürü", "sirket": "Üretim A.Ş.",
         "tarih": "2019 - 2025",
         "gorevler": [
             "Yıllık 50M TL bütçe yönetimi",
             "Finansal tablolar hazırlama ve analiz",
             "Vergi beyannameleri ve mevzuat takibi",
             "SAP FI/CO modülleri ile muhasebe süreçleri",
             "5 kişilik finans ekibini yönettim"
         ]},
        {"pozisyon": "Muhasebe Uzmanı", "sirket": "Ticaret Ltd.",
         "tarih": "2017 - 2019",
         "gorevler": [
             "Genel muhasebe ve mizan hazırlama",
             "E-fatura ve e-beyanname süreçleri",
             "Mutabakat ve tahsilat takibi"
         ]},
    ],
    "Lisans — İşletme, Ankara Üniversitesi (2013-2017)",
    ["Muhasebe", "Finans", "Finansal Analiz", "Bütçeleme", "Vergi", "KDV",
     "SAP", "SAP FI", "SAP CO", "Excel", "Bilanço", "Gelir Tablosu", "SMMM"]
)

# =====================================================================
# CV 8: Makine Mühendisi
# =====================================================================
cv_olustur(
    "08_makine_muhendisi.pdf",
    "Murat Kılıç",
    "murat.kilic@email.com | 0539 888 99 00 | Bursa",
    "7 yıllık makine mühendisliği deneyimine sahip. Otomotiv sektöründe ürün "
    "geliştirme ve üretim süreçlerinde uzmanım. SolidWorks ve CATIA ile "
    "profesyonel düzeyde tasarım yapıyorum.",
    [
        {"pozisyon": "Kıdemli Makine Mühendisi", "sirket": "Otomotiv A.Ş.",
         "tarih": "2020 - 2025",
         "gorevler": [
             "Otomotiv parçaları tasarımı (SolidWorks, CATIA)",
             "FEM analizi ve prototip geliştirme",
             "Üretim süreç optimizasyonu",
             "Tedarikçi yönetimi ve kalite kontrol",
             "IATF 16949 süreçlerine uyum"
         ]},
        {"pozisyon": "Makine Mühendisi", "sirket": "Makine Ltd.",
         "tarih": "2018 - 2020",
         "gorevler": [
             "Makine tasarımı ve imalat süreçleri",
             "AutoCAD ile teknik resim",
             "CNC üretim takibi"
         ]},
    ],
    "Lisans — Makine Mühendisliği, Uludağ Üniversitesi (2014-2018)",
    ["SolidWorks", "AutoCAD", "CATIA", "FEM", "ANSYS", "CAD", "CAM",
     "CNC", "Üretim", "Kalite Kontrol", "IATF", "ISO 9001", "Ar-Ge"]
)

# =====================================================================
# CV 9: Hemşire / Sağlık Personeli
# =====================================================================
cv_olustur(
    "09_hemsire.pdf",
    "Selin Aydın",
    "selin.aydin@email.com | 0540 999 00 11 | İzmir",
    "9 yıllık hemşirelik deneyimine sahip. Yoğun bakım ve acil servis "
    "alanlarında uzmanlaşmış bir sağlık profesyoneliyim. Hasta bakımı, "
    "tıbbi müdahale ve ekip çalışması konularında deneyimliyim.",
    [
        {"pozisyon": "Yoğun Bakım Hemşiresi", "sirket": "Devlet Hastanesi",
         "tarih": "2019 - 2025",
         "gorevler": [
             "Yoğun bakım hastalarının takibi ve bakımı",
             "Tıbbi müdahaleler ve ilaç uygulamaları",
             "Hasta ve hasta yakınları ile iletişim",
             "Enfeksiyon kontrolü ve sterilizasyon",
             "Vardiyalı çalışma ve kriz yönetimi"
         ]},
        {"pozisyon": "Acil Servis Hemşiresi", "sirket": "Özel Hastane",
         "tarih": "2016 - 2019",
         "gorevler": [
             "Acil müdahale ve triyaj",
             "Hasta kayıt ve takip sistemleri",
             "Doktor ve ekip ile koordinasyon"
         ]},
    ],
    "Lisans — Hemşirelik, Ege Üniversitesi (2012-2016)",
    ["Hemşirelik", "Hasta Bakımı", "Yoğun Bakım", "Acil Servis",
     "Klinik", "Enfeksiyon Kontrolü", "İletişim", "Ekip Çalışması"]
)

# =====================================================================
# CV 10: İngilizce Öğretmeni
# =====================================================================
cv_olustur(
    "10_ingilizce_ogretmeni.pdf",
    "Deniz Koç",
    "deniz.koc@email.com | 0541 000 11 22 | İstanbul",
    "6 yıllık İngilizce öğretmenliği deneyimine sahip. İletişim odaklı öğretim "
    "yöntemleri ve teknoloji destekli eğitim konularında uzmanım. CELTA "
    "sertifikasına sahibim.",
    [
        {"pozisyon": "İngilizce Öğretmeni", "sirket": "Özel Kolej",
         "tarih": "2020 - 2025",
         "gorevler": [
             "9-12. sınıf öğrencilerine İngilizce dersleri",
             "Müfredat geliştirme ve ders planı hazırlama",
             "Ölçme ve değerlendirme süreçleri",
             "Öğrenci velileriyle iletişim",
             "E-learning platformları kullanımı"
         ]},
        {"pozisyon": "İngilizce Öğretmeni", "sirket": "Dil Kursu",
         "tarih": "2019 - 2020",
         "gorevler": [
             "Yetişkin ve çocuk gruplarına İngilizce dersleri",
             "Cambridge sınavları hazırlık"
         ]},
    ],
    "Lisans — İngiliz Dili ve Edebiyatı, Boğaziçi Üniversitesi (2015-2019)<br/>"
    "CELTA Sertifikası (2021)",
    ["İngilizce", "Öğretmenlik", "Pedagoji", "Müfredat", "Ölçme Değerlendirme",
     "E-Learning", "Uzaktan Eğitim", "İletişim", "CELTA"]
)

# =====================================================================
# CV 11: Veri Analisti / Data Scientist
# =====================================================================
cv_olustur(
    "11_veri_analisti.pdf",
    "Ceren Yıldırım",
    "ceren.yildirim@email.com | 0542 111 22 33 | Ankara",
    "5 yıllık veri analizi ve veri bilimi deneyimine sahip. Python, SQL ve "
    "makine öğrenmesi konularında uzmanım. Büyük veri projelerinde çalıştım "
    "ve iş kararlarına yön veren içgörüler üretttim.",
    [
        {"pozisyon": "Senior Veri Analisti", "sirket": "Teknoloji A.Ş.",
         "tarih": "2021 - 2025",
         "gorevler": [
             "Python ve SQL ile büyük veri analizi",
             "Machine learning modelleri geliştirme (scikit-learn)",
             "Tableau ile dashboard ve raporlama",
             "A/B testi tasarımı ve analizi",
             "İş birimlerine veri odaklı öneriler sunma"
         ]},
        {"pozisyon": "Veri Analisti", "sirket": "Danışmanlık Ltd.",
         "tarih": "2019 - 2021",
         "gorevler": [
             "Müşteri verilerinin analizi ve raporlama",
             "Excel ve SQL ile veri işleme",
             "Power BI dashboard geliştirme"
         ]},
    ],
    "Lisans — İstatistik, Hacettepe Üniversitesi (2015-2019)",
    ["Python", "SQL", "Pandas", "NumPy", "Machine Learning", "Scikit-Learn",
     "Tableau", "Power BI", "Excel", "İstatistik", "A/B Testi", "Veri Analizi",
     "Veri Görselleştirme", "R"]
)

# =====================================================================
# CV 12: İK Uzmanı
# =====================================================================
cv_olustur(
    "12_ik_uzmani.pdf",
    "Gizem Şen",
    "gizem.sen@email.com | 0543 222 33 44 | İstanbul",
    "7 yıllık insan kaynakları deneyimine sahip. İşe alım, performans yönetimi "
    "ve çalışan bağlılığı konularında uzmanım. İK süreçlerinin dijitalleşmesi "
    "projelerinde yer aldım.",
    [
        {"pozisyon": "İK Yöneticisi", "sirket": "Holding A.Ş.",
         "tarih": "2020 - 2025",
         "gorevler": [
             "Yıllık 200+ işe alım süreci yönetimi",
             "Performans değerlendirme sistemleri kurma",
             "Çalışan bağlılığı anketleri ve iyileştirme planları",
             "İK süreçlerinin dijitalleşmesi (HRIS)",
             "4 kişilik İK ekibini yönettim"
         ]},
        {"pozisyon": "İK Uzmanı", "sirket": "Teknoloji Ltd.",
         "tarih": "2018 - 2020",
         "gorevler": [
             "İşe alım ve mülakat süreçleri",
             "Oryantasyon programları",
             "Bordro ve özlük işleri"
         ]},
    ],
    "Lisans — İşletme, Marmara Üniversitesi (2014-2018)",
    ["İnsan Kaynakları", "İşe Alım", "Performans Yönetimi",
     "Çalışan Bağlılığı", "Oryantasyon", "Bordro", "HRIS",
     "İletişim", "Liderlik", "Eğitim"]
)

print("\n🎉 12 adet test CV'si başarıyla oluşturuldu!")
print(f"📁 Klasör: {os.path.abspath(OUTPUT_DIR)}")