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
    return f"Hole {st.session_state.hole_index} of {st.session_state.round['holes_played']} • Shot {shot_number()}"


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
    st.session_state.round["holes"] = []

    st.button("Start Round", use_container_width=True, on_click=lambda: go("hole_setup"))


# =========================
# HOLE SETUP (PAR + YARDAGE + CONFIRM)
# =========================
elif st.session_state.page == "hole_setup":
    st.subheader(f"Hole {st.session_state.hole_index} Setup")

    st.write("Select Hole Par")
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
            "Hole Yardage (yards)",
            50,
            800,
            st.session_state.temp_yardage,
            step=1
        )

        c1, c2 = st.columns(2)

        if c1.button("⬅ Back", use_container_width=True):
            st.session_state.temp_par = None
            st.session_state.temp_yardage = None
            if st.session_state.hole_index > 1:
                st.session_state.hole_index -= 1
                st.session_state.round["holes"].pop()
            go("hole_setup")

        if c2.button("Confirm Hole", use_container_width=True):
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
# SHOT RESULT (HOLE MAP)
# =========================
elif st.session_state.page == "shot_result":
    st.caption(progress())
    st.subheader("Tap where the ball finished")

    # GREEN AREA
    st.markdown("### Green")
    g1, g2 = st.columns(2)

    g1.button("Green", use_container_width=True,
              on_click=lambda: (
                  st.session_state.update({"shot": {"shot_number": shot_number(), "result": "green"}}),
                  go("putt_distance")
              ))

    g2.button("Hole", use_container_width=True,
              on_click=lambda: (
                  st.session_state.update({"shot": {"shot_number": shot_number(), "result": "hole"}}),
                  save_shot(),
                  finish_hole()
              ))

    st.button("Greenside Bunker", use_container_width=True,
              on_click=lambda: (
                  st.session_state.update({"shot": {"shot_number": shot_number(), "result": "greenside_bunker"}}),
                  save_shot(),
                  go("approach_distance")
              ))

    # FAIRWAY AREA
    st.markdown("### Fairway")
    f1, f2, f3 = st.columns(3)

    f1.button("Left Rough", use_container_width=True,
              on_click=lambda: (
                  st.session_state.update({"shot": {"shot_number": shot_number(), "result": "rough", "direction": "left"}}),
                  save_shot(),
                  go("approach_distance")
              ))

    f2.button("Fairway", use_container_width=True,
              on_click=lambda: (
                  st.session_state.update({"shot": {"shot_number": shot_number(), "result": "fairway"}}),
                  save_shot(),
                  go("approach_distance")
              ))

    f3.button("Right Rough", use_container_width=True,
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

    # OTHER
    st.markdown("### Other")
    o1, o2 = st.columns(2)

    o1.button("Water", use_container_width=True,
              on_click=lambda: (
                  st.session_state.update({"shot": {"shot_number": shot_number(), "result": "water"}}),
                  go("shot_direction")
              ))

    o2.button("Out of Bounds", use_container_width=True,
              on_click=lambda: (
                  st.session_state.update({"shot": {"shot_number": shot_number(), "result": "out_of_bounds"}}),
                  go("shot_direction")
              ))

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
# PUTT RESULT (VISUAL MAP)
# =========================
elif st.session_state.page == "putt_result":
    st.caption(progress())
    st.subheader("Where did the putt go?")

    # Top
    c1, c2, c3 = st.columns(3)
    c2.button("Left", use_container_width=True,
              on_click=lambda: (
                  st.session_state.shot.update({"result": "left"}),
                  save_shot(),
                  go("putt_distance")
              ))

    # Middle
    c1, c2, c3 = st.columns(3)
    c1.button("Short", use_container_width=True,
              on_click=lambda: (
                  st.session_state.shot.update({"result": "short"}),
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

    # Bottom
    c1, c2, c3 = st.columns(3)
    c2.button("Long", use_container_width=True,
              on_click=lambda: (
                  st.session_state.shot.update({"result": "long"}),
                  save_shot(),
                  go("putt_distance")
              ))

    st.button("⬅ Back", use_container_width=True, on_click=back)


# =========================
# SUMMARY / STATS RECAP
# =========================
elif st.session_state.page == "summary":
    st.title("Round Stats Recap 📊")

    holes = st.session_state.round["holes"]
    holes_played = len(holes)

    # Fairways
    fw_holes = [h for h in holes if h["par"] in (4, 5)]
    fw_hit = sum(1 for h in fw_holes if h["shots"][0]["result"] == "fairway")

    st.subheader("Fairways Hit")
    st.write(f"{fw_hit} / {len(fw_holes)}")

    # GIR
    gir = 0
    for h in holes:
        for s in h["shots"]:
            if s.get("result") == "green" and s["shot_number"] <= h["par"] - 2:
                gir += 1
                break

    st.subheader("Greens in Regulation")
    st.write(f"{gir} / {holes_played}")

    # Putting
    total_putts = sum(1 for h in holes for s in h["shots"] if "putt_distance" in s)
    st.subheader("Putting")
    st.write(f"Total Putts: {total_putts}")
    st.write(f"Putts per Hole: {total_putts / holes_played:.2f}")

    # Distances
    par4_app = []
    par3_tee = []

    for h in holes:
        shots = h["shots"]
        if h["par"] == 4 and len(shots) > 1 and "distance_to_hole" in shots[1]:
            par4_app.append(shots[1]["distance_to_hole"])
        if h["par"] == 3 and "distance_to_hole" in shots[0]:
            par3_tee.append(shots[0]["distance_to_hole"])

    st.subheader("Distance Averages")
    if par4_app:
        st.write(f"Avg Par 4 Approach: {sum(par4_app)/len(par4_app):.1f} yds")
    if par3_tee:
        st.write(f"Avg Par 3 Tee Shot: {sum(par3_tee)/len(par3_tee):.1f} yds")

