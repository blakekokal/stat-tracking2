import streamlit as st
import pandas as pd
from datetime import date
import json

# Initialize session state
if 'stage' not in st.session_state:
    st.session_state.stage = 'initial'
if 'round_data' not in st.session_state:
    st.session_state.round_data = {}
if 'current_hole' not in st.session_state:
    st.session_state.current_hole = 1
if 'hole_data' not in st.session_state:
    st.session_state.hole_data = {}
if 'shot_number' not in st.session_state:
    st.session_state.shot_number = 1
if 'on_green' not in st.session_state:
    st.session_state.on_green = False
if 'all_holes' not in st.session_state:
    st.session_state.all_holes = []

st.title("⛳ Golf Stat Tracker")

# Initial Info Stage
if st.session_state.stage == 'initial':
    st.header("Round Information")
    
    round_date = st.date_input("Date", value=date.today())
    player_name = st.text_input("Player Name")
    course_name = st.text_input("Golf Course Name")
    num_holes = st.radio("Number of Holes", [9, 18])
    
    if st.button("Start Round"):
        if player_name and course_name:
            st.session_state.round_data = {
                'date': str(round_date),
                'player': player_name,
                'course': course_name,
                'num_holes': num_holes
            }
            st.session_state.stage = 'hole_setup'
            st.rerun()
        else:
            st.error("Please fill in all fields")

# Hole Setup Stage
elif st.session_state.stage == 'hole_setup':
    st.header(f"Hole {st.session_state.current_hole} Setup")
    
    par = st.selectbox("Par", [3, 4, 5])
    yards = st.number_input("Yardage", min_value=50, max_value=650, value=350)
    
    if st.button("Start Hole"):
        st.session_state.hole_data = {
            'hole_number': st.session_state.current_hole,
            'par': par,
            'yards': yards,
            'shots': [],
            'total_shots': 0,
            'putts': 0
        }
        st.session_state.shot_number = 1
        st.session_state.on_green = False
        st.session_state.stage = 'tee_shot'
        st.rerun()

# Tee Shot Stage
elif st.session_state.stage == 'tee_shot':
    st.header(f"Hole {st.session_state.current_hole} - Shot {st.session_state.shot_number}")
    st.subheader("Tee Shot")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Fairway"):
            st.session_state.hole_data['shots'].append({'shot': st.session_state.shot_number, 'result': 'Fairway', 'distance': None, 'putt': False})
            st.session_state.stage = 'distance_input'
            st.rerun()
        if st.button("Left Rough"):
            st.session_state.hole_data['shots'].append({'shot': st.session_state.shot_number, 'result': 'Left Rough', 'distance': None, 'putt': False})
            st.session_state.stage = 'distance_input'
            st.rerun()
        if st.button("Right Rough"):
            st.session_state.hole_data['shots'].append({'shot': st.session_state.shot_number, 'result': 'Right Rough', 'distance': None, 'putt': False})
            st.session_state.stage = 'distance_input'
            st.rerun()
    
    with col2:
        if st.button("Fairway Bunker"):
            st.session_state.hole_data['shots'].append({'shot': st.session_state.shot_number, 'result': 'Fairway Bunker', 'distance': None, 'putt': False})
            st.session_state.stage = 'distance_input'
            st.rerun()
        if st.button("Water"):
            st.session_state.hole_data['shots'].append({'shot': st.session_state.shot_number, 'result': 'Water', 'distance': None, 'putt': False})
            st.session_state.stage = 'distance_input'
            st.rerun()
        if st.button("OB"):
            st.session_state.hole_data['shots'].append({'shot': st.session_state.shot_number, 'result': 'OB', 'distance': None, 'putt': False})
            st.session_state.stage = 'distance_input'
            st.rerun()
    
    with col3:
        if st.button("Green"):
            st.session_state.hole_data['shots'].append({'shot': st.session_state.shot_number, 'result': 'Green', 'distance': None, 'putt': False})
            st.session_state.on_green = True
            st.session_state.stage = 'putt_distance'
            st.rerun()
        if st.button("Greenside Bunker"):
            st.session_state.hole_data['shots'].append({'shot': st.session_state.shot_number, 'result': 'Greenside Bunker', 'distance': None, 'putt': False})
            st.session_state.stage = 'distance_input'
            st.rerun()
        if st.button("Hole (Ace!)"):
            st.session_state.hole_data['shots'].append({'shot': st.session_state.shot_number, 'result': 'Hole', 'distance': None, 'putt': False})
            st.session_state.hole_data['total_shots'] = st.session_state.shot_number
            st.session_state.stage = 'hole_complete'
            st.rerun()

# Distance Input (for non-green shots)
elif st.session_state.stage == 'distance_input':
    st.header(f"Hole {st.session_state.current_hole} - After Shot {st.session_state.shot_number}")
    st.subheader(f"Previous shot: {st.session_state.hole_data['shots'][-1]['result']}")
    
    distance = st.number_input("Distance to hole (yards)", min_value=0, max_value=650, value=100)
    
    if st.button("Next Shot"):
        st.session_state.hole_data['shots'][-1]['distance'] = distance
        st.session_state.shot_number += 1
        st.session_state.stage = 'next_shot'
        st.rerun()

# Putt Distance Input
elif st.session_state.stage == 'putt_distance':
    st.header(f"Hole {st.session_state.current_hole} - On the Green")
    st.subheader(f"Shot {st.session_state.shot_number} landed on the green")
    
    distance_feet = st.number_input("Distance to hole (feet)", min_value=0, max_value=100, value=20)
    
    if st.button("Start Putting"):
        st.session_state.hole_data['shots'][-1]['distance'] = distance_feet
        st.session_state.shot_number += 1
        st.session_state.stage = 'putt'
        st.rerun()

# Next Shot Stage (not on green)
elif st.session_state.stage == 'next_shot':
    st.header(f"Hole {st.session_state.current_hole} - Shot {st.session_state.shot_number}")
    st.subheader(f"Distance to hole: {st.session_state.hole_data['shots'][-1]['distance']} yards")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Fairway"):
            st.session_state.hole_data['shots'].append({'shot': st.session_state.shot_number, 'result': 'Fairway', 'distance': None, 'putt': False})
            st.session_state.stage = 'distance_input'
            st.rerun()
        if st.button("Left Rough"):
            st.session_state.hole_data['shots'].append({'shot': st.session_state.shot_number, 'result': 'Left Rough', 'distance': None, 'putt': False})
            st.session_state.stage = 'distance_input'
            st.rerun()
        if st.button("Right Rough"):
            st.session_state.hole_data['shots'].append({'shot': st.session_state.shot_number, 'result': 'Right Rough', 'distance': None, 'putt': False})
            st.session_state.stage = 'distance_input'
            st.rerun()
    
    with col2:
        if st.button("Fairway Bunker"):
            st.session_state.hole_data['shots'].append({'shot': st.session_state.shot_number, 'result': 'Fairway Bunker', 'distance': None, 'putt': False})
            st.session_state.stage = 'distance_input'
            st.rerun()
        if st.button("Water"):
            st.session_state.hole_data['shots'].append({'shot': st.session_state.shot_number, 'result': 'Water', 'distance': None, 'putt': False})
            st.session_state.stage = 'distance_input'
            st.rerun()
        if st.button("OB"):
            st.session_state.hole_data['shots'].append({'shot': st.session_state.shot_number, 'result': 'OB', 'distance': None, 'putt': False})
            st.session_state.stage = 'distance_input'
            st.rerun()
    
    with col3:
        if st.button("Green"):
            st.session_state.hole_data['shots'].append({'shot': st.session_state.shot_number, 'result': 'Green', 'distance': None, 'putt': False})
            st.session_state.on_green = True
            st.session_state.stage = 'putt_distance'
            st.rerun()
        if st.button("Greenside Bunker"):
            st.session_state.hole_data['shots'].append({'shot': st.session_state.shot_number, 'result': 'Greenside Bunker', 'distance': None, 'putt': False})
            st.session_state.stage = 'distance_input'
            st.rerun()
        if st.button("Hole"):
            st.session_state.hole_data['shots'].append({'shot': st.session_state.shot_number, 'result': 'Hole', 'distance': None, 'putt': False})
            st.session_state.hole_data['total_shots'] = st.session_state.shot_number
            st.session_state.stage = 'hole_complete'
            st.rerun()

# Putt Stage
elif st.session_state.stage == 'putt':
    st.header(f"Hole {st.session_state.current_hole} - Putt {st.session_state.shot_number}")
    
    prev_distance = st.session_state.hole_data['shots'][-1].get('distance')
    if prev_distance:
        st.subheader(f"Previous distance: {prev_distance} feet")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Hole (Made it!)"):
            st.session_state.hole_data['shots'].append({'shot': st.session_state.shot_number, 'result': 'Hole', 'distance': 0, 'putt': True})
            st.session_state.hole_data['total_shots'] = st.session_state.shot_number
            # Count putts
            putt_count = sum(1 for shot in st.session_state.hole_data['shots'] if shot.get('putt'))
            st.session_state.hole_data['putts'] = putt_count
            st.session_state.stage = 'hole_complete'
            st.rerun()
    
    with col2:
        distance_feet = st.number_input("Distance remaining (feet)", min_value=0, max_value=100, value=5, key=f"putt_{st.session_state.shot_number}")
        if st.button("Next Putt"):
            st.session_state.hole_data['shots'].append({'shot': st.session_state.shot_number, 'result': 'Green', 'distance': distance_feet, 'putt': True})
            st.session_state.shot_number += 1
            st.rerun()

# Hole Complete Stage
elif st.session_state.stage == 'hole_complete':
    st.header(f"Hole {st.session_state.current_hole} Complete! 🎉")
    
    total_shots = st.session_state.hole_data['total_shots']
    par = st.session_state.hole_data['par']
    putts = st.session_state.hole_data['putts']
    
    score_diff = total_shots - par
    if score_diff == -2:
        score_text = "Eagle! 🦅"
    elif score_diff == -1:
        score_text = "Birdie! 🐦"
    elif score_diff == 0:
        score_text = "Par"
    elif score_diff == 1:
        score_text = "Bogey"
    elif score_diff == 2:
        score_text = "Double Bogey"
    else:
        score_text = f"+{score_diff}"
    
    st.metric("Score", f"{total_shots} ({score_text})")
    st.metric("Putts", putts)
    
    # Save hole data
    st.session_state.all_holes.append(st.session_state.hole_data.copy())
    
    # Check if round is complete
    if st.session_state.current_hole >= st.session_state.round_data['num_holes']:
        if st.button("Finish Round"):
            st.session_state.stage = 'round_summary'
            st.rerun()
    else:
        if st.button("Next Hole"):
            st.session_state.current_hole += 1
            st.session_state.stage = 'hole_setup'
            st.rerun()

# Round Summary
elif st.session_state.stage == 'round_summary':
    st.header("Round Complete! 🏆")
    
    st.subheader(f"{st.session_state.round_data['player']} - {st.session_state.round_data['course']}")
    st.write(f"Date: {st.session_state.round_data['date']}")
    
    total_score = sum(hole['total_shots'] for hole in st.session_state.all_holes)
    total_par = sum(hole['par'] for hole in st.session_state.all_holes)
    total_putts = sum(hole['putts'] for hole in st.session_state.all_holes)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Score", total_score)
    with col2:
        st.metric("Score to Par", f"{total_score - total_par:+d}")
    with col3:
        st.metric("Total Putts", total_putts)
    
    # Detailed scorecard
    st.subheader("Scorecard")
    scorecard_data = []
    for hole in st.session_state.all_holes:
        scorecard_data.append({
            'Hole': hole['hole_number'],
            'Par': hole['par'],
            'Yards': hole['yards'],
            'Score': hole['total_shots'],
            'Putts': hole['putts']
        })
    
    df = pd.DataFrame(scorecard_data)
    st.dataframe(df, use_container_width=True)
    
    # Download data
    round_summary = {
        'round_info': st.session_state.round_data,
        'holes': st.session_state.all_holes
    }
    
    st.download_button(
        label="Download Round Data (JSON)",
        data=json.dumps(round_summary, indent=2),
        file_name=f"golf_round_{st.session_state.round_data['date']}.json",
        mime="application/json"
    )
    
    if st.button("Start New Round"):
        # Reset everything
        st.session_state.stage = 'initial'
        st.session_state.round_data = {}
        st.session_state.current_hole = 1
        st.session_state.hole_data = {}
        st.session_state.shot_number = 1
        st.session_state.on_green = False
        st.session_state.all_holes = []
        st.rerun()
