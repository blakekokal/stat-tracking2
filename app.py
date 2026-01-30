import streamlit as st
import pandas as pd
from io import BytesIO

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
# HOLE SETUP
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
            "Hole Yardage (yards)", 50, 800, st.session_state.temp_yardage, step=1
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

    st.button("⬅ Back", use_container_width=True, on_click=back)


# =========================
# SUMMARY + EXPORT
# =========================
elif st.session_state.page == "summary":
    st.title("Round Stats Recap 📊")

    holes = st.session_state.round["holes"]
    holes_played = len(holes)

    rows = []
    for h in holes:
        for s in h["shots"]:
            rows.append({
                "hole": h["hole_number"],
                "par": h["par"],
                "hole_yardage": h["yardage"],
                "shot_number": s.get("shot_number"),
                "result": s.get("result"),
                "direction": s.get("direction"),
                "distance_to_hole": s.get("distance_to_hole"),
                "putt_distance": s.get("putt_distance"),
            })

    df = pd.DataFrame(rows)

    total_shots = len(df)
    total_par = sum(h["par"] for h in holes)
    st.subheader("Score")
    st.write(f"{total_shots} (Par {total_par}, {total_shots - total_par:+})")

    # FAIRWAYS
    fw_holes = [h for h in holes if h["par"] in (4, 5)]
    fw_shots = [h["shots"][0] for h in fw_holes]
    fw_hit = sum(1 for s in fw_shots if s["result"] == "fairway")
    fw_left = sum(1 for s in fw_shots if s.get("direction") == "left")
    fw_right = sum(1 for s in fw_shots if s.get("direction") == "right")

    st.subheader("Fairways Hit (Par 4 & 5)")
    st.write(f"{fw_hit} / {len(fw_holes)} ({fw_hit / len(fw_holes) * 100:.1f}%)")
    st.write(f"Miss Left: {fw_left} • Miss Right: {fw_right}")

    # GIR + PROXIMITY
    gir = 0
    miss_dir = {"left": 0, "right": 0, "short": 0, "long": 0}
    first_putt = []
    first_putt_gir = []
    first_putt_miss = []

    for h in holes:
        putts = [s for s in h["shots"] if s.get("putt_distance") is not None]
        if not putts:
            continue

        fp = putts[0]
        first_putt.append(fp["putt_distance"])

        if fp["shot_number"] <= h["par"] - 1:
            gir += 1
            first_putt_gir.append(fp["putt_distance"])
        else:
            first_putt_miss.append(fp["putt_distance"])
            prev = h["shots"][fp["shot_number"] - 2]
            if prev.get("direction") in miss_dir:
                miss_dir[prev["direction"]] += 1

    st.subheader("Greens in Regulation")
    st.write(f"{gir} / {holes_played} ({gir / holes_played * 100:.1f}%)")
    st.write(
        f"Miss L/R/S/L: "
        f"{miss_dir['left']} / {miss_dir['right']} / "
        f"{miss_dir['short']} / {miss_dir['long']}"
    )

    st.subheader("Putting & Proximity")
    st.write(f"Average First Putt: {sum(first_putt) / len(first_putt):.1f} ft")
    if first_putt_gir:
        st.write(f"Average Proximity (GIR): {sum(first_putt_gir) / len(first_putt_gir):.1f} ft")
    if first_putt_miss:
        st.write(f"Average Proximity (Missed Green): {sum(first_putt_miss) / len(first_putt_miss):.1f} ft")

    # EXPORT
    st.subheader("Export Round Data")

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇ Download CSV (Google Sheets)", csv, "round_data.csv", mime="text/csv")

    try:
        excel_buffer = BytesIO()
        df.to_excel(excel_buffer, index=False)
        st.download_button(
            "⬇ Download Excel",
            excel_buffer.getvalue(),
            "round_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception:
        st.info("Excel export unavailable on this server. Use CSV or enable openpyxl.")
