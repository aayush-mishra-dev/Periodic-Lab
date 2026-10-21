import streamlit as st

from core.settings import APP_NAME                      # noqa: E402

st.set_page_config(page_title=APP_NAME, page_icon="⚛️", layout="wide")

from core.data import AVAILABLE, DF                     # noqa: E402  (loads the data once)
from core.style import apply_style, footer, touch_fix   # noqa: E402
from explorer.page import explorer_tab                  # noqa: E402
from tabs.compare import compare_tab                    # noqa: E402
from tabs.history import history_tab                    # noqa: E402
from tabs.iupac import iupac_tab                        # noqa: E402
from tabs.quiz import quiz_tab                          # noqa: E402
from tabs.visitors import visitors_tab                  # noqa: E402
from core.visits import record_visit                    # noqa: E402

if "selected_z" not in st.session_state:
    st.session_state.selected_z = 26                    # start on Iron

apply_style(len(DF), len(AVAILABLE))
touch_fix()
record_visit()                                          # counts this visit once

explorer, compare, quiz, iupac, history, visitors = st.tabs([
    ":material/grid_view: Explorer",
    ":material/compare_arrows: Compare",
    ":material/quiz: Quiz",
    ":material/badge: IUPAC Names",
    ":material/history_edu: History",
    ":material/public: Visitors",
])
with explorer:
    explorer_tab()
with compare:
    with st.container(key="card_compare"):
        compare_tab(DF)
with quiz:
    quiz_tab(DF)
with iupac:
    with st.container(key="card_iupac"):
        iupac_tab(DF)
with history:
    history_tab()
with visitors:
    visitors_tab()

footer()
