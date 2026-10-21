
import datetime
import ipaddress
import json
import threading
from pathlib import Path

import requests
import streamlit as st

LOCAL_FILE = Path(__file__).resolve().parent.parent / "visits.json"
UNKNOWN = "ZZ"                     # code used when the country can't be worked out
LOCAL_COUNTRY = "IN"               # visits from your own Wi-Fi or computer count as India
_file_lock = threading.Lock()
_country_cache = {}


# ---------- Finding the visitor's country ----------

def client_ip():
    """The visitor's IP address, as passed along by the hosting service."""
    try:
        headers = st.context.headers
        forwarded = headers.get("X-Forwarded-For") or headers.get("X-Real-Ip")
        if forwarded:
            return forwarded.split(",")[0].strip()
        ip = getattr(st.context, "ip_address", None)
        if ip:
            return ip
        # Streamlit gives no IP for visits on your own computer; spot those from the address
        host = headers.get("Host", "").split(":")[0]
        if host in ("localhost", "127.0.0.1") or host.startswith(("192.168.", "10.")):
            return "127.0.0.1"
        return None
    except Exception:
        return None


def lookup_country(ip):
    """Two-letter country code for an IP address, e.g. 'IN'. Uses the free country.is service."""
    if not ip:
        return UNKNOWN
    try:
        address = ipaddress.ip_address(ip)
        if address.is_private or address.is_loopback:
            return LOCAL_COUNTRY               # someone on your own Wi-Fi or computer
    except ValueError:
        return UNKNOWN
    if ip in _country_cache:
        return _country_cache[ip]
    try:
        reply = requests.get(f"https://api.country.is/{ip}", timeout=3)
        code = reply.json().get("country") or UNKNOWN
    except Exception:
        code = UNKNOWN
    _country_cache[ip] = code
    return code


# ---------- Saving and loading the counts ----------

def supabase_config():
    try:
        cfg = st.secrets["supabase"]
        return cfg["url"].rstrip("/"), cfg["key"]
    except Exception:
        return None


def supabase_headers(key):
    headers = {"apikey": key, "Content-Type": "application/json"}
    if not key.startswith("sb_"):              # older Supabase keys also go here
        headers["Authorization"] = f"Bearer {key}"
    return headers


def save_visit(country, day, db):
    if db:
        url, key = db
        try:
            requests.post(f"{url}/rest/v1/rpc/record_visit", json={"c": country, "d": day},
                          headers=supabase_headers(key), timeout=5)
        except Exception:
            pass
        return
    with _file_lock:
        data = read_local()
        data["countries"][country] = data["countries"].get(country, 0) + 1
        data["days"][day] = data["days"].get(day, 0) + 1
        LOCAL_FILE.write_text(json.dumps(data, indent=2))


def read_local():
    try:
        data = json.loads(LOCAL_FILE.read_text())
        data.setdefault("countries", {})
        data.setdefault("days", {})
        return data
    except Exception:
        return {"countries": {}, "days": {}}


@st.cache_data(ttl=60, show_spinner=False)
def load_stats():
    """{'countries': {'IN': 12, ...}, 'days': {'2026-10-20': 5, ...}, 'online': bool}"""
    db = supabase_config()
    if not db:
        return {**read_local(), "online": False}
    url, key = db
    headers = supabase_headers(key)
    try:
        countries = requests.get(f"{url}/rest/v1/visit_countries?select=country,count",
                                 headers=headers, timeout=5).json()
        days = requests.get(f"{url}/rest/v1/visit_days?select=day,count&order=day.desc&limit=90",
                            headers=headers, timeout=5).json()
        return {"countries": {r["country"]: r["count"] for r in countries},
                "days": {r["day"]: r["count"] for r in days}, "online": True}
    except Exception:
        return {"countries": {}, "days": {}, "online": True, "error": True}


# ---------- Called once when someone opens the site ----------

def record_visit():
    """Count this visit once per browser session, in the background so the page isn't slowed."""
    ss = st.session_state
    if ss.get("visit_counted"):
        return
    ss.visit_counted = True
    ip = client_ip()
    db = supabase_config()
    day = datetime.datetime.now(datetime.timezone.utc).date().isoformat()

    def work():
        save_visit(lookup_country(ip), day, db)

    threading.Thread(target=work, daemon=True).start()
