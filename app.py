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

    if st.button("Start Round", use_container_width=True):
        go("hole_setup")


# =========================
# HOLE SETUP
# =========================
elif st.session_state.page == "hole_setup":
    st.subheader(f"Hole {st.session_state.hole_index} Setup")

    c1, c2, c3 = st.columns(3)
    if c1.button("Par 3"):
        st.session_state.temp_par, st.session_state.temp_yardage = 3, 170
    if c2.button("Par 4"):
        st.session_state.temp_par, st.session_state.temp_yardage = 4, 400
    if c3.button("Par 5"):
        st.session_state.temp_par, st.session_state.temp_yardage = 5, 520

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

    c1, c2 = st.columns(2)
    if c1.button("Left Rough", use_container_width=True):
        st.session_state.shot = {"shot_number": shot_number(), "result": "rough", "direction": "left"}
        save_shot()
        go("approach_distance")

    if c2.button("Right Rough", use_container_width=True):
        st.session_state.shot = {"shot_number": shot_number(), "result": "rough", "direction": "right"}
        save_shot()
        go("approach_distance")


# =========================
# APPROACH DISTANCE
# =========================
elif st.session_state.page == "approach_distance":
    st.caption(progress())
    st.subheader(f"Shot {shot_number()} – distance to hole")

    dist = st.number_input("Yards", 0, 400, 150, step=1)

    if st.button("Next", use_container_width=True):
        st.session_state.shot["distance_to_hole"] = dist
        go("shot_result")


# =========================
# PUTTING DISTANCE
# =========================
elif st.session_state.page == "putt_distance":
    st.caption(progress())
    st.subheader("Putting – distance to hole")

    feet = st.number_input("Feet", 0, 100, 15, step=1)

    if st.button("Next", use_container_width=True):
        st.session_state.shot["putt_distance"] = feet
        go("putt_result")


# =========================
# PUTT RESULT
# =========================
elif st.session_state.page == "putt_result":
    st.caption(progress())
    st.subheader("Where did the putt go?")

    for label in ["Left", "Right", "Short", "Long", "Hole"]:
        if st.button(label, use_container_width=True):
            st.session_state.shot["result"] = label.lower()
            save_shot()
            if label == "Hole":
                finish_hole()
            else:
                go("putt_distance")


# =========================
# SUMMARY + EXPORT
# =========================
elif st.session_state.page == "summary":
    st.title("Round Stats Recap 📊")

    round_date = st.session_state.round["date"].strftime("%m/%d/%Y")
    st.caption(f"{round_date} • {st.session_state.round.get('course','')}")

    holes = st.session_state.round["holes"]
    holes_played = len(holes)

    rows = []
    for h in holes:
        for s in h["shots"]:
            rows.append({
                "date": round_date,
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

    st.subheader("Export Round Data")
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇ Download CSV", csv, "round_data.csv", mime="text/csv")

    try:
        excel_buffer = BytesIO()
        df.to_excel(excel_buffer, index=False)
        st.download_button("⬇ Download Excel", excel_buffer.getvalue(), "round_data.xlsx")
    except Exception:
        st.info("Excel export unavailable. CSV recommended.")
