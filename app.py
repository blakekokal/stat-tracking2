import streamlit as st
from copy import deepcopy
from datetime import date

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(page_title="Golf Shot Tracker", layout="centered")

# =========================================================
# CSS — MAX TIGHT (STREAMLIT LIMIT)
# =========================================================
st.markdown(
    """
    <style>
    section.main > div {
        padding-top: 0.4rem;
    }

    /* Tightest possible Streamlit buttons */
    div.stButton > button {
        width: 100%;
        height: 3.0em;
        font-size: 1.05rem;
        margin-top: 0.15em;
        margin-bottom: 0.15em;
        border-radius: 10px;
    }

    /* Color cues */
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
    st.session_state.screen = "ROUND_SETUP"
    st.session_state.action = None
    st.session_state.payload = None
    st.session_state.undo_stack = []
    st.session_state.game = {
        "round": {},
        "holes": [],
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
# ACTION HANDLER (NO UI)
# =========================================================
if st.session_state.action:

    if st.session_state.action == "START_ROUND":
        push_undo()
        st.session_state.game["round"] = st.session_state.payload
        goto("HOLE_SETUP")

    elif st.session_state.action == "CONFIRM_HOLE":
        push_undo()
        st.session_state.game["holes"].append({
            "par": st.session_state.payload["par"],
            "yardage": st.session_state.payload["yardage"],
            "shots": [],
            "strokes": 0,
            "gir_missed": False,
            "putts": 0,
            "prox_gir": None,
            "prox_missed_gir": None,
        })
        goto("SHOT_RESULT")

    elif st.session_state.action == "SHOT_RESULT":
        push_undo()
        hole = st.session_state.game["holes"][-1]
        result = st.session_state.payload

        hole["strokes"] += 1
        if result in ["Water", "OB"]:
            hole["strokes"] += 1

        hole["shots"].append({"result": result})
        shot_num = len(hole["shots"])

        if result == "Hole":
            goto("END_HOLE")
        elif result == "Green":
            goto("GREEN_DISTANCE")
        else:
            if shot_num <= hole["par"]:
                hole["gir_missed"] = True
            goto("DISTANCE_YARDS")

    elif st.session_state.action == "DISTANCE_YARDS":
        push_undo()
        st.session_state.game["holes"][-1]["shots"][-1]["distance"] = st.session_state.payload
        goto("SHOT_RESULT")

    elif st.session_state.action == "GREEN_DISTANCE":
        push_undo()
        hole = st.session_state.game["holes"][-1]
        feet = st.session_state.payload

        if hole["gir_missed"]:
            hole["prox_missed_gir"] = feet
        else:
            hole["prox_gir"] = feet

        hole["shots"][-1]["feet"] = feet
        goto("PUTT")

    elif st.session_state.action == "PUTT":
        push_undo()
        hole = st.session_state.game["holes"][-1]
        hole["strokes"] += 1
        hole["putts"] += 1
        if st.session_state.payload == "Hole":
            goto("END_HOLE")

    elif st.session_state.action == "NEXT_HOLE":
        push_undo()
        st.session_state.game["hole_index"] += 1
        if st.session_state.game["hole_index"] < st.session_state.game["round"]["holes"]:
            goto("HOLE_SETUP")
        else:
            goto("SUMMARY")

    elif st.session_state.action == "UNDO":
        undo()

    st.rerun()

# =========================================================
# UI
# =========================================================
st.title("⛳ Golf Shot Tracker")

# ---------------- ROUND SETUP ----------------
if st.session_state.screen == "ROUND_SETUP":
    st.markdown("### Round Setup")
    d = st.date_input("Date", date.today())
    player = st.text_input("Player Name")
    course = st.text_input("Course Name")
    holes = st.radio("Holes", [9, 18])

    if st.button("Start Round"):
        fire("START_ROUND", {
            "date": str(d),
            "player": player,
            "course": course,
            "holes": holes
        })

# ---------------- HOLE SETUP ----------------
elif st.session_state.screen == "HOLE_SETUP":
    idx = st.session_state.game["hole_index"] + 1
    st.markdown(f"### Hole {idx}")
    par = st.radio("Par", [3, 4, 5])
    yardage = st.number_input("Yardage (yards)", 50, 700, step=1)

    if st.button("Confirm Hole"):
        fire("CONFIRM_HOLE", {"par": par, "yardage": yardage})

# ---------------- SHOT RESULT (MAX-TIGHT LAYOUT) ----------------
elif st.session_state.screen == "SHOT_RESULT":
    st.markdown("### Where did the ball finish?")

    # HOLE
    st.markdown('<div class="goal">', unsafe_allow_html=True)
    if st.button("HOLE"):
        fire("SHOT_RESULT", "Hole")
    st.markdown('</div>', unsafe_allow_html=True)

    # GREEN + GS BUNK
    c1, c2 = st.columns(2, gap="small")
    with c1:
        st.markdown('<div class="goal">', unsafe_allow_html=True)
        if st.button("GREEN"):
            fire("SHOT_RESULT", "Green")
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        if st.button("GS BUNK"):
            fire("SHOT_RESULT", "Greenside Bunker")

    # LEFT / FAIRWAY / RIGHT
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

    # WATER / OB
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

# ---------------- DISTANCE ----------------
elif st.session_state.screen == "DISTANCE_YARDS":
    st.markdown("### Distance to Hole (yards)")
    yards = st.number_input("Yards", 1, 600, step=1)
    if st.button("Confirm Distance"):
        fire("DISTANCE_YARDS", yards)

# ---------------- GREEN DISTANCE ----------------
elif st.session_state.screen == "GREEN_DISTANCE":
    st.markdown("### On the Green")
    feet = st.number_input("Feet to Hole", 0, 200, step=1)
    if st.button("Confirm Distance"):
        fire("GREEN_DISTANCE", feet)

# ---------------- PUTTING ----------------
elif st.session_state.screen == "PUTT":
    st.markdown("### Putting")
    for opt in ["Left", "Right", "Short", "Long", "Hole"]:
        if st.button(opt):
            fire("PUTT", opt)

# ---------------- END HOLE ----------------
elif st.session_state.screen == "END_HOLE":
    hole = st.session_state.game["holes"][-1]
    score = hole["strokes"] - hole["par"]
    st.markdown("### Hole Complete")
    st.metric("Score vs Par", f"{score:+}")
    if st.button("Next Hole"):
        fire("NEXT_HOLE")

# ---------------- SUMMARY ----------------
elif st.session_state.screen == "SUMMARY":
    st.markdown("### Round Complete")
    st.write(st.session_state.game)
    if st.button("Restart"):
        st.session_state.clear()
        st.rerun()
