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
    page = st.session_state.page
    if page in ["approach_distance", "shot_direction", "putt_distance"]:
        go("shot_result")
    elif page == "putt_result":
        go("putt_distance")
    elif page == "shot_result":
        go("hole_setup")
    else:
        go("shot_result")


# =========================
# ROUND SETUP
# =========================
if st.session_state.page == "round":
    st.title("Golf Stat Tracker")

    st.session_state.round["player"] = st.text_input("Player")
    st.session_state.round["course"] = st.text_input("Course")
    st.session_state.round["holes_played"] = st.number_input("Holes", 1, 18, 18)
    st.session_state.round["holes"] = []

    st.button("Start Round", use_container_width=True)


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
            "Yardage", 50, 800, st.session_state.temp_yardage, step=1
        )

        c1, c2 = st.columns(2)
        c1.button("Back", use_container_width=True, on_click=back)
        c2.button(
            "Confirm",
            use_container_width=True,
            on_click=lambda: (
                st.session_state.update({
                    "hole": {
                        "hole_number": st.session_state.hole_index,
                        "par": st.session_state.temp_par,
                        "yardage": st.session_state.temp_yardage,
                        "shots": []
                    }
                }),
                st.session_state.update({"temp_par": None, "temp_yardage": None}),
                go("shot_result")
            )
        )


# =========================
# SHOT RESULT (MOBILE)
# =========================
elif st.session_state.page == "shot_result":
    st.caption(progress())

    with st.container():
        st.button("HOLE", use_container_width=True,
                  on_click=lambda: (
                      st.session_state.update({"shot": {"shot_number": shot_number(), "result": "hole"}}),
                      save_shot(),
                      finish_hole()
                  ))

        st.button("Green", use_container_width=True,
                  on_click=lambda: (
                      st.session_state.update({"shot": {"shot_number": shot_number(), "result": "green"}}),
                      go("putt_distance")
                  ))

        st.button("Greenside Bunker", use_container_width=True,
                  on_click=lambda: (
                      st.session_state.update({"shot": {"shot_number": shot_number(), "result": "greenside_bunker"}}),
                      save_shot(),
                      go("approach_distance")
                  ))

        st.button("Fairway", use_container_width=True,
                  on_click=lambda: (
                      st.session_state.update({"shot": {"shot_number": shot_number(), "result": "fairway"}}),
                      save_shot(),
                      go("approach_distance")
                  ))

        r1, r2 = st.columns(2)
        r1.button("Left Rough", use_container_width=True,
                  on_click=lambda: (
                      st.session_state.update({"shot": {"shot_number": shot_number(), "result": "rough", "direction": "left"}}),
                      save_shot(),
                      go("approach_distance")
                  ))
        r2.button("Right Rough", use_container_width=True,
                  on_click=lambda: (
                      st.session_state.update({"shot": {"shot_number": shot_number(), "result": "rough", "direction": "right"}}),
                      save_shot(),
                      go("approach_distance")
                  ))

        st.button("Fairway Bunker", use_container_width=True,
                  on_click=lambda: (
                      st.session_state.update({"shot": {"shot_number": shot_number(), "result": "fairway_bunker"}}),
                      go("shot_direction")
                  ))

        o1, o2 = st.columns(2)
        o1.button("Water", use_container_width=True,
                  on_click=lambda: (
                      st.session_state.update({"shot": {"shot_number": shot_number(), "result": "water"}}),
                      go("shot_direction")
                  ))
        o2.button("OB", use_container_width=True,
                  on_click=lambda: (
                      st.session_state.update({"shot": {"shot_number": shot_number(), "result": "out_of_bounds"}}),
                      go("shot_direction")
                  ))

        st.button("Back", use_container_width=True, on_click=back)


# =========================
# APPROACH DISTANCE
# =========================
elif st.session_state.page == "approach_distance":
    st.caption(progress())
    st.session_state.shot = {
        "shot_number": shot_number(),
        "distance_to_hole": st.number_input("Yards", 0, 400, 50, step=1)
    }
    c1, c2 = st.columns(2)
    c1.button("Back", use_container_width=True, on_click=back)
    c2.button("Next", use_container_width=True, on_click=lambda: go("shot_result"))


# =========================
# SHOT DIRECTION
# =========================
elif st.session_state.page == "shot_direction":
    st.caption(progress())
    d1, d2, d3, d4 = st.columns(4)
    for label, col in zip(["Left", "Right", "Short", "Long"], [d1, d2, d3, d4]):
        col.button(label, use_container_width=True,
                   on_click=lambda l=label: (
                       st.session_state.shot.update({"direction": l.lower()}),
                       save_shot(),
                       go("approach_distance")
                   ))
    st.button("Back", use_container_width=True, on_click=back)


# =========================
# PUTTING DISTANCE
# =========================
elif st.session_state.page == "putt_distance":
    st.caption(progress())
    st.session_state.shot = {
        "shot_number": shot_number(),
        "putt_distance": st.number_input("Feet", 0, 100, 15, step=1)
    }
    c1, c2 = st.columns(2)
    c1.button("Back", use_container_width=True, on_click=back)
    c2.button("Next", use_container_width=True, on_click=lambda: go("putt_result"))


# =========================
# PUTT RESULT (MOBILE GRID)
# =========================
elif st.session_state.page == "putt_result":
    st.caption(progress())

    c1, c2, c3 = st.columns(3)
    c2.button("Long", use_container_width=True,
              on_click=lambda: (
                  st.session_state.shot.update({"result": "long"}),
                  save_shot(),
                  go("putt_distance")
              ))

    c1, c2, c3 = st.columns(3)
    c1.button("Left", use_container_width=True,
              on_click=lambda: (
                  st.session_state.shot.update({"result": "left"}),
                  save_shot(),
                  go("putt_distance")
              ))
    c2.button("Hole", use_container_width=True,
              on_click=lambda: (
                  st.session_state.shot.update({"result": "hole"}),
                  save_shot(),
                  finish_hole()
              ))
    c3.button("Right", use_container_width=True,
              on_click=lambda: (
                  st.session_state.shot.update({"result": "right"}),
                  save_shot(),
                  go("putt_distance")
              ))

    c1, c2, c3 = st.columns(3)
    c2.button("Short", use_container_width=True,
              on_click=lambda: (
                  st.session_state.shot.update({"result": "short"}),
                  save_shot(),
                  go("putt_distance")
              ))

    st.button("Back", use_container_width=True, on_click=back)


# =========================
# SUMMARY
# =========================
elif st.session_state.page == "summary":
    st.title("Round Summary")
    st.json(st.session_state.round)
