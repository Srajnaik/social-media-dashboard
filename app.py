import time

# Fix for Python 3.8+ compatibility
if not hasattr(time, "clock"):
    time.clock = time.perf_counter

import streamlit as st
import pandas as pd
import aiml
import os
import re
import plotly.express as px

# ---------------------------------------------------
# PAGE SETTINGS
# ---------------------------------------------------
st.set_page_config(
    page_title="Social Media Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

# ---------------------------------------------------
# LOAD DATA
# ---------------------------------------------------
@st.cache_data
def load_data():
    return pd.read_csv("social_media_usage.csv")

df = load_data()

# ---------------------------------------------------
# LOAD AIML BOT
# ---------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("social_media_usage.csv")

    # Remove extra spaces if any
    df["App"] = df["App"].str.strip()

    return df
# ---------------------------------------------------
# QUERY HANDLER
# ---------------------------------------------------
def execute_dataset_query(response):

    if response.startswith("QUERY_AVG_TIME_"):

        app_name = response.replace("QUERY_AVG_TIME_", "")

        filtered = df[df["App"].str.lower() == app_name.lower()]

        avg_time = filtered["Daily_Minutes_Spent"].mean()

        return f"Average time spent on {app_name}: {avg_time:.1f} minutes"

    elif response.startswith("QUERY_AVG_LIKES_"):

        app_name = response.replace("QUERY_AVG_LIKES_", "")

        filtered = df[df["App"].str.lower() == app_name.lower()]

        avg_likes = filtered["Likes_Per_Day"].mean()

        return f"Average likes on {app_name}: {avg_likes:.1f}"

    elif response.startswith("QUERY_MAX_POSTS_"):

        app_name = response.replace("QUERY_MAX_POSTS_", "")

        filtered = df[df["App"].str.lower() == app_name.lower()]

        max_posts = filtered["Posts_Per_Day"].max()

        return f"Maximum posts on {app_name}: {max_posts}"

    elif "QUERY_MOST_POPULAR" in response:

        app_totals = df.groupby("App")["Daily_Minutes_Spent"].sum()

        popular = app_totals.idxmax()

        return f"Most popular app is {popular}"

    return response

# ---------------------------------------------------
# TITLE
# ---------------------------------------------------
st.title("📊 Social Media Analytics Dashboard")

# ---------------------------------------------------
# METRICS
# ---------------------------------------------------
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Users", df["User_ID"].nunique())

with col2:
    st.metric("Average Screen Time", round(df["Daily_Minutes_Spent"].mean(), 1))

with col3:
    st.metric("Average Likes", round(df["Likes_Per_Day"].mean(), 1))

# ---------------------------------------------------
# CHARTS
# ---------------------------------------------------
st.subheader("Charts")

chart1, chart2 = st.columns(2)

with chart1:

    app_minutes = df.groupby("App", as_index=False)["Daily_Minutes_Spent"].sum()

    fig1 = px.pie(
        app_minutes,
        values="Daily_Minutes_Spent",
        names="App",
        title="Screen Time Share",
        hole=0.4
    )

    st.plotly_chart(fig1, use_container_width=True)

with chart2:

    app_likes = df.groupby("App", as_index=False)["Likes_Per_Day"].mean()

    fig2 = px.bar(
        app_likes,
        x="App",
        y="Likes_Per_Day",
        color="App",
        title="Average Likes"
    )

    st.plotly_chart(fig2, use_container_width=True)

# ---------------------------------------------------
# CHATBOT
# ---------------------------------------------------
st.subheader("🤖 AIML Chatbot")

if "messages" not in st.session_state:

    st.session_state.messages = []

# Show messages
for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
prompt = st.chat_input("Ask a question")

if prompt:

    # Show user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    # Clean input
    clean_prompt = re.sub(r"[^\w\s]", "", prompt).upper()

    # AIML response
    raw_response = kernel.respond(clean_prompt)

    # Final response
    if raw_response:
        final_response = execute_dataset_query(raw_response)
    else:
        final_response = "Sorry, I don't understand that question."

    # Save assistant message
    st.session_state.messages.append({
        "role": "assistant",
        "content": final_response
    })

    # Rerun
    st.rerun()