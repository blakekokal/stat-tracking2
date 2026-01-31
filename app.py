import streamlit as st
from copy import deepcopy
from datetime import date

st.set_page_config(page_title="Golf Tracker", layout="centered")

# =========================================================
# INITIALIZATION
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
# CORE HELPERS
# =========================================================
def push_undo():
    st.session_state.undo_stack.append(deepcopy((
        st.session_state.screen,
        st.session_state.game
    )))

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
# ACTION HANDLER (RUNS BEFORE UI)
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
            "green_reached": False,
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
            hole["green_reached"] = True
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
# UI RENDERING (NO STATE MUTATION)
# =========================================================
st.title("⛳ Golf Shot Tracker")

# ---------------- ROUND SETUP ----------------
if st.session_state.screen == "ROUND_SETUP":
    st.subheader("Round Setup")

    d = st.date_input("Date", date.today())
    player = st.text_input("Player Name")
    course = st.text_input("Course Name")
    holes = st.radio("Holes", [9, 18])

    if st.button("Start Round", use_container_width=True):
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
    st.subheader(f"Hole {idx}")

    par = st.radio("Par", [3, 4, 5])
    yardage = st.number_input("Yardage (yards)", 50, 700, step=1)

    if st.button("Confirm Hole", use_container_width=True):
        st.session_state.action = "CONFIRM_HOLE"
        st.session_state.payload = {"par": par, "yardage": yardage}
        st.rerun()

    if st.button("Undo", use_container_width=True):
        st.session_state.action = "UNDO"
        st.rerun()

# ---------------- SHOT RESULT ----------------
elif st.session_state.screen == "SHOT_RESULT":
    hole = st.session_state.game["holes"][-1]
    shot_num = len(hole["shots"]) + 1
    st.subheader(f"Shot {shot_num}")

    options = ["Left Rough", "Right Rough", "Fairway Bunker",
               "Greenside Bunker", "Green", "Water", "OB", "Hole"]

    if hole["par"] in [4, 5] and shot_num == 1:
        options.insert(0, "Fairway")

    result = st.radio("Where did it finish?", options)

    if st.button("Confirm", use_container_width=True):
        st.session_state.action = "SHOT_RESULT"
        st.session_state.payload = result
        st.rerun()

    if st.button("Undo", use_container_width=True):
        st.session_state.action = "UNDO"
        st.rerun()

# ---------------- DISTANCE (YARDS) ----------------
elif st.session_state.screen == "DISTANCE_YARDS":
    st.subheader("Distance to Hole (yards)")
    d = st.number_input("Yards", 1, 600, step=1)

    if st.button("Confirm Distance", use_container_width=True):
        st.session_state.action = "DISTANCE_YARDS"
        st.session_state.payload = d
        st.rerun()

    if st.button("Undo", use_container_width=True):
        st.session_state.action = "UNDO"
        st.rerun()

# ---------------- GREEN DISTANCE ----------------
elif st.session_state.screen == "GREEN_DISTANCE":
    st.subheader("Distance to Hole (feet)")
    f = st.number_input("Feet", 0, 200, step=1)

    if st.button("Confirm", use_container_width=True):
        st.session_state.action = "GREEN_DISTANCE"
        st.session_state.payload = f
        st.rerun()

    if st.button("Undo", use_container_width=True):
        st.session_state.action = "UNDO"
        st.rerun()

# ---------------- PUTTING ----------------
elif st.session_state.screen == "PUTT":
    st.subheader("Putt Result")
    r = st.radio("Result", ["Left", "Right", "Short", "Long", "Hole"])

    if st.button("Confirm Putt", use_container_width=True):
        st.session_state.action = "PUTT"
        st.session_state.payload = r
        st.rerun()

    if st.button("Undo", use_container_width=True):
        st.session_state.action = "UNDO"
        st.rerun()

# ---------------- END HOLE ----------------
elif st.session_state.screen == "END_HOLE":
    hole = st.session_state.game["holes"][-1]
    score = hole["strokes"] - hole["par"]

    st.subheader("Hole Complete")
    st.metric("Score vs Par", f"{score:+}")

    if st.button("Next Hole", use_container_width=True):
        st.session_state.action = "NEXT_HOLE"
        st.rerun()

# ---------------- SUMMARY ----------------
elif st.session_state.screen == "SUMMARY":
    st.subheader("Round Complete")
    st.write(st.session_state.game)

    if st.button("Restart"):
        st.session_state.clear()
        st.rerun()
