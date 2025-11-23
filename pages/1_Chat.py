
import streamlit as st
import pandas as pd
import re


@st.cache_data
def load_data():
    return pd.read_csv("road_america_lap_time_R1.csv")   

df = load_data()

st.title("🏁 Racing Data Chat Explorer")
st.write("Ask questions about the telemetry dataset using natural language.")


with st.expander("📄 View Raw Data"):
    st.dataframe(df.head())


if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


for entry in st.session_state.chat_history:
    with st.chat_message(entry["role"]):
        st.write(entry["content"])


user_input = st.chat_input("Ask something about the data...")

def respond_to_query(query):
    q = query.lower()

   
    vehicle_match = re.search(r"(vehicle\s*|gr86-)\s*([0-9-]+)", q)
    if vehicle_match:
        vid = vehicle_match.group(2)
        result = df[df["vehicle_id"].str.contains(vid)]
        return f"Showing data for vehicle `{vid}`:", result
    
   
    lap_match = re.search(r"lap\s*([0-9]+)", q)
    if lap_match:
        lap_num = int(lap_match.group(1))
        result = df[df["lap"] == lap_num]
        return f"Showing records for lap `{lap_num}`:", result

   
    if "how many vehicles" in q or "count vehicles" in q:
        count = df["vehicle_id"].nunique()
        return f"There are **{count} unique vehicles** in the dataset.", None

    
    if "highest value" in q:
        row = df.loc[df["value"].idxmax()]
        return f"Highest value is **{row['value']}** from vehicle **{row['vehicle_id']}**.", None

    
    return "I didn't understand that, but here's the dataset:", df.head()


if user_input:
    
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    
    text_response, table_response = respond_to_query(user_input)

    
    st.session_state.chat_history.append({"role": "assistant", "content": text_response})

    
    with st.chat_message("assistant"):
        st.write(text_response)
        if isinstance(table_response, pd.DataFrame):
            st.dataframe(table_response)
st.markdown(
    """
    <div style="
        background-color: #f0f4f8;
        border-left: 5px solid #FF4B4B;
        padding: 15px;
        border-radius: 10px;
        font-family: 'Arial';
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    ">
        <strong>💡 Suggested Questions:</strong>
        <ul style='margin-top: 10px;'>
            <li>Show me vehicle 32768</li>
            <li>Lap 5 data</li>
            <li>How many vehicles are in the dataset?</li>
            <li>What is the highest value?</li>
        </ul>
    </div>
    """,
    unsafe_allow_html=True
)