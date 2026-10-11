import os
from urllib.parse import urlparse

import requests
import streamlit as st

st.set_page_config(
    page_title="ŞAHAN VIP • Birleşik Panel",
    page_icon="⚡",
    layout="wide",
)

st.markdown("""
<style>
    .stApp { background: #090a0d; }
    section[data-testid="stSidebar"] { background: #242630; }
    h1, h2, h3 { color: #e8edf5; }
    div[data-testid="stMetric"] {
        background: #171a22; border: 1px solid #2b303b;
        padding: 12px; border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

st.sidebar.markdown("## 🔴 ŞAHAN & DevilDev")
st.sidebar.caption("VIP SUITE • Streamlit")
page = st.sidebar.radio(
    "Menü",
    [
        "⚡ Tekli URL Taraması",
        "✉️ Hotmail Checker",
        "🔎 Raw API Konsolu",
    ],
)

def normalize_public_url(raw: str) -> str:
    raw = raw.strip()
    if not raw:
        raise ValueError("Lütfen bir URL gir.")
    if "://" not in raw:
        raw = "https://" + raw
    parsed = urlparse(raw)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise ValueError("Geçerli bir http:// veya https:// adresi gir.")
    host = parsed.hostname.lower()
    if host in ("localhost",) or host.endswith(".localhost") or host.endswith(".local"):
        raise ValueError("Yerel adreslere istek gönderilemez.")
    if parsed.username or parsed.password:
        raise ValueError("URL içine kullanıcı adı/şifre ekleme.")
    return raw

if page == "⚡ Tekli URL Taraması":
    st.title("⚡ ŞAHAN VIP - Tekli URL Taraması")
    st.write("Bir web adresinin erişilebilirliğini ve HTTP durumunu kontrol et.")
    url = st.text_input("Hedef URL", placeholder="https://example.com")
    timeout = st.slider("Zaman aşımı (saniye)", 3, 20, 10)
    if st.button("🚀 URL'yi Kontrol Et", type="primary", use_container_width=True):
        try:
            target = normalize_public_url(url)
            with st.spinner("Adres kontrol ediliyor..."):
                response = requests.get(
                    target,
                    timeout=timeout,
                    allow_redirects=True,
                    headers={"User-Agent": "SahanPanel/1.0"},
                )
            st.success("İstek tamamlandı.")
            c1, c2, c3 = st.columns(3)
            c1.metric("HTTP Durumu", response.status_code)
            c2.metric("Yanıt Süresi", f"{response.elapsed.total_seconds():.2f} sn")
            c3.metric("İçerik Boyutu", f"{len(response.content):,} bayt")
            st.write("Son URL:", response.url)
            st.write("İçerik türü:", response.headers.get("content-type", "Bilinmiyor"))
            with st.expander("Yanıt gövdesinin ilk 5.000 karakteri"):
                st.code(response.text[:5000] or "(Boş yanıt)")
        except requests.RequestException as exc:
            st.error(f"İstek başarısız: {exc}")
        except ValueError as exc:
            st.warning(str(exc))

elif page == "✉️ Hotmail Checker":
    st.title("✉️ Hotmail Checker")
    st.info(
        "Bu bölüm Streamlit'e uyarlanmış güvenli hesap bağlantısı alanıdır. "
        "Toplu parola denemesi veya başkalarına ait hesapları kontrol etme yerine, "
        "Microsoft'un resmî OAuth giriş akışı kullanılmalıdır."
    )
    st.subheader("Microsoft hesabını bağlama")
    st.write(
        "OAuth kurulumu için Microsoft Entra uygulama kaydı, Client ID ve "
        "Streamlit uygulamanızın yönlendirme adresi gerekir. İstemci sırrını "
        "koda yazmak yerine Streamlit Secrets içinde saklayın."
    )
    st.code(
        '[microsoft]\\n'
        'client_id = "YOUR_CLIENT_ID"\\n'
        'client_secret = "YOUR_CLIENT_SECRET"\\n'
        'tenant_id = "consumers"\\n'
        'redirect_uri = "https://YOUR-APP.streamlit.app"\\n',
        language="toml",
    )
    st.caption(
        "Bu örnek, OAuth kimlik bilgilerini doğrulamadan giriş yapılmış gibi göstermez. "
        "OAuth akışı yapılandırılınca kullanıcı yalnızca Microsoft'un resmî giriş sayfasına yönlendirilmelidir."
    )
    st.link_button(
        "Microsoft hesap güvenliği",
        "https://account.microsoft.com/security",
        use_container_width=False,
    )

elif page == "🔎 Raw API Konsolu":
    st.title("🔎 Raw API Konsolu")
    st.write("Erişme yetkin olan herkese açık bir API uç noktasının yanıtını görüntüle.")
    endpoint = st.text_input("API URL", placeholder="https://api.example.com/status")
    method = st.selectbox("HTTP yöntemi", ["GET", "POST"])
    body = ""
    if method == "POST":
        body = st.text_area("JSON gövdesi (isteğe bağlı)", placeholder='{"status":"test"}')
    timeout = st.slider("Zaman aşımı (saniye)", 3, 20, 10, key="api_timeout")
    if st.button("API İsteği Gönder", type="primary"):
        try:
            target = normalize_public_url(endpoint)
            kwargs = {
                "timeout": timeout,
                "headers": {"Accept": "application/json", "User-Agent": "SahanPanel/1.0"},
            }
            if method == "POST":
                if body.strip():
                    import json
                    kwargs["json"] = json.loads(body)
                response = requests.post(target, **kwargs)
            else:
                response = requests.get(target, **kwargs)
            st.write(f"HTTP durumu: **{response.status_code}**")
            st.write(f"Yanıt süresi: **{response.elapsed.total_seconds():.2f} sn**")
            st.code(response.text[:20000] or "(Boş yanıt)")
        except ValueError as exc:
            st.warning(str(exc))
        except requests.RequestException as exc:
            st.error(f"İstek başarısız: {exc}")
        except Exception as exc:
            st.error(f"Girdi işlenemedi: {exc}")

st.sidebar.divider()
st.sidebar.caption("Hesap parolalarını uygulamaya veya loglara yapıştırmayın.")
