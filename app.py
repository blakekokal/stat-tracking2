import streamlit as st
import pandas as pd

# ------------------------------
# Initialize session state
# ------------------------------
for key, default in [
    ("round", None),
    ("current_hole", 1),
    ("current_shot", 1),
    ("current_hole_obj", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ------------------------------
# Helper Functions
# ------------------------------
MAIN_LIES = ["fairway", "rough", "bunker", "water", "green", "hole"]

def start_new_round(player_name, course_name, holes_played, course_par):
    st.session_state.round = {
        "player_name": player_name,
        "course_name": course_name,
        "holes_played": holes_played,
        "course_par": course_par,
        "holes": []
    }

def add_shot(distance, start_lie, end_lie, distance_to_hole):
    shot = {
        "shot_number": st.session_state.current_shot,
        "distance": distance,
        "start_lie": start_lie,
        "end_lie": end_lie,
        "distance_to_hole": distance_to_hole
    }
    st.session_state.current_hole_obj["shots"].append(shot)

def finish_hole():
    st.session_state.round["holes"].append(st.session_state.current_hole_obj)
    st.session_state.current_hole += 1
    st.session_state.current_shot = 1
    st.session_state.current_hole_obj = None

def go_back_shot():
    if st.session_state.current_shot > 1:
        st.session_state.current_hole_obj["shots"].pop()
        st.session_state.current_shot -= 1
    else:
        if st.session_state.current_hole > 1:
            st.session_state.current_hole -= 1
            prev_hole = st.session_state.round["holes"].pop()
            st.session_state.current_hole_obj = prev_hole
            st.session_state.current_shot = len(prev_hole["shots"])

# ------------------------------
# App UI
# ------------------------------
st.title("Golf Stat Tracker")

# ------------------------------
# Round Setup
# ------------------------------
if st.session_state.round is None:
    st.header("Round Setup")
    player = st.text_input("Player Name")
    course = st.text_input("Course Name")
    holes_played = st.number_input("Holes Played", min_value=1, max_value=18, value=18, step=1)
    course_par = st.number_input("Course Par", min_value=9, max_value=72, value=holes_played*4, step=1)
    if player and course:
        if st.button("Start Round"):
            start_new_round(player, course, holes_played, course_par)
            st.experimental_rerun()  # only here, safe on setup

# ------------------------------
# Hole & Shot Entry
# ------------------------------
elif st.session_state.current_hole <= st.session_state.round["holes_played"]:
    hole_num = st.session_state.current_hole

    # Hole setup
    if st.session_state.current_hole_obj is None:
        st.subheader(f"Hole {hole_num} Setup")
        par = st.number_input(f"Hole {hole_num} Par", min_value=3, max_value=5, step=1, key=f"par{hole_num}")
        yardage = st.number_input(f"Hole {hole_num} Yardage", min_value=50, max_value=800, step=1, key=f"yard{hole_num}")
        if st.button("Start Hole"):
            st.session_state.current_hole_obj = {
                "hole_number": hole_num,
                "par": par,
                "yardage": yardage,
                "shots": []
            }
            st.session_state.current_shot = 1

    # Shot entry
    else:
        shot_num = st.session_state.current_shot
        st.subheader(f"Hole {hole_num} - Shot {shot_num}")
        st.caption(f"Progress: Hole {hole_num} of {st.session_state.round['holes_played']}, Shot {shot_num}")

        start_lie = "tee" if shot_num==1 else st.session_state.current_hole_obj["shots"][-1]["end_lie"]
        distance = None
        distance_to_hole = None

        # Go back button
        if st.button("Go Back / Edit Last Shot"):
            go_back_shot()

        # Distance input for non-putts
        if start_lie != "green":
            distance = st.number_input("Shot distance (yards)", min_value=0, step=1, format="%d")

        # Shot lie selection
        clicked_lie = st.radio("Where did the ball go?", MAIN_LIES)

        # Stepwise side selection
        if clicked_lie == "rough":
            side = st.radio("Which rough?", ["left rough","right rough","short rough","long rough"])
            clicked_lie = side
        elif clicked_lie == "bunker":
            side = st.radio("Which bunker?", ["left bunker","right bunker","fairway bunker"])
            clicked_lie = side
        elif clicked_lie == "water":
            side = st.radio("Which water?", ["left water","right water","long water"])
            clicked_lie = side
        elif clicked_lie == "green":
            distance_to_hole = st.number_input("Distance from hole (ft)", min_value=0, step=1, format="%d")

        # Confirm shot button
        if st.button("Confirm Shot"):
            add_shot(distance, start_lie, clicked_lie, distance_to_hole)
            if clicked_lie == "hole":
                finish_hole()
            else:
                st.session_state.current_shot += 1

# ------------------------------
# Round Summary & Export
# ------------------------------
elif st.session_state.current_hole > st.session_state.round["holes_played"]:
    rnd = st.session_state.round
    st.header("🏁 Round Summary")

    # Convert shots to DataFrame
    rows = []
    for h in rnd["holes"]:
        for s in h["shots"]:
            rows.append([
                rnd["player_name"],
                rnd["course_name"],
                h["hole_number"],
                h["par"],
                h["yardage"],
                s["shot_number"],
                s["distance"],
                s["start_lie"],
                s["end_lie"],
                s["distance_to_hole"]
            ])
    df = pd.DataFrame(rows, columns=[
        "Player","Course","Hole","Par","Hole_Yardage","Shot#",
        "Distance","Start_Lie","End_Lie","Distance_to_Hole"
    ])

    # Score
    total_score = df.groupby("Hole")["Shot#"].max().sum()
    st.subheader("Score")
    st.metric("Total Score", total_score)
    st.metric("Score vs Par", total_score - rnd["course_par"])

    st.subheader("Shots Table")
    st.dataframe(df)

    # Export
    st.subheader("Export Round Data")
    excel_file = "round.xlsx"
    df.to_excel(excel_file, index=False)
    with open(excel_file,"rb") as f:
        st.download_button("Download Excel", data=f, file_name="round.xlsx")
    csv_file = "round.csv"
    df.to_csv(csv_file, index=False)
    with open(csv_file,"rb") as f:
        st.download_button("Download CSV", data=f, file_name="round.csv")

    st.success("Round complete! Download your Excel or CSV file above.")
