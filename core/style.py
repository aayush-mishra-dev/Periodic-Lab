"""The app's look: fonts, colours, spacing, cards and the banner at the top."""

import streamlit as st

from core.helpers import embed_html
from core.settings import APP_NAME

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

:root {
    --navy: #0F1B2D;
    --blue: #1D4ED8;
    --blue-soft: #E6EDFD;
    --orange: #E4572E;
    --line: #E3E8F0;
    --muted: #55627A;
}

html, body, .stApp, .stMarkdown, p, label, button, input, textarea, li {
    font-family: 'Inter', system-ui, sans-serif;
}
h1, h2, h3, h4, h5 {
    font-family: 'Space Grotesk', 'Inter', sans-serif !important;
    letter-spacing: -0.02em;
    color: var(--navy);
}
h3 { font-size: 1.35rem !important; margin-bottom: 0.25rem !important; }
.block-container { padding-top: 1.5rem; padding-bottom: 4rem; max-width: 1440px; }

/* No white flash or fading while the page updates after a click */
[data-stale="true"], .stale-element, .element-container[data-stale="true"] {
    opacity: 1 !important;
    transition: none !important;
}

/* Hide the "Deploy" button and keep the top bar out of the way */
.stAppDeployButton, [data-testid="stAppDeployButton"] { display: none !important; }
/* Hide Streamlit's top bar completely, so nothing covers or blocks the top of the page */
header[data-testid="stHeader"] { display: none !important; }
.block-container { padding-top: 1.5rem !important; }

/* Space between the blocks inside every section */
[data-testid="stVerticalBlock"] { gap: 0.9rem; }

/* Cards: every container whose key starts with "card" */
[class*="st-key-card"] {
    background: #FFFFFF;
    border: 1px solid var(--line);
    border-radius: 20px;
    box-shadow: 0 1px 2px rgba(15, 27, 45, 0.04), 0 8px 24px rgba(15, 27, 45, 0.05);
    padding: 22px 24px;
}

/* Banner */
.hero {
    position: relative; overflow: hidden;
    background: var(--navy); color: #FFFFFF; border-radius: 24px;
    padding: 30px 34px; margin-bottom: 20px;
}
.hero-kicker {
    font-size: 12px; font-weight: 700; letter-spacing: 0.14em;
    text-transform: uppercase; color: #A9BCE6;
}
.hero-title {
    font-family: 'Space Grotesk', sans-serif; font-weight: 700;
    font-size: clamp(30px, 5vw, 48px); line-height: 1.1; margin: 8px 0 10px;
}
.hero-sub { color: #D4DDF0; font-size: 16px; max-width: 560px; line-height: 1.5; }
.hero-chips { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 18px; }
.hero-chips span {
    padding: 6px 13px; border-radius: 999px;
    background: rgba(255, 255, 255, 0.10); font-size: 13px;
}
.hero-tiles {
    position: absolute; right: 34px; top: 50%; transform: translateY(-50%);
    display: grid; grid-template-columns: repeat(4, 58px); gap: 8px;
}
.hero-tiles div {
    width: 58px; height: 58px; border-radius: 12px; color: #1F2937;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    font-family: 'Space Grotesk', sans-serif; font-weight: 700; font-size: 22px; line-height: 1;
}
.hero-tiles small { font-size: 10px; font-weight: 500; margin-bottom: 3px; }
@media (max-width: 900px) { .hero-tiles { display: none; } .hero { padding: 24px 22px; } }

/* Tabs (two sets of selectors: newer and older Streamlit versions) */
.stTabs [role="tablist"], .stTabs [data-baseweb="tab-list"] {
    gap: 6px; background: #FFFFFF; padding: 6px; border-radius: 14px;
    border: 1px solid var(--line); margin-bottom: 10px; flex-wrap: wrap;
}
.stTabs [role="tab"], .stTabs [data-baseweb="tab"] {
    padding: 8px 16px; border-radius: 10px; height: auto; border-bottom: none !important;
}
.stTabs [role="tab"] p, .stTabs [data-baseweb="tab"] p { font-size: 15px; font-weight: 600; }
.stTabs [role="tab"][aria-selected="true"], .stTabs [data-baseweb="tab"][aria-selected="true"] {
    background: var(--blue-soft); color: var(--blue);
}
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display: none; }
.stTabs [role="tablist"] > div:last-child:not([role="tab"]) { display: none; }

/* Buttons: comfortable size, clear spacing, easy to tap */
.stButton button {
    border-radius: 12px; font-weight: 500; min-height: 44px;
    padding: 0.5rem 1.1rem; margin-bottom: 4px;
}
/* Quiz answers and result buttons fill their column, so they line up neatly */
.st-key-quiz_options [data-testid="stButton"], .st-key-quiz_options .stButton,
.st-key-quiz_options button, .st-key-quiz_actions [data-testid="stButton"],
.st-key-quiz_actions .stButton, .st-key-quiz_actions button { width: 100% !important; }
.st-key-quiz_options button { justify-content: flex-start; text-align: left; min-height: 52px; }

/* Pills and segmented buttons get a little breathing room */
[data-testid="stButtonGroup"] { gap: 8px !important; flex-wrap: wrap; }

/* Dropdown sections (History, quiz review, About This Element) */
[data-testid="stExpander"] details {
    background: #FFFFFF; border: 1px solid var(--line); border-radius: 14px;
}
[data-testid="stExpander"] summary { font-weight: 600; font-size: 15px; padding: 14px 16px; }

/* Tables */
[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; }

/* Show the full table on wide screens and the compact one on phones */
@media (max-width: 820px), (max-height: 500px) { .st-key-tablewrap_full { display: none !important; } }
@media (min-width: 821px) and (min-height: 501px) { .st-key-tablewrap_compact { display: none !important; } }
/* Trim the space under the phone table: its height follows the screen width */
.st-key-tablewrap_compact [data-testid="stElementContainer"]:has(.js-plotly-plot),
.st-key-tablewrap_compact [data-testid="stPlotlyChart"] {
    max-height: calc(56vw + 6px) !important; overflow: hidden !important;
}
/* On phones, give the table card as much width as possible */
@media (max-width: 820px) { .st-key-card_table { padding: 12px 4px !important; } }

/* Let a finger on any chart scroll the page normally (taps are handled by the helper) */
.js-plotly-plot, .js-plotly-plot * { touch-action: pan-x pan-y !important; }
@media (max-width: 820px) {
    [class*="st-key-card"] { padding: 16px 14px; border-radius: 16px; }
    .block-container { padding-left: 0.8rem; padding-right: 0.8rem; }
}

/* Section titles and element chips */
.pe-section-title {
    font-family: 'Space Grotesk', sans-serif; font-size: 26px; font-weight: 700;
    color: var(--navy); margin: 22px 0 -4px;
}
.pe-chips { display: flex; flex-wrap: wrap; gap: 6px; }
.pe-chip {
    display: inline-flex; align-items: center; justify-content: center;
    min-width: 40px; height: 36px; padding: 0 8px; border-radius: 8px;
    font-family: 'Space Grotesk', sans-serif; font-weight: 700; color: #1F2937;
}


/* ---------- Animations ---------- */
@keyframes pe-rise { from { opacity: 0; transform: translateY(14px); } to { opacity: 1; transform: none; } }
@keyframes pe-float { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-7px); } }
@keyframes pe-pop {
    0% { transform: scale(0.8); opacity: 0; }
    60% { transform: scale(1.06); opacity: 1; }
    100% { transform: scale(1); }
}
@keyframes pe-grow { from { width: 0; } }
@keyframes pe-draw { from { stroke-dasharray: 0 1000; } }

.hero { animation: pe-rise 0.6s ease both; }
.hero-tiles div { animation: pe-float 4s ease-in-out infinite; }
.hero-tiles div:nth-child(2) { animation-delay: 0.4s; }
.hero-tiles div:nth-child(3) { animation-delay: 0.8s; }
.hero-tiles div:nth-child(4) { animation-delay: 1.2s; }
.hero-tiles div:nth-child(5) { animation-delay: 1.6s; }
.hero-tiles div:nth-child(6) { animation-delay: 2.0s; }
.hero-tiles div:nth-child(7) { animation-delay: 2.4s; }
.hero-tiles div:nth-child(8) { animation-delay: 2.8s; }
.stTabs [role="tabpanel"] { animation: pe-rise 0.35s ease both; }
.pe-pop { animation: pe-pop 0.45s cubic-bezier(0.2, 0.8, 0.2, 1) both; }
.pe-chip { animation: pe-pop 0.35s ease both; }
.pe-feedback { animation: pe-rise 0.35s ease both; }
.pe-bar { animation: pe-grow 0.9s ease-out both; }
.pe-ring { animation: pe-draw 1.2s ease-out both; }
.stButton button { transition: transform 0.15s ease, box-shadow 0.15s ease; }
@media (hover: hover) {
    .stButton button:hover { transform: translateY(-1px); box-shadow: 0 4px 14px rgba(15, 27, 45, 0.08); }
}
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after { animation: none !important; transition: none !important; }
}

/* The tiny invisible helper that makes tapping the table work on phones */
.st-key-pe_touch_fix { display: none !important; }

/* History timeline: sideways on wide screens, top-to-bottom on phones */
@media (max-width: 820px) { .st-key-timeline_wide { display: none !important; } }
@media (min-width: 821px) { .st-key-timeline_narrow { display: none !important; } }

/* Footer */
.pe-footer { text-align: center; color: var(--muted); font-size: 13px; margin-top: 32px; }
</style>
"""

HERO_TILES = [("1", "H", "#F4A261"), ("2", "He", "#B5A8E0"), ("6", "C", "#2A9D8F"),
              ("8", "O", "#7FB3D5"), ("11", "Na", "#E76F51"), ("26", "Fe", "#E9C46A"),
              ("29", "Cu", "#E9C46A"), ("79", "Au", "#8AB17D")]


def apply_style(element_count, property_count):
    st.markdown(CSS, unsafe_allow_html=True)
    tiles = "".join(f"<div style='background:{c}'><small>{z}</small>{s}</div>"
                    for z, s, c in HERO_TILES)
    st.markdown(
        "<div class='hero'>"
        "<div class='hero-kicker'>Interactive Chemistry Lab - Initiative by Aayush Mishra</div>"
        f"<div class='hero-title'>{APP_NAME}</div>"
        "<div class='hero-sub'>Explore how the elements are arranged, and why their "
        "properties rise and fall.</div>"
        "<div class='hero-chips'>"
        f"<span>{element_count} elements</span><span>{property_count} properties</span>"
        "<span>Quiz · Compare · History</span></div>"
        f"<div class='hero-tiles'>{tiles}</div></div>",
        unsafe_allow_html=True,
    )


def footer():
    st.markdown(f"<div class='pe-footer'>{APP_NAME} · Initiative by Aayush Mishra "
                "</div>", unsafe_allow_html=True)


TOUCH_FIX = """
<script>
// Phone helper for the charts. Plotly grabs finger touches on its charts, which stops
// the page from scrolling when your finger lands on one. This script keeps touches
// away from Plotly, so the page scrolls normally, and turns a quick tap into a mouse
// click at the same spot, so tapping the periodic table still selects an element.
(function () {
  const win = window.parent;
  if (!win || win.__peTouchFix) return;
  win.__peTouchFix = true;
  let start = null;

  function mouse(type, x, y, target) {
    target.dispatchEvent(new win.MouseEvent(type, {
      bubbles: true, cancelable: true, view: win, clientX: x, clientY: y,
      button: 0, buttons: type === "mousedown" ? 1 : 0
    }));
  }

  win.addEventListener("touchstart", function (e) {
    const plot = e.target.closest && e.target.closest(".js-plotly-plot");
    if (!plot) { start = null; return; }
    e.stopPropagation();                       // Plotly never sees the touch
    const t = e.touches[0];
    start = { x: t.clientX, y: t.clientY, time: Date.now(), moved: false };
  }, { capture: true, passive: true });

  win.addEventListener("touchmove", function (e) {
    if (!start) return;
    e.stopPropagation();
    const t = e.touches[0];
    if (Math.abs(t.clientX - start.x) + Math.abs(t.clientY - start.y) > 10) start.moved = true;
  }, { capture: true, passive: true });

  win.addEventListener("touchend", function (e) {
    if (!start) return;
    e.stopPropagation();
    const tap = !start.moved && Date.now() - start.time < 600;
    const x = start.x, y = start.y;
    start = null;
    if (!tap) return;
    const target = win.document.elementFromPoint(x, y);
    if (!target) return;
    mouse("mousemove", x, y, target);         // Plotly works out what's under the finger...
    win.setTimeout(function () {               // ...then, a moment later, the click
      mouse("mousedown", x, y, target);
      mouse("mouseup", x, y, target);
      mouse("click", x, y, target);
    }, 120);
  }, { capture: true, passive: true });
})();
</script>
"""


def touch_fix():
    with st.container(key="pe_touch_fix"):
        embed_html(TOUCH_FIX, height=10)
