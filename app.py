import streamlit as st

# =========================
# Session State Init
# =========================
def init():
    if "page" not in st.session_state:
        st.session_state.page = "round"
    if "round" not in st.session_state:
        st.session_state.round = {}
    if "hole" not in st.session_state:
        st.session_state.hole = {}
    if "shot" not in st.session_state:
        st.session_state.shot = {}

init()

# =========================
# Helpers
# =========================
def go(page):
    st.session_state.page = page

def big_button(label, next_page=None):
    if st.button(label, use_container_width=True):
        if next_page:
            go(next_page)

def set_and_go(key, value, next_page):
    st.session_state.shot[key] = value
    go(next_page)

# =========================
# ROUND SETUP
# =========================
if st.session_state.page == "round":
    st.title("Golf Stat Tracker")

    st.session_state.round["player"] = st.text_input("Player Name")
    st.session_state.round["course"] = st.text_input("Course Name")
    st.session_state.round["holes_played"] = st.number_input("Holes Played", 1, 18, 18)
    st.session_state.round["course_par"] = st.number_input(
        "Course Par", 9, 90, st.session_state.round["holes_played"] * 4
    )
    st.session_state.round["holes"] = []

    big_button("Start Round", "hole")

# =========================
# HOLE SETUP
# =========================
elif st.session_state.page == "hole":
    hole_num = len(st.session_state.round["holes"]) + 1
    st.header(f"Hole {hole_num}")

    st.session_state.hole = {
        "number": hole_num,
        "par": st.number_input("Hole Par", 3, 5, 4),
        "yardage": st.number_input("Hole Yardage", 50, 800, 400),
        "shots": []
    }

    big_button("Start Hole", "shot_distance")

# =========================
# SHOT – DISTANCE
# =========================
elif st.session_state.page == "shot_distance":
    shot_num = len(st.session_state.hole["shots"]) + 1
    st.header(f"Hole {st.session_state.hole['number']} – Shot {shot_num}")

    st.session_state.shot = {
        "number": shot_num,
        "distance": st.number_input("How far did the shot go? (yards)", 0, 400, 150)
    }

    big_button("Next", "shot_result")

# =========================
# SHOT – RESULT
# =========================
elif st.session_state.page == "shot_result":
    st.header("Where did the ball go?")

    cols = st.columns(2)
    for i, opt in enumerate(["Fairway", "Rough", "Bunker", "Water", "Green", "Hole"]):
        if cols[i % 2].button(opt, use_container_width=True):
            st.session_state.shot["result"] = opt.lower()
            if opt == "Green":
                go("putt_distance")
            elif opt in ["Fairway", "Hole"]:
                go("save_shot")
            else:
                go("shot_direction")

# =========================
# SHOT – DIRECTION
# =========================
elif st.session_state.page == "shot_direction":
    st.header("Which direction?")

    cols = st.columns(2)
    for i, d in enumerate(["Left", "Right", "Short", "Long"]):
        if cols[i % 2].button(d, use_container_width=True):
            set_and_go("direction", d.lower(), "save_shot")

# =========================
# PUTTING DISTANCE
# =========================
elif st.session_state.page == "putt_distance":
    st.header("Putting")

    st.session_state.shot["putt_distance"] = st.number_input(
        "How far from the hole? (feet)", 0, 100, 15
    )

    big_button("Next", "save_shot")

# =========================
# SAVE SHOT
# =========================
elif st.session_state.page == "save_shot":
    st.session_state.hole["shots"].append(st.session_state.shot)

    if st.session_state.shot["result"] == "hole":
        st.session_state.round["holes"].append(st.session_state.hole)

        if len(st.session_state.round["holes"]) >= st.session_state.round["holes_played"]:
            go("summary")
        else:
            go("hole")
    else:
        go("shot_distance")

# =========================
# SUMMARY
# =========================
elif st.session_state.page == "summary":
    st.title("Round Complete")
    st.json(st.session_state.round)
