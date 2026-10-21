"""The element card with every property and a short write-up."""

import pandas as pd
import streamlit as st

from core.settings import ACCENT, EXCEPTIONS
from core.data import PROPERTIES
from core.helpers import element_header, element_row, fmt_prop, pretty_config, stat


def exception_box(prop_name, text):
    return ("<div style='margin-top:12px;padding:10px 12px;border-radius:10px;"
            "background:rgba(228,87,46,0.12)'>"
            f"<div style='font-size:12px;font-weight:700;color:{ACCENT}'>Exception · {prop_name}</div>"
            f"<div style='font-size:13px;margin-top:2px'>{text}</div></div>")



def show_card(df, z, prop_name):
    row = element_row(df, z)

    badges = []
    for col in ["state", "radioactive", "crystal"]:
        if isinstance(row.get(col), str):
            badges.append(row[col])
    badge_html = "".join(
        f"<span style='display:inline-block;font-size:12px;padding:3px 9px;margin:0 6px 6px 0;"
        f"border-radius:12px;background:rgba(127,127,127,0.15)'>{b}</span>" for b in badges)

    cells = "".join(stat(name, fmt_prop(row[p["col"]], name)) for name, p in PROPERTIES.items())
    note = (exception_box(prop_name, EXCEPTIONS[(prop_name, row["symbol"])])
            if (prop_name, row["symbol"]) in EXCEPTIONS else "")

    with st.container(key="card_element"):
        st.markdown(element_header(row), unsafe_allow_html=True)
        st.markdown(f"<div style='margin-top:10px'>{badge_html}</div>", unsafe_allow_html=True)
        st.markdown(f"**Electronic Configuration**  \n`{pretty_config(row['electronic_configuration'])}`")
        st.markdown(
            "<div style='display:grid;grid-template-columns:1fr 1fr;gap:14px 12px;margin-top:6px'>"
            + cells + "</div>" + note,
            unsafe_allow_html=True,
        )

        with st.expander("About This Element"):
            if isinstance(row["description"], str):
                st.write(row["description"])
            if isinstance(row["uses"], str):
                st.markdown(f"**Uses:** {row['uses']}")
            if isinstance(row["name_origin"], str):
                st.markdown(f"**Name:** {row['name_origin']}")
            found = []
            if isinstance(row["discoverers"], str):
                found.append(row["discoverers"].rstrip("."))
            if isinstance(row["discovery_location"], str):
                found.append(row["discovery_location"])
            if pd.notna(row.get("discovery_year")):
                found.append(str(int(row["discovery_year"])))
            if found:
                st.markdown(f"**Discovered:** {', '.join(found)}")
