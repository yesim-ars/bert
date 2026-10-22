"""
Yapay Zeka Destekli İK Karar Destek Sistemi — v3.0
Hibrit Karar Destek Yaklaşımı — Kural Tabanlı + BERT

Bu sürüm:
- PDF/DOCX/TXT CV okuma + Türkçe karakter normalizasyonu
- Kategori bazlı beceri skoru (kural tabanlı)
- ZAMAN AĞIRLIKLI deneyim hesabı
- İLGİLİ DÖNEM analizi
- Pozisyon profili (yazılım/pazarlama/yönetim/...)
- Kademeli kritik beceri kontrolü
- Dil becerisi tespiti
- 🆕 BERT ile KATEGORİ TAHMİNİ
- 🆕 GÜVEN SKORU ve hibrit karar
- 🆕 AKTİF ÖĞRENME (kullanıcı geri bildirimi)
"""

import streamlit as st
import pdfplumber
from docx import Document
import re
import os
import json
from datetime import datetime

# =====================================================================
# SAYFA AYARLARI
# =====================================================================
st.set_page_config(
    page_title="İK Karar Destek Sistemi",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Yapay Zeka Destekli İK Karar Destek Sistemi")
st.caption("Hibrit Karar Destek Yaklaşımı — Kural Tabanlı + BERT")


# =====================================================================
# BERT MODELİNİ YÜKLE (CACHE'Lİ)
# =====================================================================
@st.cache_resource
def bert_modeli_yukle():
    """BERT modelini ve tokenizer'ı yükler (bir kez yüklenir)."""
    try:
        import torch
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        
        model_dir = "models/bert_cv_classifier"
        
        if not os.path.exists(model_dir):
            return None, None, None, None
        
        device = torch.device("cpu")
        tokenizer = AutoTokenizer.from_pretrained(model_dir)
        model = AutoModelForSequenceClassification.from_pretrained(model_dir)
        model.to(device)
        model.eval()
        
        # Kategori listesi
        kategoriler = [
            "egitim", "finans", "gastronomi", "hukuk", "ik",
            "insaat", "lojistik", "medya", "muhendislik", "pazarlama",
            "saglik", "tasarim", "veri", "yazilim", "yonetim",
        ]
        
        return model, tokenizer, device, kategoriler
    except Exception as e:
        st.error(f"BERT modeli yüklenemedi: {e}")
        return None, None, None, None


# BERT modelini yükle
bert_model, bert_tokenizer, bert_device, bert_kategoriler = bert_modeli_yukle()
BERT_HAZIR = bert_model is not None

if BERT_HAZIR:
    st.sidebar.success("🧠 BERT modeli yüklendi")
else:
    st.sidebar.warning("⚠️ BERT modeli yüklenemedi (sadece kural tabanlı çalışır)")


# BERT kategori tahmini
KATEGORI_TR = {
    "egitim": "Eğitim",
    "finans": "Finans",
    "gastronomi": "Gastronomi",
    "hukuk": "Hukuk",
    "ik": "İnsan Kaynakları",
    "insaat": "İnşaat",
    "lojistik": "Lojistik",
    "medya": "Medya",
    "muhendislik": "Mühendislik",
    "pazarlama": "Pazarlama",
    "saglik": "Sağlık",
    "tasarim": "Tasarım",
    "veri": "Veri",
    "yazilim": "Yazılım",
    "yonetim": "Yönetim",
}


def bert_tahmin_et(metin: str):
    """BERT ile kategori tahmini yapar ve tüm olasılıkları döner."""
    if not BERT_HAZIR:
        return None
    
    import torch
    
    encoding = bert_tokenizer(
        metin,
        truncation=True,
        padding="max_length",
        max_length=256,
        return_tensors="pt",
    )
    
    input_ids = encoding["input_ids"].to(bert_device)
    attention_mask = encoding["attention_mask"].to(bert_device)
    
    with torch.no_grad():
        outputs = bert_model(input_ids=input_ids, attention_mask=attention_mask)
        logits = outputs.logits
        probs = torch.softmax(logits, dim=-1)
        tahmin_idx = torch.argmax(probs, dim=-1).item()
        guven = probs[0][tahmin_idx].item()
    
    tahmin_kategori = bert_kategoriler[tahmin_idx]
    olasiliklar = {
        bert_kategoriler[i]: probs[0][i].item()
        for i in range(len(bert_kategoriler))
    }
    
    return {
        "kategori": tahmin_kategori,
        "guven": guven,
        "olasiliklar": olasiliklar,
    }


# =====================================================================
# BECERİ ANAHTAR KELİMELERİ (Kural Tabanlı)
# =====================================================================
BECERI_ANAHTARLARI = {
    "yazılım": [
        "python", "java", "javascript", "typescript", "c++", "c#", "go",
        "ruby", "php", "swift", "kotlin", "rust", "scala",
        "sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch",
        "git", "github", "gitlab", "docker", "kubernetes", "aws", "azure",
        "gcp", "linux", "bash", "django", "flask", "fastapi", "spring",
        "node.js", "express", "react", "angular", "vue", "next.js",
        "rest api", "graphql", "mikroservis", "html", "css", "tailwind",
        "test", "unit test", "ci/cd", "devops", "agile", "scrum",
        "machine learning", "deep learning", "tensorflow", "pytorch",
    ],
    "veri": [
        "pandas", "numpy", "excel", "analiz", "raporlama",
        "matplotlib", "seaborn", "tableau", "power bi", "looker",
        "veri analizi", "veri bilimi", "data science", "istatistik",
        "etl", "veri madenciligi", "big data", "hadoop", "spark",
    ],
    "pazarlama": [
        "pazarlama", "satis", "sales", "marketing",
        "google ads", "meta ads", "facebook ads", "instagram ads",
        "seo", "sem", "sosyal medya", "social media",
        "kampanya", "musteri", "iletisim", "marka", "branding",
        "reklam", "advertising", "icerik", "content",
        "google analytics", "crm", "hubspot", "salesforce",
        "b2b", "b2c", "e-ticaret",
    ],
    "yonetim": [# Liderlik
        "liderlik", "leadership", "takim", "team",
        "takim yonetimi", "ekip yonetimi",
        "mentorluk", "mentoring", "coaching", "kocluk",
        "yonettim", "yonetici", "manager", "direktör", "director",
        "head of", "chief", "cto", "ceo", "cfo", "coo",
        # Proje yönetimi
        "proje yonetimi", "project management", "proje lideri",
        "program yonetimi", "portfolio yonetimi", "pmo",
        "prince2", "pmp", "capm", "pgmp",
        "ms project", "primavera",
        # Metodoloji
        "agile", "scrum", "kanban", "safe", "less", "xp",
        "scrum master", "csm", "psm", "safe agilist",
        "lean", "six sigma", "kaizen", "5s", "kanban",
        "yesil kayis", "kara kayis", "green belt", "black belt",
        # Strateji
        "strateji", "strategic planning", "stratejik planlama",
        "swot", "pestel", "porters", "rekabet analizi",
        "benchmarking", "kpi", "okr", "mbo",
        # Süreç
        "surec iyilestirme", "process improvement",
        "surec yonetimi", "is surecleri", "bpm",
        "degisim yonetimi", "change management",
        "risk yonetimi", "risk management", "ic denetim",
        # Operasyon
        "operasyon yonetimi", "operations",
        "butce", "budget", "butce yonetimi",
        "finansal planlama", "p&l", "kar zarar",
        "maliyet yonetimi", "cost management",
        # İK
        "insan kaynaklari", "ik", "hr", "human resources",
        "ise alim", "recruitment", "talent acquisition",
        "oryantasyon", "onboarding", "egitim", "training",
        "performans yonetimi", "performance management",
        "ucret yonetimi", "calisan bagliligi",
        # İş geliştirme
        "is gelistirme", "business development", "bd",
        "is ortakligi", "partnership", "stratejik ortaklik",
        # Tedarik
        "tedarik zinciri", "supply chain", "lojistik", "logistics",
        "satin alma", "procurement", "purchasing",
        "depo yonetimi", "warehouse management",
        "stok yonetimi", "inventory management",
        # Kalite
        "kalite yonetimi", "quality management",
        "toplam kalite yonetimi", "tqm",
        "iso 9001", "iso 14001", "iso 45001",
        # Karar / iletişim
        "karar verme", "decision making",
        "problem cozme", "problem solving",
        "muzakere", "negotiation", "ikna", "persuasion",
        "sunum", "presentation",
        # Araçlar
        "jira", "asana", "trello", "monday.com",
        "notion", "confluence", "slack", "microsoft teams",
    ],
    "tasarim": [
        "figma", "sketch", "adobe xd", "photoshop", "illustrator",
        "indesign", "after effects", "premiere", "ui", "ux",
        "wireframe", "prototype", "kullanici deneyimi",
        "tasarim sistemi", "responsive design", "tipografi",
        "logo tasarim", "kurumsal kimlik", "ambalaj",
        "motion graphics", "3d modelleme", "animasyon",
    ],
    "finans": [
        # Türkçe
        "finans", "finance", "muhasebe", "accounting",
        "mali musavir", "mali müşavir", "smmm", "cpa", "cfa",
        "vergi", "butce", "budget", "cfo",
        "finansal analiz", "denetim", "audit",
        "hazine", "treasury", "finans muduru", "finans müdürü",
        "muhasebe muduru", "muhasebe müdürü",
        "muhasebe", "genel muhasebe", "finans", "finansal analiz",
        "finansal raporlama", "bilanco", "bilanço",
        "gelir tablosu", "nakit akisi", "nakit akışı",
        "mizan", "yevmiye", "defter", "fatura", "e-fatura",
        "mutabakat", "tahsilat", "odeme", "ödeme",
        "bordro", "ozluk", "özlük",
        "vergi", "kdv", "kurumlar vergisi", "gelir vergisi",
        "vergi beyannamesi", "e-beyanname", "vergi mevzuati",
        "butceleme", "bütçeleme", "maliyet analizi",
        "kar analizi", "kâr analizi", "basabas noktasi",
        "fiyatlandirma", "finansal modelleme",
        "denetim", "ic denetim", "iç denetim", "dis denetim",
        "uyum", "compliance",
        "bankacilik", "kredi", "kredi analizi", "sigorta",
        "portfoy yonetimi", "portföy yönetimi",
        "hazine", "risk analizi", "yatirim analizi",
        "sigorta", "sigorta uzmani", "sigorta uzmanı",
        "sigortacilik", "sigortacılık", "aktüer", "aktuerya",
        "kredi analisti", "kredi uzmani", "kredi uzmanı",
        "portfoy yoneticisi", "portföy yöneticisi",
        "yatirim danismani", "yatırım danışmanı",
        "finansal analist", "mali analist", "mali musavir",
        # İngilizce
        "finance", "accounting", "financial analysis",
        "financial reporting", "balance sheet", "income statement",
        "cash flow", "budgeting", "cost analysis",
        "financial modeling", "dcf", "npv", "irr",
        "audit", "internal audit", "external audit",
        "treasury", "risk analysis", "investment analysis",
        "ifrs", "tfrs", "gaap", "sox", "spk",
        "m&a", "mergers & acquisitions",
        # Araçlar
        "sap", "sap fi", "sap co", "oracle erp",
        "logo", "mikro", "netsis", "eta", "uyumsoft",
        "quickbooks", "xero", "zoho books",
        "excel", "ileri excel", "vba", "power bi",
    ],
    "muhendislik": [
        "solidworks", "autocad", "catia", "inventor", "fusion 360",
        "ansys", "matlab", "cad", "cam", "cnc", "fem",
        "uretim", "imalat", "kalite kontrol", "iso 9001",
        "iatf", "ar-ge", "prototip", "plc", "scada", "otomasyon",
    ],
    "muhendislik": [
        "metalurji muhendisi", "metalurji mühendisi", "metalurji",
        "malzeme muhendisi", "malzeme mühendisi", "malzeme",
        "maden muhendisi", "maden mühendisi",
        "jeoloji muhendisi", "jeoloji mühendisi",
        "petrol muhendisi", "petrol mühendisi",
        "havacilik muhendisi", "havacılık mühendisi",
        "uzay muhendisi", "uzay mühendisi",
        "biyomedikal muhendisi", "biyomedikal mühendisi",
        "cevre muhendisi", "çevre mühendisi",
        "proses muhendisi", "proses mühendisi",
        "tasarim muhendisi", "tasarım mühendisi",
        "uretim muhendisi", "üretim mühendisi",
        "kalite muhendisi", "kalite mühendisi",
        "arge muhendisi", "ar-ge mühendisi",
        "proje muhendisi", "proje mühendisi",
    ],
    "saglik": [
        "hemsirelik", "hasta bakimi", "yogun bakim", "acil servis",
        "klinik", "hastane", "enfeksiyon kontrolu", "sterilizasyon",
        "triyaj", "ilac uygulama", "vital bulgular",
        "ameliyathane", "anestezi", "pediatri", "kardiyoloji",
        "eczacilik", "fizyoterapi", "diyetisyen", "psikoloji",
    ],
    "egitim": [
        # Türkçe
        "ogretmenlik", "öğretmenlik", "egitmenlik", "eğitmenlik",
        "pedagoji", "pedagojik formasyon", "andragoloji",
        "mufredat", "müfredat", "curriculum",
        "ders plani", "ders planı", "lesson plan",
        "sinif yonetimi", "sınıf yönetimi",
        "olcme degerlendirme", "ölçme değerlendirme",
        "sinav hazirlama", "sınav hazırlama",
        "uzaktan egitim", "uzaktan eğitim",
        "online egitim", "online eğitim",
        "rehberlik", "ozel egitim", "özel eğitim",
        "okul oncesi", "okul öncesi",
        "kurumsal egitim", "hizmet ici egitim",
        "seminer", "workshop", "atolye",
        "stem", "steam", "kodlama egitimi",
        "matematik", "fizik", "kimya", "biyoloji",
        "turkce", "edebiyat", "tarih", "cografya",
        "ingilizce ogretmeni", "fen bilgisi",
        "sosyal bilgiler", "gorsel sanatlar",
        "beden egitimi", "muzik",
        # İngilizce
        "teaching", "teacher", "instructor", "trainer",
        "e-learning", "elearning", "distance learning",
        "online education", "instructional design",
        "assessment", "evaluation",
        "lms", "moodle", "canvas lms", "blackboard",
        "edmodo", "scorm", "xapi",
        "google classroom", "microsoft teams for education",
        "edtech", "education technology",
        "adult education", "corporate training",
        # Sertifikalar
        "celta", "delta", "tesol", "tefl",
    ],
    "ik": [
        # Türkçe
        "insan kaynaklari", "ik", "ise alim", "işe alım",
        "performans yonetimi", "performans yönetimi",
        "oryantasyon", "bordro", "ozluk", "özlük",
        "is hukuku", "iş hukuku", "4857", "is kanunu", "iş kanunu",
        "calisan bagliligi", "çalışan bağlılığı",
        "calisan memnuniyeti", "çalışan memnuniyeti",
        "egitim ve gelisim", "eğitim ve gelişim",
        "kariyer planlama", "ucret yonetimi", "ücret yönetimi",
        "yan haklar", "performans degerlendirme",
        "mentorluk", "coaching", "liderlik",
        # İngilizce
        "hr", "human resources", "recruitment", "recruiter",
        "talent acquisition", "onboarding", "offboarding",
        "payroll", "compensation", "benefits",
        "performance management", "l&d", "training & development",
        "career planning", "employee engagement",
        "employee relations", "change management",
        "candidate assessment", "candidate experience",
        "employer branding", "diversity", "inclusion", "d&i",
        "succession planning", "talent management",
        # Araçlar ve sertifikalar
        "hris", "ats", "workday", "bamboohr", "sap hr", "oracle hcm",
        "linkedin recruiter", "greenhouse", "lever",
        "kariyer.net", "aday havuzu", "aday takip sistemi",
        "people analytics", "hr analytics",
    ],
    "ofis": [
        # Türkçe
        "microsoft office", "ms office", "ofis",
        "word", "excel", "powerpoint", "outlook", "access",
        "google workspace", "google docs", "google sheets",
        "google slides", "google drive",
        "slack", "zoom", "microsoft teams", "skype", "webex",
        "notion", "evernote", "onenote", "confluence",
        "jira", "asana", "trello", "monday.com",
        "dokumantasyon", "raporlama", "sekreterlik",
        "idari isler", "idari işler", "ofis yonetimi",
        "toplanti yonetimi", "takvim yonetimi",
        "yazışma", "evrak yonetimi", "arsiv",
    ],
    "dil": [
        "ingilizce", "english", "almanca", "german", "fransizca",
        "french", "ispanyolca", "spanish", "rusca", "russian",
        "arapca", "arabic", "cince", "chinese",
    ],
    "hukuk": [
        "hukuk", "avukatlik", "dava", "dava takibi",
        "hukuki danismanlik", "sozlesme", "ticaret hukuku",
        "is hukuku", "ceza hukuku", "aile hukuku",
        "fikri mulkiyet", "patent", "marka tescili",
        "uyum", "compliance", "kvkk", "gdpr",
        "arabuluculuk", "tahkim", "uyap", "mevzuat", "ictihat",
    ],
    "medya": [
        "gazetecilik", "haber yazma", "roportaj",
        "editoryal", "icerik uretimi", "kopya yazarligi",
        "senaryo", "storytelling", "podcast", "yayincilik",
        "video produksiyon", "kamera", "kurgu",
        "adobe premiere", "final cut", "davinci resolve",
        "ses kurgu", "sosyal medya yonetimi", "wordpress", "cms",
    ],
    "lojistik": [# Temel
        "lojistik", "logistics", "tedarik zinciri", "supply chain",
        "satin alma", "procurement", "purchasing",
        "depo yonetimi", "warehouse management", "wms",
        "stok yonetimi", "inventory management",
        "sevkiyat", "shipping", "nakliye",
        "ithalat", "ihracat", "import", "export",
        "gumruk", "customs", "gumruk mevzuati",
        "incoterms", "dis ticaret", "foreign trade",
        # Araçlar
        "erp", "sap mm", "sap sd", "oracle scm",
        "kargo", "kurye", "filo yonetimi",
        "soguk zincir", "cold chain",
        "tehlikeli madde", "adr",
        "tms", "wms",
        # Metrikler
        "verimlilik", "kpi", "surec iyilestirme",
        # Yönetim
        "tedarik zinciri yonetimi", "lojistik yonetimi",
        "tedarik zinciri muduru", "lojistik muduru",
        "depo sorumlusu", "sevkiyat sorumlusu",
        "satin alma muduru", "ithalat ihracat uzmani",
    ],
    "gastronomi": [
        "ascilik", "mutfak", "gastronomi", "culinary",
        "turk mutfagi", "italyan mutfagi", "fransiz mutfagi",
        "pastane", "pasta", "ekmek", "tatli",
        "haccp", "gida guvenligi", "food safety",
        "mutfak yonetimi", "menu planlama", "food cost",
        "servis", "restoran yonetimi", "barista", "kahve",
        "kokteyl", "miksoloji", "sarap", "ziyafet", "catering",
    ],
    "insaat": [
        "insaat", "civil engineering", "santiye",
        "autocad", "revit", "bim", "sketchup", "archicad",
        "sap2000", "etabs", "sta4cad", "idecad",
        "statik", "betonarme", "celik yapi",
        "geoteknik", "zemin etudu", "temel tasarimi",
        "insaat yonetimi", "construction management",
        "maliyet yonetimi", "metraj", "hakedis",
        "sozlesme yonetimi", "fidic", "kalite kontrol",
        "isg", "is guvenligi", "yapi denetim",
        "kentsel donusum", "yesil bina", "leed",
    ],
}


# =====================================================================
# POZİSYON PROFİLLERİ
# =====================================================================
POZISYON_PROFILLERI = {
    "yazılım": {
        "anahtar_kelimeler": [
            "yazilim", "yazılım", "developer", "software",
            "python", "java", "javascript", "frontend", "backend",
            "fullstack", "programci", "coder",
            "software engineer", "yazilim muhendisi",
            "web developer", "mobile developer",
        ],
        "agirliklar": {"beceri": 0.50, "deneyim": 0.35, "egitim": 0.15},
        "ilgili_kategoriler": ["yazılım", "veri"],
        "ana_kritik": ["python", "java", "javascript", "typescript",
                       "c++", "c#", "go", "ruby", "php"],
        "ikincil_kritik": ["sql", "git", "docker"],
    },
    "pazarlama": {
        "anahtar_kelimeler": [
            "pazarlama", "marketing", "satis", "sales", "reklam",
            "seo", "sosyal medya", "marka", "musteri",
        ],
        "agirliklar": {"beceri": 0.35, "deneyim": 0.45, "egitim": 0.20},
        "ilgili_kategoriler": ["pazarlama", "veri"],
        "ana_kritik": ["pazarlama", "satis", "marketing", "sales"],
        "ikincil_kritik": ["google ads", "seo", "iletisim"],
    },
    "yonetim": {
        "anahtar_kelimeler": [
            "yonetici", "manager", "direktör", "director", "lider",
            "takim lideri", "head of", "chief", "cto", "ceo", "cfo",
            "coo", "chro", "vp", "genel mudur",
            # Yönetim kelimeleri
            "yonetim", "yönetim", "management",
            # Danışmanlık
            "danisman", "danışman", "consultant", "consulting",
            "yonetim danismani", "yönetim danışmanı",
            # Proje / Program
            "proje yoneticisi", "program yoneticisi",
            "portfoy yoneticisi", "pmo",
            "proje lideri", "program lideri",
            # Ürün / Scrum
            "urun yoneticisi", "product manager",
            "urun sahibi", "product owner",
            "scrum master",
            # Operasyon
            "operasyon muduru", "operasyon direktoru",
            "is gelistirme", "business development",
            # Strateji
            "strateji muduru", "strateji direktoru",
            "stratejik planlama",
            # Süreç
            "surec iyilestirme", "lean uzmani",
            "six sigma uzmani",
        ],
        "agirliklar": {"beceri": 0.25, "deneyim": 0.55, "egitim": 0.20},
        "ilgili_kategoriler": ["yonetim", "pazarlama", "yazılım"],
        "ana_kritik": [# Liderlik
                    "liderlik", "leadership", "yonettim", "yonetici",
                    "manager", "takim yonetimi", "ekip yonetimi", 
                    # Strateji
                    "strateji", "stratejik planlama", "swot", "pestel",
                    # Süreç
                    "proje yonetimi", "surec iyilestirme", "lean",
                    "six sigma", "kaizen", "degisim yonetimi",
                    # Karar
                    "karar verme", "problem cozme", "muzakere", "ikna",
                    # Performans
                    "kpi", "okr", "performans yonetimi", "hedef yonetimi",
                    # Operasyon
                    "operasyon yonetimi", "butce yonetimi", "finansal planlama",
                    # Metodoloji
                    "agile", "scrum", "kanban", "pmp", "prince2",],
        "ikincil_kritik": ["proje yonetimi", "strateji", "mentorluk"],
    },
    "muhendislik": {
        "anahtar_kelimeler": [
            "makine muhendisi", "elektrik muhendisi", "elektronik muhendisi",
            "endustri muhendisi", "insaat muhendisi", "otomotiv muhendisi",
            "kimya muhendisi", "gida muhendisi", "ziraat muhendisi",
            "mechanical engineer", "electrical engineer",
        ],
        "agirliklar": {"beceri": 0.50, "deneyim": 0.35, "egitim": 0.15},
        "ilgili_kategoriler": ["muhendislik", "veri"],
        "ana_kritik": [# Genel mühendislik
                    "solidworks", "autocad", "catia", "ansys",
                    "cad", "cam", "fem", "matlab", "simulink",
                    # Metalurji & Malzeme
                    "metalurji", "malzeme", "metal", "aluminyum", "celik",
                    # Üretim
                    "uretim", "imalat", "iso 9001", "iatf", "kalite kontrol",
                    # Otomasyon
                    "plc", "scada", "otomasyon", "hmi",
                    # Diğer
                    "iso 14001", "iso 45001", "arge", "prototip",],
        "ikincil_kritik": ["cnc", "iso 9001", "ar-ge", "uretim"],
    },
    "tasarim": {
        "anahtar_kelimeler": [
            "tasarim", "tasarım", "design", "ui", "ux", "ui/ux",
            "grafik tasarim", "görsel tasarım", "figma",
            "ui designer", "ux designer", "product designer",
        ],
        "agirliklar": {"beceri": 0.55, "deneyim": 0.30, "egitim": 0.15},
        "ilgili_kategoriler": ["tasarim", "yazılım", "pazarlama"],
        "ana_kritik": ["figma", "sketch", "adobe xd", "photoshop",
                       "illustrator", "ui", "ux", "tasarim"],
        "ikincil_kritik": ["kullanici deneyimi", "prototype", "wireframe"],
    },
    "finans": {
        "anahtar_kelimeler": [
            "finans", "finance", "muhasebe", "accounting",
            "mali musavir", "smmm", "cpa", "cfa", "vergi",
            "butce", "cfo", "denetim", "audit",
        ],
        "agirliklar": {"beceri": 0.40, "deneyim": 0.45, "egitim": 0.15},
        "ilgili_kategoriler": ["finans", "veri","ofis"],
        "ana_kritik": [
            # Muhasebe odaklı
            "muhasebe", "finans", "vergi", "butce",
            "smmm", "cpa", "finansal analiz", "bilanço",
            "gelir tablosu", "kdv",
            # Sigorta & Kredi
            "sigorta", "sigortacilik", "kredi", "kredi analizi",
            "kredi analisti", "risk analizi", "bankacilik",
            "portfoy yonetimi", "hazine",
            # Denetim & Uyum
            "denetim", "ic denetim", "dis denetim", "uyum",
            "ifrs", "tfrs", "sox", "spk", "gaap",
            # Yatırım
            "yatirim analizi", "finansal modelleme", "dcf", "npv", "irr",
            # Araçlar
            "excel", "sap", "erp", "vba",
        ],
        "ikincil_kritik": ["sap", "erp", "excel"],
    },
    "saglik": {
        "anahtar_kelimeler": [
            "saglik", "sağlık", "hemsire", "hemşire", "hemsirelik",
            "hemşirelik", "nurse", "doktor", "doctor",
            "klinik", "hastane", "eczaci", "fizyoterapist",
        ],
        "agirliklar": {"beceri": 0.40, "deneyim": 0.45, "egitim": 0.15},
        "ilgili_kategoriler": ["saglik", "ofis"],
        "ana_kritik": ["hemsirelik", "hasta bakimi", "klinik",
                       "hastane", "acil servis", "yogun bakim"],
        "ikincil_kritik": ["enfeksiyon kontrolu", "triyaj"],
    },
    "egitim": {
        "anahtar_kelimeler": [
            "ogretmen", "öğretmen", "ogretmenlik", "öğretmenlik",
            "teacher", "egitmen", "eğitmen", "instructor",
            "egitim", "eğitim", "pedagoji",
        ],
        "agirliklar": {"beceri": 0.35, "deneyim": 0.40, "egitim": 0.25},
        "ilgili_kategoriler": ["egitim", "dil"],
        "ana_kritik": ["ogretmenlik", "pedagoji", "mufredat", "egitim",
                    "e-learning", "celta", "tesol", "tefl",
                    "sinav hazirlama", "rehberlik", "okul oncesi",
                    "stem", "steam", "kodlama egitimi",
                    "fizik", "kimya", "biyoloji", "matematik",
                    "turkce", "edebiyat", "tarih", "cografya",
                    "fen bilgisi", "sosyal bilgiler",],
        "ikincil_kritik": ["uzaktan egitim", "lms", "sinif yonetimi"],
    },
    "ik": {
        "anahtar_kelimeler": [
            "insan kaynaklari", "ik uzmani", "ik yoneticisi",
            "hr", "human resources", "recruitment",
            "ise alim", "işe alım",
        ],
        "agirliklar": {"beceri": 0.40, "deneyim": 0.40, "egitim": 0.20},
        "ilgili_kategoriler": ["ik", "yonetim"],
        "ana_kritik": ["insan kaynaklari", "ise alim", "recruitment",
                       "performans yonetimi", "oryantasyon"],
        "ikincil_kritik": ["hris", "bordro", "ozluk"],
    },
    "veri": {
        "anahtar_kelimeler": [
            "analist", "iş analisti", "is analisti", "business analyst",
            "sistem analisti", "sistem analyst",
            "ürün analisti", "product analyst",
            "veri analisti", "veri bilimci", "data analyst",
            "data scientist", "data engineer", "bi analyst",
            "business intelligence", "veri muhendisi",
            "veri uzmani", "analytics engineer",
            "raporlama uzmani", "iş zekası", "is zekasi",
        ],
        "agirliklar": {"beceri": 0.45, "deneyim": 0.35, "egitim": 0.20},
        "ilgili_kategoriler": ["veri", "yazılım"],
        "ana_kritik": ["sql", "python", "pandas", "tableau",
                       "power bi", "excel", "veri analizi"],
        "ikincil_kritik": ["numpy", "matplotlib", "istatistik",
                            "machine learning"],
    },
    "hukuk": {
        "anahtar_kelimeler": [
            "hukuk", "avukat", "hukuk musaviri", "hukuk danismani",
            "legal", "lawyer", "attorney", "hukukcu",
        ],
        "agirliklar": {"beceri": 0.40, "deneyim": 0.40, "egitim": 0.20},
        "ilgili_kategoriler": ["hukuk", "ofis"],
        "ana_kritik": ["hukuk", "avukatlik", "dava", "sozlesme",
                       "ticaret hukuku", "is hukuku"],
        "ikincil_kritik": ["uyap", "mevzuat", "compliance", "kvkk"],
    },
    "medya": {
        "anahtar_kelimeler": [
            "gazeteci", "muhabir", "editor", "yazar",
            "icerik ureticisi", "content creator", "youtuber",
            "podcast", "sunucu", "spiker", "senarist",
            "medya", "media", "journalist",
        ],
        "agirliklar": {"beceri": 0.50, "deneyim": 0.35, "egitim": 0.15},
        "ilgili_kategoriler": ["medya", "pazarlama"],
        "ana_kritik": ["gazetecilik", "haber yazma", "icerik uretimi",
                       "kopya yazarligi", "editoryal", "senaryo"],
        "ikincil_kritik": ["podcast", "video produksiyon",
                            "sosyal medya yonetimi"],
    },
    "lojistik": {
        "anahtar_kelimeler": [
            "lojistik", "tedarik zinciri", "supply chain",
            "depo", "sevkiyat", "ithalat", "ihracat",
            "gumruk", "kargo", "nakliye", "filo",
            "logistics", "warehouse",
        ],
        "agirliklar": {"beceri": 0.45, "deneyim": 0.40, "egitim": 0.15},
        "ilgili_kategoriler": ["lojistik", "veri"],
        "ana_kritik": ["lojistik", "tedarik zinciri", "satin alma",
                       "depo yonetimi", "sevkiyat", "ithalat", "ihracat"],
        "ikincil_kritik": ["erp", "sap", "wms", "incoterms"],
    },
    "gastronomi": {
        "anahtar_kelimeler": [
            "asci", "bas asci", "chef", "pastane", "gastronomi",
            "mutfak", "restoran", "garson", "barista", "barmen",
            "catering", "yemek",
        ],
        "agirliklar": {"beceri": 0.50, "deneyim": 0.35, "egitim": 0.15},
        "ilgili_kategoriler": ["gastronomi", "ofis"],
        "ana_kritik": ["ascilik", "mutfak", "gastronomi",
                       "pastane", "haccp", "gida guvenligi"],
        "ikincil_kritik": ["menu planlama", "food cost",
                            "restoran yonetimi"],
    },
    "insaat": {
        "anahtar_kelimeler": [
            "insaat muhendisi", "santiye", "mimar", "ic mimar",
            "peyzaj", "sehir plancisi", "harita",
            "yapi denetim", "insaat", "construction",
        ],
        "agirliklar": {"beceri": 0.50, "deneyim": 0.35, "egitim": 0.15},
        "ilgili_kategoriler": ["insaat", "muhendislik"],
        "ana_kritik": ["insaat", "autocad", "revit", "bim",
                       "statik", "betonarme", "santiye"],
        "ikincil_kritik": ["sap2000", "etabs", "metraj",
                            "hakedis", "isg"],
    },
    "genel": {
        "anahtar_kelimeler": [],
        "agirliklar": {"beceri": 0.40, "deneyim": 0.35, "egitim": 0.25},
        "ilgili_kategoriler": ["yazılım", "veri", "pazarlama", "yonetim"],
        "ana_kritik": [],
        "ikincil_kritik": [],
        "ozel_durum": "genel",
    },
}


# =====================================================================
# TÜRKÇE KARAKTER NORMALİZASYONU
# =====================================================================
def turkce_normalize(metin: str) -> str:
    ceviriler = str.maketrans({
        "İ": "i", "I": "i", "ı": "i",
        "Ş": "s", "ş": "s", "Ğ": "g", "ğ": "g",
        "Ü": "u", "ü": "u", "Ö": "o", "ö": "o",
        "Ç": "c", "ç": "c", "Â": "a", "â": "a",
    })
    return metin.translate(ceviriler).lower()


def pozisyon_profili_bul(pozisyon: str) -> dict:
    """Pozisyon adına göre hangi profil kullanılacak?
    En spesifikten en gene doğru sıralı kontrol eder.
    """
    poz_lower = turkce_normalize(pozisyon)
    
    # Öncelik sırası: en spesifik → en genel
    oncelik_sirasi = [
        "lojistik", "gastronomi", "saglik", "muhendislik",
        "insaat", "hukuk", "medya", "tasarim", "finans",
        "ik", "egitim", "veri", "yazilim", "pazarlama",
        "yonetim",  # En son — çünkü "yönetici" çok genel
    ]
    
    for profil_adi in oncelik_sirasi:
        if profil_adi == "genel":
            continue
        profil = POZISYON_PROFILLERI.get(profil_adi, {})
        for kw in profil.get("anahtar_kelimeler", []):
            if kw in poz_lower:
                return profil
    
    return POZISYON_PROFILLERI["genel"]


# =====================================================================
# DOSYA OKUMA
# =====================================================================
def read_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += (page.extract_text() or "") + "\n"
    return text


def read_docx(file):
    doc = Document(file)
    return "\n".join([p.text for p in doc.paragraphs])


def extract_text(uploaded_file):
    if uploaded_file.name.endswith(".pdf"):
        return read_pdf(uploaded_file)
    elif uploaded_file.name.endswith(".docx"):
        return read_docx(uploaded_file)
    else:
        return uploaded_file.read().decode("utf-8", errors="ignore")


# =====================================================================
# BECERİ ARAMA
# =====================================================================
def beceri_var_mi(beceri: str, metin: str) -> bool:
    beceri = turkce_normalize(beceri)
    metin = turkce_normalize(metin)
    if len(beceri) <= 4:
        if any(k in beceri for k in ["+", "#", ".", "/", "-"]):
            pattern = r"(?:^|[\s,;:()\[\]])" + re.escape(beceri) + r"(?:$|[\s,;:()\[\]])"
            return bool(re.search(pattern, metin))
        else:
            pattern = r"\b" + re.escape(beceri) + r"\b"
            return bool(re.search(pattern, metin))
    else:
        return beceri in metin


def becerileri_kategorilere_gore_bul(metin_lower: str) -> dict:
    sonuc = {}
    for kategori, beceriler in BECERI_ANAHTARLARI.items():
        bulunanlar = [b for b in beceriler if beceri_var_mi(b, metin_lower)]
        sonuc[kategori] = bulunanlar
    return sonuc


# =====================================================================
# YIL AĞIRLIĞI VE DENEYİM HESABI
# =====================================================================
def yil_agirligi(yil: int, simdiki_yil: int = 2025) -> float:
    yas = simdiki_yil - yil
    if yas <= 3:
        return 1.0
    elif yas <= 6:
        return 0.7
    elif yas <= 10:
        return 0.4
    else:
        return 0.2


def zaman_agirlikli_deneyim(is_deneyimi_metni: str, simdiki_yil: int = 2025) -> dict:
    pattern = r"(20\d{2})\s*[-\u2010\u2011\u2012\u2013\u2014\u2015–—]\s*(20\d{2}|halen|devam|present)"
    araliklar = re.findall(pattern, is_deneyimi_metni)
    if not araliklar:
        return {"ham_yil": 0, "agirlikli_yil": 0, "detaylar": []}
    toplam_ham = 0
    toplam_agirlikli = 0
    detaylar = []
    for baslangic, bitis in araliklar:
        baslangic_int = int(baslangic)
        bitis_int = int(bitis) if bitis.isdigit() else simdiki_yil
        donem_ham = 0
        donem_agirlikli = 0
        for yil in range(baslangic_int, bitis_int):
            donem_ham += 1
            donem_agirlikli += yil_agirligi(yil, simdiki_yil)
        toplam_ham += donem_ham
        toplam_agirlikli += donem_agirlikli
        detaylar.append({
            "tarih": f"{baslangic_int}-{bitis_int}",
            "ham_yil": donem_ham,
            "agirlikli_yil": round(donem_agirlikli, 2),
        })
    return {
        "ham_yil": toplam_ham,
        "agirlikli_yil": round(toplam_agirlikli, 2),
        "detaylar": detaylar,
    }


def ilgili_deneyim_hesapla(is_deneyimi_metni: str, ilgili_kategoriler: list,
                            ana_kritik: list, simdiki_yil: int = 2025) -> dict:
    pattern = r"(20\d{2})\s*[-\u2010\u2011\u2012\u2013\u2014\u2015–—]\s*(20\d{2}|halen|devam|present)"
    matches = list(re.finditer(pattern, is_deneyimi_metni))
    if not matches:
        return {"ilgili_ham_yil": 0, "ilgili_agirlikli_yil": 0, "bloklar": []}
    ilgili_ham = 0
    ilgili_agirlikli = 0
    bloklar = []
    for i, match in enumerate(matches):
        geri_baslangic = max(0, match.start() - 200)
        if i + 1 < len(matches):
            bitis_konum = matches[i + 1].start()
        else:
            bitis_konum = len(is_deneyimi_metni)
        blok_metni = is_deneyimi_metni[geri_baslangic:bitis_konum]
        ilgili_beceri_sayisi = 0
        for kategori in ilgili_kategoriler:
            for beceri in BECERI_ANAHTARLARI[kategori]:
                if beceri_var_mi(beceri, blok_metni):
                    ilgili_beceri_sayisi += 1
        baslangic_int = int(match.group(1))
        bitis_str = match.group(2)
        bitis_int = int(bitis_str) if bitis_str.isdigit() else simdiki_yil
        blok_ham = 0
        blok_agirlikli = 0
        for yil in range(baslangic_int, bitis_int):
            blok_ham += 1
            blok_agirlikli += yil_agirligi(yil, simdiki_yil)
        ana_kritik_var = any(beceri_var_mi(k, blok_metni) for k in ana_kritik)
        ilgili_mi = ana_kritik_var or ilgili_beceri_sayisi >= 5
        if ilgili_mi:
            ilgili_ham += blok_ham
            ilgili_agirlikli += blok_agirlikli
        bloklar.append({
            "tarih": f"{baslangic_int}-{bitis_int}",
            "ham_yil": blok_ham,
            "agirlikli_yil": round(blok_agirlikli, 2),
            "ilgili_mi": ilgili_mi,
            "ilgili_beceri_sayisi": ilgili_beceri_sayisi,
        })
    return {
        "ilgili_ham_yil": ilgili_ham,
        "ilgili_agirlikli_yil": round(ilgili_agirlikli, 2),
        "bloklar": bloklar,
    }


# =====================================================================
# CV ANALİZ FONKSİYONU (v3.0 — BERT Entegre)
# =====================================================================
def cv_analiz(metin: str, pozisyon: str):
    metin_lower = turkce_normalize(metin)
    profil = pozisyon_profili_bul(pozisyon)
    ilgili_kategoriler = profil["ilgili_kategoriler"]
    agirliklar = profil["agirliklar"]
    
    # --- 1) BECERİ ANALİZİ ---
    kategori_becerileri = becerileri_kategorilere_gore_bul(metin_lower)
    tum_beceriler = []
    ilgili_beceriler = []
    for kategori, beceriler in kategori_becerileri.items():
        if kategori == "dil":
            continue
        for b in beceriler:
            tum_beceriler.append(b)
            if kategori in ilgili_kategoriler:
                ilgili_beceriler.append(b)
    beceri_skoru = min(len(ilgili_beceriler) * 12 + len(tum_beceriler) * 2, 100)
    
    # --- 2) İŞ DENEYİMİ METNİNİ ÇIKAR ---
    satirlar = metin_lower.split("\n")
    is_baslangic_satir = -1
    is_bitis_satir = len(satirlar)
    basliklar_is = ["iş deneyimi", "is deneyimi", "deneyim",
                    "work experience", "experience", "iş tecrübesi"]
    for i, satir in enumerate(satirlar):
        if satir.strip() in basliklar_is:
            is_baslangic_satir = i
            break
    basliklar_egitim = ["eğitim", "egitim", "education",
                        "beceriler", "beceri", "skills"]
    if is_baslangic_satir != -1:
        for i in range(is_baslangic_satir + 1, len(satirlar)):
            if satirlar[i].strip() in basliklar_egitim:
                is_bitis_satir = i
                break
    if is_baslangic_satir != -1:
        is_deneyimi_metni = "\n".join(satirlar[is_baslangic_satir:is_bitis_satir])
    else:
        is_deneyimi_metni = metin_lower
    
    # --- 3) ZAMAN AĞIRLIKLI DENEYİM ---
    zaman_analizi = zaman_agirlikli_deneyim(is_deneyimi_metni)
    ilgili_analiz = ilgili_deneyim_hesapla(
        is_deneyimi_metni, ilgili_kategoriler,
        profil.get("ana_kritik", [])
    )
    ham_toplam_yil = zaman_analizi["ham_yil"]
    agirlikli_toplam_yil = zaman_analizi["agirlikli_yil"]
    ilgili_ham_yil = ilgili_analiz["ilgili_ham_yil"]
    ilgili_agirlikli_yil = ilgili_analiz["ilgili_agirlikli_yil"]
    
    yil_match = re.findall(r"(\d+)\s*(?:yil|yillik|yildir|year)", metin_lower)
    if yil_match:
        ham_toplam_yil = max(ham_toplam_yil, max(int(y) for y in yil_match))
    
    ay_match = re.findall(r"(\d+)\s*(?:ay|month)", is_deneyimi_metni)
    staj_yil = 0
    if ay_match and ham_toplam_yil == 0:
        toplam_ay = sum(int(a) for a in ay_match)
        staj_yil = round(toplam_ay / 12, 1)
    
    if ilgili_agirlikli_yil > 0:
        deneyim_yili = ilgili_agirlikli_yil
    elif agirlikli_toplam_yil > 0:
        deneyim_yili = agirlikli_toplam_yil
    elif staj_yil > 0:
        deneyim_yili = staj_yil
    else:
        deneyim_yili = ham_toplam_yil
    
    deneyim_yil_skoru = min(deneyim_yili / 10, 1.0) * 100
    
    ilgili_beceri_sayisi_is = 0
    for kategori in ilgili_kategoriler:
        for beceri in BECERI_ANAHTARLARI[kategori]:
            if beceri_var_mi(beceri, is_deneyimi_metni):
                ilgili_beceri_sayisi_is += 1
    
        if ilgili_beceri_sayisi_is == 0:
            deneyim_alaka_carpani = 0.20
        elif ilgili_beceri_sayisi_is <= 2:
            deneyim_alaka_carpani = 0.50
        elif ilgili_beceri_sayisi_is <= 4:
            deneyim_alaka_carpani = 0.80
        elif ilgili_beceri_sayisi_is <= 8:
            deneyim_alaka_carpani = 0.90 
        else:
            deneyim_alaka_carpani = 1.00
    
    deneyim_skoru = deneyim_yil_skoru * deneyim_alaka_carpani
    
    # --- 4) EĞİTİM SKORU ---
    egitim_seviyesi = 0
    if any(x in metin_lower for x in ["doktora", "phd"]):
        egitim_seviyesi = 100
    elif any(x in metin_lower for x in ["yuksek lisans", "master", "msc"]):
        egitim_seviyesi = 80
    elif any(x in metin_lower for x in ["lisans", "bachelor", "universite"]):
        egitim_seviyesi = 60
    elif any(x in metin_lower for x in ["on lisans", "lise"]):
        egitim_seviyesi = 40
    
    # --- 5) DİL BECERİLERİ ---
    dil_becerileri = kategori_becerileri.get("dil", [])
    
    # --- 6) KRİTİK BECERİ KONTROLÜ ---
    ana_kritik = profil.get("ana_kritik", [])
    ikincil_kritik = profil.get("ikincil_kritik", [])
    ana_kritik_mevcut = [k for k in ana_kritik if beceri_var_mi(k, metin_lower)]
    ana_kritik_eksik = len(ana_kritik) > 0 and len(ana_kritik_mevcut) == 0
    ikincil_kritik_eksik = [k for k in ikincil_kritik
                            if not beceri_var_mi(k, metin_lower)]
    
    # --- 7) GENEL SKOR ---
    genel_skor = (
        beceri_skoru * agirliklar["beceri"] +
        deneyim_skoru * agirliklar["deneyim"] +
        egitim_seviyesi * agirliklar["egitim"]
    )
    
    profil_adi = next(
        (k for k, v in POZISYON_PROFILLERI.items() if v is profil),
        "genel"
    )
    
    # --- 8) 🆕 BERT TAHMİNİ ---
    bert_sonuc = bert_tahmin_et(metin)
    
    return {
        "beceri_skoru": round(beceri_skoru, 1),
        "deneyim_yili": round(deneyim_yili, 1),
        "ham_deneyim_yili": ham_toplam_yil,
        "agirlikli_deneyim_yili": agirlikli_toplam_yil,
        "ilgili_ham_yil": ilgili_ham_yil,
        "ilgili_agirlikli_yil": ilgili_agirlikli_yil,
        "staj_yil": staj_yil,
        "deneyim_yil_skoru": round(deneyim_yil_skoru, 1),
        "deneyim_alaka_carpani": deneyim_alaka_carpani,
        "deneyim_skoru": round(deneyim_skoru, 1),
        "egitim_skoru": egitim_seviyesi,
        "genel_skor": round(genel_skor, 1),
        "bulunan_beceriler": tum_beceriler,
        "ilgili_beceriler": ilgili_beceriler,
        "dil_becerileri": dil_becerileri,
        "ana_kritik_eksik": ana_kritik_eksik,
        "ana_kritik_liste": ana_kritik,
        "ikincil_kritik_eksik": ikincil_kritik_eksik,
        "ilgili_bloklar": ilgili_analiz["bloklar"],
        "profil_adi": profil_adi,
        "agirliklar": agirliklar,
        "bert": bert_sonuc,  # 🆕
    }


# =====================================================================
# ARAYÜZ
# =====================================================================
st.sidebar.header("📄 Aday CV Yükle")
uploaded_file = st.sidebar.file_uploader(
    "PDF, DOCX veya TXT dosyası seçin",
    type=["pdf", "docx", "txt"]
)

pozisyon = st.sidebar.text_input(
    "Pozisyon Adı",
    placeholder="Örn: Junior Python Developer"
)

if uploaded_file and pozisyon:
    metin = extract_text(uploaded_file)
    
    with st.expander("📝 Çıkarılan Metni Gör"):
        st.text(metin[:3000] + ("..." if len(metin) > 3000 else ""))
    
    sonuc = cv_analiz(metin, pozisyon)
    
    st.subheader(f"📊 Analiz Sonucu — {pozisyon}")
    ag = sonuc["agirliklar"]
    st.caption(
        f"🎯 Pozisyon profili: **{sonuc['profil_adi']}** — "
        f"Beceri %{int(ag['beceri']*100)}, "
        f"Deneyim %{int(ag['deneyim']*100)}, "
        f"Eğitim %{int(ag['egitim']*100)}"
    )
    
    # ================================================================
    # 🆕 BERT TAHMİN BÖLÜMÜ (EN ÜSTTE)
    # ================================================================
    if sonuc["bert"]:
        bert = sonuc["bert"]
        with st.container():
            st.markdown("### 🧠 BERT Yapay Zeka Tahmini")
            col_b1, col_b2, col_b3 = st.columns([2, 1, 1])
            
            with col_b1:
                st.markdown(
                    f"**Tahmin edilen kategori:** "
                    f"**{KATEGORI_TR[bert['kategori']]}**"
                )
                st.markdown(
                    f"**Pozisyon profili:** "
                    f"**{KATEGORI_TR.get(sonuc['profil_adi'], sonuc['profil_adi'])}**"
                )
            
            with col_b2:
                st.metric(
                    "BERT Güveni",
                    f"%{bert['guven']*100:.1f}"
                )
            
            with col_b3:
                # Normalize ederek karşılaştır (Türkçe karakter farkı olmasın)
                bert_kat_norm = turkce_normalize(bert["kategori"])
                profil_adi_norm = turkce_normalize(sonuc["profil_adi"])
                uyum = "✅ Uyumlu" if bert_kat_norm == profil_adi_norm else "⚠️ Farklı"
                st.metric("Uyum", uyum)
            
            # Tüm olasılıkları göster
            with st.expander("📊 BERT'in tüm olasılıkları"):
                sirali = sorted(
                    bert["olasiliklar"].items(),
                    key=lambda x: -x[1]
                )
                for kat, olas in sirali:
                    if olas > 0.01:  # %1'den fazla olanları göster
                        bar = "█" * int(olas * 50)
                        st.write(
                            f"`{KATEGORI_TR[kat]:25s}` "
                            f"{bar} %{olas*100:.1f}"
                        )
            
            # Hibrit karar değerlendirmesi
            bert_kat_norm = turkce_normalize(bert["kategori"])
            profil_adi_norm = turkce_normalize(sonuc["profil_adi"])

            if bert_kat_norm == profil_adi_norm:
                if bert["guven"] >= 0.85:
                    st.success(
                        "✅ **BERT ve kural tabanlı sistem UYUMLU.** "
                        "Yüksek güven ile doğrulandı."
                    )
                else:
                    st.info(
                        f"ℹ️ **BERT ve kural tabanlı sistem uyumlu** ancak "
                        f"BERT güveni orta düzeyde (%{bert['guven']*100:.1f}). "
                        f"Detaylı inceleme önerilir."
                    )
            else:
                st.warning(
                    f"⚠️ **BERT ({KATEGORI_TR[bert['kategori']]}) ile "
                    f"pozisyon profili ({KATEGORI_TR.get(sonuc['profil_adi'], sonuc['profil_adi'])}) "
                    f"UYUŞMUYOR.** Bu aday farklı bir alandan olabilir."
                )
        
        st.markdown("---")
    
    # ================================================================
    # KURAL TABANLI METRİKLER
    # ================================================================
    st.markdown("### 📈 Kural Tabanlı Analiz")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Genel Skor", f"{sonuc['genel_skor']}/100")
    col2.metric("Beceri", f"{sonuc['beceri_skoru']}/100")
    col3.metric("Deneyim", f"{sonuc['deneyim_yili']} yıl")
    col4.metric("Eğitim", f"{sonuc['egitim_skoru']}/100")
    
    st.progress(min(sonuc['genel_skor'] / 100, 1.0))
    
    # Deneyim Zaman Analizi
    with st.expander("⏱️ Deneyim Zaman Analizi Detayı"):
        st.markdown(f"**Ham deneyim:** {sonuc['ham_deneyim_yili']} yıl")
        st.markdown(f"**Zaman ağırlıklı deneyim:** {sonuc['agirlikli_deneyim_yili']} yıl")
        if sonuc['staj_yil'] > 0:
            st.markdown(f"**Staj (ay bazlı):** {sonuc['staj_yil']} yıl")
        st.markdown(f"**İlgili pozisyonlardaki ham deneyim:** {sonuc['ilgili_ham_yil']} yıl")
        st.markdown(f"**İlgili pozisyonlardaki ağırlıklı deneyim:** {sonuc['ilgili_agirlikli_yil']} yıl")
        st.markdown(f"**➡️ Efektif deneyim:** {sonuc['deneyim_yili']} yıl")
        
        st.markdown("#### 📋 Pozisyon Blokları")
        if sonuc['ilgili_bloklar']:
            for blok in sonuc['ilgili_bloklar']:
                ikon = "✅" if blok['ilgili_mi'] else "⚠️"
                st.write(
                    f"{ikon} **{blok['tarih']}** — "
                    f"{blok['ham_yil']} yıl (ağırlıklı: {blok['agirlikli_yil']}) — "
                    f"İlgili beceri: {blok['ilgili_beceri_sayisi']}"
                )
        else:
            st.info("Tarih aralığı tespit edilemedi.")
    
    # Deneyim alaka uyarısı
    if sonuc['deneyim_alaka_carpani'] < 1.0:
        st.warning(
            f"⚠️ **Deneyim alaka düzeyi düşük** "
            f"(çarpan: {sonuc['deneyim_alaka_carpani']:.2f})."
        )
    else:
        st.success(
            f"✅ **Deneyim alakalı** "
            f"(çarpan: {sonuc['deneyim_alaka_carpani']:.2f})."
        )
    
    # Kritik beceri uyarıları
    if sonuc['ana_kritik_eksik']:
        st.error(
            f"🚨 **Ana kritik beceri eksikliği:** "
            f"{', '.join(f'`{k}`' for k in sonuc['ana_kritik_liste'])}"
        )
    if sonuc['ikincil_kritik_eksik']:
        st.warning(
            f"⚠️ **Tercih edilen beceriler eksik:** "
            f"{', '.join(f'`{k}`' for k in sonuc['ikincil_kritik_eksik'])}"
        )
    
    # Beceri listesi
    st.markdown("### 🔍 Tespit Edilen Beceriler")
    if sonuc['ilgili_beceriler']:
        st.markdown("**✅ Pozisyonla ilgili beceriler:**")
        st.write(", ".join(f"`{b}`" for b in sonuc['ilgili_beceriler']))
    
    diger = [b for b in sonuc['bulunan_beceriler']
             if b not in sonuc['ilgili_beceriler']]
    if diger:
        st.markdown("**ℹ️ Diğer tespit edilen beceriler:**")
        st.write(", ".join(f"`{b}`" for b in diger))
    
    if sonuc['dil_becerileri']:
        st.markdown("### 🌐 Dil Becerileri")
        st.write(", ".join(f"`{d}`" for d in sonuc['dil_becerileri']))
    
    # ================================================================
    # KARAR DESTEK ÖNERİSİ (Hibrit)
    # ================================================================
        # Karar destek önerisi
    st.markdown("### 💡 Karar Destek Önerisi")
    
    skor = sonuc['genel_skor']
    
    # 🆕 GENEL PROFİL TAVANI: Belirsiz pozisyonlar için skoru sınırla
    if sonuc['profil_adi'] == "genel":
        skor = min(skor, 55)
        st.warning(
            "⚠️ **Bu pozisyon için özel bir profil bulunamadı.** "
            "Pozisyon adı çok genel veya belirsiz. Skor **55 ile sınırlandırıldı**. "
            "Daha spesifik bir pozisyon adı deneyin: "
            "`Veri Analisti`, `Finansal Analist`, `İş Analisti`, "
            "`Pazarlama Analisti` gibi."
        )
    
    if sonuc['ana_kritik_eksik']:
        skor = min(skor, 50)
    elif sonuc['ikincil_kritik_eksik']:
        if skor > 90:
            skor = 90
    
    # BERT uyumsuzsa ceza
    if sonuc["bert"]:
        bert_kat_norm = turkce_normalize(sonuc["bert"]["kategori"])
        profil_norm = turkce_normalize(sonuc["profil_adi"])
        if bert_kat_norm != profil_norm and sonuc["bert"]["guven"] >= 0.60:
            skor = min(skor, 60)
            st.warning(
                f"⚠️ **BERT farklı bir kategori öneriyor** "
                f"({KATEGORI_TR[sonuc['bert']['kategori']]}). "
                f"Skor bu nedenle sınırlandırıldı."
            )
    
    if skor >= 70:
        st.success("✅ **Görüşmeye davet edilmesi önerilir.** (Karar sizin!)")
    elif skor >= 50:
        st.warning("⚠️ **Sınırda aday.** Detaylı inceleme tavsiye edilir.")
    else:
        st.error("❌ **Düşük uyum.** Ancak nihai karar sizin.")
    
    st.info(
        "ℹ️ Bu sistem yalnızca **öneri** sunar. "
        "Nihai işe alım kararı insan tarafından verilmelidir."
    )
    
    # ================================================================
    # 🆕 AKTİF ÖĞRENME — KULLANICI GERİ BİLDİRİMİ
    # ================================================================
    st.markdown("---")
    st.markdown("### 🎓 Bu Analiz Doğru muydu?")
    st.caption("Geri bildiriminiz modeli geliştirmek için kullanılacak.")
    
    geri_bildirim_klasoru = "data/feedback"
    os.makedirs(geri_bildirim_klasoru, exist_ok=True)
    
    col_fb1, col_fb2, col_fb3 = st.columns(3)
    
    with col_fb1:
        if st.button("✅ Doğru", key="fb_dogru"):
            # Geri bildirimi kaydet
            kayit = {
                "tarih": datetime.now().isoformat(),
                "cv_metni": metin[:5000],
                "pozisyon": pozisyon,
                "bert_tahmini": sonuc["bert"]["kategori"] if sonuc["bert"] else None,
                "bert_guveni": sonuc["bert"]["guven"] if sonuc["bert"] else None,
                "kural_profili": sonuc["profil_adi"],
                "genel_skor": sonuc["genel_skor"],
                "geri_bildirim": "dogru",
                "dogru_kategori": sonuc["bert"]["kategori"] if sonuc["bert"] else sonuc["profil_adi"],
            }
            dosya = os.path.join(
                geri_bildirim_klasoru,
                f"fb_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            with open(dosya, "w", encoding="utf-8") as f:
                json.dump(kayit, f, ensure_ascii=False, indent=2)
            st.success("✅ Geri bildiriminiz kaydedildi. Teşekkürler!")
    
    with col_fb2:
        if st.button("❌ Yanlış", key="fb_yanlis"):
            st.session_state["yanlis_geri_bildirim"] = True
    
    with col_fb3:
        if st.button("🤔 Emin Değilim", key="fb_belirsiz"):
            kayit = {
                "tarih": datetime.now().isoformat(),
                "cv_metni": metin[:5000],
                "pozisyon": pozisyon,
                "bert_tahmini": sonuc["bert"]["kategori"] if sonuc["bert"] else None,
                "geri_bildirim": "belirsiz",
            }
            dosya = os.path.join(
                geri_bildirim_klasoru,
                f"fb_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            with open(dosya, "w", encoding="utf-8") as f:
                json.dump(kayit, f, ensure_ascii=False, indent=2)
            st.info("🤔 Geri bildiriminiz kaydedildi. Teşekkürler!")
    
    # Yanlış geri bildirim formu
    if st.session_state.get("yanlis_geri_bildirim", False):
        with st.form("yanlis_form"):
            st.markdown("**Doğru kategori nedir?**")
            dogru_kategori = st.selectbox(
                "Seçin",
                options=list(KATEGORI_TR.keys()),
                format_func=lambda x: KATEGORI_TR[x],
            )
            aciklama = st.text_input("Kısa açıklama (opsiyonel)")
            
            if st.form_submit_button("Gönder"):
                kayit = {
                    "tarih": datetime.now().isoformat(),
                    "cv_metni": metin[:5000],
                    "pozisyon": pozisyon,
                    "bert_tahmini": sonuc["bert"]["kategori"] if sonuc["bert"] else None,
                    "bert_guveni": sonuc["bert"]["guven"] if sonuc["bert"] else None,
                    "kural_profili": sonuc["profil_adi"],
                    "geri_bildirim": "yanlis",
                    "dogru_kategori": dogru_kategori,
                    "aciklama": aciklama,
                }
                dosya = os.path.join(
                    geri_bildirim_klasoru,
                    f"fb_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                )
                with open(dosya, "w", encoding="utf-8") as f:
                    json.dump(kayit, f, ensure_ascii=False, indent=2)
                st.session_state["yanlis_geri_bildirim"] = False
                st.success(f"✅ Teşekkürler! '{KATEGORI_TR[dogru_kategori]}' olarak kaydedildi.")

else:
    st.info("👈 Başlamak için sol panelden bir CV yükleyin ve pozisyon adını girin.")
    
    if BERT_HAZIR:
        st.markdown("---")
        st.markdown("### 🧠 BERT Modeli Hazır")
        st.success(
            f"✅ BERT modeli yüklendi — {len(bert_kategoriler)} kategori tanınıyor."
        )
        st.markdown("**Tanınan kategoriler:**")
        for kat in bert_kategoriler:
            st.write(f"  - {KATEGORI_TR[kat]}")