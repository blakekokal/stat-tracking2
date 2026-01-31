import streamlit as st
from copy import deepcopy
from datetime import date

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(page_title="Golf Shot Tracker", layout="centered")

# =========================================================
# STYLES (BIG BUTTONS, MOBILE SAFE)
# =========================================================
st.markdown(
    """
    <style>
    div.stButton > button {
        width: 100%;
        height: 3.8em;
        font-size: 1.15rem;
        margin-top: 0.5em;
        margin-bottom: 0.5em;
        border-radius: 12px;
    }
    .undo-btn button {
        background-color: #f2f2f2;
        color: #333;
        border: 1px solid #ccc;
        height: 3em;
        font-size: 1rem;
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

# =========================================================
# ACTION HANDLER (NO UI HERE)
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
        st.session_state.action = "START_ROUND"
        st.session_state.payload = {
            "date": str(d),
            "player": player,
            "course": course,
            "holes": holes
        }
        st.rerun()

# ---------------- HOLE SETUP ----------------
elif st.session_state.screen == "HOLE_SETUP":
    idx = st.session_state.game["hole_index"] + 1
    st.markdown(f"### Hole {idx}")
    par = st.radio("Par", [3, 4, 5])
    yardage = st.number_input("Yardage (yards)", 50, 700, step=1)

    if st.button("Confirm Hole"):
        st.session_state.action = "CONFIRM_HOLE"
        st.session_state.payload = {"par": par, "yardage": yardage}
        st.rerun()

    st.markdown('<div class="undo-btn">', unsafe_allow_html=True)
    if st.button("Undo"):
        st.session_state.action = "UNDO"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- SHOT RESULT (BUTTON LIES) ----------------
elif st.session_state.screen == "SHOT_RESULT":
    hole = st.session_state.game["holes"][-1]
    shot_num = len(hole["shots"]) + 1

    st.markdown(f"### Shot {shot_num}")
    st.markdown("#### Where did the ball finish?")

    if shot_num == 1 and hole["par"] in [4, 5]:
        options = [
            "Fairway", "Left Rough", "Right Rough",
            "Fairway Bunker", "Greenside Bunker",
            "Green", "Water", "OB", "Hole"
        ]
    elif shot_num == 1 and hole["par"] == 3:
        options = [
            "Green", "Fairway", "Left Rough", "Right Rough",
            "Short", "Long", "Greenside Bunker",
            "Water", "OB", "Hole"
        ]
    else:
        options = [
            "Green", "Greenside Bunker",
            "Left Rough", "Right Rough",
            "Fairway Bunker", "Water", "OB", "Hole"
        ]

    for opt in options:
        if st.button(opt):
            st.session_state.action = "SHOT_RESULT"
            st.session_state.payload = opt
            st.rerun()

    st.markdown('<div class="undo-btn">', unsafe_allow_html=True)
    if st.button("Undo"):
        st.session_state.action = "UNDO"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- DISTANCE (YARDS) ----------------
elif st.session_state.screen == "DISTANCE_YARDS":
    st.markdown("### Distance to Hole")
    yards = st.number_input("Yards", 1, 600, step=1)

    if st.button("Confirm Distance"):
        st.session_state.action = "DISTANCE_YARDS"
        st.session_state.payload = yards
        st.rerun()

    st.markdown('<div class="undo-btn">', unsafe_allow_html=True)
    if st.button("Undo"):
        st.session_state.action = "UNDO"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- GREEN DISTANCE ----------------
elif st.session_state.screen == "GREEN_DISTANCE":
    st.markdown("### On the Green")
    feet = st.number_input("Feet to Hole", 0, 200, step=1)

    if st.button("Confirm Distance"):
        st.session_state.action = "GREEN_DISTANCE"
        st.session_state.payload = feet
        st.rerun()

    st.markdown('<div class="undo-btn">', unsafe_allow_html=True)
    if st.button("Undo"):
        st.session_state.action = "UNDO"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- PUTTING ----------------
elif st.session_state.screen == "PUTT":
    st.markdown("### Putting")

    for opt in ["Left", "Right", "Short", "Long", "Hole"]:
        if st.button(opt):
            st.session_state.action = "PUTT"
            st.session_state.payload = opt
            st.rerun()

    st.markdown('<div class="undo-btn">', unsafe_allow_html=True)
    if st.button("Undo"):
        st.session_state.action = "UNDO"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- END HOLE ----------------
elif st.session_state.screen == "END_HOLE":
    hole = st.session_state.game["holes"][-1]
    score = hole["strokes"] - hole["par"]

    st.markdown("### Hole Complete")
    st.metric("Score vs Par", f"{score:+}")

    if st.button("Next Hole"):
        st.session_state.action = "NEXT_HOLE"
        st.rerun()

# ---------------- SUMMARY ----------------
elif st.session_state.screen == "SUMMARY":
    st.markdown("### Round Complete")
    st.write(st.session_state.game)

    if st.button("Restart"):
        st.session_state.clear()
        st.rerun()
