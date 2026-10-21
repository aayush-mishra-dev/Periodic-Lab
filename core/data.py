"""Loads the element data once, and works out which properties are available."""

import pandas as pd
import streamlit as st
from mendeleev.fetch import fetch_table

from core.settings import (
    ALL_CATEGORIES, ALL_PROPERTIES, CRYSTAL_NAMES, FAMILY_NAMES, KJ_PER_EV, SECTIONS,
    VALENCY,
)


def is_f_series(z):
    return 57 <= z <= 71 or 89 <= z <= 103



def in_f_row(z):
    return 58 <= z <= 71 or 90 <= z <= 103



def valency(z, group):
    if is_f_series(z) or group != group:     # f-block or missing group
        return None
    return VALENCY.get(int(group))



def state_at_room_temp(mp, bp):
    if pd.notna(bp) and bp < 298.15:
        return "Gas"
    if pd.notna(mp) and mp < 298.15:
        return "Liquid"
    if pd.notna(mp) or pd.notna(bp):
        return "Solid"
    return None



def load_ionisation():
    """Every ionisation energy, as rows of (atomic_number, degree, energy in eV)."""
    ie = fetch_table("ionizationenergies")
    if "degree" in ie.columns:                       # older mendeleev
        ie = ie[["atomic_number", "degree", "energy"]]
    else:                                            # newer mendeleev
        ie = pd.DataFrame({"atomic_number": ie["atomic_number"],
                           "degree": ie["ion_charge"] + 1,
                           "energy": ie["ionization_energy"]})
    return (ie.dropna().groupby(["atomic_number", "degree"], as_index=False).first()
            .sort_values(["atomic_number", "degree"]))



def add_phase_data(df):
    if "melting_point" in df.columns and df["melting_point"].notna().any():
        return df
    try:
        pt = fetch_table("phasetransitions")
        pt = pt.groupby("atomic_number")[["melting_point", "boiling_point"]].first().reset_index()
        df = df.drop(columns=[c for c in ["melting_point", "boiling_point"] if c in df.columns])
        df = df.merge(pt, on="atomic_number", how="left")
    except Exception:
        pass
    return df


@st.cache_data

def load_data():
    df = fetch_table("elements")
    df["name"] = df["name"].replace({"Aluminum": "Aluminium", "Cesium": "Caesium"})
    ie = load_ionisation()

    first = ie[ie["degree"] == 1][["atomic_number", "energy"]]
    df = df.merge(first.rename(columns={"energy": "ie1_ev"}), on="atomic_number", how="left")

    try:
        series = fetch_table("series")[["id", "name"]]
        series.columns = ["series_id", "family"]
        df = df.merge(series, on="series_id", how="left")
        df["family"] = df["family"].replace(FAMILY_NAMES).str.title()
    except Exception:
        df["family"] = None
    # Keep families matching where elements are drawn (Lu, Lr sit in the f-rows)
    df.loc[df["atomic_number"].between(58, 71), "family"] = "Lanthanoids"
    df.loc[df["atomic_number"].between(90, 103), "family"] = "Actinoids"

    df = add_phase_data(df)
    for col in ["atomic_weight", "density", "melting_point", "boiling_point",
                "abundance_crust", "discovery_year", "electron_affinity",
                "covalent_radius_pyykko", "en_pauling"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df["radius"] = df["covalent_radius_pyykko"]
    df["ie1_kj"] = df["ie1_ev"] * KJ_PER_EV
    # Electron gain enthalpy = -(electron affinity). Positive values are unreliable
    # (the extra electron is not held), so they are treated as "positive or unknown".
    ea = df["electron_affinity"]
    df["eg_kj"] = (-ea * KJ_PER_EV).where(ea >= 0)
    df["valency"] = pd.to_numeric(
        pd.Series([valency(z, g) for z, g in zip(df["atomic_number"], df["group_id"])]),
        errors="coerce")
    if "discovery_year" in df.columns:
        df["discovery_year"] = df["discovery_year"].where(df["discovery_year"] > 1000)
    if "melting_point" in df.columns:
        bp = df["boiling_point"] if "boiling_point" in df.columns else pd.Series(float("nan"), index=df.index)
        df["state"] = [state_at_room_temp(m, b) for m, b in zip(df["melting_point"], bp)]
    if "is_radioactive" in df.columns:
        df["radioactive"] = df["is_radioactive"].map(
            lambda v: None if pd.isna(v) else ("Radioactive" if v else "Stable"))
    if "lattice_structure" in df.columns:
        df["crystal"] = df["lattice_structure"].map(CRYSTAL_NAMES)

    for col in ["description", "uses", "name_origin", "discoverers", "discovery_location"]:
        if col not in df.columns:
            df[col] = None
    return df, ie


# ---------- Loaded once, then shared by every part of the app ----------

DF, IE = load_data()
CATEGORIES = {k: v for k, v in ALL_CATEGORIES.items()
              if v[0] in DF.columns and DF[v[0]].notna().any()}
PROPERTIES = {k: v for k, v in ALL_PROPERTIES.items()
              if v["col"] in DF.columns and DF[v["col"]].notna().any()}
AVAILABLE = {**CATEGORIES, **PROPERTIES}
AVAILABLE_SECTIONS = {name: [p for p in items if p in AVAILABLE]
                      for name, items in SECTIONS.items()}
AVAILABLE_SECTIONS = {name: items for name, items in AVAILABLE_SECTIONS.items() if items}
CONFIGS = dict(zip(DF["symbol"], DF["electronic_configuration"]))
