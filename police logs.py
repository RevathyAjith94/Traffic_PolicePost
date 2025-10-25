import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px


# DATABASE CONNECTION
#-----------------------------
def create_connection():
  
  try:

        connection = mysql.connector.connect(
        host = "gateway01.ap-southeast-1.prod.aws.tidbcloud.com",
        port = 4000,
        user = "YmTYmWgYmbJyrz1.root",
        password = "vOWwxuhJosGHLoC1",
        database ="securecheck"
        
    )
        
#  CREATE CURSOR INSIDE CONNECTION
#------------------------------------
        mycursor = connection.cursor(buffered=True, dictionary =True)
        st.success("Database Connected Successfully ")

        return connection, mycursor

  except   Exception as e:
        st.error(f"Database Connection Error: {e}")
        return None,None
  
#----------------------------------


# FETCH DATA FROM DATABASE
#---------------------------------

def fetch_data(query):
     connection,cursor = create_connection()
     if connection:
        try:
            
                cursor.execute(query)
                result = cursor.fetchall()
                df = pd.DataFrame(result)
                return df
        except Exception as e:
            st.error(f"Query Error: {e}")
            return pd.DataFrame()
        finally:
            cursor.close()
            connection.close()
     else:
        return pd.DataFrame()
     
     # ---------------------------
# STREAMLIT UI
# ---------------------------
st.set_page_config(page_title="Securecheck Police Dashboard - Full", layout="wide")
st.title("🚓 SecureCheck Police Dashboard")
st.markdown("Medium + Complex Queries Dashboard for Law Enforcement")


# FETCH DATA FROM DB FIRST
#-----------------------------

query = "SELECT * FROM police_post"
data = fetch_data(query)

# KEY METRICS
#----------------------
st.header("🔑Key Metrics")
col1, col2, col3, col4 = st.columns(4)

total_stops = data.shape[0]
col1.metric("Total Stops", total_stops)

arrests = data[data['stop_outcome'].str.contains("arrest", case=False, na=False)].shape[0]
col2.metric("Total Arrests", arrests)

warnings = data[data['stop_outcome'].str.contains("warning", case=False, na=False)].shape[0]
col3.metric("Total Warnings", warnings)

drug_related = data[data['drugs_related_stop'] == 1].shape[0]
col4.metric("Drug Related Stops", drug_related)

# VISUALS INSIGHT
#-----------------------------
st.header("📊Visual Insights")
tab1, tab2 = st.tabs(["Stops by Violation", "Driver Gender Distribution"])

with tab1:
    if not data.empty and 'violation' in data.columns:
        violation_data = data['violation'].value_counts().reset_index()
        violation_data.columns = ['Violation', 'Count']
        fig = px.bar(violation_data, x='Violation', y='Count', color='Violation',
                     title="Stops by Violation Type")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⚠️No data available for violation chart.")

with tab2:
    if not data.empty and 'driver_gender' in data.columns:
        gender_data = data['driver_gender'].value_counts().reset_index()
        gender_data.columns = ['Gender', 'Count']
        fig = px.pie(gender_data, names='Gender', values='Count', title="Driver Gender Distribution")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⚠️No data available for Driver Gender chart.")


 # ADVANCED INSIGHT
# ---------------------------
st.header("🧩 Advanced Insights")

advanced_queries = [
    "Total Number of Police Stops",
    "Number of Arrests vs. Warnings",
    "Average Age of Drivers Stopped",
    "Top 5 Most Frequent Search Types",
    "Count of stops by Gender",
    "Most Common Violation for Arrests",
    "Top 10 Vehicles involved in Drug-Related Stops",
    "Most Frequently Searched Vehicles",
    "Driver Age Group with Highest Arrest Rate",
    "Gender Distribution by Country",
    "Race & Gender Combination with Highest Search Rate",
    "Time of Day with Most Stops",
    "Average Stop Duration by Violation",
    "Stops During Night vs Arrests",
    "Countries with Highest Drug-Related Stops",
    "Yearly Breakdown of Stops and Arrests by Country",
    "Driver Violation Trends by Age & Race",
    "Time Period Analysis of Stops",
    "Violations with High Search & Arrest Rates",
    "Driver Demographics by Country",
    "Top 5 Violations with Highest Arrest Rates"
]

selected_query = st.selectbox("Select an Advanced Query", advanced_queries)
st.info(f"Query placeholder selected: **{selected_query}**")
st.markdown("Results would appear here after running the actual SQL query.")
    


# ---------------------------
# QUERY MAP
# ---------------------------
query_map = {
    
    # Medium-Level Queries
 #------------------------------- 
 #  🚗 Vehicle-Based  

"Top 10 Vehicles (Drug-Related Stops)🛑": """
        SELECT vehicle_number, COUNT(*) AS count FROM police_post WHERE drugs_related_stop=1 GROUP BY vehicle_number ORDER BY count DESC LIMIT 10;
    """,

"Most Frequently Searched Vehicles": """
        SELECT vehicle_number, COUNT(*) AS count FROM police_post WHERE search_conducted=1 GROUP BY vehicle_number ORDER BY count DESC LIMIT 10;
    """,
 #🧍 Demographic-Based

 "Driver Age Group with Highest Arrest Rate": """
        SELECT driver_age, COUNT(*) AS arrests FROM police_post WHERE stop_outcome LIKE '%arrest%' GROUP BY driver_age ORDER BY arrests DESC LIMIT 10;
    """,

"Gender Distribution by Country": """
        SELECT country_name, driver_gender, COUNT(*) AS count FROM police_post GROUP BY country_name, driver_gender ORDER BY country_name;
    """,
 
 "Race & Gender Combination with Highest Search Rate":"""
        SELECT driver_race, driver_gender, COUNT(*) AS search_count FROM police_post WHERE search_conducted=1 GROUP BY driver_race, driver_gender ORDER BY search_count DESC;
    """,      
# 🕒 Time & Duration Based
"Most Common Violation Types":"""
      SELECT violation, COUNT(*) AS count FROM police_post GROUP BY violation ORDER BY count DESC LIMIT 10;""",

"Stops During Night vs Arrests":"""
     SELECT CASE WHEN HOUR(stop_time) BETWEEN 20 AND 5 THEN 'Night' ELSE 'Day' END AS time_period,COUNT(*) AS total_stops,SUM(CASE WHEN stop_outcome LIKE '%arrest%' THEN 1 ELSE 0 END) AS arrests FROM police_post
     GROUP BY time_period;
    """,

"Average Stop Duration by Violation":"""
    SELECT violation, AVG(stop_duration) AS avg_duration FROM police_post GROUP BY violation;
   """,
#⚖️ Violation-Based

"Top 5 Most Frequent Search Types":"""
    SELECT search_type, COUNT(*) AS count FROM police_post WHERE search_type != 'None' GROUP BY search_type ORDER BY count DESC LIMIT 5;
    """,

"Stops by Driver Race":"""
    SELECT driver_race, COUNT(*) AS count FROM police_post GROUP BY driver_race ORDER BY count DESC; 
    """,

"Stops by Country":"""
    SELECT country_name, COUNT(*) AS total_stops FROM police_post GROUP BY country_name ORDER BY total_stops DESC;
    """,

"Arrests vs Warnings":"""
    SELECT stop_outcome, COUNT(*) AS count FROM police_post GROUP BY stop_outcome;
    """,
#🌍 Location-Based
"Stops by Hour of Day":"""
    SELECT HOUR(stop_time) AS hour, COUNT(*) AS stop_count FROM police_post GROUP BY hour ORDER BY hour;
    """,

"Drivers Under 25 Most Common Violations":"""
    SELECT violation, COUNT(*) AS count FROM police_post WHERE driver_age < 25 GROUP BY violation ORDER BY count DESC;
   """,

"Countries with Highest Drug-Related Stops":"""
   SELECT country_name, COUNT(*) AS drug_stops FROM police_post WHERE drugs_related_stop=1 GROUP BY country_name ORDER BY drug_stops DESC;
  """,

  # Complex Queries 
# ---------------------------
 
    
    "Yearly Stops & Arrests by Country": """
        SELECT country_name, YEAR(stop_datetime) AS year, COUNT(*) AS total_stops,SUM(CASE WHEN stop_outcome LIKE '%arrest%' THEN 1 ELSE 0 END) AS total_arrests FROM police_post GROUP BY country_name, YEAR(stop_datetime)
        ORDER BY country_name, year;
    """,
    "Driver Violation Trends by Age & Race": """
        SELECT driver_age, driver_race, violation, COUNT(*) AS count FROM police_post GROUP BY driver_age, driver_race, violation ORDER BY count DESC;
    """,
    "Time Period Analysis (Stops by Year/Month/Hour)": """
        SELECT YEAR(stop_datetime) AS year,MONTH(stop_datetime) AS month,HOUR(stop_time) AS hour,COUNT(*) AS stop_count FROM police_post GROUP BY year, month, hour
        ORDER BY year, month, hour;
    """,
    "Violations with High Search & Arrest Rates": """
        SELECT violation,SUM(CASE WHEN search_conducted=1 THEN 1 ELSE 0 END) AS search_count,SUM(CASE WHEN stop_outcome LIKE '%arrest%' THEN 1 ELSE 0 END) AS arrest_count FROM police_post GROUP BY violation  HAVING search_count>10 OR arrest_count>10
        ORDER BY search_count DESC;
    """,
    "Driver Demographics by Country": """
        SELECT country_name, driver_age, driver_gender, driver_race, COUNT(*) AS count FROM police_post GROUP BY country_name, driver_age, driver_gender, driver_race ORDER BY count DESC;
    """,
    "Top 5 Violations with Highest Arrest Rates": """
        SELECT violation,SUM(CASE WHEN stop_outcome LIKE '%arrest%' THEN 1 ELSE 0 END)/COUNT(*) AS arrest_rate FROM police_post GROUP BY violation ORDER BY arrest_rate DESC LIMIT 5;
    """
}


selected_query = st.selectbox("Select a Query", list(query_map.keys()))

if st.button("Run Query"):
    result = fetch_data(query_map[selected_query])
    if not result.empty:
        st.dataframe(result, use_container_width=True)

        # Automatically add charts for numeric columns
        numeric_cols = result.select_dtypes(include='number').columns.tolist()
        if numeric_cols:
            if len(numeric_cols) == 1:
                fig = px.bar(result, x=result.columns[0], y=numeric_cols[0], title=selected_query, text=numeric_cols[0])
            else:
                fig = px.bar(result, x=result.columns[0], y=numeric_cols, title=selected_query)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⚠️No results found for this query.")


      
st.markdown("---")  
st.markdown("Built with  ❤️ for Law Enforcement by SecureCheck")
st.header("🧑‍✈️📝Custom Natural Language Filter🔮")

st.markdown("Fill in the details below to get a natural language prediction of the stop outcome based on existing data.")


st.header("📝 Add New Police Log & Predict Outcome and Violation")

# INPUT FIELD
#-----------------------------

driver_age = st.number_input("Driver Age", min_value=16, max_value=100, value=27)
driver_gender = st.selectbox("Driver Gender", ["male", "female"])
driver_race = st.text_input("Driver Race")
search_conducted = st.selectbox("Was a Search Conducted?", ["0", "1"])
search_type = st.text_input("Search Type")
drugs_related_stop = st.selectbox("Was it Drug Related?", ["0", "1"])
stop_duration = st.selectbox("Stop Duration", options=data['stop_duration'].dropna().unique())
vehicle_number = st.text_input("Vehicle Number")
stop_date = st.date_input("Stop Date")
stop_time = st.time_input("Stop Time")
county_name = st.text_input("County Name")

#  PREDICT BUTTON 
#-----------------------------------
if st.button("🔮Predict Stop Outcome & Violation"):

    # Filter data for prediction
    filtered_data = data[
        (data['driver_gender'] == driver_gender) &
        (data['driver_age'] == driver_age) &
        (data['search_conducted'] == int(search_conducted)) &
        (data['stop_duration'] == stop_duration) &
        (data['drugs_related_stop'] == int(drugs_related_stop))
    ]

    # PREDICT STOP OUTCOME AND VIOLATION
    #----------------------------------------------
    if not filtered_data.empty:
        predicted_outcome = filtered_data['stop_outcome'].mode()[0]
        predicted_violation = filtered_data['violation'].mode()[0]
    else:
        predicted_outcome = "warning"  # Default fallback
        predicted_violation = "speeding"  # Default fallback

    # NATURAL LANGUAGE SUMMARY
    #--------------------------------------
    search_text = "A search was conducted" if int(search_conducted) else "No search was conducted"
    drug_text = "was drug-related" if int(drugs_related_stop) else "was not drug-related"

    st.markdown(f"""
**Prediction Summary**
- **Predicted Violation:** {predicted_violation}
- **Predicted Stop Outcome:** {predicted_outcome}

A {driver_age}-year-old {driver_gender} driver in {county_name} was stopped at {stop_time.strftime('%I:%M %p')} on {stop_date}.
{search_text}, and the stop {drug_text}.
Stop duration: **{stop_duration}**.
Vehicle Number: **{vehicle_number}**.
""")


