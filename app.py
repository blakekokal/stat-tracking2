import streamlit as st

# -----------------------------
# Initialize session state
# -----------------------------
defaults = {
    "round": None,
    "hole": None,
    "shot": None,
    "step": "round_setup",  # controls screen
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# -----------------------------
# Round Setup
# -----------------------------
if st.session_state.step == "round_setup":
    st.title("Golf Stat Tracker")

    player = st.text_input("Player Name")
    course = st.text_input("Course Name")
    holes = st.number_input("Holes Played", 1, 18, 18)
    course_par = st.number_input("Course Par", 9, 90, holes * 4)

    if st.button("Start Round") and player and course:
        st.session_state.round = {
            "player": player,
            "course": course,
            "holes_played": holes,
            "course_par": course_par,
            "holes": []
        }
        st.session_state.step = "hole_setup"


# -----------------------------
# Hole Setup
# -----------------------------
elif st.session_state.step == "hole_setup":
    hole_number = len(st.session_state.round["holes"]) + 1
    st.header(f"Hole {hole_number}")

    par = st.number_input("Hole Par", 3, 5, 4)
    yardage = st.number_input("Hole Yardage", 50, 800, 400)

    if st.button("Start Hole"):
        st.session_state.hole = {
            "hole_number": hole_number,
            "par": par,
            "yardage": yardage,
            "shots": []
        }
        st.session_state.shot = {
            "shot_number": 1
        }
        st.session_state.step = "shot_distance"


# -----------------------------
# Shot Step A — Distance
# -----------------------------
elif st.session_state.step == "shot_distance":
    st.header(f"Hole {st.session_state.hole['hole_number']} – Shot {st.session_state.shot['shot_number']}")

    distance = st.number_input("How far did the shot go? (yards)", 0, 400, 150)

    if st.button("Next"):
        st.session_state.shot["distance"] = distance
        st.session_state.step = "shot_result"


# -----------------------------
# Shot Step B — Where it went
# -----------------------------
elif st.session_state.step == "shot_result":
    st.header("Where did the ball go?")

    options = ["Fairway", "Rough", "Bunker", "Water", "Green", "Hole"]
    cols = st.columns(3)

    for i, opt in enumerate(options):
        if cols[i % 3].button(opt):
            st.session_state.shot["result"] = opt.lower()
            if opt.lower() == "green":
                st.session_state.step = "putt_distance"
            elif opt.lower() in ["fairway", "hole"]:
                st.session_state.step = "save_shot"
            else:
                st.session_state.step = "shot_direction"


# -----------------------------
# Shot Step C — Direction
# -----------------------------
elif st.session_state.step == "shot_direction":
    st.header("Which side?")

    for d in ["Left", "Right", "Short", "Long"]:
        if st.button(d):
            st.session_state.shot["direction"] = d.lower()
            st.session_state.step = "save_shot"


# -----------------------------
# Shot Step D — Putting distance
# -----------------------------
elif st.session_state.step == "putt_distance":
    st.header("Putting")

    feet = st.number_input("How far from the hole? (feet)", 0, 100, 15)

    if st.button("Next"):
        st.session_state.shot["putt_distance"] = feet
        st.session_state.step = "save_shot"


# -----------------------------
# Save Shot
# -----------------------------
elif st.session_state.step == "save_shot":
    st.session_state.hole["shots"].append(st.session_state.shot)

    if st.session_state.shot["result"] == "hole":
        st.session_state.round["holes"].append(st.session_state.hole)

        if len(st.session_state.round["holes"]) == st.session_state.round["holes_played"]:
            st.session_state.step = "summary"
        else:
            st.session_state.step = "hole_setup"
    else:
        st.session_state.shot = {
            "shot_number": st.session_state.shot["shot_number"] + 1
        }
        st.session_state.step = "shot_distance"


# -----------------------------
# Summary (placeholder)
# -----------------------------
elif st.session_state.step == "summary":
    st.title("Round Complete")
    st.write(st.session_state.round)
