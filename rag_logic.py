import pandas as pd
import numpy as np
import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

# ==========================================
# STEP 1: LOADING AND PROCESSING DATA
# ==========================================

def load_transaction_data(file_path):
    """
    This function reads a CSV file and converts it into two parts:
    1. A pandas DataFrame (useful for charts and math)
    2. A list of LangChain 'Documents' (useful for the AI to read)
    """
    # Read the CSV file into a DataFrame
    df = pd.read_csv(file_path)
    
    # Standardize column names (lowercase and trimmed)
    df.columns = [col.strip().lower() for col in df.columns]
    
    # Check if we have the columns we need
    required_cols = {'date', 'amount', 'category'}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"CSV must contain at least: {required_cols}")
        
    documents = []
    # Loop through each row to create a text description for the AI
    for _, row in df.iterrows():
        # We turn each transaction into a readable sentence
        content = f"On {row['date']}, I spent ${row['amount']} at {row.get('vendor', 'Unknown')} in the {row['category']} category."
        
        # We store this text along with some extra data (metadata)
        metadata = {
            "date": row['date'],
            "amount": row['amount'],
            "category": row['category']
        }
        documents.append(Document(page_content=content, metadata=metadata))
        
    return documents, df

# ==========================================
# STEP 2: SETTING UP THE AI SEARCH INDEX
# ==========================================

def initialize_ai_search(documents, persist_directory="./chroma_db"):
    """
    Computes 'embeddings' (math versions of text) for our transactions
    and saves them in a local Chroma database.
    """
    # embeddings help the AI find things that 'mean' the same thing, not just exact words
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Create the vector database from our document list
    vector_store = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=persist_directory
    )
    return vector_store

def find_related_transactions(query, vector_store, k=5):
    """
    Searches the database for the k most relevant transactions to a user query.
    """
    if not vector_store:
        return []
    
    # similarity_search finds the closest matches in the database
    return vector_store.similarity_search(query, k=k)

# ==========================================
# STEP 3: CALCULATING FINANCIAL RISKS
# ==========================================

def analyze_spending_risks(df, food_limit=200, shopping_limit=300):
    """
    Analyzes the spreadsheet data to find risky spending patterns.
    """
    # 1. Ensure dates are in the right format
    df['date'] = pd.to_datetime(df['date'])
    
    # 2. Total spending by category
    category_totals = df.groupby('category')['amount'].sum().to_dict()
    
    risks = []
    # 3. Check for Budget Overruns
    thresholds = {"food": food_limit, "shopping": shopping_limit}
    for category, total in category_totals.items():
        limit = thresholds.get(category.lower(), 500) # Default $500 limit
        if total > limit:
            risks.append({
                "type": "Budget Overrun",
                "category": category,
                "severity": "High" if total > limit * 1.5 else "Medium",
                "message": f"Spent ${total:.2f} on {category}. Your limit is ${limit}."
            })
            
    # 4. Detect "Anomalies" (Large, unusual purchases)
    if len(df) > 5:
        mean_spend = df['amount'].mean()
        std_dev = df['amount'].std()
        # Anything more than 2 standard deviations above the mean is an 'outlier'
        outliers = df[df['amount'] > mean_spend + (2 * std_dev)]
        for _, row in outliers.iterrows():
            risks.append({
                "type": "Large Purchase",
                "category": row['category'],
                "severity": "Medium",
                "message": f"Found unusual ${row['amount']} spend at {row.get('vendor', 'Unknown')}."
            })

    return {
        "category_totals": category_totals,
        "risks": risks,
        "total_spending": df['amount'].sum()
    }

def format_risk_summary(metrics):
    """
    Converts our math results into a simple text summary for the AI to read.
    """
    text = f"Total Spending: ${metrics['total_spending']:.2f}\n\nRisks Identified:\n"
    if not metrics['risks']:
        text += "- No major risks found!"
    else:
        for risk in metrics['risks']:
            text += f"- [{risk['severity']}] {risk['type']}: {risk['message']}\n"
    return text
