import streamlit as st
import pandas as pd
import os
import plotly.express as px
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate

# Import our simple functions from the logic file
from rag_logic import (
    load_transaction_data, 
    initialize_ai_search, 
    find_related_transactions, 
    analyze_spending_risks, 
    format_risk_summary
)

# ==========================================
# SECTION 1: PAGE CONFIGURATION & STYLING
# ==========================================

# Set up the browser tab title and icon
st.set_page_config(page_title="Beginner AI Finance Guide", page_icon="💰", layout="wide")

# Apply some custom CSS to make it look "Stunning"
st.markdown("""
<style>
    .main { background-color: #f1f3f5; }
    .stMetric { background-color: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .risk-card { padding: 15px; border-radius: 8px; border-left: 5px solid #ff4b4b; background-color: #fff1f1; margin-bottom: 10px; }
    .risk-high { border-left-color: #ff4b4b; }
    .risk-medium { border-left-color: #ffa500; background-color: #fff9f1; }
    .risk-low { border-left-color: #2e7d32; background-color: #f1f8f1; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# SECTION 2: THE SIDEBAR (INPUTS)
# ==========================================

with st.sidebar:
    st.title("Settings ⚙️")
    # API Key for the AI (Claude)
    api_key = st.text_input("1. Enter Anthropic API Key", type="password", help="Needed to talk to the AI")
    # File uploader for the transaction spreadsheet
    uploaded_file = st.file_uploader("2. Upload transaction CSV", type=["csv"])
    
    st.divider()
    # Handy button to let users try the app quickly
    if st.button("Get Sample CSV"):
        sample = pd.DataFrame({
            "date": ["2026-04-01", "2026-04-05", "2026-04-10"],
            "amount": [50.0, 150.0, 20.0],
            "category": ["Food", "Shopping", "Transport"],
            "vendor": ["Grocery Store", "Mall", "Uber"]
        })
        st.download_button("Download Now", sample.to_csv(index=False), "sample.csv", "text/csv")

# ==========================================
# SECTION 3: MAIN APP LOGIC
# ==========================================

st.title("AI Financial Risk & Intervention 🤖💸")
st.write("A beginner-friendly tool to analyze your spending and get smart AI advice.")

# Only run the app if the user has provided the API Key
if not api_key:
    st.info("👋 Hello! Please enter your Anthropic API Key in the sidebar to start.")
else:
    # Only run if a file is uploaded
    if uploaded_file is not None:
        
        # We use 'session_state' to remember data even when the page refreshes
        if 'app_initialized' not in st.session_state:
            with st.spinner("Step 1: Analyzing your data..."):
                # 1. Load the data
                docs, df = load_transaction_data(uploaded_file)
                # 2. Setup the AI search engine
                vector_db = initialize_ai_search(docs)
                # 3. Calculate financial risks
                metrics = analyze_spending_risks(df)
                
                # Save everything so we don't have to redo it every click
                st.session_state.df = df
                st.session_state.vector_db = vector_db
                st.session_state.metrics = metrics
                st.session_state.app_initialized = True

        # Create two tabs for a clean look
        tab1, tab2 = st.tabs(["📊 Spending Dashboard", "💬 Ask the AI"])

        # --- DASHBOARD TAB ---
        with tab1:
            st.header("Financial Health Overview")
            
            # Show 3 simple metric boxes at the top
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Spent", f"${st.session_state.metrics['total_spending']:,.2f}")
            with col2:
                top_cat = max(st.session_state.metrics['category_totals'], key=st.session_state.metrics['category_totals'].get)
                st.metric("Biggest Expense", top_cat)
            with col3:
                risk_count = len(st.session_state.metrics['risks'])
                st.metric("Risk Alerts", risk_count)

            st.divider()

            # Create TWO columns for charts
            chart_col1, chart_col2 = st.columns(2)
            
            with chart_col1:
                st.subheader("Spending by Category")
                # Create a simple Pie Chart using Plotly
                fig_pie = px.pie(
                    values=list(st.session_state.metrics['category_totals'].values()), 
                    names=list(st.session_state.metrics['category_totals'].keys()),
                    hole=0.4
                )
                st.plotly_chart(fig_pie, use_container_width=True)

            with chart_col2:
                st.subheader("Daily Spending Trend")
                # Create a Line Chart showing spending over time
                trend = st.session_state.df.groupby('date')['amount'].sum().reset_index()
                fig_line = px.line(trend, x='date', y='amount', markers=True)
                st.plotly_chart(fig_line, use_container_width=True)

            # Show Risk Alerts
            st.subheader("Smart Intervention Alerts 🚨")
            for risk in st.session_state.metrics['risks']:
                # Change color based on severity
                color_class = f"risk-{risk['severity'].lower()}"
                st.markdown(f"""
                    <div class="risk-card {color_class}">
                        <strong>{risk['type']}</strong><br>{risk['message']}
                    </div>
                """, unsafe_allow_html=True)

        # --- AI ASSISTANT TAB ---
        with tab2:
            st.header("AI Financial Advisor")
            st.write("The AI knows about your risks and specific transactions mentioned below.")
            
            # Store chat messages so they stay on the screen
            if "chat_history" not in st.session_state:
                st.session_state.chat_history = []

            # Display all previous messages
            for msg in st.session_state.chat_history:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

            # Input box for the user to type
            if user_input := st.chat_input("Ex: Why is my food spending so high?"):
                # Save and show user message
                st.session_state.chat_history.append({"role": "user", "content": user_input})
                with st.chat_message("user"):
                    st.markdown(user_input)

                # Generate AI response
                with st.spinner("AI is thinking..."):
                    # 1. Find relevant transactions from the database
                    related_docs = find_related_transactions(user_input, st.session_state.vector_db)
                    context_text = "\n".join([d.page_content for d in related_docs])
                    
                    # 2. Get the pre-calculated risk summary
                    risk_summary = format_risk_summary(st.session_state.metrics)

                    # 3. Create the prompt for the AI
                    prompt = f"""
                    You are a financial advisor. Use this context to help the user.
                    
                    RISK SUMMARY:
                    {risk_summary}
                    
                    RELATED TRANSACTIONS:
                    {context_text}
                    
                    USER QUESTION: {user_input}
                    
                    ADVICE:"""

                    # 4. Call the Claude API
                    llm = ChatAnthropic(anthropic_api_key=api_key, model="claude-3-5-sonnet-20240620")
                    response = llm.invoke(prompt)
                    
                    # 5. Show and save the AI message
                    with st.chat_message("assistant"):
                        st.markdown(response.content)
                    st.session_state.chat_history.append({"role": "assistant", "content": response.content})
    else:
        st.warning("Please upload a CSV file to begin your financial analysis.")
