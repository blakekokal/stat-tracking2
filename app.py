import streamlit as st

# =========================
# SESSION STATE
# =========================
if "page" not in st.session_state:
    st.session_state.page = "round"
if "round" not in st.session_state:
    st.session_state.round = {"holes": []}
if "hole_index" not in st.session_state:
    st.session_state.hole_index = 1
if "hole" not in st.session_state:
    st.session_state.hole = None
if "shot" not in st.session_state:
    st.session_state.shot = None


def go(p):
    st.session_state.page = p


def shot_number():
    return len(st.session_state.hole["shots"]) + 1


# =========================
# ROUND START
# =========================
if st.session_state.page == "round":
    st.title("Golf Stat Tracker")

    st.session_state.round["player"] = st.text_input("Player")
    st.session_state.round["course"] = st.text_input("Course")
    st.session_state.round["holes_played"] = st.number_input("Holes", 1, 18, 18)

    with st.form("start_form"):
        start = st.form_submit_button("Start Round")

    if start:
        st.session_state.round["holes"] = []
        st.session_state.hole_index = 1
        go("hole_setup")


# =========================
# HOLE SETUP
# =========================
elif st.session_state.page == "hole_setup":
    st.subheader(f"Hole {st.session_state.hole_index}")

    with st.form("hole_form"):
        par = st.radio("Par", [3, 4, 5], horizontal=True)
        yardage = st.number_input("Yardage (yards)", 50, 800, 400, step=1)

        c1, c2 = st.columns(2)
        back = c1.form_submit_button("Back")
        confirm = c2.form_submit_button("Confirm Hole")

    if back:
        go("round")

    if confirm:
        st.session_state.hole = {
            "hole_number": st.session_state.hole_index,
            "par": par,
            "yardage": yardage,
            "shots": []
        }
        go("shot_result")


# =========================
# SHOT RESULT (SPATIAL, FORM)
# =========================
elif st.session_state.page == "shot_result":
    st.subheader(f"Hole {st.session_state.hole_index} • Shot {shot_number()}")

    with st.form("shot_form"):
        choice = None

        if st.form_submit_button("HOLE"):
            choice = "hole"
        elif st.form_submit_button("Green"):
            choice = "green"
        elif st.form_submit_button("Greenside Bunker"):
            choice = "greenside_bunker"
        elif st.form_submit_button("Fairway"):
            choice = "fairway"

        c1, c2 = st.columns(2)
        if c1.form_submit_button("Left Rough"):
            choice = "rough_left"
        if c2.form_submit_button("Right Rough"):
            choice = "rough_right"

        c1, c2 = st.columns(2)
        if c1.form_submit_button("Water"):
            choice = "water"
        if c2.form_submit_button("Out of Bounds"):
            choice = "out_of_bounds"

        back = st.form_submit_button("Back")

    if back:
        go("hole_setup")

    if choice:
        shot = {"shot_number": shot_number(), "result": choice}
        st.session_state.hole["shots"].append(shot)

        if choice == "green":
            go("putt_distance")
        elif choice == "hole":
            st.session_state.round["holes"].append(st.session_state.hole)
            st.session_state.hole_index += 1
            go("hole_setup" if st.session_state.hole_index <= st.session_state.round["holes_played"] else "summary")
        else:
            go("approach_distance")


# =========================
# APPROACH DISTANCE
# =========================
elif st.session_state.page == "approach_distance":
    with st.form("distance_form"):
        d = st.number_input("Distance to hole (yards)", 0, 400, 50, step=1)
        back = st.form_submit_button("Back")
        next_btn = st.form_submit_button("Confirm Distance")

    if back:
        st.session_state.hole["shots"].pop()
        go("shot_result")

    if next_btn:
        st.session_state.hole["shots"][-1]["distance_to_hole"] = d
        go("shot_result")


# =========================
# PUTTING DISTANCE
# =========================
elif st.session_state.page == "putt_distance":
    with st.form("putt_dist_form"):
        d = st.number_input("Putt distance (feet)", 0, 100, 15, step=1)
        back = st.form_submit_button("Back")
        next_btn = st.form_submit_button("Next")

    if back:
        st.session_state.hole["shots"].pop()
        go("shot_result")

    if next_btn:
        st.session_state.hole["shots"].append(
            {"shot_number": shot_number(), "putt_distance": d}
        )
        go("putt_result")


# =========================
# PUTT RESULT (ORIENTED)
# =========================
elif st.session_state.page == "putt_result":
    with st.form("putt_result_form"):
        c1, c2, c3 = st.columns(3)
        long = c2.form_submit_button("Long")

        c1, c2, c3 = st.columns(3)
        left = c1.form_submit_button("Left")
        hole = c2.form_submit_button("Hole")
        right = c3.form_submit_button("Right")

        c1, c2, c3 = st.columns(3)
        short = c2.form_submit_button("Short")

        back = st.form_submit_button("Back")

    if back:
        st.session_state.hole["shots"].pop()
        go("putt_distance")

    result = None
    if long:
        result = "long"
    elif left:
        result = "left"
    elif right:
        result = "right"
    elif short:
        result = "short"
    elif hole:
        result = "hole"

    if result:
        st.session_state.hole["shots"][-1]["result"] = result

        if result == "hole":
            st.session_state.round["holes"].append(st.session_state.hole)
            st.session_state.hole_index += 1
            go("hole_setup" if st.session_state.hole_index <= st.session_state.round["holes_played"] else "summary")
        else:
            go("putt_distance")


# =========================
# SUMMARY
# =========================
elif st.session_state.page == "summary":
    st.title("Round Complete")
    st.json(st.session_state.round)
