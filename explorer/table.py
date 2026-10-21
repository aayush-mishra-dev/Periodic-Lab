"""The interactive periodic table: tiles, labels, trend arrows and the selected-element panel."""

import copy

import plotly.graph_objects as go
import streamlit as st

from core.data import CATEGORIES, PROPERTIES
from core.helpers import (category_label, colour_value, discrete_scale, display_group, fmt,
                          fmt_prop, position, pretty_config)
from core.settings import (ACCENT, ARROW_COLOUR, MISSING_BORDER,
                           MISSING_TEXT, NA_LABELS, WHITE, EXCEPTIONS, TRENDS)

# The empty space above the transition metals, where the selected element is shown
PANEL = dict(x0=2.62, x1=12.38, y0=0.6, y1=3.4)


def axis_labels():
    grey = dict(size=13, color="#6B7280")
    labels = [dict(x=g, y=0.12, text=str(g), font=grey) for g in range(1, 19)]
    labels += [dict(x=0.12, y=p, text=str(p), font=grey) for p in range(1, 8)]
    labels += [dict(x=3.42, y=9, text="Lanthanoids", xanchor="right", font=grey),
               dict(x=3.42, y=10, text="Actinoids", xanchor="right", font=grey)]
    for a in labels:
        a.update(xref="x", yref="y", showarrow=False)
    return labels


def trend_arrows(prop_name):
    across, down, _, _ = TRENDS[prop_name]
    arrow = dict(xref="x", yref="y", axref="x", ayref="y", text="", showarrow=True,
                 arrowhead=2, arrowsize=1, arrowwidth=4, arrowcolor=ARROW_COLOUR)
    box = dict(xref="x", yref="y", showarrow=False, font=dict(size=13, color=ARROW_COLOUR),
               bgcolor="rgba(255,255,255,0.97)", bordercolor=ARROW_COLOUR,
               borderwidth=1.5, borderpad=5)
    stacked = down.replace(" ", "<br>")
    return [
        dict(arrow, x=18.0, y=-0.72, ax=1.0, ay=-0.72),
        dict(box, x=9.5, y=-0.72, text=f"<b>Across a Period:</b> {across}"),
        dict(arrow, x=19.35, y=7.3, ax=19.35, ay=1.0),
        dict(box, x=19.35, y=4.15, text=f"<b>Down a<br>Group:</b><br>{stacked}"),
    ]


@st.cache_resource(show_spinner=False)
def base_table(prop_name, show_arrows, compact, _df):
    """Everything that doesn't change when you click an element. Built once per view.
    compact=True draws a small version that fits a phone screen."""
    df = _df

    def blank(fill):
        return [[fill] * 18 for _ in range(10)]

    base, base_text = blank(None), blank("")
    colour, text = blank(None), blank("")
    xs, ys, syms, order, hovers, missing = [], [], [], [], [], []
    categorical = prop_name in CATEGORIES

    if categorical:
        col, colours = CATEGORIES[prop_name]
        names = list(colours)
    else:
        p = PROPERTIES[prop_name]
        col = p["col"]
        cvals = {z: colour_value(v, p) for z, v in zip(df["atomic_number"], df[col])}
        valid = [c for c in cvals.values() if c is not None]
        lo, hi = min(valid), max(valid)
        if lo == hi:
            hi = lo + 1

    for row in df.itertuples(index=False):
        z = row.atomic_number
        x, y = position(z, row.group_id, row.period)
        base[y - 1][x - 1] = 0
        xs.append(x)
        ys.append(y)
        syms.append(row.symbol)
        order.append(z)
        value = getattr(row, col)

        if categorical:
            if value in colours:
                colour[y - 1][x - 1] = names.index(value)
                text[y - 1][x - 1] = f"<b>{row.symbol}</b>"
            else:
                base_text[y - 1][x - 1] = row.symbol
                missing.append((x, y))
            hovers.append(f"{row.name} (Z = {z})<br>{category_label(prop_name, value)}")
            continue

        cv = cvals[z]
        extra = ("<br><i>Exception: click to see why</i>"
                 if (prop_name, row.symbol) in EXCEPTIONS else "")
        if cv is None:
            base_text[y - 1][x - 1] = row.symbol
            missing.append((x, y))
            hovers.append(f"{row.name} (Z = {z})<br>{prop_name}: {NA_LABELS.get(prop_name, 'no data')}")
        else:
            colour[y - 1][x - 1] = cv
            if p["tile"] and not compact:
                text[y - 1][x - 1] = (f"<b>{row.symbol}</b><br><span style='font-size:11px'>"
                                      f"{fmt(value, '', p['digits'])}</span>")
            else:
                text[y - 1][x - 1] = f"<b>{row.symbol}</b>"
            hovers.append(f"{row.name} (Z = {z})<br>{prop_name}: {fmt_prop(value, prop_name)}{extra}")

    grid = dict(x=list(range(1, 19)), y=list(range(1, 11)),
                xgap=1.5 if compact else 4, ygap=1.5 if compact else 4,
                hoverinfo="skip", showscale=False,
                texttemplate="%{text}", textfont=dict(size=10.5 if compact else 18))

    fig = go.Figure()
    # Layer 0: white tile under every element (shows through when there is no data)
    fig.add_trace(go.Heatmap(z=base, text=base_text, colorscale=WHITE, zmin=0, zmax=1,
                             **{**grid, "textfont": dict(size=9.5 if compact else 17, color=MISSING_TEXT)}))
    # Layer 1: coloured tiles
    if categorical:
        fig.add_trace(go.Heatmap(z=colour, text=text,
                                 colorscale=discrete_scale(list(colours.values())),
                                 zmin=-0.5, zmax=len(colours) - 0.5, **grid))
    else:
        fig.add_trace(go.Heatmap(z=colour, text=text, colorscale="YlGnBu",
                                 zmin=lo, zmax=hi, **grid))
    # Layer 2: invisible clickable squares
    fig.add_trace(go.Scatter(
        x=xs, y=ys, mode="markers",
        marker=dict(symbol="square", size=20 if compact else 56, color="rgba(0,0,0,0)"),
        customdata=hovers, hovertemplate="%{customdata}<extra></extra>",
        showlegend=False,
    ))
    # Layer 3: orange dots on exceptions to this property only
    ex = [(x + 0.32, y - 0.32) for x, y, s in zip(xs, ys, syms) if (prop_name, s) in EXCEPTIONS]
    if ex:
        fig.add_trace(go.Scatter(
            x=[e[0] for e in ex], y=[e[1] for e in ex], mode="markers",
            marker=dict(size=5 if compact else 11, color=ACCENT,
                        line=dict(color="white", width=1 if compact else 1.5)),
            hoverinfo="skip", showlegend=False,
        ))

    shapes = [dict(type="rect", x0=x - 0.44, x1=x + 0.44, y0=y - 0.44, y1=y + 0.44,
                   line=dict(color=MISSING_BORDER, width=1.5, dash="dot"))
              for x, y in missing]
    if compact:
        for s in shapes:
            s["line"]["width"] = 0.8
        fig.update_layout(shapes=shapes)
        fig.update_xaxes(range=[0.45, 18.55], constrain="domain", visible=False, fixedrange=True)
        fig.update_yaxes(range=[10.55, 0.45], constrain="domain", scaleanchor="x",
                         constraintoward="top", visible=False, fixedrange=True)
        # Tall enough for a phone held sideways; in portrait the page trims the empty
        # space underneath, so the table always fills the screen's width
        fig.update_layout(height=480,
                          margin=dict(l=0, r=0, t=0, b=0), dragmode=False)
        return fig, order

    shapes.append(dict(type="rect", **PANEL, fillcolor="#F8FAFC",
                       line=dict(color="#E3E8F0", width=1), layer="below"))
    annotations = axis_labels()
    if show_arrows and prop_name in TRENDS:
        annotations += trend_arrows(prop_name)

    fig.update_layout(shapes=shapes, annotations=annotations)
    # Range is symmetric around the middle of the table (9.5), so the table sits centred
    fig.update_xaxes(range=[-1.1, 20.1], constrain="domain", visible=False, fixedrange=True)
    fig.update_yaxes(range=[10.6, -1.3], constrain="domain", scaleanchor="x",
                     visible=False, fixedrange=True)
    fig.update_layout(height=760, margin=dict(l=0, r=0, t=6, b=6), dragmode=False,
                      hoverlabel=dict(font_size=14))
    return fig, order


def selected_panel(row, prop_name):
    """Shapes and text for the big selected-element display inside the table."""
    z = int(row["atomic_number"])
    mass = fmt(row["atomic_weight"], "", 3)

    if prop_name in PROPERTIES:
        value = fmt_prop(row[PROPERTIES[prop_name]["col"]], prop_name)
    else:
        value = category_label(prop_name, row[CATEGORIES[prop_name][0]])
    family = row["family"] if isinstance(row.get("family"), str) else ""

    # A plain tile, so it never clashes with whatever colouring the table is showing
    shapes = [dict(type="rect", x0=2.85, x1=4.95, y0=0.82, y1=3.18, fillcolor="#FFFFFF",
                   line=dict(color="#CBD5E1", width=2))]
    dark, grey = "#0F1B2D", "#55627A"
    subtitle = (f"Period {int(row['period'])} · Group {display_group(z, row['group_id'])} · "
                f"{row['block']}-block{' · ' + family if family else ''}")
    lines = [
        # inside the big tile
        (3.9, 1.18, f"{z}", 15, "#55627A", "center"),
        (3.9, 1.98, f"<b>{row['symbol']}</b>", 50, "#0F1B2D", "center"),
        (3.9, 2.82, mass, 14, "#55627A", "center"),
        # next to it
        (5.3, 1.22, f"<b>{row['name']}</b>", 30, dark, "left"),
        (5.3, 1.82, subtitle, 14, grey, "left"),
        (5.3, 2.3, pretty_config(row["electronic_configuration"]), 17, dark, "left"),
        (5.3, 2.85, f"<b>{prop_name}: {value}</b>", 17, ACCENT, "left"),
    ]
    annotations = [dict(x=x, y=y, xref="x", yref="y", text=text, showarrow=False,
                        xanchor=anchor, font=dict(size=size, color=colour))
                   for x, y, text, size, colour, anchor in lines]
    return shapes, annotations


def table_figure(df, prop_name, show_arrows, selected_z, compact=False):
    base, order = base_table(prop_name, show_arrows, compact, df)
    fig = copy.deepcopy(base)
    row = df[df["atomic_number"] == selected_z].iloc[0]
    x, y = position(selected_z, row["group_id"], row["period"])
    outline = dict(type="rect", x0=x - 0.5, x1=x + 0.5, y0=y - 0.5, y1=y + 0.5,
                   line=dict(color=ACCENT, width=2 if compact else 3.5))
    if compact:
        fig.layout.shapes = fig.layout.shapes + (outline,)
        return fig, order
    shapes, annotations = selected_panel(row, prop_name)
    shapes.append(outline)
    fig.layout.shapes = fig.layout.shapes + tuple(shapes)
    fig.layout.annotations = fig.layout.annotations + tuple(annotations)
    return fig, order
