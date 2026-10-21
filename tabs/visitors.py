"""The Visitors tab: how many people have opened the site, and from where."""

import datetime

import plotly.graph_objects as go
import pycountry
import streamlit as st

from core.helpers import show_chart
from core.settings import ACCENT, LINE_BLUE, NO_TOOLBAR
from core.visits import UNKNOWN, load_stats


def country_info(code):
    """'IN' -> ('India', 'IND'). Unknown codes give ('Unknown', None)."""
    if code == UNKNOWN:
        return "Unknown or local network", None
    country = pycountry.countries.get(alpha_2=code)
    if not country:
        return code, None
    return getattr(country, "common_name", None) or country.name, country.alpha_3


def stat_tile(label, value):
    return (f"<div style='flex:1;min-width:140px;padding:16px 18px;border-radius:16px;"
            f"background:#F4F6FA;border:1px solid #E3E8F0'>"
            f"<div style='font-size:12px;color:#55627A;text-transform:uppercase;"
            f"letter-spacing:.06em'>{label}</div>"
            f"<div style='font-family:Space Grotesk,Inter,sans-serif;font-size:32px;"
            f"font-weight:700;color:#0F1B2D'>{value:,}</div></div>")


@st.fragment
def visitors_tab():
    stats = load_stats()
    countries = stats["countries"]
    days = stats["days"]
    total = sum(countries.values())
    today = datetime.datetime.now(datetime.timezone.utc).date().isoformat()
    known = [c for c in countries if c != UNKNOWN]

    with st.container(key="card_visitors"):
        st.markdown("### Visitors")
        st.caption("Hey there! Share this platform with your friends so that they can learn and benefit as well! ")
        if stats.get("error"):
            st.warning("Couldn't reach the visitor database just now. Try again in a minute.")
        st.markdown(
            "<div style='display:flex;flex-wrap:wrap;gap:12px;margin:6px 0 4px'>"
            + stat_tile("Total Visits", total) + stat_tile("Today", days.get(today, 0))
            + stat_tile("Countries", len(known)) + "</div>",
            unsafe_allow_html=True)
        if total == 0:
            st.info("No visits recorded yet. Share the link!")
            return

    ranked = sorted(countries.items(), key=lambda kv: kv[1], reverse=True)
    names = [country_info(c)[0] for c, _ in ranked]

    with st.container(key="card_visitors_map"):
        st.markdown("### Where Visitors Come From")
        mapped = [(country_info(c), n) for c, n in ranked if country_info(c)[1]]
        if mapped:
            fig = go.Figure(go.Choropleth(
                locations=[info[1] for info, _ in mapped], z=[n for _, n in mapped],
                text=[info[0] for info, _ in mapped], colorscale="Blues",
                marker_line_color="white", marker_line_width=0.5, showscale=False,
                hovertemplate="%{text}: %{z} visits<extra></extra>"))
            fig.update_geos(showframe=False, showcoastlines=False, projection_type="natural earth",
                            bgcolor="rgba(0,0,0,0)", landcolor="#EEF1F6", showland=True)
            fig.update_layout(height=380, margin=dict(l=0, r=0, t=0, b=0), dragmode=False)
            show_chart(fig, config=NO_TOOLBAR, key="visit_map")
        else:
            st.caption("")

    left, right = st.columns(2, gap="medium")
    with left:
        with st.container(key="card_visitors_top"):
            st.markdown("### Top Countries")
            top = list(zip(names, [n for _, n in ranked]))[:10][::-1]
            fig = go.Figure(go.Bar(x=[n for _, n in top], y=[c for c, _ in top], orientation="h",
                                   marker_color=LINE_BLUE, text=[n for _, n in top],
                                   textposition="outside", cliponaxis=False,
                                   hovertemplate="%{y}: %{x} visits<extra></extra>"))
            fig.update_xaxes(fixedrange=True, showgrid=False, showticklabels=False)
            fig.update_yaxes(fixedrange=True)
            fig.update_layout(height=60 + 34 * len(top), margin=dict(l=10, r=30, t=10, b=10),
                              dragmode=False)
            show_chart(fig, config=NO_TOOLBAR, key="visit_top")
    with right:
        with st.container(key="card_visitors_days"):
            st.markdown("### Visits per Day")
            start = datetime.date.fromisoformat(today) - datetime.timedelta(days=29)
            dates = [start + datetime.timedelta(days=i) for i in range(30)]
            counts = [days.get(d.isoformat(), 0) for d in dates]
            fig = go.Figure(go.Bar(x=dates, y=counts,
                                   marker_color=[ACCENT if d.isoformat() == today else LINE_BLUE
                                                 for d in dates],
                                   hovertemplate="%{x|%d %b}: %{y} visits<extra></extra>"))
            fig.update_xaxes(fixedrange=True, tickformat="%d %b")
            fig.update_yaxes(fixedrange=True, gridcolor="#EEF1F6", rangemode="tozero")
            fig.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10), dragmode=False)
            show_chart(fig, config=NO_TOOLBAR, key="visit_days")
            st.caption("Last 30 days (dates in UTC).")
