import streamlit as st

# =========================
# SESSION STATE INIT
# =========================
if "page" not in st.session_state:
    st.session_state.page = "round"

if "round" not in st.session_state:
    st.session_state.round = {"holes": []}

if "hole_index" not in st.session_state:
    st.session_state.hole_index = 1

if "hole" not in st.session_state:
    st.session_state.hole = {}

if "shot" not in st.session_state:
    st.session_state.shot = {}

if "temp_par" not in st.session_state:
    st.session_state.temp_par = None

if "temp_yardage" not in st.session_state:
    st.session_state.temp_yardage = None


# =========================
# HELPERS
# =========================
def go(page):
    st.session_state.page = page


def shot_number():
    return len(st.session_state.hole.get("shots", [])) + 1


def progress():
    return f"Hole {st.session_state.hole_index}/{st.session_state.round['holes_played']} • Shot {shot_number()}"


def save_shot():
    st.session_state.hole["shots"].append(st.session_state.shot)


def finish_hole():
    st.session_state.round["holes"].append(st.session_state.hole)
    st.session_state.hole_index += 1
    if st.session_state.hole_index > st.session_state.round["holes_played"]:
        go("summary")
    else:
        go("hole_setup")


def back():
    if st.session_state.page in ["approach_distance", "shot_direction", "putt_distance"]:
        go("shot_result")
    elif st.session_state.page == "putt_result":
        go("putt_distance")
    elif st.session_state.page == "shot_result":
        go("hole_setup")
    else:
        go("round")


# =========================
# ROUND SETUP
# =========================
if st.session_state.page == "round":
    st.title("Golf Stat Tracker")

    st.session_state.round["player"] = st.text_input("Player")
    st.session_state.round["course"] = st.text_input("Course")
    st.session_state.round["holes_played"] = st.number_input("Holes", 1, 18, 18)

    if st.button("Start Round", use_container_width=True):
        st.session_state.round["holes"] = []
        st.session_state.hole_index = 1
        go("hole_setup")


# =========================
# HOLE SETUP
# =========================
elif st.session_state.page == "hole_setup":
    st.subheader(f"Hole {st.session_state.hole_index}")

    p1, p2, p3 = st.columns(3)

    if p1.button("Par 3", use_container_width=True):
        st.session_state.temp_par = 3
        st.session_state.temp_yardage = 170

    if p2.button("Par 4", use_container_width=True):
        st.session_state.temp_par = 4
        st.session_state.temp_yardage = 400

    if p3.button("Par 5", use_container_width=True):
        st.session_state.temp_par = 5
        st.session_state.temp_yardage = 520

    if st.session_state.temp_par:
        st.session_state.temp_yardage = st.number_input(
            "Yardage (yards)",
            50, 800,
            st.session_state.temp_yardage,
            step=1
        )

        c1, c2 = st.columns(2)

        if c1.button("Back", use_container_width=True):
            st.session_state.temp_par = None
            st.session_state.temp_yardage = None
            go("round")

        if c2.button("Confirm", use_container_width=True):
            st.session_state.hole = {
                "hole_number": st.session_state.hole_index,
                "par": st.session_state.temp_par,
                "yardage": st.session_state.temp_yardage,
                "shots": []
            }
            st.session_state.temp_par = None
            st.session_state.temp_yardage = None
            go("shot_result")


# =========================
# SHOT RESULT
# =========================
elif st.session_state.page == "shot_result":
    st.caption(progress())

    if st.button("HOLE", use_container_width=True):
        st.session_state.shot = {"shot_number": shot_number(), "result": "hole"}
        save_shot()
        finish_hole()

    if st.button("Green", use_container_width=True):
        st.session_state.shot = {"shot_number": shot_number(), "result": "green"}
        go("putt_distance")

    if st.button("Greenside Bunker", use_container_width=True):
        st.session_state.shot = {"shot_number": shot_number(), "result": "greenside_bunker"}
        save_shot()
        go("approach_distance")

    if st.button("Fairway", use_container_width=True):
        st.session_state.shot = {"shot_number": shot_number(), "result": "fairway"}
        save_shot()
        go("approach_distance")

    r1, r2 = st.columns(2)
    if r1.button("Left Rough", use_container_width=True):
        st.session_state.shot = {"shot_number": shot_number(), "result": "rough", "direction": "left"}
        save_shot()
        go("approach_distance")

    if r2.button("Right Rough", use_container_width=True):
        st.session_state.shot = {"shot_number": shot_number(), "result": "rough", "direction": "right"}
        save_shot()
        go("approach_distance")

    if st.button("Fairway Bunker", use_container_width=True):
        st.session_state.shot = {"shot_number": shot_number(), "result": "fairway_bunker"}
        go("shot_direction")

    o1, o2 = st.columns(2)
    if o1.button("Water", use_container_width=True):
        st.session_state.shot = {"shot_number": shot_number(), "result": "water"}
        go("shot_direction")

    if o2.button("OB", use_container_width=True):
        st.session_state.shot = {"shot_number": shot_number(), "result": "out_of_bounds"}
        go("shot_direction")

    if st.button("Back", use_container_width=True):
        back()


# =========================
# APPROACH DISTANCE
# =========================
elif st.session_state.page == "approach_distance":
    st.caption(progress())

    st.session_state.shot["distance_to_hole"] = st.number_input(
        "Distance to hole (yards)", 0, 400, 50, step=1
    )

    c1, c2 = st.columns(2)
    if c1.button("Back", use_container_width=True):
        back()
    if c2.button("Next", use_container_width=True):
        go("shot_result")


# =========================
# SHOT DIRECTION
# =========================
elif st.session_state.page == "shot_direction":
    st.caption(progress())

    d1, d2, d3, d4 = st.columns(4)
    if d1.button("Left", use_container_width=True):
        st.session_state.shot["direction"] = "left"
        save_shot()
        go("approach_distance")
    if d2.button("Right", use_container_width=True):
        st.session_state.shot["direction"] = "right"
        save_shot()
        go("approach_distance")
    if d3.button("Short", use_container_width=True):
        st.session_state.shot["direction"] = "short"
        save_shot()
        go("approach_distance")
    if d4.button("Long", use_container_width=True):
        st.session_state.shot["direction"] = "long"
        save_shot()
        go("approach_distance")

    if st.button("Back", use_container_width=True):
        back()


# =========================
# PUTTING DISTANCE
# =========================
elif st.session_state.page == "putt_distance":
    st.caption(progress())

    st.session_state.shot["putt_distance"] = st.number_input(
        "Putt distance (feet)", 0, 100, 15, step=1
    )

    c1, c2 = st.columns(2)
    if c1.button("Back", use_container_width=True):
        back()
    if c2.button("Next", use_container_width=True):
        go("putt_result")


# =========================
# PUTT RESULT
# =========================
elif st.session_state.page == "putt_result":
    st.caption(progress())

    c1, c2, c3 = st.columns(3)
    if c2.button("Long", use_container_width=True):
        st.session_state.shot["result"] = "long"
        save_shot()
        go("putt_distance")

    c1, c2, c3 = st.columns(3)
    if c1.button("Left", use_container_width=True):
        st.session_state.shot["result"] = "left"
        save_shot()
        go("putt_distance")
    if c2.button("Hole", use_container_width=True):
        st.session_state.shot["result"] = "hole"
        save_shot()
        finish_hole()
    if c3.button("Right", use_container_width=True):
        st.session_state.shot["result"] = "right"
        save_shot()
        go("putt_distance")

    c1, c2, c3 = st.columns(3)
    if c2.button("Short", use_container_width=True):
        st.session_state.shot["result"] = "short"
        save_shot()
        go("putt_distance")

    if st.button("Back", use_container_width=True):
        back()


# =========================
# SUMMARY
# =========================
elif st.session_state.page == "summary":
    st.title("Round Complete")
    st.json(st.session_state.round)
