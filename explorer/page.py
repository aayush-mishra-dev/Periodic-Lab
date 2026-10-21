"""The Explorer tab: puts the table, element card, atom and graphs together."""

import streamlit as st

from core.data import AVAILABLE_SECTIONS, CONFIGS, DF, IE
from core.helpers import element_options, show_chart
from core.settings import NO_TOOLBAR
from explorer.atom import show_atom, show_ionisation
from explorer.card import show_card
from explorer.legend import show_legend
from explorer.table import table_figure
from explorer.trends import show_deep_dive

TABLE_CLICK_LAYER = 2      # the invisible clickable squares are the 3rd layer of the table


def pick_one(label_text, options, key):
    if hasattr(st, "segmented_control"):
        return st.segmented_control(label_text, options, default=options[0], key=key) or options[0]
    return st.radio(label_text, options, horizontal=True, key=key)


def pick_wrapping(label_text, options, key):
    if hasattr(st, "pills"):
        return st.pills(label_text, options, default=options[0], key=key) or options[0]
    return st.radio(label_text, options, horizontal=True, key=key)


def jump_to_search():
    choice = st.session_state.get("search")
    if choice:
        st.session_state.selected_z = int(choice.split(" ")[0])
        st.session_state.search = None


def read_table_click(order):
    """Check whether an element was just clicked, before drawing anything.
    Doing this first means one quick redraw per click instead of two.
    There are two tables (full size and phone size), so check both."""
    for key in ("table", "table_compact"):
        state = st.session_state.get(key)
        if not state:
            continue
        points = [p for p in state["selection"]["points"]
                  if p.get("curve_number") == TABLE_CLICK_LAYER]
        if points:
            idx = points[0]["point_index"]
            if idx != st.session_state.get(f"last_click_{key}"):
                st.session_state[f"last_click_{key}"] = idx
                st.session_state.selected_z = order[idx]


@st.fragment
def explorer_tab():
    """A fragment: clicking in here only redraws this tab, not the whole app."""
    df = DF
    order = list(df["atomic_number"])
    read_table_click(order)
    z = st.session_state.selected_z

    with st.container(key="card_controls"):
        top_left, top_mid, top_right = st.columns([3, 2, 1], vertical_alignment="bottom")
        with top_left:
            section = pick_one("Show", list(AVAILABLE_SECTIONS), key="section")
        with top_mid:
            st.selectbox("Find an Element", element_options(df), index=None,
                         placeholder="Type a name, symbol or number…",
                         key="search", on_change=jump_to_search)
        with top_right:
            show_arrows = st.toggle("Trend Arrows", value=True)
        prop_name = pick_wrapping("Colour the Table By", AVAILABLE_SECTIONS[section],
                                  key=f"prop_{section}")

    with st.container(key="card_table"):
        # Two versions of the table. The page's style shows the big one on wide screens
        # and the small one on phones, so the right one appears without any guessing.
        with st.container(key="tablewrap_full"):
            fig, _ = table_figure(df, prop_name, show_arrows, z)
            show_chart(fig, on_select="rerun", selection_mode="points", key="table",
                       config=NO_TOOLBAR)
        with st.container(key="tablewrap_compact"):
            small, _ = table_figure(df, prop_name, False, z, compact=True)
            show_chart(small, on_select="rerun", selection_mode="points",
                       key="table_compact", config=NO_TOOLBAR)
            st.caption("Tap an element to select it. Turn your phone sideways for a bigger table.")
        show_legend(df, prop_name, show_arrows)

    left, right = st.columns([1, 1], gap="medium")
    with left:
        show_card(df, z, prop_name)
    with right:
        show_atom(df, z, CONFIGS)

    show_deep_dive(df, IE, prop_name, z, CONFIGS, show_ionisation)
