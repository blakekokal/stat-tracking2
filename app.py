import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import date

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
# STROKES GAINED BASELINE
# =========================
def expected_strokes(distance_yards=None, putt_feet=None, handicap=0):
    adj = handicap * 0.05

    if putt_feet is not None:
        return max(0.5, (putt_feet * 0.05) + adj)

    if distance_yards is None:
        return 0

    if distance_yards > 200:
        return 3.2 + adj
    if distance_yards > 150:
        return 3.0 + adj
    if distance_yards > 100:
        return 2.8 + adj
    if distance_yards > 50:
        return 2.3 + adj
    return 1.8 + adj


# =========================
# ROUND SETUP
# =========================
if st.session_state.page == "round":
    st.title("Golf Stat Tracker")

    st.session_state.round["date"] = st.date_input("Round Date", value=date.today())
    st.session_state.round["player"] = st.text_input("Player Name")
    st.session_state.round["course"] = st.text_input("Course Name")
    st.session_state.round["holes_played"] = st.number_input("Holes Played", 1, 18, 18)
    st.session_state.round["holes"] = []

    st.button("Start Round", use_container_width=True, on_click=lambda: go("hole_setup"))


# =========================
# HOLE SETUP
# =========================
elif st.session_state.page == "hole_setup":
    st.subheader(f"Hole {st.session_state.hole_index} Setup")

    p1, p2, p3 = st.columns(3)
    if p1.button("Par 3"): st.session_state.temp_par, st.session_state.temp_yardage = 3, 170
    if p2.button("Par 4"): st.session_state.temp_par, st.session_state.temp_yardage = 4, 400
    if p3.button("Par 5"): st.session_state.temp_par, st.session_state.temp_yardage = 5, 520

    if st.session_state.temp_par:
        st.session_state.temp_yardage = st.number_input(
            "Hole Yardage (yards)", 50, 800, st.session_state.temp_yardage, step=1
        )

        if st.button("Confirm Hole", use_container_width=True):
            st.session_state.hole = {
                "hole_number": st.session_state.hole_index,
                "par": st.session_state.temp_par,
                "yardage": st.session_state.temp_yardage,
                "shots": []
            }
            st.session_state.temp_par = None
            go("shot_result")


# =========================
# SHOT RESULT
# =========================
elif st.session_state.page == "shot_result":
    st.caption(progress())
    st.subheader("Tap where the ball finished")

    st.button("HOLE", use_container_width=True,
              on_click=lambda: (
                  st.session_state.update({"shot": {"shot_number": shot_number(), "result": "hole"}}),
                  save_shot(),
                  finish_hole()
              ))

    st.markdown("### Green")
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

    st.markdown("### Fairway")
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
        "distance_to_hole": st.number_input("Yards", 0, 400, 150, step=1)
    }

    st.button("Next", use_container_width=True, on_click=lambda: go("shot_result"))


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

    st.button("Next", use_container_width=True, on_click=lambda: go("putt_result"))


# =========================
# PUTT RESULT
# =========================
elif st.session_state.page == "putt_result":
    st.caption(progress())
    st.subheader("Where did the putt go?")

    for label in ["Left", "Right", "Short", "Long", "Hole"]:
        if st.button(label, use_container_width=True):
            st.session_state.shot.update({"result": label.lower()})
            save_shot()
            if label == "Hole":
                finish_hole()
            else:
                go("putt_distance")


# =========================
# SUMMARY + STROKES GAINED
# =========================
elif st.session_state.page == "summary":
    st.title("Round Stats Recap 📊")

    handicap = st.number_input("Strokes Gained Baseline Handicap", -5.0, 20.0, 0.0, step=0.5)

    sg = {"OTT": 0, "APP": 0, "SG": 0, "PUTT": 0}

    for h in st.session_state.round["holes"]:
        shots = h["shots"]

        for s in shots:
            if "putt_distance" in s:
                before = expected_strokes(putt_feet=s["putt_distance"], handicap=handicap)
                after = 0 if s.get("result") == "hole" else expected_strokes(putt_feet=3, handicap=handicap)
                sg["PUTT"] += before - (1 + after)
                continue

            dist = s.get("distance_to_hole")
            before = expected_strokes(distance_yards=dist, handicap=handicap)
            after = expected_strokes(distance_yards=50, handicap=handicap)

            cat = "APP"
            if s["shot_number"] == 1:
                cat = "OTT"
            elif dist is not None and dist <= 100:
                cat = "SG"

            sg[cat] += before - (1 + after)

    st.subheader("Strokes Gained")
    st.write(f"Off the Tee: {sg['OTT']:+.2f}")
    st.write(f"Approach: {sg['APP']:+.2f}")
    st.write(f"Short Game: {sg['SG']:+.2f}")
    st.write(f"Putting: {sg['PUTT']:+.2f}")
    st.write(f"Total: {sum(sg.values()):+.2f}")
