"""Colours, property definitions, trends, exceptions and other fixed settings."""

APP_NAME = "Periodic Lab"

GREY_HEX = "#E5E7EB"

GREY = [[0, GREY_HEX], [1, GREY_HEX]]

WHITE = [[0, "#FFFFFF"], [1, "#FFFFFF"]]

MISSING_BORDER = "#9CA3AF"

MISSING_TEXT = "#6B7280"

YLGNBU = ["#ffffd9", "#edf8b1", "#c7e9b4", "#7fcdbb", "#41b6c4",
          "#1d91c0", "#225ea8", "#253494", "#081d58"]

ARROW_COLOUR = "#1F2937"

ACCENT = "#E4572E"

LINE_BLUE = "#225ea8"

SHELL_COLOURS = ["#225ea8", "#41b6c4", "#8AB17D", "#E9C46A", "#F4A261", "#E76F51", "#B5A8E0"]

NO_TOOLBAR = {"displayModeBar": False, "scrollZoom": False, "doubleClick": False}

KJ_PER_EV = 96.485

SHELL_LETTERS = "KLMNOPQ"

BLOCK_COLOURS = {"s": "#F4A261", "p": "#E9C46A", "d": "#8AB17D", "f": "#7FB3D5"}


FAMILY_COLOURS = {
    "Alkali Metals": "#E76F51",
    "Alkaline Earth Metals": "#F4A261",
    "Transition Metals": "#E9C46A",
    "Post-Transition Metals": "#A8DADC",
    "Metalloids": "#8AB17D",
    "Other Non-Metals": "#2A9D8F",
    "Halogens": "#7FB3D5",
    "Noble Gases": "#B5A8E0",
    "Lanthanoids": "#F2B5D4",
    "Actinoids": "#D4A5A5",
}


FAMILY_NAMES = {"Nonmetals": "Other Non-Metals", "Poor metals": "Post-Transition Metals",
                "Lanthanides": "Lanthanoids", "Actinides": "Actinoids"}


STATE_COLOURS = {"Solid": "#C9B79C", "Liquid": "#7FB3D5", "Gas": "#F2B5D4"}


RADIOACTIVE_COLOURS = {"Stable": "#8AB17D", "Radioactive": "#E76F51"}


CRYSTAL_NAMES = {
    "BCC": "Body-Centred Cubic", "FCC": "Face-Centred Cubic", "HEX": "Hexagonal",
    "SC": "Simple Cubic", "CUB": "Cubic (Other)", "DIA": "Diamond",
    "RHL": "Rhombohedral", "TET": "Tetragonal", "ORC": "Orthorhombic", "MCL": "Monoclinic",
}


CRYSTAL_COLOURS = {
    "Body-Centred Cubic": "#E76F51", "Face-Centred Cubic": "#F4A261", "Hexagonal": "#E9C46A",
    "Simple Cubic": "#A8DADC", "Cubic (Other)": "#8AB17D", "Diamond": "#2A9D8F",
    "Rhombohedral": "#7FB3D5", "Tetragonal": "#B5A8E0", "Orthorhombic": "#F2B5D4",
    "Monoclinic": "#D4A5A5",
}


VALENCY = {1: 1, 2: 2, 13: 3, 14: 4, 15: 3, 16: 2, 17: 1, 18: 0}


# label: (column, {category: colour})
ALL_CATEGORIES = {
    "Block": ("block", BLOCK_COLOURS),
    "Family": ("family", FAMILY_COLOURS),
    "State at 25 °C": ("state", STATE_COLOURS),
    "Radioactivity": ("radioactive", RADIOACTIVE_COLOURS),
    "Crystal Structure": ("crystal", CRYSTAL_COLOURS),
}


def prop(col, unit="", digits=0, flip=False, log=False, tile=True):
    """Settings for one numeric property."""
    return dict(col=col, unit=unit, digits=digits, flip=flip, log=log, tile=tile)


ALL_PROPERTIES = {
    "Atomic Radius": prop("radius", "pm"),
    "Ionisation Enthalpy": prop("ie1_kj", "kJ/mol"),
    "Electronegativity": prop("en_pauling", digits=2),
    "Electron Gain Enthalpy": prop("eg_kj", "kJ/mol", flip=True),
    "Valency": prop("valency"),
    "Atomic Mass": prop("atomic_weight", "u", 1),
    "Density": prop("density", "g/cm³", None),
    "Melting Point": prop("melting_point", "K"),
    "Boiling Point": prop("boiling_point", "K"),
    "Abundance in Crust": prop("abundance_crust", "mg/kg", None, log=True, tile=False),
    "Year Discovered": prop("discovery_year"),
}


SECTIONS = {
    "Classification": ["Block", "Family", "State at 25 °C", "Radioactivity", "Crystal Structure"],
    "Trends": ["Atomic Radius", "Ionisation Enthalpy", "Electronegativity",
                        "Electron Gain Enthalpy", "Valency"],
    "Physical": ["Atomic Mass", "Density", "Melting Point", "Boiling Point",
                           "Abundance in Crust", "Year Discovered"],
}


# label: (across a period, down a group, diagonal symbol, overall trend)
TRENDS = {
    "Atomic Radius": ("decreases", "increases", "↙", "largest atoms towards the bottom-left"),
    "Ionisation Enthalpy": ("increases", "decreases", "↗", "highest towards the top-right"),
    "Electronegativity": ("increases", "decreases", "↗", "highest towards the top-right (F)"),
    "Electron Gain Enthalpy": ("more negative", "less negative", "↗",
                               "most negative towards the top-right"),
}


# (property, symbol): why this element breaks the trend
EXCEPTIONS = {
    ("Ionisation Enthalpy", "B"):
        "Lower than Be, even though the trend says it should be higher. B loses a 2p electron, "
        "which is higher in energy and shielded by the filled 2s, so it is easier to remove "
        "than Be's 2s electron.",
    ("Ionisation Enthalpy", "O"):
        "Lower than N. Nitrogen's half-filled 2p³ is extra stable. In oxygen, two electrons "
        "share one 2p orbital, and their repulsion makes one of them easier to remove.",
    ("Ionisation Enthalpy", "Al"):
        "Lower than Mg, for the same reason as B: Al loses a 3p electron, which is easier to "
        "remove than Mg's 3s electron.",
    ("Ionisation Enthalpy", "S"):
        "Lower than P, for the same reason as O: phosphorus has a stable half-filled 3p³, "
        "while sulfur has a paired 3p electron that is pushed out more easily.",
    ("Electron Gain Enthalpy", "F"):
        "Less negative than Cl, even though F is above it. Fluorine's 2p subshell is very "
        "small and crowded, so the incoming electron is strongly repelled.",
    ("Atomic Radius", "Ga"):
        "About the same size as Al (slightly smaller here) despite having an extra shell. "
        "The ten 3d electrons shield the nucleus poorly, so the outer electrons are pulled in "
        "harder.",
    ("Electronegativity", "Ga"):
        "Higher than Al above it. Poor shielding by the 3d electrons makes the nucleus pull "
        "harder on bonding electrons.",
    ("Atomic Radius", "Hf"):
        "Almost the same size as Zr above it. The fourteen 4f electrons of the lanthanoids "
        "shield poorly, shrinking the atoms that follow: the lanthanoid contraction.",
    ("Melting Point", "Ga"):
        "Melts at about 30 °C, low enough to melt in your hand, even though its neighbours "
        "melt far higher. Gallium's unusual crystal is made of loosely held Ga₂ pairs.",
    ("Melting Point", "Hg"):
        "The only metal that is liquid at room temperature. Its 6s electrons are held so "
        "tightly (a relativistic effect) that they barely take part in metallic bonding.",
}


NOTES = {
    "Family": "Elements in the same family have similar chemistry.",
    "State at 25 °C": "Worked out from each element's melting and boiling points.",
    "Radioactivity": "Radioactive elements have no stable isotopes.",
    "Crystal Structure": "How the atoms pack together in the solid element.",
    "Atomic Radius": "Covalent radius (Pyykkö). Darker = larger atom.",
    "Ionisation Enthalpy": "First ionisation enthalpy. Darker = harder to remove an electron.",
    "Electronegativity": "Pauling scale. Darker = pulls shared electrons more strongly.",
    "Electron Gain Enthalpy": "Darker = more negative, so more energy released on gaining an electron.",
    "Valency": "Common valency of main-group elements.",
    "Atomic Mass": "Darker = heavier atom.",
    "Density": "Darker = denser.",
    "Melting Point": "In kelvin (subtract 273 for °C). Darker = higher melting point.",
    "Boiling Point": "In kelvin (subtract 273 for °C). Darker = higher boiling point.",
    "Abundance in Crust": "Log scale: each step in colour is roughly ten times more abundant.",
    "Year Discovered": "Darker = discovered more recently.",
}


NA_LABELS = {
    "Valency": "Variable (d/f-block)",
    "Year Discovered": "Known since ancient times",
    "Electron Gain Enthalpy": "Positive or unknown",
}


IUPAC_ROOTS = ["nil", "un", "bi", "tri", "quad", "pent", "hex", "sept", "oct", "enn"]
