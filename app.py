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

        start_lie = "tee" if shot_num == 1 else st.session_state.current_hole_obj["shots"][-1]["end_lie"]
        distance = None
        distance_to_hole = None

        # Go back button
        if st.button("Go Back / Edit Last Shot"):
            go_back_shot()

        # Distance input for non-putts
        if start_lie != "green":
            distance = st.number_input("Shot distance (yards)", min_value=0, step=1, format="%d")

        # Big buttons for shot destination
        st.write("Where did the ball go? (Tap one)")
        clicked_lie = None
        cols = st.columns(3)  # 3 big buttons per row
        for i, lie in enumerate(MAIN_LIES):
            if cols[i % 3].button(lie.capitalize(), key=f"btn_{hole_num}_{shot_num}_{lie}"):
                clicked_lie = lie

        if clicked_lie:
            end_lie = clicked_lie

            # Stepwise selection for rough/bunker/water
            if end_lie == "rough":
                st.write("Which rough?")
                rough_cols = st.columns(2)
                rough_options = ["left rough","right rough","short rough","long rough"]
                for i, option in enumerate(rough_options):
                    if rough_cols[i % 2].button(option, key=f"rough_{hole_num}_{shot_num}_{option}"):
                        end_lie = option

            elif end_lie == "bunker":
                st.write("Which bunker?")
                bunker_cols = st.columns(2)
                bunker_options = ["left bunker","right bunker","fairway bunker"]
                for i, option in enumerate(bunker_options):
                    if bunker_cols[i % 2].button(option, key=f"bunker_{hole_num}_{shot_num}_{option}"):
                        end_lie = option

            elif end_lie == "water":
                st.write("Which water?")
                water_cols = st.columns(2)
                water_options = ["left water","right water","long water"]
                for i, option in enumerate(water_options):
                    if water_cols[i % 2].button(option, key=f"water_{hole_num}_{shot_num}_{option}"):
                        end_lie = option

            elif end_lie == "green":
                distance_to_hole = st.number_input("Distance from hole (ft)", min_value=0, step=1, format="%d")

            # Confirm shot button
            if st.button("Confirm Shot"):
                add_shot(distance, start_lie, end_lie, distance_to_hole)
                if end_lie == "hole":
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

    # Score calculations
    strokes_per_hole = df.groupby("Hole")["Shot#"].max()
    total_score = strokes_per_hole.sum()
    score_vs_par = total_score - rnd["course_par"]
    st.subheader("Score")
    st.metric("Total Score", total_score)
    st.metric("Score vs Par", score_vs_par)

    # Putts
    putts_df = df[df["Start_Lie"]=="green"]
    total_putts = len(putts_df)
    putts_per_hole = round(total_putts / len(rnd["holes"]), 2) if len(rnd["holes"]) else 0
    gir_hits = 0
    for h_num, group in df.groupby("Hole"):
        par = group.iloc[0]["Par"]
        shots_to_green = group[group["End_Lie"]=="green"]["Shot#"]
        if not shots_to_green.empty and shots_to_green.min() <= par - 2:
            gir_hits += 1
    putts_per_gir = round(total_putts / gir_hits, 2) if gir_hits else "N/A"
    st.subheader("Putting")
    st.write(f"Total Putts: {total_putts}")
    st.write(f"Putts per Hole: {putts_per_hole}")
    st.write(f"Putts per GIR: {putts_per_gir}")

    # Fairways hit/missed
    fw_df = df.groupby("Hole").first()  # tee shots
    fw_hit = fw_df[fw_df["End_Lie"].str.contains("fairway")].shape[0]
    fw_missed = fw_df[~fw_df["End_Lie"].str.contains("fairway")].shape[0]
    fw_missed_left = fw_df[fw_df["End_Lie"].str.contains("left")].shape[0]
    fw_missed_right = fw_df[fw_df["End_Lie"].str.contains("right")].shape[0]
    st.subheader("Fairways")
    st.write(f"Hit: {fw_hit}, Missed: {fw_missed} (Left: {fw_missed_left}, Right: {fw_missed_right})")

    # GIR
    gir_total = len(rnd["holes"])
    gir_missed_left = 0
    gir_missed_right = 0
    gir_missed_short = 0
    gir_missed_long = 0
    for h_num, group in df.groupby("Hole"):
        par = group.iloc[0]["Par"]
        shots_to_green = group[group["End_Lie"]=="green"]["Shot#"]
        if not shots_to_green.empty and shots_to_green.min() <= par - 2:
            continue  # GIR made
        else:
            last_shot = group[group["End_Lie"]!="hole"].iloc[-1]
            lie = last_shot["End_Lie"]
            if "left" in lie: gir_missed_left += 1
            elif "right" in lie: gir_missed_right += 1
            elif "short" in lie: gir_missed_short += 1
            elif "long" in lie: gir_missed_long += 1
    st.subheader("Greens in Regulation")
    st.write(f"GIR: {gir_hits}/{gir_total}")
    st.write(f"Missed Left: {gir_missed_left}, Right: {gir_missed_right}, Short: {gir_missed_short}, Long: {gir_missed_long}")

    # Directional bias of all shots
    directions = {"left":0,"right":0,"short":0,"long":0}
    for lie in df["End_Lie"]:
        for d in directions.keys():
            if d in str(lie):
                directions[d] += 1
    st.subheader("Directional Bias")
    st.write(directions)

    # Strokes by category
    categories = {"tee":0,"approach":0,"short_game":0,"putting":0}
    for _, row in df.iterrows():
        if row["Start_Lie"]=="green":
            categories["putting"] += 1
        elif row["Shot#"]==1:
            categories["tee"] += 1
        elif row["Distance"] and row["Distance"] > 100:
            categories["approach"] += 1
        else:
            categories["short_game"] += 1
    st.subheader("Shots by Category")
    st.write(categories)

    # Show shot table
    st.subheader("All Shots Table")
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
