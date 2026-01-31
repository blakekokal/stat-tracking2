import streamlit as st
import pandas as pd
from copy import deepcopy
from datetime import date

# ----------------------------
# CONFIG
# ----------------------------
st.set_page_config(page_title="Golf Round Tracker", layout="centered")

# ----------------------------
# HELPERS
# ----------------------------
def push_undo():
    st.session_state.undo_stack.append(deepcopy(st.session_state.game))

def undo():
    if st.session_state.undo_stack:
        st.session_state.game = st.session_state.undo_stack.pop()

def reset_app():
    for k in list(st.session_state.keys()):
        del st.session_state[k]

# ----------------------------
# INITIAL STATE
# ----------------------------
if "screen" not in st.session_state:
    st.session_state.screen = "round_setup"
    st.session_state.game = {
        "round": {},
        "holes": [],
        "current_hole": 0,
        "stats": {
            "fairways": [],
            "gir": [],
            "scramble": [],
            "putts": [],
            "first_putts": [],
            "prox_gir": [],
            "prox_missed_gir": []
        }
    }
    st.session_state.undo_stack = []

# ----------------------------
# UI
# ----------------------------
st.title("⛳ Golf Shot Tracker")

# ----------------------------
# ROUND SETUP
# ----------------------------
if st.session_state.screen == "round_setup":
    st.subheader("Round Setup")

    round_date = st.date_input("Date", value=date.today())
    player = st.text_input("Player Name")
    course = st.text_input("Course Name")
    holes = st.radio("Holes", [9, 18])

    if st.button("Start Round"):
        st.session_state.game["round"] = {
            "date": str(round_date),
            "player": player,
            "course": course,
            "holes": holes
        }
        st.session_state.screen = "hole_setup"

# ----------------------------
# HOLE SETUP
# ----------------------------
elif st.session_state.screen == "hole_setup":
    hole_num = st.session_state.game["current_hole"] + 1
    st.subheader(f"Hole {hole_num} Setup")

    par = st.radio("Par", [3, 4, 5])
    yardage = st.number_input("Hole Yardage (yards)", min_value=50, max_value=700, step=1)

    if st.button("Confirm Hole"):
        st.session_state.game["holes"].append({
            "par": par,
            "yardage": yardage,
            "shots": [],
            "strokes": 0,
            "gir_missed": False,
            "green_reached": False
        })
        st.session_state.screen = "shot_result"

# ----------------------------
# SHOT RESULT
# ----------------------------
elif st.session_state.screen == "shot_result":
    hole = st.session_state.game["holes"][-1]
    shot_num = len(hole["shots"]) + 1

    st.subheader(f"Shot {shot_num} – Result")

    options = [
        "Left Rough", "Right Rough", "Fairway Bunker",
        "Greenside Bunker", "Green", "Water", "OB", "Hole"
    ]

    if hole["par"] in [4, 5] and shot_num == 1:
        options.insert(0, "Fairway")

    result = st.radio("Where did it finish?", options)

    if st.button("Confirm Result"):
        push_undo()
        hole["strokes"] += 1

        if result in ["Water", "OB"]:
            hole["strokes"] += 1

        if result == "Hole":
            hole["shots"].append({"result": result})
            st.session_state.screen = "end_hole"
        elif result == "Green":
            hole["green_reached"] = True
            hole["shots"].append({"result": result})
            st.session_state.screen = "green_distance"
        else:
            if shot_num <= hole["par"]:
                hole["gir_missed"] = True
            hole["shots"].append({"result": result})
            st.session_state.screen = "distance_to_hole"

    if st.button("Undo"):
        undo()

# ----------------------------
# DISTANCE TO HOLE (YARDS)
# ----------------------------
elif st.session_state.screen == "distance_to_hole":
    st.subheader("Distance to Hole")

    dist = st.number_input("Distance (yards)", min_value=1, max_value=600, step=1)

    if st.button("Confirm Distance"):
        push_undo()
        st.session_state.game["holes"][-1]["shots"][-1]["distance"] = dist
        st.session_state.screen = "shot_result"

    if st.button("Undo"):
        undo()

# ----------------------------
# GREEN DISTANCE (FEET)
# ----------------------------
elif st.session_state.screen == "green_distance":
    st.subheader("Distance to Hole (On Green)")

    feet = st.number_input("Feet to hole", min_value=0, max_value=200, step=1)

    if st.button("Confirm"):
        push_undo()
        hole = st.session_state.game["holes"][-1]
        hole["shots"][-1]["feet"] = feet

        if hole["gir_missed"]:
            st.session_state.game["stats"]["prox_missed_gir"].append(feet)
        else:
            st.session_state.game["stats"]["prox_gir"].append(feet)
            st.session_state.game["stats"]["first_putts"].append(feet)

        st.session_state.screen = "putt"

    if st.button("Undo"):
        undo()

# ----------------------------
# PUTTING
# ----------------------------
elif st.session_state.screen == "putt":
    st.subheader("Putt Result")

    result = st.radio("Putt result", ["Left", "Right", "Short", "Long", "Hole"])

    if st.button("Confirm Putt"):
        push_undo()
        hole = st.session_state.game["holes"][-1]
        hole["strokes"] += 1

        if result == "Hole":
            st.session_state.game["stats"]["putts"].append(
                len([s for s in hole["shots"] if s.get("feet") is not None])
            )
            st.session_state.screen = "end_hole"
        else:
            st.session_state.screen = "putt"

    if st.button("Undo"):
        undo()

# ----------------------------
# END HOLE
# ----------------------------
elif st.session_state.screen == "end_hole":
    hole = st.session_state.game["holes"][-1]
    score = hole["strokes"] - hole["par"]

    st.subheader("Hole Complete")
    st.write(f"Score vs Par: {score:+}")

    if hole["par"] in [4, 5]:
        tee = hole["shots"][0]["result"]
        st.session_state.game["stats"]["fairways"].append(tee == "Fairway")

    gir = not hole["gir_missed"]
    st.session_state.game["stats"]["gir"].append(gir)
    st.session_state.game["stats"]["scramble"].append(
        hole["gir_missed"] and score <= 0
    )

    if st.button("Next Hole"):
        st.session_state.game["current_hole"] += 1
        if st.session_state.game["current_hole"] < st.session_state.game["round"]["holes"]:
            st.session_state.screen = "hole_setup"
        else:
            st.session_state.screen = "summary"

# ----------------------------
# SUMMARY
# ----------------------------
elif st.session_state.screen == "summary":
    st.subheader("Round Summary")

    df = pd.DataFrame({
        "Fairway Hit": st.session_state.game["stats"]["fairways"],
        "GIR": st.session_state.game["stats"]["gir"],
        "Scramble": st.session_state.game["stats"]["scramble"]
    })

    st.dataframe(df)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", csv, "round_stats.csv")

    if st.button("Start New Round"):
        reset_app()
