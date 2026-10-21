"""The History tab: how the periodic table was built, and the stories behind the elements."""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from core.data import DF
from core.helpers import show_chart
from core.settings import ACCENT, LINE_BLUE, NO_TOOLBAR

MILESTONES = [
    (1669, "Brand finds phosphorus"),
    (1789, "Lavoisier's list"),
    (1829, "Döbereiner's triads"),
    (1862, "Telluric screw"),
    (1865, "Newlands' octaves"),
    (1869, "Mendeleev's table"),
    (1870, "Meyer's curve"),
    (1894, "Noble Gases"),
    (1913, "Moseley"),
    (1945, "Seaborg's actinides"),
    (2016, "Period 7 complete"),
]

NAMED_AFTER_PEOPLE = [
    ("Cm", "Curium", "Marie and Pierre Curie, pioneers of radioactivity"),
    ("Es", "Einsteinium", "Albert Einstein"),
    ("Fm", "Fermium", "Enrico Fermi, who built the first nuclear reactor"),
    ("Md", "Mendelevium", "Dmitri Mendeleev, creator of the periodic table"),
    ("No", "Nobelium", "Alfred Nobel, founder of the Nobel Prizes"),
    ("Lr", "Lawrencium", "Ernest Lawrence, inventor of the cyclotron"),
    ("Rf", "Rutherfordium", "Ernest Rutherford, who discovered the nucleus"),
    ("Sg", "Seaborgium", "Glenn Seaborg, who was still alive when it was named"),
    ("Bh", "Bohrium", "Niels Bohr, of the Bohr model of the atom"),
    ("Mt", "Meitnerium", "Lise Meitner, who explained nuclear fission"),
    ("Rg", "Roentgenium", "Wilhelm Röntgen, discoverer of X-rays"),
    ("Cn", "Copernicium", "Nicolaus Copernicus, who put the Sun at the centre"),
    ("Fl", "Flerovium", "Georgy Flerov, nuclear physicist"),
    ("Og", "Oganesson", "Yuri Oganessian, still alive and still making elements"),
]

NAMED_AFTER_PLACES = [
    ("Mg", "Magnesium", "Magnesia, a region of Greece"),
    ("Cu", "Copper", "Cyprus, the ancient source of copper"),
    ("Sr", "Strontium", "Strontian, a village in Scotland"),
    ("Sc", "Scandium", "Scandinavia"),
    ("Ga", "Gallium", "Gallia, the Latin name for France"),
    ("Ge", "Germanium", "Germany"),
    ("Ru", "Ruthenium", "Ruthenia, a Latin name for Russia"),
    ("Ho", "Holmium", "Holmia, the Latin name for Stockholm"),
    ("Tm", "Thulium", "Thule, a mythical land in the far north"),
    ("Lu", "Lutetium", "Lutetia, the Latin name for Paris"),
    ("Hf", "Hafnium", "Hafnia, the Latin name for Copenhagen"),
    ("Po", "Polonium", "Poland, Marie Curie's home country"),
    ("Fr", "Francium", "France"),
    ("Eu", "Europium", "Europe"),
    ("Am", "Americium", "The Americas"),
    ("Bk", "Berkelium", "Berkeley, California"),
    ("Cf", "Californium", "California"),
    ("Db", "Dubnium", "Dubna, Russia"),
    ("Hs", "Hassium", "Hesse, a state in Germany"),
    ("Ds", "Darmstadtium", "Darmstadt, Germany"),
    ("Nh", "Nihonium", "Nihon, Japanese for Japan"),
    ("Mc", "Moscovium", "The Moscow region"),
    ("Ts", "Tennessine", "Tennessee, USA"),
]


def chart(fig, key, height=340):
    fig.update_layout(height=height, dragmode=False, margin=dict(l=10, r=10, t=10, b=10))
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True, gridcolor="#EEF1F6")
    show_chart(fig, config=NO_TOOLBAR, key=key)


def timeline_figure():
    xs = list(range(len(MILESTONES)))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[-0.5, len(xs) - 0.5], y=[0, 0], mode="lines",
                             line=dict(color="#C4CCD8", width=3), hoverinfo="skip"))
    fig.add_trace(go.Scatter(
        x=xs, y=[0] * len(xs), mode="markers",
        marker=dict(size=16, color=[ACCENT if y == 1869 else LINE_BLUE for y, _ in MILESTONES],
                    line=dict(color="white", width=2)),
        customdata=[f"{y}: {t}" for y, t in MILESTONES],
        hovertemplate="%{customdata}<extra></extra>"))
    for i, (year, title) in enumerate(MILESTONES):
        up = i % 2 == 0
        fig.add_annotation(x=i, y=0, ax=0, ay=-48 if up else 48, showarrow=True, arrowwidth=1.5,
                           arrowcolor="#C4CCD8", arrowhead=0, standoff=11,
                           text=f"<b>{year}</b><br>{title}", font=dict(size=12),
                           yanchor="bottom" if up else "top")
    fig.update_xaxes(visible=False, range=[-0.7, len(xs) - 0.3])
    fig.update_yaxes(visible=False, range=[-1, 1])
    fig.update_layout(showlegend=False)
    return fig


def vertical_timeline():
    rows = ""
    for i, (year, title) in enumerate(MILESTONES):
        colour = ACCENT if year == 1869 else LINE_BLUE
        line = "" if i == len(MILESTONES) - 1 else (
            "<div style='position:absolute;left:7px;top:18px;bottom:-14px;width:2px;"
            "background:#C4CCD8'></div>")
        rows += (f"<div style='position:relative;display:flex;gap:14px;align-items:flex-start;"
                 f"padding-bottom:14px'>{line}"
                 f"<div style='width:16px;height:16px;border-radius:50%;background:{colour};"
                 f"border:2px solid white;box-shadow:0 0 0 1px #C4CCD8;flex-shrink:0;"
                 f"margin-top:2px;position:relative;z-index:1'></div>"
                 f"<div><b>{year}</b><br><span style='font-size:14px;color:#55627A'>{title}"
                 f"</span></div></div>")
    return f"<div style='padding:4px 0 0 2px'>{rows}</div>"


def milestones(df, mass):
    st.markdown("### The Milestones")

    with st.expander("1669 · Hennig Brand Boils Urine and Finds Phosphorus"):
        st.write("Brand, a German alchemist, was trying to make gold. He boiled down huge "
                 "amounts of urine and instead got a white substance that glowed in the dark. "
                 "Phosphorus became the first element whose discoverer we know by name. "
                 "Before that, elements such as these were simply 'known since ancient times':")
        ancient = df[df["discoverers"].fillna("").str.contains("ancient", case=False)]
        st.markdown(" · ".join(f"**{s}** {n}" for s, n in zip(ancient["symbol"], ancient["name"])))

    with st.expander("1789 · Lavoisier's List of 33 'Simple Substances'"):
        st.write("Antoine Lavoisier wrote the first modern list of elements: substances that "
                 "could not be broken down any further. It had 33 entries. Most were real "
                 "elements like oxygen, hydrogen and sulfur, but the list also included light "
                 "and 'caloric' (heat), and some compounds such as lime that nobody could yet "
                 "split apart.")

    with st.expander("1829 · Döbereiner's Triads"):
        st.write("Johann Döbereiner noticed groups of three similar elements. Arranged by "
                 "atomic mass, the middle element's mass was roughly the average of the other "
                 "two. Here are his triads, checked with today's atomic masses:")
        triads = []
        for a, b, c in [("Li", "Na", "K"), ("Ca", "Sr", "Ba"), ("Cl", "Br", "I")]:
            avg = (mass[a] + mass[c]) / 2
            triads.append({"Triad": f"{a}, {b}, {c}",
                           "Average of 1st and 3rd": round(avg, 2),
                           "Actual middle mass": round(mass[b], 2),
                           "Off by": f"{abs(avg - mass[b]) / mass[b] * 100:.1f}%"})
        st.dataframe(pd.DataFrame(triads), hide_index=True)
        st.caption("It worked for only a few groups, so the idea was dropped.")

    with st.expander("1862 · De Chancourtois' Telluric Screw"):
        st.write("Alexandre-Émile Béguyer de Chancourtois, a French geologist, wrote the "
                 "elements in order of atomic mass along a spiral wound around a cylinder. "
                 "Similar elements lined up one above another. It was the first arrangement to "
                 "show periodicity, but his paper left out the diagram, so chemists ignored it.")

    with st.expander("1865 · Newlands' Law of Octaves"):
        st.write("John Newlands lined up the known elements by atomic mass and saw that every "
                 "eighth element behaved like the first, like the eighth note in a musical "
                 "scale. Noble gases were not yet known, so the rows looked like this:")
        rows = [["Li", "Be", "B", "C", "N", "O", "F"],
                ["Na", "Mg", "Al", "Si", "P", "S", "Cl"],
                ["K", "Ca", "", "", "", "", ""]]
        st.dataframe(pd.DataFrame(rows, columns=[str(i) for i in range(1, 8)]), hide_index=True)
        st.caption("Na repeats Li and Cl repeats F. Beyond calcium the pattern broke down. "
                   "The Chemical Society laughed at the idea, but gave him the Davy Medal in 1887.")

    with st.expander("1869 · Mendeleev's Periodic Law"):
        st.write("Dmitri Mendeleev arranged elements by atomic mass but put chemical behaviour "
                 "first. He left gaps for elements nobody had found yet and predicted their "
                 "properties. When gallium and germanium were discovered, his predictions "
                 "were remarkably close:")
        st.dataframe(pd.DataFrame({
            "Property": ["Atomic Mass", "Density (g/cm³)", "Melting Point", "Oxide", "Chloride"],
            "Eka-aluminium (predicted)": ["68", "5.9", "Low", "E₂O₃", "ECl₃"],
            "Gallium (found 1875)": ["70", "5.94", "302.93 K", "Ga₂O₃", "GaCl₃"],
            "Eka-silicon (predicted)": ["72", "5.5", "High", "EO₂", "ECl₄"],
            "Germanium (found 1886)": ["72.6", "5.36", "1231 K", "GeO₂", "GeCl₄"],
        }), hide_index=True)

    with st.expander("1870 · Lothar Meyer's Atomic Volume Curve"):
        st.write("Working at the same time as Mendeleev, Lothar Meyer plotted each element's "
                 "atomic volume (molar mass ÷ density) against its atomic mass. The curve rose "
                 "and fell in waves, with the alkali metals at every peak. Here is the same "
                 "curve drawn from modern data, against atomic number:")
        solid = df[(df["atomic_number"] <= 86) & (df["state"] != "Gas")
                   & df["density"].notna() & df["atomic_weight"].notna()]
        volume = solid["atomic_weight"] / solid["density"]
        fig = go.Figure(go.Scatter(x=solid["atomic_number"], y=volume, mode="lines+markers",
                                   line=dict(color=LINE_BLUE, width=2.5), marker=dict(size=5),
                                   customdata=solid["name"],
                                   hovertemplate="%{customdata}: %{y:.1f} cm³/mol<extra></extra>"))
        for sym in ["Li", "Na", "K", "Rb", "Cs"]:
            r = solid[solid["symbol"] == sym]
            if not r.empty:
                fig.add_annotation(x=int(r["atomic_number"].iloc[0]),
                                   y=float((r["atomic_weight"] / r["density"]).iloc[0]),
                                   text=f"<b>{sym}</b>", showarrow=False, yshift=14,
                                   font=dict(color=ACCENT))
        fig.update_xaxes(title="Atomic Number")
        fig.update_yaxes(title="Atomic Volume (cm³/mol)")
        chart(fig, "meyer")
        st.caption("Gases are left out, because their volume is enormous and would hide the pattern.")

    with st.expander("1894–1898 · The Noble Gases: A Whole New Group"):
        st.write("Lord Rayleigh noticed that nitrogen taken from air was slightly heavier than "
                 "nitrogen made in the lab. With William Ramsay he found the reason: a new, "
                 "unreactive gas, argon. Mendeleev's table had no place for it, so an entirely "
                 "new group was added. Helium had already been spotted in the Sun's light in "
                 "1868, decades before it was found on Earth.")
        gases = df[df["symbol"].isin(["He", "Ne", "Ar", "Kr", "Xe"])]
        st.dataframe(pd.DataFrame({
            "Element": gases["name"], "Symbol": gases["symbol"],
            "Found on Earth": gases["discovery_year"].astype("Int64"),
            "Discovered by": gases["discoverers"],
        }), hide_index=True)

    with st.expander("1913 · Moseley and the Modern Periodic Law"):
        st.write("Henry Moseley fired electrons at different metals and measured the X-rays "
                 "they gave off. The X-ray frequency went up in neat, even steps, one step per "
                 "proton. This showed that the true order comes from the atomic number, not "
                 "the atomic mass. Moseley was killed at Gallipoli in 1915, aged 27. Ordering "
                 "by mass puts these pairs the wrong way round:")
        by_z = df.sort_values("atomic_number")
        pairs = []
        rows = by_z[["atomic_number", "symbol", "atomic_weight"]].values
        for (z1, s1, m1), (z2, s2, m2) in zip(rows[:-1], rows[1:]):
            if z2 <= 92 and pd.notna(m1) and pd.notna(m2) and m1 > m2:
                pairs.append({"Pair": f"{s1} → {s2}", "Z": f"{int(z1)} → {int(z2)}",
                              "Atomic Mass": f"{m1:.2f} → {m2:.2f}"})
        st.dataframe(pd.DataFrame(pairs), hide_index=True)
        st.caption("Mendeleev had already swapped Te and I by hand to keep them in the right groups.")

    with st.expander("1945 · Seaborg Moves the Actinides"):
        st.write("Glenn Seaborg, working on the first man-made elements, realised that thorium, "
                 "uranium and the elements after them form a series like the lanthanoids. He "
                 "moved them into their own row at the bottom of the table, which is the layout "
                 "used today. Colleagues warned it would ruin his reputation. Instead it became part of "
                 "the work that won him the 1951 Nobel Prize in Chemistry, and element 106 was "
                 "later named seaborgium in his honour.")

    with st.expander("2016 · Period 7 Is Complete"):
        st.write("IUPAC approved the names of the last four elements discovered, filling every "
                 "gap in the seventh row:")
        st.dataframe(pd.DataFrame({
            "Z": [113, 115, 117, 118],
            "Name": ["Nihonium (Nh)", "Moscovium (Mc)", "Tennessine (Ts)", "Oganesson (Og)"],
            "Named after": ["Nihon, Japanese for Japan", "The Moscow region",
                            "Tennessee, USA", "Physicist Yuri Oganessian"],
        }), hide_index=True)
        st.caption("Element 119 has not been made yet. Its temporary name would be ununennium (Uue).")


def name_stories(df):
    st.markdown("### Stories Behind the Names")
    names = dict(zip(df["symbol"], df["name"]))

    with st.expander(f"Named After Scientists ({len(NAMED_AFTER_PEOPLE)} elements)"):
        st.dataframe(pd.DataFrame(
            [{"Element": f"{n} ({s})", "Named after": who} for s, n, who in NAMED_AFTER_PEOPLE]),
            hide_index=True)
        st.caption("Only two elements have been named after people who were alive at the time: "
                   "seaborgium and oganesson.")

    with st.expander(f"Named After Places ({len(NAMED_AFTER_PLACES)} elements)"):
        st.dataframe(pd.DataFrame(
            [{"Element": f"{names.get(s, n)} ({s})", "Named after": where}
             for s, n, where in NAMED_AFTER_PLACES]),
            hide_index=True)

    with st.expander("Four Elements from One Small Village: Ytterby"):
        st.write("A quarry near the village of Ytterby, in Sweden, produced an unusual black "
                 "mineral. Chemists kept finding new elements in it, and four of them are named "
                 "after the village:")
        st.markdown("**Yttrium (Y)** · **Terbium (Tb)** · **Erbium (Er)** · **Ytterbium (Yb)**")
        st.caption("No other place on Earth has given its name to as many elements.")


def discovery_numbers(df):
    st.markdown("### Discovery in Numbers")
    years = df["discovery_year"]

    with st.expander("How Many Elements Were Known Over Time"):
        ancient = df["discoverers"].fillna("").str.contains("ancient", case=False)
        if not ancient.any():
            ancient = years.isna()
        timeline = list(range(1650, 2026))
        counts = [int(ancient.sum() + (years <= y).sum()) for y in timeline]
        known_1869 = counts[timeline.index(1869)]
        fig = go.Figure(go.Scatter(x=timeline, y=counts, mode="lines", line_shape="hv",
                                   line=dict(color=LINE_BLUE, width=3),
                                   hovertemplate="%{x}: %{y} elements<extra></extra>"))
        fig.add_vline(x=1869, line=dict(color=ACCENT, width=2, dash="dash"))
        fig.add_annotation(x=1869, y=known_1869,
                           text=f"Mendeleev's table (1869):<br>{known_1869} elements known",
                           showarrow=True, ax=-90, ay=-50, arrowcolor=ACCENT,
                           font=dict(color=ACCENT))
        fig.update_xaxes(title="Year")
        fig.update_yaxes(title="Elements Known")
        chart(fig, "known")

    with st.expander("Discoveries by Decade"):
        decades = (years.dropna() // 10 * 10).astype(int).value_counts().sort_index()
        best = decades.idxmax()
        fig = go.Figure(go.Bar(x=[f"{d}s" for d in decades.index], y=decades.values,
                               marker_color=[ACCENT if d == best else LINE_BLUE for d in decades.index],
                               hovertemplate="%{x}: %{y} elements<extra></extra>"))
        fig.update_yaxes(title="Elements Discovered")
        chart(fig, "decades")
        found = df[(years // 10 * 10) == best]["symbol"].tolist()
        st.caption(f"The busiest decade was the {best}s: {', '.join(found)}. New tools such as "
                   "electrolysis, spectroscopy and particle accelerators each set off a burst "
                   "of discoveries.")

    if df["discovery_location"].notna().any():
        with st.expander("Where Elements Were Discovered"):
            places = (df["discovery_location"].dropna().str.split("/").explode().str.strip()
                      .value_counts().head(10).sort_values())
            fig = go.Figure(go.Bar(x=places.values, y=places.index, orientation="h",
                                   marker_color=LINE_BLUE,
                                   hovertemplate="%{y}: %{x} elements<extra></extra>"))
            fig.update_xaxes(title="Elements Discovered")
            chart(fig, "places", height=380)
            st.caption("Sweden punches far above its size, thanks to its unusual minerals, "
                       "Ytterby among them.")


@st.fragment
def history_tab():
    df = DF
    mass = dict(zip(df["symbol"], df["atomic_weight"]))

    with st.container(key="card_history_timeline"):
        st.markdown("### How the Periodic Table Was Built")
        st.caption("From alchemy to superheavy elements. Open the milestones below for "
                   "the full story.")
        # Wide screens get the sideways timeline; phones get a top-to-bottom list,
        # because 11 labels side by side don't fit on a narrow screen
        with st.container(key="timeline_wide"):
            chart(timeline_figure(), "timeline", height=260)
        with st.container(key="timeline_narrow"):
            st.markdown(vertical_timeline(), unsafe_allow_html=True)

    milestones(df, mass)
    name_stories(df)
    discovery_numbers(df)
