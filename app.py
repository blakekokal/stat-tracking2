import streamlit as st

# =========================
# Session State Init
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


# =========================
# Helpers
# =========================
def go(page):
    st.session_state.page = page


def save_shot():
    st.session_state.hole["shots"].append(st.session_state.shot)


def finish_hole():
    st.session_state.round["holes"].append(st.session_state.hole)
    st.session_state.hole_index += 1
    if st.session_state.hole_index > st.session_state.round["holes_played"]:
        go("summary")
    else:
        go("hole_setup")


def shot_number():
    return len(st.session_state.hole.get("shots", [])) + 1


def progress():
    return f"Hole {st.session_state.hole_index} of {st.session_state.round['holes_played']} • Shot {shot_number()}"


def back():
    transitions = {
        "approach_distance": "shot_result",
        "shot_direction": "shot_result",
        "putt_distance": "shot_result",
        "putt_result": "putt_distance",
    }
    go(transitions.get(st.session_state.page, "shot_result"))


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

    st.button("Start Round", use_container_width=True, on_click=lambda: go("hole_setup"))


# =========================
# HOLE SETUP
# =========================
elif st.session_state.page == "hole_setup":
    st.subheader(f"Hole {st.session_state.hole_index} Setup")

    st.session_state.hole = {
        "hole_number": st.session_state.hole_index,
        "par": st.number_input("Hole Par", 3, 5, 4),
        "yardage": st.number_input("Hole Yardage (yards)", 50, 800, 400),
        "shots": []
    }

    st.button("Confirm Hole", use_container_width=True, on_click=lambda: go("shot_result"))


# =========================
# SHOT RESULT – HOLE MAP
# =========================
elif st.session_state.page == "shot_result":
    st.caption(progress())
    st.subheader("Tap where the ball finished")

    # GREEN AREA
    st.markdown("### Green")
    g1, g2 = st.columns(2)

    g1.button(
        "Green",
        use_container_width=True,
        on_click=lambda: (
            st.session_state.update({"shot": {"shot_number": shot_number(), "result": "green"}}),
            go("putt_distance")
        )
    )

    g2.button(
        "Hole",
        use_container_width=True,
        on_click=lambda: (
            st.session_state.update({"shot": {"shot_number": shot_number(), "result": "hole"}}),
            save_shot(),
            finish_hole()
        )
    )

    st.button(
        "Greenside Bunker",
        use_container_width=True,
        on_click=lambda: (
            st.session_state.update({"shot": {"shot_number": shot_number(), "result": "greenside_bunker"}}),
            save_shot(),
            go("approach_distance")
        )
    )

    # FAIRWAY AREA
    st.markdown("### Fairway")
    f1, f2, f3 = st.columns(3)

    f1.button(
        "Left Rough",
        use_container_width=True,
        on_click=lambda: (
            st.session_state.update({
                "shot": {"shot_number": shot_number(), "result": "rough", "direction": "left"}
            }),
            save_shot(),
            go("approach_distance")
        )
    )

    f2.button(
        "Fairway",
        use_container_width=True,
        on_click=lambda: (
            st.session_state.update({"shot": {"shot_number": shot_number(), "result": "fairway"}}),
            save_shot(),
            go("approach_distance")
        )
    )

    f3.button(
        "Right Rough",
        use_container_width=True,
        on_click=lambda: (
            st.session_state.update({
                "shot": {"shot_number": shot_number(), "result": "rough", "direction": "right"}
            }),
            save_shot(),
            go("approach_distance")
        )
    )

    st.button(
        "Fairway Bunker",
        use_container_width=True,
        on_click=lambda: (
            st.session_state.update({"shot": {"shot_number": shot_number(), "result": "fairway_bunker"}}),
            go("shot_direction")
        )
    )

    # OTHER
    st.markdown("### Other")
    o1, o2 = st.columns(2)

    o1.button(
        "Water",
        use_container_width=True,
        on_click=lambda: (
            st.session_state.update({"shot": {"shot_number": shot_number(), "result": "water"}}),
            go("shot_direction")
        )
    )

    o2.button(
        "Out of Bounds",
        use_container_width=True,
        on_click=lambda: (
            st.session_state.update({"shot": {"shot_number": shot_number(), "result": "out_of_bounds"}}),
            go("shot_direction")
        )
    )

    st.button("⬅ Back", use_container_width=True, on_click=back)


# =========================
# APPROACH DISTANCE
# =========================
elif st.session_state.page == "approach_distance":
    st.caption(progress())
    st.subheader(f"Shot {shot_number()} – distance to hole")

    st.session_state.shot = {
        "shot_number": shot_number(),
        "distance_to_hole": st.number_input("Yards", 0, 400, 50, step=1)
    }

    c1, c2 = st.columns(2)
    c1.button("⬅ Back", use_container_width=True, on_click=back)
    c2.button("Next", use_container_width=True, on_click=lambda: go("shot_result"))


# =========================
# SHOT DIRECTION
# =========================
elif st.session_state.page == "shot_direction":
    st.caption(progress())
    st.subheader("Which direction?")

    d1, d2, d3, d4 = st.columns(4)
    d1.button("Left", use_container_width=True,
              on_click=lambda: (
                  st.session_state.shot.update({"direction": "left"}),
                  save_shot(),
                  go("approach_distance")
              ))
    d2.button("Right", use_container_width=True,
              on_click=lambda: (
                  st.session_state.shot.update({"direction": "right"}),
                  save_shot(),
                  go("approach_distance")
              ))
    d3.button("Short", use_container_width=True,
              on_click=lambda: (
                  st.session_state.shot.update({"direction": "short"}),
                  save_shot(),
                  go("approach_distance")
              ))
    d4.button("Long", use_container_width=True,
              on_click=lambda: (
                  st.session_state.shot.update({"direction": "long"}),
                  save_shot(),
                  go("approach_distance")
              ))

    st.button("⬅ Back", use_container_width=True, on_click=back)


# =========================
# PUTTING DISTANCE
# =========================
elif st.session_state.page == "putt_distance":
    st.caption(progress())
    st.subheader("Putting – distance to hole")

    st.session_state.shot = {
        "shot_number": shot_number(),
        "putt_distance": st.number_input("Feet", 0, 100, 15, step=1)
    }

    c1, c2 = st.columns(2)
    c1.button("⬅ Back", use_container_width=True, on_click=back)
    c2.button("Next", use_container_width=True, on_click=lambda: go("putt_result"))


# =========================
# PUTT RESULT
# =========================
elif st.session_state.page == "putt_result":
    st.caption(progress())
    st.subheader("Where did the putt go?")

    for label in ["Left", "Right", "Short", "Long", "Hole"]:
        st.button(
            label,
            use_container_width=True,
            on_click=lambda l=label: (
                st.session_state.shot.update({"result": l.lower()}),
                save_shot(),
                finish_hole() if l == "Hole" else go("putt_distance")
            )
        )

    st.button("⬅ Back", use_container_width=True, on_click=back)


# =========================
# SUMMARY
# =========================
elif st.session_state.page == "summary":
    st.title("Round Complete 🏁")
    st.json(st.session_state.round)
