import streamlit as st

# ============================
# Session State Initialization
# ============================
if "page" not in st.session_state:
    st.session_state.page = "round_setup"

if "round" not in st.session_state:
    st.session_state.round = {
        "holes": []
    }

if "hole" not in st.session_state:
    st.session_state.hole = None

if "shot" not in st.session_state:
    st.session_state.shot = None


# ============================
# Helper
# ============================
def big_buttons(options, cols=2):
    buttons = st.columns(cols)
    clicked = None
    for i, opt in enumerate(options):
        if buttons[i % cols].button(opt, use_container_width=True):
            clicked = opt
    return clicked


# ============================
# ROUND SETUP
# ============================
if st.session_state.page == "round_setup":
    st.title("Golf Stat Tracker")

    player = st.text_input("Player Name")
    course = st.text_input("Course Name")
    holes = st.number_input("Holes Played", 1, 18, 18)
    par = st.number_input("Course Par", 9, 90, holes * 4)

    if st.button("Start Round", use_container_width=True):
        st.session_state.round.update({
            "player": player,
            "course": course,
            "holes_played": holes,
            "course_par": par,
            "holes": []
        })
        st.session_state.page = "hole_setup"


# ============================
# HOLE SETUP
# ============================
elif st.session_state.page == "hole_setup":
    hole_number = len(st.session_state.round["holes"]) + 1
    st.header(f"Hole {hole_number}")

    hole_par = st.number_input("Hole Par", 3, 5, 4)
    hole_yards = st.number_input("Hole Yardage", 50, 800, 400)

    if st.button("Start Hole", use_container_width=True):
        st.session_state.hole = {
            "hole_number": hole_number,
            "par": hole_par,
            "yardage": hole_yards,
            "shots": []
        }
        st.session_state.shot = {
            "number": 1
        }
        st.session_state.page = "shot_distance"


# ============================
# SHOT 1: DISTANCE
# ============================
elif st.session_state.page == "shot_distance":
    st.header(f"Hole {st.session_state.hole['hole_number']} – Shot {st.session_state.shot['number']}")
    yards = st.number_input("How far did the shot go? (yards)", 0, 400, 150)

    if st.button("Next", use_container_width=True):
        st.session_state.shot["distance"] = yards
        st.session_state.page = "shot_result"


# ============================
# SHOT 2: RESULT (BIG BUTTONS)
# ============================
elif st.session_state.page == "shot_result":
    st.header("Where did the ball go?")

    choice = big_buttons(
        ["Fairway", "Rough", "Bunker", "Water", "Green", "Hole"],
        cols=2
    )

    if choice:
        st.session_state.shot["result"] = choice.lower()
        if choice == "Green":
            st.session_state.page = "putt_distance"
        elif choice in ["Fairway", "Hole"]:
            st.session_state.page = "save_shot"
        else:
            st.session_state.page = "shot_direction"


# ============================
# SHOT 3: DIRECTION
# ============================
elif st.session_state.page == "shot_direction":
    st.header("Which direction?")

    direction = big_buttons(
        ["Left", "Right", "Short", "Long"],
        cols=2
    )

    if direction:
        st.session_state.shot["direction"] = direction.lower()
        st.session_state.page = "save_shot"


# ============================
# PUTTING DISTANCE
# ============================
elif st.session_state.page == "putt_distance":
    st.header("Putting")

    feet = st.number_input("How far from the hole? (feet)", 0, 100, 15)

    if st.button("Next", use_container_width=True):
        st.session_state.shot["putt_distance"] = feet
        st.session_state.page = "save_shot"


# ============================
# SAVE SHOT
# ============================
elif st.session_state.page == "save_shot":
    st.session_state.hole["shots"].append(st.session_state.shot)

    if st.session_state.shot["result"] == "hole":
        st.session_state.round["holes"].append(st.session_state.hole)

        if len(st.session_state.round["holes"]) >= st.session_state.round["holes_played"]:
            st.session_state.page = "summary"
        else:
            st.session_state.page = "hole_setup"
    else:
        st.session_state.shot = {
            "number": st.session_state.shot["number"] + 1
        }
        st.session_state.page = "shot_distance"


# ============================
# SUMMARY (TEMP)
# ============================
elif st.session_state.page == "summary":
    st.title("Round Complete")
    st.write("Raw round data (stats next):")
    st.json(st.session_state.round)
