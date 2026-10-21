"""The Compare tab."""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from core.settings import ACCENT, NO_TOOLBAR
from core.data import CATEGORIES, PROPERTIES
from core.helpers import (
    category_label, colour_value, element_header, element_options, element_row,
    fmt_prop, show_chart,
)


QUICK_SETS = {
    "Period 2": list(range(3, 11)),
    "Period 3": list(range(11, 19)),
    "Group 1": [3, 11, 19, 37, 55],
    "Group 2": [4, 12, 20, 38, 56],
    "Halogens": [9, 17, 35, 53],
    "Noble Gases": [2, 10, 18, 36, 54],
}


COMPARE_COLOURS = ["#225ea8", "#E4572E", "#2A9D8F", "#E9C46A",
                   "#B5A8E0", "#F4A261", "#7FB3D5", "#8AB17D"]


def set_compare(labels):
    choice = st.session_state.get("quick_pick")
    if choice:
        st.session_state.cmp_multi = [labels[z] for z in QUICK_SETS[choice]]
        st.session_state.quick_pick = None



@st.fragment
def compare_tab(df):
    ss = st.session_state
    labels = dict(zip(df["atomic_number"], element_options(df)))
    if "cmp_multi" not in ss:
        ss.cmp_multi = [labels[z] for z in (11, 12, 13, 17)]

    st.subheader("Compare Elements")
    if hasattr(st, "pills"):
        st.pills("Quick Picks", list(QUICK_SETS), key="quick_pick",
                 on_change=set_compare, args=(labels,))
    else:
        st.selectbox("Quick Picks", list(QUICK_SETS), index=None, key="quick_pick",
                     on_change=set_compare, args=(labels,))

    chosen = st.multiselect("Elements to Compare", list(labels.values()), key="cmp_multi",
                            max_selections=8, placeholder="Pick 2 to 8 elements")
    if len(chosen) < 2:
        st.info("Pick at least two elements to compare.")
        return
    els = [element_row(df, int(c.split(" ")[0])) for c in chosen]

    per_row = min(len(els), 4)
    for start in range(0, len(els), per_row):
        cols = st.columns(per_row)
        for c, el in zip(cols, els[start:start + per_row]):
            c.markdown(element_header(el, 52), unsafe_allow_html=True)

    cell = "padding:7px 10px;white-space:nowrap"
    head = "".join(f"<th style='text-align:left;{cell}'>{el['symbol']}</th>" for el in els)
    rows = ""
    for name, p in PROPERTIES.items():
        cvs = [colour_value(el[p["col"]], p) for el in els]
        valid = [c for c in cvs if c is not None]
        best = max(valid) if len(valid) >= 2 and len(set(valid)) > 1 else None
        tds = ""
        for el, cv in zip(els, cvs):
            text = fmt_prop(el[p["col"]], name)
            if best is not None and cv == best:
                text = f"<b style='color:{ACCENT}'>{text}</b>"
            tds += f"<td style='{cell}'>{text}</td>"
        rows += f"<tr><td style='{cell};opacity:0.75'>{name}</td>{tds}</tr>"
    for name, (col, _) in CATEGORIES.items():
        tds = "".join(f"<td style='{cell}'>{category_label(name, el[col])}</td>" for el in els)
        rows += f"<tr><td style='{cell};opacity:0.75'>{name}</td>{tds}</tr>"

    st.markdown(
        "<div style='overflow-x:auto;margin-top:12px'>"
        "<table style='border-collapse:collapse;font-size:14px;width:100%'>"
        f"<tr><th style='text-align:left;{cell}'>Property</th>{head}</tr>{rows}</table></div>",
        unsafe_allow_html=True,
    )
    st.caption("The highest value in each row is highlighted. For electron gain enthalpy, "
               "highest means most negative.")

    names = list(PROPERTIES)
    chart_prop = st.selectbox("Chart a Property", names,
                              index=names.index("Ionisation Enthalpy") if "Ionisation Enthalpy" in names else 0,
                              key="cmp_prop")
    p = PROPERTIES[chart_prop]
    xs, ys, colours, texts = [], [], [], []
    for i, el in enumerate(els):
        if pd.notna(el[p["col"]]):
            xs.append(el["symbol"])
            ys.append(el[p["col"]])
            colours.append(COMPARE_COLOURS[i % len(COMPARE_COLOURS)])
            texts.append(fmt_prop(el[p["col"]], chart_prop))
    if len(xs) < 2:
        st.caption("Not enough data for this property.")
        return
    fig = go.Figure(go.Bar(x=xs, y=ys, marker_color=colours, text=texts, textposition="outside",
                           cliponaxis=False, hovertemplate="%{x}: %{text}<extra></extra>"))
    fig.update_xaxes(type="category", fixedrange=True)
    fig.update_yaxes(fixedrange=True, gridcolor="#EEF1F6", type="log" if p["log"] else "linear",
                     title=f"{chart_prop} ({p['unit']})" if p["unit"] else chart_prop)
    fig.update_layout(height=380, plot_bgcolor="white", dragmode=False,
                      margin=dict(l=10, r=10, t=30, b=10))
    show_chart(fig, config=NO_TOOLBAR, key="compare")
