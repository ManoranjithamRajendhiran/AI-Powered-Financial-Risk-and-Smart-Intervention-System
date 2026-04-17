# 💰 AI Financial Risk & Smart Intervention System (Beginner Friendly)

Welcome! This project is a simple yet powerful AI tool built with **Python** and **Streamlit**. It helps you analyze your spending, identify financial risks (like overspending), and get smart advice from an AI Assistant.

## 🚀 Features
- **Interactive Dashboard**: View your spending trends and category breakdowns with beautiful charts.
- **Risk Detection**: Automated alerts for budget overruns and unusual spending spikes.
- **AI Financial Advisor**: Chat with an AI (powered by Claude) that knows your spending history.

## 📚 Beginner's Guide: How it Works
This project is split into two simple parts:

1.  **`rag_logic.py` (The Brain)**: 
    - This file contains functions to read your spreadsheet (`load_transaction_data`).
    - It uses a "Vector Database" (`initialize_ai_search`) to help the AI find specific transactions later.
    - It runs simple math (`analyze_spending_risks`) to find where you've spent too much.

2.  **`app.py` (The Face)**:
    - This is the website logic. It uses **Streamlit** to create buttons, uploaders, and tabs.
    - It uses **Plotly** to draw the colorful charts.
    - It manages the chat conversation between you and the AI.

## 🛠️ How to Run
1.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
2.  **Start the App**:
    ```bash
    streamlit run app.py
    ```
3.  **Use the Sidebar**:
    - Enter your **Anthropic API Key**.
    - Upload a CSV file with columns: `date`, `amount`, `category`, and `vendor`.

## 📂 Project Structure
- `app.py`: The main user interface code.
- `rag_logic.py`: The logic for data processing and AI search.
- `mock_transactions.csv`: Sample data you can use to test.
- `requirements.txt`: List of libraries needed to run the app.

---
*Created with beginners in mind. Feel free to explore the code and see how the data flows!*