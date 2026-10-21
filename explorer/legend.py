"""The colour key under the table."""

import streamlit as st

from core.settings import ACCENT, EXCEPTIONS, NA_LABELS, NOTES, TRENDS, YLGNBU
from core.data import CATEGORIES, PROPERTIES
from core.helpers import category_label, colour_value, fmt_prop, swatch


def show_legend(df, prop_name, show_arrows):
    if prop_name in CATEGORIES:
        col, colours = CATEGORIES[prop_name]
        present = set(df[col].dropna())
        items = "".join(swatch(c, category_label(prop_name, k))
                        for k, c in colours.items() if k in present)
        if df[col].isna().any():
            items += swatch("#FFFFFF", "No Data", dashed=True)
        body = f"<div style='font-size:14px;line-height:2'>{items}</div>"
    else:
        p = PROPERTIES[prop_name]
        cv = df[p["col"]].map(lambda v: colour_value(v, p))
        light = df[p["col"]][cv.idxmin()]
        dark = df[p["col"]][cv.idxmax()]
        body = (
            "<div style='display:flex;flex-wrap:wrap;align-items:center;gap:10px;font-size:14px'>"
            f"<span>{fmt_prop(light, prop_name)}</span>"
            f"<span style='flex:1;min-width:140px;max-width:360px;height:14px;border-radius:7px;"
            f"background:linear-gradient(90deg, {', '.join(YLGNBU)})'></span>"
            f"<span>{fmt_prop(dark, prop_name)}</span>"
            f"<span style='margin-left:12px'>{swatch('#FFFFFF', NA_LABELS.get(prop_name, 'No Data'), dashed=True)}</span>"
            "</div>"
        )
    if any(p_ == prop_name for p_, _ in EXCEPTIONS):
        body += (f"<div style='font-size:14px;margin-top:6px'>"
                 f"{swatch(ACCENT, 'Exception to the trend (click the element to see why)', True)}</div>")
    if prop_name in NOTES:
        body += f"<div style='font-size:12px;opacity:0.7;margin-top:4px'>{NOTES[prop_name]}</div>"
    if show_arrows and prop_name in TRENDS:
        _, _, symbol, overall = TRENDS[prop_name]
        body += (f"<div style='font-size:14px;margin-top:8px'>"
                 f"<b>{symbol} Overall:</b> {overall}</div>")
    st.markdown(body, unsafe_allow_html=True)
