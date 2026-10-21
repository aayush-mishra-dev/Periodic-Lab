"""Small helpers used all over the app: formatting, positions, little bits of HTML."""

import math
import re

import pandas as pd
import plotly.io as pio
import streamlit as st
import streamlit.components.v1 as components

from core.settings import BLOCK_COLOURS, GREY_HEX, IUPAC_ROOTS, MISSING_BORDER, NA_LABELS
from core.data import PROPERTIES, is_f_series

# Plotly's built-in themes are slow to apply to every chart, so start from a blank one
# and set the few things we need in show_chart instead.
pio.templates.default = "none"


def show_chart(fig, **kwargs):
    """Draw a Plotly chart with a transparent background so it sits cleanly on its card."""
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font=dict(family="Inter, sans-serif", color="#0F1B2D"),
                      hoverlabel=dict(bgcolor="#0F1B2D", font_color="#FFFFFF"))
    fig.update_xaxes(automargin=True, zeroline=False, linecolor="#C4CCD8")
    fig.update_yaxes(automargin=True, zeroline=False)
    return st.plotly_chart(fig, theme=None, **kwargs)



def draw_html(html):
    """Put a self-contained HTML/SVG snippet straight into the page (no iframe, no flash).
    Lines are joined first, because indented lines would otherwise be read as code."""
    one_line = " ".join(line.strip() for line in html.splitlines() if line.strip())
    st.markdown(one_line, unsafe_allow_html=True)


def embed_html(html, height):
    """Show a self-contained HTML snippet (newer Streamlit: st.iframe)."""
    if hasattr(st, "iframe"):
        st.iframe(html, height=height)
    else:
        components.html(html, height=height)



def fmt(value, unit="", digits=2):
    if value is None or value != value:      # missing or NaN
        return "–"
    if digits is None:
        text = f"{value:,.0f}" if abs(value) >= 1000 else f"{value:.3g}"
    else:
        text = f"{value:.{digits}f}"
    return f"{text} {unit}".strip()



def fmt_prop(value, name):
    p = PROPERTIES[name]
    if pd.isna(value):
        return NA_LABELS.get(name, "–")
    return fmt(value, p["unit"], p["digits"])



def colour_value(value, p):
    """The number used for colouring: flipped and/or logged when needed."""
    if value is None or pd.isna(value):
        return None
    value = -value if p["flip"] else float(value)
    if p["log"]:
        return math.log10(value) if value > 0 else None
    return value



def position(z, group, period):
    if 58 <= z <= 71:        # lanthanoids: Ce to Lu
        return z - 54, 9
    if 90 <= z <= 103:       # actinoids: Th to Lr
        return z - 86, 10
    if z in (57, 89):        # La and Ac sit in group 3
        return 3, period
    return int(group), period



def display_group(z, group):
    return 3 if is_f_series(z) else int(group)



def discrete_scale(colours):
    n = len(colours)
    scale = []
    for i, c in enumerate(colours):
        scale += [[i / n, c], [(i + 1) / n, c]]
    return scale



def category_label(prop_name, value):
    if not isinstance(value, str):
        return "no data"
    return f"{value}-block" if prop_name == "Block" else value



def element_row(df, z):
    return df[df["atomic_number"] == z].iloc[0]



def element_row_by_symbol(df, symbol):
    return df[df["symbol"] == symbol].iloc[0]



def element_options(df):
    return [f"{z} · {n} ({s})" for z, n, s in zip(df["atomic_number"], df["name"], df["symbol"])]



def option_name(row):
    return f"{row['name']} ({row['symbol']})"



def shell_counts(conf, configs):
    """'[Ar] 3d6 4s2' -> {1: 2, 2: 8, 3: 14, 4: 2}"""
    shells = {}
    for token in str(conf).split():
        if token.startswith("["):
            for n, c in shell_counts(configs.get(token[1:-1], ""), configs).items():
                shells[n] = shells.get(n, 0) + c
            continue
        m = re.match(r"(\d+)([spdfg])(\d*)", token)
        if m:
            n = int(m.group(1))
            shells[n] = shells.get(n, 0) + int(m.group(3) or 1)
    return dict(sorted(shells.items()))



def pretty_config(conf):
    """'[Ar] 3d6 4s2' -> '[Ar] 3d⁶ 4s²'"""
    sup = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")
    return re.sub(r"([spdfg])(\d+)", lambda m: m.group(1) + m.group(2).translate(sup), str(conf))



def iupac_name(z):
    parts = [IUPAC_ROOTS[int(d)] for d in str(z)]
    name = ("".join(parts) + "ium").replace("ennnil", "ennil").replace("iium", "ium")
    symbol = "".join(p[0] for p in parts).capitalize()
    return name.capitalize(), symbol, parts



def swatch(colour, text, round_=False, dashed=False):
    radius = "50%" if round_ else "4px"
    border = f"1.5px dotted {MISSING_BORDER}" if dashed else "1px solid rgba(0,0,0,0.15)"
    return (f"<span style='display:inline-flex;align-items:center;gap:6px;margin-right:18px'>"
            f"<span style='width:16px;height:16px;border-radius:{radius};background:{colour};"
            f"display:inline-block;border:{border}'></span>{text}</span>")



def chip(text, strong=""):
    return (f"<span style='display:inline-block;margin:0 6px 6px 0;padding:4px 11px;"
            f"border-radius:999px;background:#EEF2F9;font-size:13px'>"
            f"<b>{strong}</b> {text}</span>")



def stat(label_text, value):
    return (f"<div><div style='font-size:12px;opacity:0.65'>{label_text}</div>"
            f"<div style='font-size:16px;font-weight:600'>{value}</div></div>")



def element_header(row, size=64):
    z = int(row["atomic_number"])
    tile = BLOCK_COLOURS.get(row["block"], GREY_HEX)
    subtitle = f"Period {int(row['period'])} · Group {display_group(z, row['group_id'])} · {row['block']}-block"
    if isinstance(row.get("family"), str):
        subtitle += f"<br>{row['family']}"
    return (
        "<div style='display:flex;align-items:center;gap:14px'>"
        f"<div class='pe-pop' style='width:{size}px;height:{size}px;flex-shrink:0;border-radius:12px;background:{tile};"
        "display:flex;flex-direction:column;align-items:center;justify-content:center;color:#1F2937'>"
        f"<div style='font-size:11px'>{z}</div>"
        f"<div style='font-size:{size * 0.4:.0f}px;font-weight:700;line-height:1'>{row['symbol']}</div></div>"
        f"<div><div style='font-size:22px;font-weight:700'>{row['name']}</div>"
        f"<div style='font-size:13px;opacity:0.7'>{subtitle}</div></div></div>"
    )
