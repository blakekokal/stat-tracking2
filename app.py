import streamlit as st

# =========================
# SESSION STATE
# =========================
defaults = {
    "page": "round",
    "round": {"holes": []},
    "hole_index": 1,
    "hole": None,
    "shot": None,
    "advance": False,
    "temp_par": None,
    "temp_yardage": None,
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# =========================
# NAV HELPERS
# =========================
def go(page):
    st.session_state.page = page
    st.session_state.advance = False


def shot_number():
    return len(st.session_state.hole["shots"]) + 1


def progress():
    return f"Hole {st.session_state.hole_index} / {st.session_state.round['holes_played']} • Shot {shot_number()}"


def save_shot_and_advance(next_page):
    st.session_state.hole["shots"].append(st.session_state.shot)
    st.session_state.advance = True
    st.session_state.next_page = next_page


def finish_hole():
    st.session_state.round["holes"].append(st.session_state.hole)
    st.session_state.hole_index += 1
    if st.session_state.hole_index > st.session_state.round["holes_played"]:
        go("summary")
    else:
        go("hole_setup")


# =========================
# AUTO ADVANCE (KEY FIX)
# =========================
if st.session_state.advance:
    go(st.session_state.next_page)


# =========================
# ROUND START
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

    c1, c2, c3 = st.columns(3)
    if c1.button("Par 3", use_container_width=True):
        st.session_state.temp_par = 3
        st.session_state.temp_yardage = 170
    if c2.button("Par 4", use_container_width=True):
        st.session_state.temp_par = 4
        st.session_state.temp_yardage = 400
    if c3.button("Par 5", use_container_width=True):
        st.session_state.temp_par = 5
        st.session_state.temp_yardage = 520

    if st.session_state.temp_par:
        st.session_state.temp_yardage = st.number_input(
            "Yardage", 50, 800, st.session_state.temp_yardage, step=1
        )

        c1, c2 = st.columns(2)
        if c1.button("Back", use_container_width=True):
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
# SHOT RESULT (SPATIAL)
# =========================
elif st.session_state.page == "shot_result":
    st.caption(progress())

    # HOLE (top)
    if st.button("HOLE", use_container_width=True):
        st.session_state.shot = {"shot": shot_number(), "result": "hole"}
        save_shot_and_advance("finish")

    # GREEN
    if st.button("Green", use_container_width=True):
        st.session_state.shot = {"shot": shot_number(), "result": "green"}
        go("putt_distance")

    if st.button("Greenside Bunker", use_container_width=True):
        st.session_state.shot = {"shot": shot_number(), "result": "greenside_bunker"}
        save_shot_and_advance("approach_distance")

    # FAIRWAY ZONE (TRUE GRID)
    st.markdown("### Fairway")

    if st.button("Fairway", use_container_width=True):
        st.session_state.shot = {"shot": shot_number(), "result": "fairway"}
        save_shot_and_advance("approach_distance")

    l, r = st.columns(2)
    if l.button("Left Rough", use_container_width=True):
        st.session_state.shot = {"shot": shot_number(), "result": "rough", "direction": "left"}
        save_shot_and_advance("approach_distance")

    if r.button("Right Rough", use_container_width=True):
        st.session_state.shot = {"shot": shot_number(), "result": "rough", "direction": "right"}
        save_shot_and_advance("approach_distance")

    # HAZARDS
    h1, h2 = st.columns(2)
    if h1.button("Water", use_container_width=True):
        st.session_state.shot = {"shot": shot_number(), "result": "water"}
        go("shot_direction")

    if h2.button("OB", use_container_width=True):
        st.session_state.shot = {"shot": shot_number(), "result": "out_of_bounds"}
        go("shot_direction")


# =========================
# APPROACH DISTANCE
# =========================
elif st.session_state.page == "approach_distance":
    st.caption(progress())

    st.session_state.shot["distance_to_hole"] = st.number_input(
        "Distance to hole (yards)", 0, 400, 50, step=1
    )

    if st.button("Next", use_container_width=True):
        go("shot_result")


# =========================
# PUTTING
# =========================
elif st.session_state.page == "putt_distance":
    st.caption(progress())

    st.session_state.shot["putt_distance"] = st.number_input(
        "Putt distance (feet)", 0, 100, 15, step=1
    )

    if st.button("Next", use_container_width=True):
        go("putt_result")


elif st.session_state.page == "putt_result":
    st.caption(progress())

    c1, c2, c3 = st.columns(3)
    if c2.button("Long", use_container_width=True):
        st.session_state.shot["result"] = "long"
        save_shot_and_advance("putt_distance")

    c1, c2, c3 = st.columns(3)
    if c1.button("Left", use_container_width=True):
        st.session_state.shot["result"] = "left"
        save_shot_and_advance("putt_distance")

    if c2.button("Hole", use_container_width=True):
        st.session_state.shot["result"] = "hole"
        st.session_state.hole["shots"].append(st.session_state.shot)
        finish_hole()

    if c3.button("Right", use_container_width=True):
        st.session_state.shot["result"] = "right"
        save_shot_and_advance("putt_distance")

    c1, c2, c3 = st.columns(3)
    if c2.button("Short", use_container_width=True):
        st.session_state.shot["result"] = "short"
        save_shot_and_advance("putt_distance")


# =========================
# SUMMARY
# =========================
elif st.session_state.page == "summary":
    st.title("Round Complete")
    st.json(st.session_state.round)
