"""The IUPAC names tab."""

import pandas as pd
import streamlit as st

from core.settings import IUPAC_ROOTS
from core.helpers import element_row, iupac_name


@st.fragment
def iupac_tab(df):
    st.subheader("Naming Elements with Z > 100")
    st.write("New elements get a temporary IUPAC name built from the digits of their atomic "
             "number, until an official name is approved.")

    z = st.number_input("Atomic Number", min_value=101, max_value=999, value=104, step=1)
    name, symbol, parts = iupac_name(int(z))

    left, right = st.columns([1, 2])
    with left:
        st.markdown(
            "<div style='width:120px;height:120px;border-radius:16px;background:#E9C46A;"
            "display:flex;flex-direction:column;align-items:center;justify-content:center;color:#1F2937'>"
            f"<div style='font-size:14px'>{int(z)}</div>"
            f"<div style='font-size:42px;font-weight:700;line-height:1'>{symbol}</div></div>",
            unsafe_allow_html=True)
    with right:
        st.markdown(f"### {name}")
        st.markdown(" + ".join(f"**{d}** → {p}" for d, p in zip(str(int(z)), parts)) + " + **ium**")
        if int(z) <= df["atomic_number"].max():
            official = element_row(df, int(z))
            st.success(f"Official name today: **{official['name']} ({official['symbol']})**")
        else:
            st.info("Not discovered yet, so this temporary name is all it has.")

    st.markdown("**Digit Roots**")
    roots = "".join(
        f"<div style='padding:8px;border-radius:8px;background:rgba(127,127,127,0.12);text-align:center'>"
        f"<div style='font-size:18px;font-weight:700'>{d}</div><div>{r}</div></div>"
        for d, r in enumerate(IUPAC_ROOTS))
    st.markdown(f"<div style='display:grid;grid-template-columns:repeat(5,1fr);gap:8px'>{roots}</div>",
                unsafe_allow_html=True)
    st.caption("Rules: 'bi' and 'tri' drop their final i before 'ium' (bium, trium), and "
               "'enn' drops an n before 'nil' (ennil). The symbol is the first letter of each root.")

    st.markdown("**Elements 101–118: temporary vs official names**")
    heavy = df[df["atomic_number"].between(101, 118)]
    table = pd.DataFrame({
        "Z": heavy["atomic_number"],
        "IUPAC name": [iupac_name(z_)[0] for z_ in heavy["atomic_number"]],
        "Symbol": [iupac_name(z_)[1] for z_ in heavy["atomic_number"]],
        "Official name": heavy["name"],
        "Official symbol": heavy["symbol"],
    })
    st.dataframe(table, hide_index=True)
