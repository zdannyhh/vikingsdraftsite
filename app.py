import streamlit as st  
import pandas as pd
import numpy as np
import plotly.graph_objects as go

def clear_search():
    st.session_state.search_player = ""

trait_df = pd.read_csv("traits.csv")

base_df = pd.read_csv("prospects.csv")
base_df.columns = base_df.columns.str.strip()
base_df = base_df.rename(columns={"College": "School"})

player_list = sorted(base_df["Player"].dropna().unique())

st.set_page_config(page_title="Vikings Draft Hub", layout="wide")

with st.sidebar:
    # Add a high-res Vikings Logo
    st.image("https://a.espncdn.com/i/teamlogos/nfl/500/min.png", width=80)
    st.header("Draft Capital")
    
    # Using columns for a compact, clean 'Dashboard' look
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Round 1", "Pick 18")
        st.metric("Round 3", "Pick 82")
    with c2:
        st.metric("Round 2", "Pick 49")
        st.metric("Round 3", "Pick 97")



st.markdown("""
<style>
/* Hide radio button circles */
div[role="radiogroup"] label > div:first-child {
    display: none;
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# SESSION STATE (FIXED)
# -------------------------
if "search_player_widget" not in st.session_state:
    st.session_state.search_player_widget = ""

# NEW: This checks if we need to clear the search bar BEFORE it renders
if st.session_state.get("needs_reset"):
    st.session_state.search_player_widget = ""
    st.session_state.needs_reset = False # Reset the flag

# --- STEP 1: Define the cleanup function at the top (under your imports) ---
def clear_popups():
    """Wipes all active players so popups don't follow you to other pages"""
    if "active_search_player" in st.session_state:
        del st.session_state.active_search_player
    if "selected_player" in st.session_state:
        del st.session_state.selected_player

# --- STEP 2: Replace your OLD sidebar block with this NEW one ---
with st.sidebar:
    st.markdown("## Navigation")

    # This is the ONLY place 'sidebar_nav' should appear in your code
    section = st.radio(
        "Go to:",
        ["Home", "Depth Chart", "Draft Capital", "Community", "Why"],
        key="sidebar_nav", 
        on_change=clear_popups # This kills the sticky popups
    )

st.session_state.section = section

@st.dialog("Player Fit Profile")
def show_search_player_dialog(player_name, df):
    search_name = player_name.strip()
    # Search in trait_df
    result = trait_df[trait_df["Player"].str.strip() == search_name]
    
    if not result.empty:
        player = result.iloc[0]
        
        # --- TOP ROW: HEADER (Left) and CLOSE BUTTON (Right) ---
        head_col, btn_col = st.columns([3, 1])
        
        with head_col:
            st.subheader(f"{player['Player']} | {player['Position']}")
        
        with btn_col:
            # Small button aligned to the right
            if st.button("✖ Close", key="top_close_btn"):
                if "active_search_player" in st.session_state:
                    del st.session_state.active_search_player
                st.rerun()

        # --- DATA EXTRACTION ---
        t1, v1 = player["Trait1"], pd.to_numeric(player["Val1"], errors='coerce') or 0
        t2, v2 = player["Trait2"], pd.to_numeric(player["Val2"], errors='coerce') or 0
        t3, v3 = player["Trait3"], pd.to_numeric(player["Val3"], errors='coerce') or 0
        t4, v4 = player["Trait4"], pd.to_numeric(player["Val4"], errors='coerce') or 0
        t5, v5 = player["Trait5"], pd.to_numeric(player["Val5"], errors='coerce') or 0
        
        # --- SCHEME FIT ---
        vikings_fit = round((v1 + v2 + v3 + v4 + v5) / 5, 1)

        # Row 1 Metrics
        m1, m2, m3 = st.columns(3)
        m1.metric("Vikings Fit", f"{vikings_fit}")
        m2.metric(str(t1), f"{int(v1)}")
        m3.metric(str(t2), f"{int(v2)}")
        
        # Row 2 Metrics
        m4, m5, m6 = st.columns(3)
        m4.metric(str(t3), f"{int(v3)}")
        m5.metric(str(t4), f"{int(v4)}")
        m6.metric(str(t5), f"{int(v5)}")

        # --- RADAR CHART ---
        categories = ['Vikings Fit', t1, t2, t3, t4, t5]
        values = [vikings_fit, v1, v2, v3, v4, v5]
        
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=values + [values[0]],
            theta=categories + [categories[0]],
            fill='toself',
            fillcolor='rgba(79, 38, 131, 0.5)', 
            line=dict(color='#FFC62F', width=2), 
            marker=dict(color='#FFC62F', size=7) 
        ))
        
        fig.update_layout(
            polar=dict(
                bgcolor="rgba(10, 10, 10, 0.8)", 
                radialaxis=dict(visible=True, range=[70, 100], color="gray"),
                angularaxis=dict(color="#FFC62F", rotation=90)
            ),
            showlegend=False,
            height=400,
            margin=dict(l=60, r=60, t=20, b=20), # Tightened margins
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        
        st.plotly_chart(fig, use_container_width=True)
            
    else:
        # Error handling also with a top-right close button
        head_col, btn_col = st.columns([3, 1])
        head_col.error(f"Missing data: '{player_name}'")
        if btn_col.button("✖ Close", key="err_close"):
            del st.session_state.active_search_player
            st.rerun()
# =========================================================
# HEADER & SEARCH LOGIC
# =========================================================
def handle_search():
    """This runs the second you pick a player in the search bar"""
    if st.session_state.search_player_widget != "":
        # Store the choice
        st.session_state.active_search_player = st.session_state.search_player_widget
        # IMMEDIATELY wipe the search bar widget so it doesn't re-trigger
        st.session_state.search_player_widget = ""
    else:
        # If the widget is empty, ensure the active search is also empty
        st.session_state.active_search_player = ""

header_left, header_search = st.columns([5, 4])

with header_left:
    st.markdown(
        "<h1 style='font-size:42px; font-weight:800;'>Minnesota Vikings Draft Hub</h1>",
        unsafe_allow_html=True
    )

with header_search:
    # THE MUTE SWITCH: If we are in Comparison, we show a 'Disabled' version of the bar
    # so it can't trigger any popups or hold any memory.
    if section == "Player Comparison":
        st.selectbox(
            "",
            options=["Search Disabled in Comparison"],
            index=0,
            disabled=True,
            key="search_disabled"
        )
    else:
        # This is your normal search bar, only active on other pages
        st.selectbox(
            "",
            options=[""] + player_list,
            key="search_player_widget",
            on_change=handle_search,
            format_func=lambda x: "Search a Player for Vikings Fit Score" if x == "" else x,
        )

# --- THE TRIGGER ---
# This ONLY runs if we are NOT in the comparison tool. 
# This is the physical wall that stops the popup.
if section != "Player Comparison":
    active_val = st.session_state.get("active_search_player", "")
    if active_val:
        show_search_player_dialog(active_val, trait_df)
        st.session_state.active_search_player = ""
# =========================================================
# PAGE ROUTING
# =========================================================
if section == "Home":
    pass
elif section == "Depth Chart":
    st.subheader("Depth Chart")
elif section == "Community":
    st.subheader("Community")
elif section == "Why":
    st.subheader("Why")


# =========================================================
# TABS
# =========================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Draft Index",
    "Big Board",
    "Player Fits",
    "Draft Guide",
    "Player Comparison"
])
# ---------------- TAB 1 ----------------
with tab1:

    if st.session_state.section == "Home":
        st.title("Vikings Draft Analytics Lab")

        st.write("""
        Welcome to the **Vikings Draft Site**, a scouting and analytics platform built to evaluate how NFL draft prospects fit 
        with the Minnesota Vikings' system.
        """)

        st.subheader("Vikings Draft Guide")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Prospects Tracked", 150)
            st.write("Custom scouting database with positional traits and analytics.")

        with col2:
            st.metric("KOC & Flo Fit Models", 3)
            st.write("Scheme-based scoring for offense and defense.")

        with col3:
            st.metric("Draft Tools", 5)
            st.write("Big board, comparisons, simulators, and filters.")

        st.subheader("Scouting Process")

        st.write("""
        Instead of ranking players only by hype, this site focuses on **scheme fit**, **versatility**, and **impact traits**.

        Each prospect has a **custom fit score** based on how well they fit the Vikings system.
        """)

        st.subheader("Explore")

        st.write("""
        Use the tabs above to:
        - View the **Vikings Big Board**
        - Customize the **Fit Model**
        - Compare prospects
        - Simulate draft strategies
        """)

    # -------- DEPTH CHART --------
    elif st.session_state.section == "Depth Chart":
        st.header("Minnesota Vikings Depth Chart")

        depth_data = [
            ["QB","Kyler Murray","J.J. McCarthy","Carson Wentz","Max Brosmer"],
            ["RB","Aaron Jones","Jordan Mason","Zavier Scott",""],
            ["WR","Justin Jefferson","Jeshaun Jones","",""],
            ["WR","Jordan Addison","Myles Price","",""],
            ["WR","Tai Felton","","",""],
            ["TE","T.J. Hockenson","Josh Oliver","Ben Yurosek","Gavin Bartholomew"],
            ["LT","Christian Darrisaw","Ryan Van Demark","",""],
            ["LG","Donovan Jackson","Joe Huber","",""],
            ["C","Blake Brandel","Michael Jurgens","",""],
            ["RG","Will Fries","Henry Byrd","",""],
            ["RT","Brian O'Neill","Walter Rouse","",""],
            ["DT","Jalen Redmond","Tyrion Ingram-Dawkins","Elijah Williams",""],
            ["DT","Levi Drake Rodriguez","Taki Taimani","Jaylon Hutchings",""],
            ["EDGE","Jonathan Greenard","Dallas Turner","Chaz Chambliss"],
            ["EDGE","Andrew Van Ginkel","Bo Richter","Tyler Batty",""],
            ["LB","Blake Cashman","Ivan Pace Jr.","",""],
            ["LB","Eric Wilson","","",""],
            ["CB","Isaiah Rodgers","Dwight McGlothern","",""],
            ["CB","James Pierre","Zemaiah Vaughn","",""],
            ["CB","Byron Murphy Jr","Tavierre Thomas","",""],
            ["SAF","Theo Jackson","Jay Ward",""],
            ["SAF","Josh Metellus","Kahlef Hailassie","",""]
        ]

        depth_df = pd.DataFrame(depth_data)
        depth_df.columns = ["Position","","","",""]

        position_strength = {
            "QB": 8, "RB": 6, "WR": 10, "TE": 8,
            "LT": 9, "LG": 6, "C": 5, "RG": 5, "RT": 9,
            "DT": 3, "EDGE": 7, "LB": 7, "CB": 4, "SAF": 3
        }

        def color_position(pos):
            score = position_strength.get(pos, 5)
            if score <= 4:
                return f"<span style='color:red; font-weight:bold'>{pos}</span>"
            elif score <= 6:
                return f"<span style='color:orange; font-weight:bold'>{pos}</span>"
            else:
                return f"<span style='color:green; font-weight:bold'>{pos}</span>"

        depth_df["Position"] = depth_df["Position"].apply(color_position)

        left, right = st.columns([3,2])

        with left:
            st.markdown(
                depth_df.to_html(escape=False, index=False),
                unsafe_allow_html=True
            )

        with right:
            st.subheader("Draft Targets")

            if "selected_position" not in st.session_state:
                st.session_state.selected_position = None

            row1 = st.columns(4)
            row2 = st.columns(4)
            row3 = st.columns(4)

            positions_layout = [
                ["QB","RB","WR","TE"],
                ["OT","OG","OC","EDGE"],
                ["DT","LB","CB","SAF"]
            ]

            rows = [row1, row2, row3]

            for r_idx, row in enumerate(rows):
                for c_idx, col in enumerate(row):
                    pos = positions_layout[r_idx][c_idx]
                    with col:
                        if st.button(pos):
                            st.session_state.selected_position = pos

            st.markdown("---")

            pos = st.session_state.selected_position

            if pos is None:
                st.write("Select a position")
            else:
                st.write(f"Top 5 Prospects at {pos}")

                if pos == "OT":
                    filtered = base_df[base_df["Position"].isin(["LT","RT"])]
                elif pos == "OG":
                    filtered = base_df[base_df["Position"].isin(["LG","RG"])]
                elif pos == "OC":
                    filtered = base_df[base_df["Position"] == "C"]
                else:
                    filtered = base_df[base_df["Position"] == pos]

                if "Rating" in filtered.columns:
                    filtered = filtered.sort_values("Rating", ascending=False)

                top5 = filtered.head(5)

                for _, row in top5.iterrows():
                    st.write(f"- {row['Player']}")

    # -------- NEW: DRAFT CAPITAL --------
    elif st.session_state.section == "Draft Capital":
        st.header("Minnesota Vikings 2026 Draft Capital")
        
        st.write("Overview of all 9 selections for the upcoming draft cycle.")

        # Create a clean data table for the picks
        draft_picks = [
            {"Round": 1, "Pick": 18, "Selection": "1st Round Pick", "Source": "Original"},
            {"Round": 2, "Pick": 49, "Selection": "2nd Round Pick", "Source": "Original"},
            {"Round": 3, "Pick": 82, "Selection": "3rd Round Pick", "Source": "Original"},
            {"Round": 3, "Pick": 97, "Selection": "3rd Round Pick", "Source": "Compensatory"},
            {"Round": 5, "Pick": 163, "Selection": "5th Round Pick", "Source": "via Eagles"},
            {"Round": 6, "Pick": 196, "Selection": "6th Round Pick", "Source": "via Colts"},
            {"Round": 7, "Pick": 234, "Selection": "7th Round Pick", "Source": "Original"},
            {"Round": 7, "Pick": 235, "Selection": "7th Round Pick", "Source": "via Panthers"},
            {"Round": 7, "Pick": 244, "Selection": "7th Round Pick", "Source": "via Texans"},
        ]
        
        picks_df = pd.DataFrame(draft_picks)
        
        st.dataframe(
            picks_df, 
            hide_index=True, 
            use_container_width=True
        )

        st.info("💡 The Vikings currently hold 4 picks in the top 100, providing significant flexibility for trade-ups or filling key starter roles.")

    # -------- COMMUNITY --------
    elif st.session_state.section == "Community":

        st.header("Community")

        poll = st.radio(
            "What should the Vikings prioritize?",
            ["Defensive Line", "Secondary", "Offensive Line", "Best Player Available"]
        )

        if st.button("Submit Vote"):
            st.success(f"You voted for: {poll}")

        comment = st.text_input("Leave a comment")

        if st.button("Post"):
            st.write(f"User: {comment}")

    # -------- WHY --------
    elif st.session_state.section == "Why":

        st.header("Why This Model Works")

        st.write("""
        This project simulates real NFL front office decision-making.

        The model combines:
        - Vikings Fit
        - Team Needs
        - Big Board ranking
        """)
    # ---------------- TAB 2 ----------------
with tab2:

    st.header("Big Board")

    df = base_df.copy()

    # -------------------------
    # FIX NUMERIC COLUMNS
    # -------------------------
    df["Rank"] = pd.to_numeric(df["Rank"], errors="coerce")
    df["Grade"] = pd.to_numeric(df["Grade"], errors="coerce")
    df["Athleticism"] = pd.to_numeric(df["Athleticism"], errors="coerce")
    df["Production"] = pd.to_numeric(df["Production"], errors="coerce")
    df["Weight"] = pd.to_numeric(df["Weight"], errors="coerce")

    # -------------------------
    # FIX HEIGHT CONVERSION
    # -------------------------
    def convert_height(height_val):
        if pd.isna(height_val):
            return ""
        height_str = str(height_val).strip()

        if "'" in height_str:
            return height_str

        month_map = {
            "Jan":1,"Feb":2,"Mar":3,"Apr":4,
            "May":5,"Jun":6,"Jul":7,"Aug":8,
            "Sep":9,"Oct":10,"Nov":11,"Dec":12
        }

        try:
            if "-" in height_str:
                part1, part2 = height_str.split("-")
                feet = month_map.get(part1, part1)
                feet = int(feet)
                inches = int(part2)
                return f"{feet}'{inches}\""
        except:
            return height_str

        return height_str

    df["Height"] = df["Height"].apply(convert_height)

    # -------------------------
    # SORT BY YOUR ORIGINAL RANK
    # -------------------------
    df = df.sort_values("Rank")

    # -------------------------
    # FILTER LAYOUT (YOUR ORIGINAL STYLE)
    # -------------------------
    col1, col2, col3 = st.columns(3)

    with col1:
        pos_filter = st.multiselect(
            "Filter by Position",
            options=sorted(df["Position"].dropna().unique()),
            default=[]
        )

   # -------------------------
    # DYNAMIC FILTER (SMART RANGE)
    # -------------------------
    # 1. Get the actual min and max from your data (e.g., 77 and 95)
    # We use floor/ceil so the slider has clean whole numbers
    min_grade = float(df["Grade"].min())
    max_grade = float(df["Grade"].max())

    with col2:
        grade_slider = st.slider(
            "Minimum Grade",
            min_value=min_grade, 
            max_value=max_grade,
            # Set the default starting point to the lowest player so everyone shows up
            value=min_grade, 
            step=0.5 # Smaller steps make it feel more precise
        )

    with col3:
        search = st.text_input("Search Player")

    # -------------------------
    # APPLY FILTERS
    # -------------------------
    filtered_df = df.copy()

    if pos_filter:
        filtered_df = filtered_df[
            filtered_df["Position"].isin(pos_filter)
        ]

    filtered_df = filtered_df[
        filtered_df["Grade"] >= grade_slider
    ]

    if search:
        filtered_df = filtered_df[
            filtered_df["Player"].str.contains(search, case=False, na=False)
        ]

    # -------------------------
    # DISPLAY TABLE
    # -------------------------
    st.dataframe(
        filtered_df[
            [
                "Rank", "Player", "Position", "School",
                "Height", "Weight", "Athleticism",
                "Production", "Grade"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

    st.caption(f"Showing {len(filtered_df)} players")
    
# ---------------- TAB 3 ----------------
with tab3:

    st.header("Minnesota Vikings Scheme Fits")

    offense_df = pd.read_csv("kocreal.csv")
    defense_df = pd.read_csv("flores.csv")

    off_tab, def_tab = st.tabs(["KOC Offense", "Flores Defense"])

    # ---------------- OFFENSE ---------------- #

    with off_tab:

        st.subheader("Kevin O'Connell Offensive Scheme Fits")

        st.write(
        "O'Connell's offense values athleticism, explosiveness, intelligence, and versatility."
        )

        offense_df["Scheme_Fit"] = (
            offense_df["Athleticism"] * 0.25 +
            offense_df["Explosiveness"] * 0.25 +
            offense_df["Skill"] * 0.25 +
            offense_df["IQ"] * 0.15 +
            offense_df["Versatility"] * 0.10
        )

        offense_df = offense_df.sort_values("Scheme_Fit", ascending=False)

        offense_df = offense_df.reset_index(drop=True)
        offense_df.index = offense_df.index + 1

        board = st.dataframe(
            (offense_df[["Player","Position","School","Scheme_Fit"]]
            .rename(columns={"Scheme_Fit":"Scheme Fit"})),
            use_container_width=True,
            on_select="rerun",
            selection_mode="single-row"
        )

        if board.selection.rows:
            if "active_search_player" in st.session_state:
                del st.session_state.active_search_player

            row_index = board.selection.rows[0]
            player_data = offense_df.iloc[row_index]

            @st.dialog(player_data["Player"])
            def offense_player_profile():

                position = player_data["Position"]

                st.markdown(f"### {player_data['Player']} — {position}")

                traits = {
                    "Athleticism": player_data["Athleticism"],
                    "Explosiveness": player_data["Explosiveness"],
                    "Skill": player_data["Skill"],
                    "IQ": player_data["IQ"],
                    "Versatility": player_data["Versatility"]
                }

                cols = st.columns(len(traits))

                for col,(trait,value) in zip(cols,traits.items()):
                    col.metric(trait,f"{value}")

                labels = list(traits.keys())
                values = list(traits.values())

                max_val = max(values)
                values = [(v/max_val)*100 for v in values]

                labels.append(labels[0])
                values.append(values[0])

                # --- RADAR CHART (ZOOMED & VIKINGS STYLED) ---
                fig = go.Figure()

                fig.add_trace(go.Scatterpolar(
                    r=values,
                    theta=labels,
                    fill='toself',
                    # Vikings Purple (50% opacity)
                    fillcolor='rgba(79, 38, 131, 0.5)', 
                    # Vikings Gold Border
                    line=dict(color='#FFC62F', width=2),
                    # Gold dots at each trait point
                    marker=dict(color='#FFC62F', size=7)
                ))

                fig.update_layout(
                    polar=dict(
                        # Dark aesthetic background
                        bgcolor="rgba(10, 10, 10, 0.8)",
                        radialaxis=dict(
                            visible=True, 
                            # THE NUMBER FIX: Zoomed range for elite prospects
                            range=[70, 100], 
                            color="gray",
                            tickvals=[70, 75, 80, 85, 90, 95, 100],
                            gridcolor="rgba(255, 255, 255, 0.1)"
                        ),
                        angularaxis=dict(
                            color="#FFC62F", # Gold trait labels
                            rotation=90,
                            direction="clockwise"
                        )
                    ),
                    showlegend=False,
                    height=400,
                    margin=dict(l=60, r=60, t=60, b=60),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)"
                )

                st.plotly_chart(fig, use_container_width=True)

            offense_player_profile()


    # ---------------- DEFENSE ---------------- #

    with def_tab:

        st.subheader("Brian Flores Defensive Scheme Fits")

        st.write(
        "Flores' defense emphasizes versatility, pressure ability, football IQ, and tackling."
        )

        def calculate_flores_fit(row):

            if row["Position"] in ["CB","SAF"]:

                score = (
                    row["Versatility"] * 0.25 +
                    row["Run Defense"] * 0.15 +
                    row["Football IQ"] * 0.25 +
                    row["Zone Cov."] * 0.25 +
                    row["Man Cov."] * 0.10
                )

            else:

                score = (
                    row["Versatility"] * 0.35 +
                    row["Pressure Ability"] * 0.20 +
                    row["Run Defense"] * 0.20 +
                    row["Football IQ"] * 0.25
                )

            return round(score,2)

        defense_df["Scheme_Fit"] = defense_df.apply(calculate_flores_fit,axis=1)

        defense_df = defense_df.sort_values("Scheme_Fit",ascending=False)

        defense_df = defense_df.reset_index(drop=True)
        defense_df.index = defense_df.index + 1

        board = st.dataframe(
            (defense_df[["Player","Position","School","Scheme_Fit"]]
            .rename(columns={"Scheme_Fit":"Scheme Fit"})),
            use_container_width=True,
            on_select="rerun",
            selection_mode="single-row"
        )

        if board.selection.rows:
            if "active_search_player" in st.session_state:
                del st.session_state.active_search_player

            row_index = board.selection.rows[0]
            player_data = defense_df.iloc[row_index]

            @st.dialog(player_data["Player"])
            def defense_player_profile():

                position = player_data["Position"]

                st.markdown(f"### {player_data['Player']} — {position}")

                if position in ["CB","SAF"]:

                    traits = {
                        "Versatility": player_data["Versatility"],
                        "Run Defense": player_data["Run Defense"],
                        "Football IQ": player_data["Football IQ"],
                        "Zone Cov.": player_data["Zone Cov."],
                        "Man Cov.": player_data["Man Cov."]
                    }

                else:

                    traits = {
                        "Versatility": player_data["Versatility"],
                        "Pressure Ability": player_data["Pressure Ability"],
                        "Run Defense": player_data["Run Defense"],
                        "Football IQ": player_data["Football IQ"]
                    }

                cols = st.columns(len(traits))

                for col,(trait,value) in zip(cols,traits.items()):
                    col.metric(trait,f"{value}")

                labels = list(traits.keys())
                values = list(traits.values())

                max_val = max(values)
                values = [(v/max_val)*100 for v in values]

                labels.append(labels[0])
                values.append(values[0])

                # --- RADAR CHART (ZOOMED & VIKINGS STYLED) ---
                fig = go.Figure()

                fig.add_trace(go.Scatterpolar(
                    r=values,
                    theta=labels,
                    fill='toself',
                    # Vikings Purple (50% opacity)
                    fillcolor='rgba(79, 38, 131, 0.5)', 
                    # Vikings Gold Border
                    line=dict(color='#FFC62F', width=2),
                    # Gold dots at each trait point
                    marker=dict(color='#FFC62F', size=7)
                ))

                fig.update_layout(
                    polar=dict(
                        # Dark aesthetic background
                        bgcolor="rgba(10, 10, 10, 0.8)",
                        radialaxis=dict(
                            visible=True, 
                            # THE NUMBER FIX: Zoomed range for elite prospects
                            range=[70, 100], 
                            color="gray",
                            tickvals=[70, 75, 80, 85, 90, 95, 100],
                            gridcolor="rgba(255, 255, 255, 0.1)"
                        ),
                        angularaxis=dict(
                            color="#FFC62F", # Gold trait labels
                            rotation=90,
                            direction="clockwise"
                        )
                    ),
                    showlegend=False,
                    height=400,
                    margin=dict(l=60, r=60, t=60, b=60),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)"
                )

                st.plotly_chart(fig, use_container_width=True)

            defense_player_profile()


with tab4:
    
    st.header("Vikings Draft Strategy Guide")

    offense_df = pd.read_csv("kocreal.csv")
    defense_df = pd.read_csv("flores.csv")

    # -------------------------
    # COLLEGE LOGOS
    # -------------------------

    college_logos = {
        "Oregon": "https://a.espncdn.com/i/teamlogos/ncaa/500/2483.png",
        "Clemson": "https://a.espncdn.com/i/teamlogos/ncaa/500/228.png",
        "Toledo": "https://a.espncdn.com/i/teamlogos/ncaa/500/2649.png",
        "Arizona State": "https://a.espncdn.com/i/teamlogos/ncaa/500/9.png",
        "Notre Dame": "https://a.espncdn.com/i/teamlogos/ncaa/500/87.png",
        "Oklahoma": "https://a.espncdn.com/i/teamlogos/ncaa/500/201.png",
        "Texas Tech": "https://a.espncdn.com/i/teamlogos/ncaa/500/2641.png",
        "San Diego State": "https://a.espncdn.com/i/teamlogos/ncaa/500/21.png",
        "Auburn": "https://a.espncdn.com/i/teamlogos/ncaa/500/2.png",
        "USC": "https://a.espncdn.com/i/teamlogos/ncaa/500/30.png",
        "Iowa": "https://a.espncdn.com/i/teamlogos/ncaa/500/2294.png",
        "North Dakota State": "https://a.espncdn.com/i/teamlogos/ncaa/500/2449.png",
        "Florida": "https://a.espncdn.com/i/teamlogos/ncaa/500/57.png",
        "Georgia": "https://a.espncdn.com/i/teamlogos/ncaa/500/61.png",
        "Georgia State": "https://a.espncdn.com/i/teamlogos/ncaa/500/2247.png",
        "Arizona": "https://a.espncdn.com/i/teamlogos/ncaa/500/12.png",
        "Tennessee": "https://a.espncdn.com/i/teamlogos/ncaa/500/2633.png",
        "Arkansas": "https://a.espncdn.com/i/teamlogos/ncaa/500/8.png",
        "Michigan": "https://a.espncdn.com/i/teamlogos/ncaa/500/130.png",
        "TCU": "https://a.espncdn.com/i/teamlogos/ncaa/500/2628.png",
        "Kansas State": "https://a.espncdn.com/i/teamlogos/ncaa/500/2306.png"
        
    }

    # -------------------------
    # TEAM NEED GRID
    # -------------------------

    st.subheader("Team Needs")

    team_needs = {
        "DT":9,"OC":9,"SAF":8,"RB":8,"WR":7,"CB":7,
        "OT":6,"TE":6,"EDGE":4,"LB":3,"OG":3,"QB":2
    }

    def need_color(score):
        if score >= 8:
            return "#ff4d4d"
        elif score >= 5:
            return "#ffd24d"
        else:
            return "#66cc66"

    positions = sorted(team_needs, key=lambda x: team_needs[x], reverse=True)

    row1 = st.columns(6)
    row2 = st.columns(6)

    for i, pos in enumerate(positions[:6]):
        row1[i].markdown(
            f"""<div style="background:{need_color(team_needs[pos])};
            padding:8px;text-align:center;border-radius:8px;
            font-weight:bold;font-size:13px;">{pos}</div>""",
            unsafe_allow_html=True
        )

    for i, pos in enumerate(positions[6:]):
        row2[i].markdown(
            f"""<div style="background:{need_color(team_needs[pos])};
            padding:8px;text-align:center;border-radius:8px;
            font-weight:bold;font-size:13px;">{pos}</div>""",
            unsafe_allow_html=True
        )

    # -------------------------
    # SCHEME FIT
    # -------------------------

    offense_df["Scheme_Fit"] = (
        offense_df["Athleticism"]*0.25 +
        offense_df["Explosiveness"]*0.25 +
        offense_df["Skill"]*0.25 +
        offense_df["IQ"]*0.15 +
        offense_df["Versatility"]*0.10
    )

    def flores_fit(row):
        if row["Position"] in ["CB","SAF"]:
            return (
                row["Versatility"]*0.25 +
                row["Run Defense"]*0.15 +
                row["Football IQ"]*0.25 +
                row["Zone Cov."]*0.25 +
                row["Man Cov."]*0.10
            )
        else:
            return (
                row["Versatility"]*0.35 +
                row["Pressure Ability"]*0.20 +
                row["Run Defense"]*0.20 +
                row["Football IQ"]*0.25
            )

    defense_df["Scheme_Fit"] = defense_df.apply(flores_fit, axis=1)

    prospects = pd.concat([offense_df, defense_df], ignore_index=True)

    prospects["Need_Score"] = prospects["Position"].map(team_needs).fillna(3)

    # -------------------------
    # RECOMMENDED PLAYERS
    # -------------------------

    recommended_players = {
        18: ["Dillon Thieneman", "Avieon Terrell", "Emmanuel McNeil-Warren", "Jermod McCoy", "Jordyn Tyson"],
        49: ["Jadarian Price", "Gracen Halton", "Lee Hunter", "Christen Miller", "Treydan Stukes"],
        82: ["Connor Lew", "Ja'Kobi Lane", "Bryce Lance", "Sam Hecht", "Mike Washington Jr."],
        97: ["Logan Jones", "Ted Hurst", "Jake Slaughter", "Jaishawn Barham", "Bud Clark"]
    }

# -------------------------
    # PICK BUTTONS (FIXED TO CLEAR POPUPS)
    # -------------------------

    if "selected_pick" not in st.session_state:
        st.session_state.selected_pick = 18

    pick_cols = st.columns(4)

    # When these buttons are clicked, we also need to clear any old popup selection
    if pick_cols[0].button("18"): 
        st.session_state.selected_pick = 18
        if "selected_player" in st.session_state: del st.session_state["selected_player"]

    if pick_cols[1].button("49"): 
        st.session_state.selected_pick = 49
        if "selected_player" in st.session_state: del st.session_state["selected_player"]

    if pick_cols[2].button("82"): 
        st.session_state.selected_pick = 82
        if "selected_player" in st.session_state: del st.session_state["selected_player"]

    if pick_cols[3].button("97"): 
        st.session_state.selected_pick = 97
        if "selected_player" in st.session_state: del st.session_state["selected_player"]

    selected_pick = st.session_state.selected_pick

    st.subheader(f"Recommended Players at Pick {selected_pick}")

    # -------------------------
    # PLAYER DISPLAY (WITH LOGOS)
    # -------------------------

    cols = st.columns(5)

    for col, player_name in zip(cols, recommended_players[selected_pick]):

        player_row = prospects[prospects["Player"] == player_name]

        if player_row.empty:
            col.warning("Missing Data")
            continue

        player_row = player_row.iloc[0]

        logo = college_logos.get(player_row["School"], None)

        inner = col.columns([1,3])

        if logo:
            inner[0].image(logo, width=40)

        inner[1].markdown(f"""
        **{player_row['Player']}** {player_row['Position']} | {player_row['School']}
        """)

        col.markdown(f"""
        Scheme Fit: {round(player_row['Scheme_Fit'],1)}  
        Team Need: {player_row['Need_Score']}
        """)

        # Profile button with unique key
        if col.button("Profile", key=f"{player_name}_{selected_pick}"):
            if "active_search_player" in st.session_state:
                del st.session_state.active_search_player
        
            st.session_state["selected_player"] = player_name
            st.rerun()
    # -------------------------
    # POPUP PROFILE (FIXED FOR NaN)
    # -------------------------

    if "selected_player" in st.session_state:

        player_name = st.session_state["selected_player"]
        player_row = prospects[prospects["Player"] == player_name].iloc[0]

        @st.dialog(player_name)
        def show_profile():

            st.markdown(f"### {player_row['Player']} — {player_row['Position']}")

            # 1. CHECK IF DEFENSIVE BACK
            if player_row["Position"] in ["CB","SAF"]:
                traits = {
                    "Versatility": player_row.get("Versatility", 0),
                    "Run Defense": player_row.get("Run Defense", 0),
                    "Football IQ": player_row.get("Football IQ", 0),
                    "Zone Cov.": player_row.get("Zone Cov.", 0),
                    "Man Cov.": player_row.get("Man Cov.", 0)
                }
            
        
            elif player_row["Position"] in ["WR", "OC", "RB", "OT", "OG", "QB", "TE"]:
                traits = {
                    "Athleticism": player_row.get("Athleticism", 0),
                    "Explosiveness": player_row.get("Explosiveness", 0),
                    "Skill": player_row.get("Skill", 0),
                    "IQ": player_row.get("IQ", 0),
                    "Versatility": player_row.get("Versatility", 0)
                }

            # 3. DEFAULT FOR OTHER DEFENSIVE POSITIONS (DL, LB, EDGE)
            else:
                traits = {
                    "Versatility": player_row.get("Versatility", 0),
                    "Pressure Ability": player_row.get("Pressure Ability", 0),
                    "Run Defense": player_row.get("Run Defense", 0),
                    "Football IQ": player_row.get("Football IQ", 0)
                }

            # Clean up any remaining NaNs to 0 so the chart doesn't break
            traits = {t: (0 if pd.isna(v) else v) for t, v in traits.items()}

            cols_traits = st.columns(len(traits))
            for c,(t,v) in zip(cols_traits,traits.items()):
                c.metric(t,v)

            labels = list(traits.keys())
            values = list(traits.values())

            labels.append(labels[0])
            values.append(values[0])

            fig = go.Figure()

            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=labels,
                fill='toself',
                fillcolor='rgba(79, 38, 131, 0.5)', 
                line=dict(color='#FFC62F', width=2),
                marker=dict(color='#FFC62F', size=7)
            ))

            fig.update_layout(
                polar=dict(
                    bgcolor="rgba(10, 10, 10, 0.8)",
                    radialaxis=dict(
                        visible=True, 
                        range=[70, 100], 
                        color="gray",
                        tickvals=[70, 75, 80, 85, 90, 95, 100]
                    ),
                    angularaxis=dict(color="#FFC62F", rotation=90)
                ),
                showlegend=False,
                height=400
            )

            st.plotly_chart(fig, use_container_width=True)


            if st.button("Close"):
                del st.session_state["selected_player"]
                st.rerun()

        show_profile()

with tab5:
    st.header("Player Comparison")
    st.markdown("Compare two prospects side-by-side based on their scouting traits.")

    comp_df = trait_df.copy() 
    player_list = sorted(comp_df["Player"].unique().tolist())

    is_popup_open = "selected_player" in st.session_state
    if is_popup_open:
        st.warning("⚠️ Profile Popup is active. Close it to enable comparison.")
    
    c1, c2 = st.columns(2)
    with c1:
        p1_name = st.selectbox("Search Player 1", [""] + player_list, key="comp_1", disabled=is_popup_open)
    with c2:
        p2_name = st.selectbox("Search Player 2", [""] + player_list, key="comp_2", disabled=is_popup_open)

    if p1_name and p2_name:
        p1_data = comp_df[comp_df["Player"] == p1_name].iloc[0]
        p2_data = comp_df[comp_df["Player"] == p2_name].iloc[0]

        st.markdown("---")

        col_left, col_right = st.columns(2)

        with col_left:
            st.subheader(p1_name)
            st.caption(f"{p1_data.get('Position', 'N/A')} | {p1_data.get('School', 'N/A')}")
            st.write("") # Spacer
            
            for i in range(1, 6):
                t_name = str(p1_data[f"Trait{i}"])
                val = int(pd.to_numeric(p1_data[f"Val{i}"]) or 0)
                st.metric(label=t_name, value=val)

        with col_right:
            st.subheader(p2_name)
            st.caption(f"{p2_data.get('Position', 'N/A')} | {p2_data.get('School', 'N/A')}")
            st.write("") 

            for i in range(1, 6):
                t_name = str(p2_data[f"Trait{i}"])
                val = int(pd.to_numeric(p2_data[f"Val{i}"]) or 0)
                st.metric(label=t_name, value=val)

        st.markdown("### Visual Overlap")
        
        p1_labels = [p1_data[f"Trait{i}"] for i in range(1, 6)]
        p1_vals = [pd.to_numeric(p1_data[f"Val{i}"]) or 0 for i in range(1, 6)]
        
        p2_labels = [p2_data[f"Trait{i}"] for i in range(1, 6)]
        p2_vals = [pd.to_numeric(p2_data[f"Val{i}"]) or 0 for i in range(1, 6)]

        fig_comp = go.Figure()

       
        fig_comp.add_trace(go.Scatterpolar(
            r=p1_vals + [p1_vals[0]],
            theta=p1_labels + [p1_labels[0]],
            fill='toself',
            fillcolor='rgba(79, 38, 131, 0.4)',
            line=dict(color='#FFC62F', width=2),
            name=p1_name
        ))

        fig_comp.add_trace(go.Scatterpolar(
            r=p2_vals + [p2_vals[0]],
            theta=p2_labels + [p2_labels[0]],
            fill='toself',
            fillcolor='rgba(255, 255, 255, 0.2)',
            line=dict(color='#FFFFFF', width=2),
            name=p2_name
        ))

        fig_comp.update_layout(
            polar=dict(
                bgcolor="rgba(20, 20, 20, 0.9)",
                radialaxis=dict(visible=True, range=[70, 100], color="gray"),
                angularaxis=dict(color="#FFC62F")
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=500,
            showlegend=True
        )

        st.plotly_chart(fig_comp, use_container_width=True)
    else:
        st.info("Select two players above to see the comparison metrics and chart.")
# =========================================================
# FINAL TRIGGER (PLACE AT THE VERY END OF YOUR SCRIPT)
# =========================================================
if "active_search_player" in st.session_state:
    
    if "selected_player" in st.session_state:
        del st.session_state.selected_player
    try:
        show_search_player_dialog(st.session_state.active_search_player, base_df)
    except:
        pass

elif "selected_player" in st.session_state:
    if section == "Home": 
        pass