"""The 'deep dive' graphs: how the chosen property behaves around the selected element.

Numeric properties get: across its period, down its group, across the whole table,
and where it ranks. Some properties also get an extra graph of their own (atom sizes,
bond types, successive ionisation enthalpies). Categories get a breakdown chart instead.
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from core.data import CATEGORIES, PROPERTIES, in_f_row
from core.helpers import category_label, colour_value, display_group, element_row, fmt_prop, show_chart
from core.settings import ACCENT, EXCEPTIONS, LINE_BLUE, NA_LABELS, NO_TOOLBAR

GREY_LINE = "#C4CCD8"
PERIOD_STARTS = {2: 3, 3: 11, 4: 19, 5: 37, 6: 55, 7: 87}


def style(fig, height=320, title_y=None):
    fig.update_xaxes(fixedrange=True, showgrid=False)
    fig.update_yaxes(fixedrange=True, gridcolor="#EEF1F6")
    fig.update_layout(height=height, dragmode=False, showlegend=False,
                      margin=dict(l=10, r=10, t=10, b=10))
    return fig


def neighbours(df, z, along):
    """The elements in the same period or group as z, in order."""
    row = element_row(df, z)
    if along == "period":
        sub = df[(df["period"] == row["period"]) & ~df["atomic_number"].map(in_f_row)]
        label = f"period {int(row['period'])}"
    else:
        g = display_group(z, row["group_id"])
        sub = df[((df["group_id"] == g) & ~df["atomic_number"].map(in_f_row))
                 | ((g == 3) & df["atomic_number"].isin([57, 89]))]
        label = f"group {g}"
    return sub.sort_values("atomic_number"), label


def line_figure(sub, prop_name, z):
    p = PROPERTIES[prop_name]
    col, unit, digits = p["col"], p["unit"], p["digits"]
    number = ".3g" if digits is None else f".{digits}f"
    is_sel = sub["atomic_number"] == z
    fig = go.Figure(go.Scatter(
        x=sub["symbol"], y=sub[col], mode="lines+markers",
        line=dict(color=LINE_BLUE, width=3),
        marker=dict(size=[16 if s else 9 for s in is_sel],
                    color=[ACCENT if s else LINE_BLUE for s in is_sel],
                    line=dict(color="white", width=2)),
        customdata=sub["name"],
        hovertemplate=f"%{{customdata}}<br>%{{y:{number}}} {unit}<extra></extra>",
    ))
    gaps = sub[sub[col].isna()]
    if not gaps.empty and sub[col].notna().any():
        fig.add_trace(go.Scatter(
            x=gaps["symbol"], y=[sub[col].min()] * len(gaps), mode="markers",
            marker=dict(size=9, color="white", line=dict(color="#9CA3AF", width=2)),
            customdata=gaps["name"],
            hovertemplate=f"%{{customdata}}: {NA_LABELS.get(prop_name, 'no data')}<extra></extra>"))
    found = []
    for sym, val in zip(sub["symbol"], sub[col]):
        if (prop_name, sym) in EXCEPTIONS and pd.notna(val):
            found.append(sym)
            fig.add_annotation(x=sym, y=val, text="<b>exception</b>", showarrow=True,
                               arrowhead=2, arrowwidth=2, ax=0, ay=-32, arrowcolor=ACCENT,
                               font=dict(color=ACCENT, size=12))
    fig.update_xaxes(type="category")
    fig.update_yaxes(type="log" if p["log"] else "linear", title=unit or None)
    return style(fig), gaps, found


def trend_card(df, prop_name, z, along, key):
    sub, label = neighbours(df, z, along)
    col = PROPERTIES[prop_name]["col"]
    with st.container(key=key):
        st.markdown(f"### {'Across' if along == 'period' else 'Down'} {label.title()}")
        if sub[col].notna().sum() < 2:
            st.caption("Not enough data to draw this graph.")
            return
        fig, gaps, found = line_figure(sub, prop_name, z)
        show_chart(fig, config=NO_TOOLBAR, key=f"trend_{along}")
        if not gaps.empty:
            st.caption(f"Hollow grey dots: {NA_LABELS.get(prop_name, 'no data').lower()} "
                       f"({', '.join(gaps['symbol'])}).")
        for sym in found:
            st.markdown(f"**{sym}:** {EXCEPTIONS[(prop_name, sym)]}")


def whole_table_card(df, prop_name, z):
    p = PROPERTIES[prop_name]
    col = p["col"]
    data = df[df[col].notna() & (df["atomic_number"] <= 103)]
    sel = data[data["atomic_number"] == z]
    fig = go.Figure(go.Scatter(
        x=data["atomic_number"], y=data[col], mode="lines+markers",
        line=dict(color=LINE_BLUE, width=1.6), marker=dict(size=5, color=LINE_BLUE),
        customdata=data["name"], hovertemplate="%{customdata} (Z = %{x})<extra></extra>"))
    if not sel.empty:
        fig.add_trace(go.Scatter(
            x=sel["atomic_number"], y=sel[col], mode="markers",
            marker=dict(size=16, color=ACCENT, line=dict(color="white", width=2)),
            hoverinfo="skip"))
    top = data[col].max()
    for period, start in PERIOD_STARTS.items():
        fig.add_vline(x=start - 0.5, line=dict(color=GREY_LINE, width=1, dash="dot"))
        fig.add_annotation(x=start + 0.5, y=top, text=f"P{period}", showarrow=False,
                           xanchor="left", font=dict(size=11, color="#6B7280"))
    fig.update_xaxes(title="Atomic Number")
    fig.update_yaxes(type="log" if p["log"] else "linear", title=p["unit"] or None)
    with st.container(key="card_whole"):
        st.markdown("### Across the Whole Table")
        show_chart(style(fig), config=NO_TOOLBAR, key="whole")
        st.caption("Each dotted line starts a new period. The pattern repeating period after "
                   "period is what 'periodic' means.")


def rank_card(df, prop_name, z):
    p = PROPERTIES[prop_name]
    col = p["col"]
    data = df[df[col].notna()].copy()
    data["cv"] = data[col].map(lambda v: colour_value(v, p))
    data = data.dropna(subset=["cv"]).sort_values("cv")
    is_sel = data["atomic_number"] == z
    fig = go.Figure(go.Bar(
        x=data["symbol"], y=data[col],
        marker_color=[ACCENT if s else "#B9C7E4" for s in is_sel],
        customdata=data["name"], hovertemplate="%{customdata}<extra></extra>"))
    fig.update_xaxes(showticklabels=False, type="category")
    fig.update_yaxes(type="log" if p["log"] else "linear", title=p["unit"] or None)
    with st.container(key="card_rank"):
        st.markdown("### Where It Ranks")
        if not is_sel.any():
            st.caption(f"No value for this element: {NA_LABELS.get(prop_name, 'no data').lower()}.")
            return
        position = int(is_sel.values.nonzero()[0][0])
        total = len(data)
        beats = 100 * position / max(total - 1, 1)
        row = element_row(df, z)
        st.markdown(
            f"<div style='font-size:15px'><b>{row['name']}</b> is "
            f"<b style='color:{ACCENT}'>#{total - position}</b> of {total} elements, "
            f"higher than <b>{beats:.0f}%</b> of them.</div>", unsafe_allow_html=True)
        show_chart(style(fig, height=260), config=NO_TOOLBAR, key="rank")
        st.caption("Every bar is an element, sorted from lowest to highest.")


def radius_sizes_card(df, z):
    sub, label = neighbours(df, z, "period")
    sub = sub[sub["radius"].notna()]
    is_sel = sub["atomic_number"] == z
    biggest = sub["radius"].max()
    fig = go.Figure(go.Scatter(
        x=sub["symbol"], y=[0] * len(sub), mode="markers+text",
        text=sub["symbol"], textposition="middle center",
        textfont=dict(color="white", size=12),
        marker=dict(size=[62 * r / biggest for r in sub["radius"]],
                    color=[ACCENT if s else LINE_BLUE for s in is_sel],
                    line=dict(color="white", width=2), opacity=0.9),
        customdata=sub["radius"], hovertemplate="%{x}: %{customdata:.0f} pm<extra></extra>"))
    fig.update_xaxes(type="category", showticklabels=False)
    fig.update_yaxes(visible=False, range=[-1, 1])
    with st.container(key="card_sizes"):
        st.markdown(f"### Atom Sizes Across {label.title()}")
        show_chart(style(fig, height=170), config=NO_TOOLBAR, key="sizes")
        st.caption("Each circle is drawn to scale. Atoms shrink across a period because more "
                   "protons pull the same shell in tighter.")


BOND_PARTNERS = ["H", "C", "O", "F", "Cl", "Na"]


def bond_types_card(df, z):
    row = element_row(df, z)
    en = row["en_pauling"]
    with st.container(key="card_bonds"):
        st.markdown(f"### What Kind of Bond Would {row['symbol']} Form?")
        if pd.isna(en):
            st.caption("This element has no Pauling electronegativity, so we can't predict its bonds.")
            return
        names, diffs, colours, kinds = [], [], [], []
        for s in BOND_PARTNERS:
            partner = df[df["symbol"] == s].iloc[0]
            if partner["atomic_number"] == z or pd.isna(partner["en_pauling"]):
                continue
            d = abs(en - partner["en_pauling"])
            kind = "Ionic" if d > 1.7 else ("Polar covalent" if d >= 0.4 else "Non-polar covalent")
            names.append(f"{row['symbol']}–{s}")
            diffs.append(d)
            kinds.append(kind)
            colours.append({"Ionic": ACCENT, "Polar covalent": LINE_BLUE,
                            "Non-polar covalent": "#8AB17D"}[kind])
        fig = go.Figure(go.Bar(
            x=diffs, y=names, orientation="h", marker_color=colours,
            text=[f"{d:.2f} · {k}" for d, k in zip(diffs, kinds)], textposition="outside",
            cliponaxis=False, hovertemplate="%{y}: ΔEN = %{x:.2f}<extra></extra>"))
        fig.add_vline(x=0.4, line=dict(color=GREY_LINE, dash="dot"))
        fig.add_vline(x=1.7, line=dict(color=GREY_LINE, dash="dot"))
        fig.update_xaxes(title="Difference in Electronegativity (ΔEN)",
                         range=[0, max(3.4, max(diffs) + 0.9)])
        fig.update_yaxes(autorange="reversed", showgrid=False)
        show_chart(style(fig, height=300), config=NO_TOOLBAR, key="bonds")
        st.caption("Rule of thumb: ΔEN below 0.4 shares electrons evenly, 0.4 to 1.7 shares "
                   "them unevenly (polar), and above 1.7 mostly transfers them (ionic).")


def category_cards(df, prop_name, z):
    col, colours = CATEGORIES[prop_name]
    row = element_row(df, z)
    mine = row[col]
    counts = df[col].value_counts()
    labels = [c for c in colours if c in counts.index]
    fig = go.Figure(go.Pie(
        labels=[category_label(prop_name, c) for c in labels],
        values=[int(counts[c]) for c in labels],
        marker=dict(colors=[colours[c] for c in labels], line=dict(color="white", width=2)),
        pull=[0.08 if c == mine else 0 for c in labels], hole=0.55, sort=False,
        textinfo="value", hovertemplate="%{label}: %{value} elements<extra></extra>"))
    fig.update_layout(height=320, showlegend=True, margin=dict(l=10, r=10, t=10, b=10),
                      legend=dict(orientation="v", x=1, y=0.5))
    left, right = st.columns([1.2, 1], gap="medium")
    with left:
        with st.container(key="card_breakdown"):
            st.markdown(f"### {prop_name}: The Whole Table")
            show_chart(fig, config=NO_TOOLBAR, key="breakdown")
    with right:
        with st.container(key="card_members"):
            if isinstance(mine, str):
                same = df[df[col] == mine]
                st.markdown(f"### Also {category_label(prop_name, mine)}")
                chips = "".join(
                    f"<span class='pe-chip' style='background:{colours.get(mine, '#E5E7EB')}'>"
                    f"{s}</span>" for s in same["symbol"])
                st.markdown(f"<div class='pe-chips'>{chips}</div>", unsafe_allow_html=True)
                st.caption(f"{len(same)} elements share this with {row['name']}.")
            else:
                st.markdown("### No Data")
                st.caption(f"There's no {prop_name.lower()} data for {row['name']}.")


def show_deep_dive(df, ie, prop_name, z, configs, show_ionisation):
    row = element_row(df, z)
    st.markdown(f"<div class='pe-section-title'>Deep Dive: {prop_name} · {row['name']}</div>",
                unsafe_allow_html=True)

    if prop_name in CATEGORIES:
        category_cards(df, prop_name, z)
        return

    value = fmt_prop(row[PROPERTIES[prop_name]["col"]], prop_name)
    st.caption(f"{row['name']}'s {prop_name.lower()}: {value}")

    left, right = st.columns(2, gap="medium")
    with left:
        trend_card(df, prop_name, z, "period", "card_trend_period")
    with right:
        trend_card(df, prop_name, z, "group", "card_trend_group")

    left, right = st.columns([1.3, 1], gap="medium")
    with left:
        whole_table_card(df, prop_name, z)
    with right:
        rank_card(df, prop_name, z)

    # Extra graphs that only make sense for one property
    if prop_name == "Ionisation Enthalpy":
        show_ionisation(df, ie, z, configs)
    elif prop_name == "Atomic Radius":
        radius_sizes_card(df, z)
    elif prop_name == "Electronegativity":
        bond_types_card(df, z)
