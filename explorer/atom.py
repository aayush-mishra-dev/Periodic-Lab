"""The animated atom and the successive ionisation enthalpy chart."""

import math

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from core.settings import KJ_PER_EV, NO_TOOLBAR, SHELL_COLOURS, SHELL_LETTERS
from core.helpers import chip, draw_html, element_row, shell_counts, show_chart


def nucleus_balls(cx, cy):
    """A little cluster of protons and neutrons for the nucleus."""
    balls = [(0, 0)]
    for ring, count in [(9, 6), (18, 11)]:
        for k in range(count):
            a = 2 * math.pi * k / count + ring
            balls.append((ring * math.cos(a), ring * math.sin(a)))
    out = ""
    for i, (dx, dy) in enumerate(balls):
        fill = "#E4572E" if i % 2 == 0 else "#94A3B8"
        out += (f"<circle cx='{cx + dx:.1f}' cy='{cy + dy:.1f}' r='6.2' fill='{fill}' "
                f"stroke='#0F1B2D' stroke-width='0.8'/>")
    return out



def atom_html(shells, symbol):
    size, c = 380, 190
    n = len(shells)
    inner, outer = 40, 176
    step = min(36, (outer - inner) / max(n, 1))

    orbits = ""
    for i, (_, count) in enumerate(shells.items()):
        r = inner + step * (i + 1)
        valence = i == n - 1
        colour = "#FDBA74" if valence else "#93C5FD"
        duration = 7 + i * 4
        direction = "normal" if i % 2 == 0 else "reverse"
        electrons = "".join(
            f"<circle cx='{c + r * math.cos(2 * math.pi * k / count - math.pi / 2):.1f}' "
            f"cy='{c + r * math.sin(2 * math.pi * k / count - math.pi / 2):.1f}' r='5.5' "
            f"fill='{colour}' filter='url(#pe-glow)'/>"
            for k in range(count))
        orbits += (f"<circle cx='{c}' cy='{c}' r='{r:.1f}' class='pe-track'/>"
                   f"<g class='pe-orbit' style='animation-duration:{duration}s;"
                   f"animation-direction:{direction}'>{electrons}</g>")

    # Drawn straight into the page (no iframe), so it doesn't flash white when it updates.
    # Class names start with "pe-" so they can't clash with anything else on the page.
    return f"""
<style>
  .pe-atom {{ display: flex; justify-content: center; }}
  .pe-atom-wrap {{ width: 100%; max-width: 400px; background: #0F1B2D; border-radius: 20px; }}
  .pe-atom svg {{ width: 100%; height: auto; display: block; }}
  .pe-track {{ fill: none; stroke: rgba(255,255,255,0.16); stroke-width: 1.2; }}
  .pe-orbit, .pe-nucleus {{ transform-box: view-box; transform-origin: {c}px {c}px; }}
  .pe-orbit {{ animation-name: pe-spin; animation-timing-function: linear;
               animation-iteration-count: infinite; }}
  .pe-nucleus {{ animation: pe-pulse 3s ease-in-out infinite; }}
  @media (hover: hover) and (pointer: fine) {{ .pe-atom-wrap:hover .pe-orbit, .pe-atom-wrap:hover .pe-nucleus {{ animation-play-state: paused; }} }}
  @keyframes pe-spin {{ to {{ transform: rotate(360deg); }} }}
  @keyframes pe-pulse {{ 50% {{ transform: scale(1.07); }} }}
  @media (prefers-reduced-motion: reduce) {{ .pe-orbit, .pe-nucleus {{ animation: none; }} }}
</style>
<div class="pe-atom"><div class="pe-atom-wrap">
  <svg viewBox="0 0 {size} {size}" role="img" aria-label="Animated shell model of {symbol}">
    <defs>
      <filter id="pe-glow" x="-100%" y="-100%" width="300%" height="300%">
        <feGaussianBlur stdDeviation="2.4" result="b"/>
        <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
      </filter>
    </defs>
    {orbits}
    <g class="pe-nucleus">{nucleus_balls(c, c)}</g>
    <text x="{c}" y="{c + 7}" text-anchor="middle" font-family="Space Grotesk, Inter, sans-serif"
          font-size="22" font-weight="700" fill="#FFFFFF" stroke="#0F1B2D" stroke-width="4"
          paint-order="stroke">{symbol}</text>
  </svg>
</div></div>
"""


def ie_figure(energies, shells):
    # Electrons come off the outermost shell first
    removal = []
    for n in sorted(shells, reverse=True):
        removal += [n] * shells[n]
    outer = max(shells)

    fig = go.Figure()
    for n in sorted(set(removal[:len(energies)]), reverse=True):
        idx = [i for i in range(len(energies)) if i < len(removal) and removal[i] == n]
        fig.add_trace(go.Bar(
            x=[i + 1 for i in idx], y=[energies[i] * KJ_PER_EV for i in idx],
            name=f"{SHELL_LETTERS[n - 1]} shell (n = {n})",
            marker_color="#F97316" if n == outer else SHELL_COLOURS[(n - 1) % len(SHELL_COLOURS)],
            hovertemplate="Electron %{x}: %{y:,.0f} kJ/mol<extra></extra>",
        ))
    step = 1 if len(energies) <= 12 else (2 if len(energies) <= 20 else 5)
    fig.update_xaxes(title="Electron Removed (1st, 2nd, 3rd …)", dtick=step, fixedrange=True)
    fig.update_yaxes(title="kJ/mol (Log Scale)", type="log", fixedrange=True, gridcolor="#EEF1F6")
    fig.update_layout(height=300, plot_bgcolor="white", barmode="overlay", dragmode=False,
                      margin=dict(l=10, r=10, t=10, b=10),
                      legend=dict(orientation="h", y=1.15, x=0))
    return fig



def show_atom(df, z, configs):
    row = element_row(df, z)
    shells = shell_counts(row["electronic_configuration"], configs)
    neutrons = (round(row["atomic_weight"]) - z) if pd.notna(row["atomic_weight"]) else None

    with st.container(key="card_atom"):
        st.markdown("### Inside the Atom")
        st.caption(f"{row['name']}: electrons orbiting the nucleus, shell by shell. "
                   "Orange electrons are the outermost (valence) shell. On a computer, hover to pause.")
        draw_html(atom_html(shells, row["symbol"]))
        shells_html = "".join(chip(str(cnt), SHELL_LETTERS[n - 1]) for n, cnt in shells.items())
        facts = chip(str(z), "Protons") + chip(str(z), "Electrons")
        if neutrons is not None:
            facts += chip(f"≈ {neutrons}", "Neutrons")
        facts += chip(str(list(shells.values())[-1]), "Valence Electrons")
        st.markdown(f"<div style='margin-top:8px'>{shells_html}</div><div>{facts}</div>",
                    unsafe_allow_html=True)


def show_ionisation(df, ie, z, configs):
    row = element_row(df, z)
    shells = shell_counts(row["electronic_configuration"], configs)
    energies = ie[ie["atomic_number"] == z].sort_values("degree")["energy"].tolist()[:30]
    with st.container(key="card_ie"):
        st.markdown("### Successive Ionisation Enthalpies")
        if len(energies) >= 2:
            show_chart(ie_figure(energies, shells), config=NO_TOOLBAR, key="ies")
            st.caption("Each bar is the energy to pull off one more electron. A big jump means "
                       "the next electron comes from a shell closer to the nucleus. That is why "
                       "sodium forms Na⁺ but never Na²⁺.")
        else:
            st.caption("Not enough ionisation data for this element.")
