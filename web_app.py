import streamlit as st
import sqlite3
from datetime import date

# Sayfa Yapılandırması
st.set_page_config(
    page_title="Ambalaj & Etiket Takip Sistemi",
    page_icon="📦",
    layout="wide"
)

# --- ÇOKLU KULLANICI VE GÜVENLİK SİSTEMİ ---
# Burada sen ve arkadaşların için kullanıcı adı ve şifreleri belirliyoruz.
# İstediğin gibi kullanıcı ekleyebilir veya şifreleri değiştirebilirsin!
USERS = {
    "erdem": "1234",          # Senin hesabın
    "arkadas1": "ajans55",    # Arkadaşının hesabı
    "arkadas2": "bursa16"     # Diğer arkadaşının hesabı
}

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "current_user" not in st.session_state:
    st.session_state["current_user"] = ""

def check_login(username, password):
    if username in USERS and USERS[username] == password:
        st.session_state["logged_in"] = True
        st.session_state["current_user"] = username
    else:
        st.error("Hatalı Kullanıcı Adı veya Şifre!")

if not st.session_state["logged_in"]:
    st.markdown("""
        <style>
            .main { background-color: #141414; color: #F8F9FA; }
            .stApp { background-color: #141414; }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<h1 style='text-align: center; color: #00B4D8;'>🔒 Güvenli Ekip Girişi</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #A0A0A0;'>Lütfen ekip kullanıcı adınız ve şifrenizle giriş yapın.</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            uname = st.text_input("Kullanıcı Adı")
            pwd = st.text_input("Şifre", type="password")
            submit = st.form_submit_button("Giriş Yap")
            if submit:
                check_login(uname, pwd)
                if st.session_state["logged_in"]:
                    st.rerun()
    st.stop()  # Giriş yapılmadıysa devamını çalıştırma!

# ==========================================================
# GİRİŞ BAŞARILI İSE UYGULAMA AÇILIR
# ==========================================================

st.markdown("""
<style>
    .main { background-color: #141414; color: #F8F9FA; }
    .stApp { background-color: #141414; }
    h1, h2, h3 { color: #00B4D8 !important; }
    .stButton>button {
        background-color: #2A2A2A; color: #F8F9FA;
        border: none; border-radius: 6px; padding: 10px 20px; font-weight: bold;
    }
    .stButton>button:hover { background-color: #00B4D8; color: #000000; }
</style>
""", unsafe_allow_html=True)

# Veritabanı Bağlantısı
DB = "ambalaj_web.db"

def init_db():
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS customers(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT,
        contact TEXT
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS orders(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        product TEXT NOT NULL,
        dimension TEXT,
        material TEXT,
        label_type TEXT,
        quantity INTEGER NOT NULL,
        unit_price REAL,
        total_price REAL,
        delivery_date TEXT,
        status TEXT NOT NULL DEFAULT 'Sipariş Alındı',
        FOREIGN KEY(customer_id) REFERENCES customers(id)
    )""")
    con.commit()
    con.close()

init_db()

# Üst Bilgi ve Çıkış Butonu (Kim giriş yaptı gösterir)
col_head1, col_head2 = st.columns([4, 1])
with col_head1:
    st.markdown(f"""
        <div style='background: linear-gradient(90deg, #0A192F 0%, #00B4D8 100%); padding: 15px; border-radius: 10px; margin-bottom: 20px;'>
            <h2 style='color: white !important; margin: 0;'>BENİM AMBALAJ TAKİP SİSTEMİM</h2>
            <p style='color: #E0E0E0; margin: 0;'>Aktif Kullanıcı: <b>{st.session_state["current_user"].capitalize()}</b></p>
        </div>
    """, unsafe_allow_html=True)

with col_head2:
    if st.button("🔒 Oturumu Kapat"):
        st.session_state["logged_in"] = False
        st.session_state["current_user"] = ""
        st.rerun()

# Sekmeler
tab1, tab2, tab3 = st.tabs(["📋 Siparişler", "➕ Yeni Sipariş / Müşteri", "📊 Durum & Özet"])

with tab1:
    st.subheader("Aktif Sipariş Listesi")
    con = sqlite3.connect(DB)
    orders = con.execute("""SELECT o.id, c.name, o.product, o.dimension, o.material, o.label_type, 
                          o.quantity, o.total_price, o.delivery_date, o.status 
                          FROM orders o JOIN customers c ON c.id = o.customer_id ORDER BY o.id DESC""").fetchall()
    con.close()
    
    if orders:
        for ord in orders:
            st.markdown(f"""
            <div style='background: #222222; padding: 15px; border-radius: 8px; margin-bottom: 10px; border-left: 5px solid #00B4D8;'>
                <b>Sipariş ID:</b> #{ord[0]} | <b>Müşteri:</b> {ord[1]}<br>
                <b>Ürün:</b> {ord[2]} ({ord[3]}) | <b>Malzeme:</b> {ord[4]}<br>
                <b>Adet:</b> {ord[6]} | <b>Toplam Tutar:</b> {ord[7]:,.2f} ₺<br>
                <b>Teslim Tarihi:</b> {ord[8]} | <b style='color: #00B4D8;'>Durum: {ord[9]}</b>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Henüz sisteme girilmiş bir sipariş bulunmuyor.")

with tab2:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 👤 Yeni Müşteri Ekle")
        with st.form("cust_form"):
            c_name = st.text_input("Müşteri / Firma Adı")
            c_phone = st.text_input("Telefon Numarası")
            c_contact = st.text_input("Yetkili Kişi")
            c_submit = st.form_submit_button("Müşteri Kaydet")
            
            if c_submit and c_name:
                con = sqlite3.connect(DB)
                con.execute("INSERT INTO customers(name, phone, contact) VALUES(?,?,?)", (c_name, c_phone, c_contact))
                con.commit()
                con.close()
                st.success(f"'{c_name}' başarıyla eklendi!")
                st.rerun()

    with col2:
        st.markdown("### 📦 Yeni Sipariş Gir")
        con = sqlite3.connect(DB)
        cust_rows = con.execute("SELECT id, name FROM customers ORDER BY name").fetchall()
        con.close()
        
        cust_dict = {f"{r[0]} - {r[1]}": r[0] for r in cust_rows}
        
        with st.form("order_form"):
            selected_cust = st.selectbox("Müşteri Seçin", options=list(cust_dict.keys()) if cust_dict else ["Önce müşteri ekleyin"])
            prod_name = st.text_input("Ürün Adı / Etiket Adı")
            dimension = st.text_input("Ölçü (Örn: 8 oz, 750 cc)")
            material = st.selectbox("Malzeme Türü", ["Kraft Kase", "Bagasse (Şeker Kamışı)", "Karton Bardak", "Plastik Kutu", "Diğer"])
            label_type = st.selectbox("Etiket Tipi", ["Kazınabilir Yapışkanlı", "Kuşe Etiket", "Şeffaf", "Termal Rulo", "Özel Kesim", "Diğer"])
            qty = st.number_input("Miktar (Adet)", min_value=1, value=1000)
            unit_price = st.number_input("Birim Fiyat (TL)", min_value=0.0, value=1.50, step=0.10)
            delivery_date = st.text_input("Teslim Tarihi (Örn: 25.09.2026)")
            
            o_submit = st.form_submit_button("Siparişi Sisteme Kaydet")
            
            if o_submit and cust_dict and prod_name:
                c_id = cust_dict[selected_cust]
                total_price = qty * unit_price
                con = sqlite3.connect(DB)
                con.execute("""INSERT INTO orders(customer_id, product, dimension, material, label_type, quantity, unit_price, total_price, delivery_date)
                               VALUES(?,?,?,?,?,?,?,?,?)""",
                            (c_id, prod_name, dimension, material, label_type, qty, unit_price, total_price, delivery_date))
                con.commit()
                con.close()
                st.success(f"Sipariş eklendi! Toplam Tutar: {total_price:,.2f} ₺")
                st.rerun()

with tab3:
    st.subheader("Üretim ve İstatistik Özeti")
    con = sqlite3.connect(DB)
    total_c = con.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
    total_o = con.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    active_p = con.execute("SELECT COUNT(*) FROM orders WHERE status != 'Teslim Edildi'").fetchone()[0]
    con.close()
    
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Toplam Müşteri", total_c)
    kpi2.metric("Toplam Sipariş", total_o)
    kpi3.metric("Üretimdeki İşler", active_p)
