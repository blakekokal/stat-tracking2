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

if "current_selection" not in st.session_state:
    st.session_state.current_selection = None


# =========================
# NAV
# =========================
def go(page):
    st.session_state.page = page


def shot_number():
    return len(st.session_state.hole["shots"]) + 1


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

    if st.button("Par 3", use_container_width=True):
        st.session_state.hole = {"hole_number": st.session_state.hole_index, "par": 3, "yardage": 170, "shots": []}

    if st.button("Par 4", use_container_width=True):
        st.session_state.hole = {"hole_number": st.session_state.hole_index, "par": 4, "yardage": 400, "shots": []}

    if st.button("Par 5", use_container_width=True):
        st.session_state.hole = {"hole_number": st.session_state.hole_index, "par": 5, "yardage": 520, "shots": []}

    if st.session_state.hole:
        st.session_state.hole["yardage"] = st.number_input(
            "Hole Yardage (yards)", 50, 800, st.session_state.hole["yardage"], step=1
        )

        if st.button("Confirm Hole", use_container_width=True):
            go("shot_select")

        if st.button("Back", use_container_width=True):
            st.session_state.hole = None
            go("round")


# =========================
# SHOT SELECTION
# =========================
elif st.session_state.page == "shot_select":
    st.subheader(f"Hole {st.session_state.hole_index} • Shot {shot_number()}")

    if st.button("Fairway", use_container_width=True):
        st.session_state.current_selection = "fairway"

    if st.button("Left Rough", use_container_width=True):
        st.session_state.current_selection = "left_rough"

    if st.button("Right Rough", use_container_width=True):
        st.session_state.current_selection = "right_rough"

    if st.button("Greenside Bunker", use_container_width=True):
        st.session_state.current_selection = "greenside_bunker"

    if st.button("Green", use_container_width=True):
        st.session_state.current_selection = "green"

    if st.button("Water", use_container_width=True):
        st.session_state.current_selection = "water"

    if st.button("Out of Bounds", use_container_width=True):
        st.session_state.current_selection = "out_of_bounds"

    if st.button("Hole", use_container_width=True):
        st.session_state.current_selection = "hole"

    if st.session_state.current_selection:
        if st.button("Confirm Shot", use_container_width=True):
            shot = {
                "shot_number": shot_number(),
                "result": st.session_state.current_selection
            }
            st.session_state.hole["shots"].append(shot)
            st.session_state.current_selection = None

            if shot["result"] == "green":
                go("putt_distance")
            elif shot["result"] == "hole":
                st.session_state.round["holes"].append(st.session_state.hole)
                st.session_state.hole_index += 1
                go("hole_setup" if st.session_state.hole_index <= st.session_state.round["holes_played"] else "summary")
            else:
                go("distance")

    if st.button("Back", use_container_width=True):
        st.session_state.current_selection = None
        go("hole_setup")


# =========================
# DISTANCE TO HOLE
# =========================
elif st.session_state.page == "distance":
    st.subheader("Distance to Hole")

    d = st.number_input("Yards", 0, 400, 50, step=1)

    if st.button("Confirm Distance", use_container_width=True):
        st.session_state.hole["shots"][-1]["distance_to_hole"] = d
        go("shot_select")

    if st.button("Back", use_container_width=True):
        st.session_state.hole["shots"].pop()
        go("shot_select")


# =========================
# PUTTING DISTANCE
# =========================
elif st.session_state.page == "putt_distance":
    st.subheader("Putting")

    d = st.number_input("Putt distance (feet)", 0, 100, 15, step=1)

    if st.button("Confirm Putt Distance", use_container_width=True):
        st.session_state.hole["shots"].append({
            "shot_number": shot_number(),
            "putt_distance": d
        })
        go("putt_result")

    if st.button("Back", use_container_width=True):
        go("shot_select")


# =========================
# PUTT RESULT
# =========================
elif st.session_state.page == "putt_result":
    st.subheader("Putt Result")

    if st.button("Left", use_container_width=True):
        st.session_state.hole["shots"][-1]["result"] = "left"

    if st.button("Right", use_container_width=True):
        st.session_state.hole["shots"][-1]["result"] = "right"

    if st.button("Short", use_container_width=True):
        st.session_state.hole["shots"][-1]["result"] = "short"

    if st.button("Long", use_container_width=True):
        st.session_state.hole["shots"][-1]["result"] = "long"

    if st.button("Hole", use_container_width=True):
        st.session_state.hole["shots"][-1]["result"] = "hole"
        st.session_state.round["holes"].append(st.session_state.hole)
        st.session_state.hole_index += 1
        go("hole_setup" if st.session_state.hole_index <= st.session_state.round["holes_played"] else "summary")

    if st.button("Back", use_container_width=True):
        st.session_state.hole["shots"].pop()
        go("putt_distance")


# =========================
# SUMMARY
# =========================
elif st.session_state.page == "summary":
    st.title("Round Complete")
    st.json(st.session_state.round)
