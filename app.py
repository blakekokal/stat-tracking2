import streamlit as st
from copy import deepcopy
from datetime import date

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(page_title="Golf Shot Tracker", layout="centered")

# =========================================================
# TIGHT MOBILE STYLES
# =========================================================
st.markdown(
    """
    <style>
    section.main > div { padding-top: 0.4rem; }

    div.stButton > button {
        width: 100%;
        height: 3.0em;
        font-size: 1.05rem;
        margin: 0 !important;
        border-radius: 10px;
    }

    .goal button {
        background-color: #e6f4ea;
        border: 1px solid #7ac77a;
    }

    .danger button {
        background-color: #fdeaea;
        border: 1px solid #f28b82;
    }

    .neutral button {
        background-color: #f7f7f7;
        border: 1px solid #ddd;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================
# INIT STATE
# =========================================================
if "screen" not in st.session_state:
    st.session_state.screen = "SHOT_RESULT"  # for testing layout
    st.session_state.action = None
    st.session_state.payload = None
    st.session_state.undo_stack = []
    st.session_state.game = {
        "round": {"holes": 18},
        "holes": [{
            "par": 4,
            "shots": [],
            "strokes": 0,
            "gir_missed": False,
            "putts": 0,
            "prox_gir": None,
            "prox_missed_gir": None,
        }],
        "hole_index": 0,
    }

# =========================================================
# HELPERS
# =========================================================
def push_undo():
    st.session_state.undo_stack.append(
        deepcopy((st.session_state.screen, st.session_state.game))
    )

def undo():
    if st.session_state.undo_stack:
        st.session_state.screen, st.session_state.game = st.session_state.undo_stack.pop()
    st.session_state.action = None
    st.session_state.payload = None

def goto(screen):
    st.session_state.screen = screen
    st.session_state.action = None
    st.session_state.payload = None

def fire(action, payload=None):
    st.session_state.action = action
    st.session_state.payload = payload
    st.rerun()

# =========================================================
# ACTION HANDLER
# =========================================================
if st.session_state.action == "SHOT_RESULT":
    push_undo()
    hole = st.session_state.game["holes"][-1]
    result = st.session_state.payload

    hole["strokes"] += 1
    if result in ["Water", "OB"]:
        hole["strokes"] += 1

    hole["shots"].append({"result": result})

    st.session_state.action = None
    st.session_state.payload = None
    st.rerun()

elif st.session_state.action == "UNDO":
    undo()
    st.rerun()

# =========================================================
# UI — SHOT RESULT (HOLE MAP)
# =========================================================
st.title("⛳ Shot Entry")
st.markdown("### Where did the ball finish?")

# HOLE (top)
st.markdown('<div class="goal">', unsafe_allow_html=True)
if st.button("HOLE"):
    fire("SHOT_RESULT", "Hole")
st.markdown('</div>', unsafe_allow_html=True)

# GREEN + GREENSIDE BUNKER
c1, c2 = st.columns(2, gap="small")
with c1:
    st.markdown('<div class="goal">', unsafe_allow_html=True)
    if st.button("GREEN"):
        fire("SHOT_RESULT", "Green")
    st.markdown('</div>', unsafe_allow_html=True)
with c2:
    if st.button("GS BUNK"):
        fire("SHOT_RESULT", "Greenside Bunker")

# FAIRWAY CORE
c1, c2, c3 = st.columns(3, gap="small")
with c1:
    if st.button("LEFT"):
        fire("SHOT_RESULT", "Left Rough")
with c2:
    if st.button("FAIRWAY"):
        fire("SHOT_RESULT", "Fairway")
with c3:
    if st.button("RIGHT"):
        fire("SHOT_RESULT", "Right Rough")

# FAIRWAY BUNKER
if st.button("FW BUNK"):
    fire("SHOT_RESULT", "Fairway Bunker")

# PENALTIES
c1, c2 = st.columns(2, gap="small")
with c1:
    st.markdown('<div class="danger">', unsafe_allow_html=True)
    if st.button("WATER"):
        fire("SHOT_RESULT", "Water")
    st.markdown('</div>', unsafe_allow_html=True)
with c2:
    st.markdown('<div class="danger">', unsafe_allow_html=True)
    if st.button("OB"):
        fire("SHOT_RESULT", "OB")
    st.markdown('</div>', unsafe_allow_html=True)

# UNDO
st.markdown('<div class="neutral">', unsafe_allow_html=True)
if st.button("UNDO"):
    fire("UNDO")
st.markdown('</div>', unsafe_allow_html=True)
