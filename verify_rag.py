from rag_logic import RAGEngine
import os
import pandas as pd

def verify_rag():
    print("Testing RAGEngine...")
    engine = RAGEngine(persist_directory="./test_chroma")
    
    # Create temp CSV
    csv_path = "test_data.csv"
    df = pd.DataFrame({
        "date": ["2026-01-01"],
        "amount": [10.0],
        "category": ["Food"]
    })
    df.to_csv(csv_path, index=False)
    
    try:
        print("Processing CSV...")
        docs = engine.process_csv(csv_path)
        print(f"Docs created: {len(docs)}")
        
        print("Initializing Vector DB...")
        engine.initialize_vector_db(docs)
        
        print("Querying SIMILAR transactions...")
        results = engine.query_similar_transactions("Food", k=1)
        print(f"Results found: {len(results)}")
        if len(results) > 0:
            print(f"Result content: {results[0].page_content}")
            print("Verification SUCCESSFUL!")
        else:
            print("Verification FAILED: No results found.")
            
    finally:
        if os.path.exists(csv_path):
            os.remove(csv_path)
        # We'll leave the test_chroma dir for now or clean up
        import shutil
        if os.path.exists("./test_chroma"):
            shutil.rmtree("./test_chroma")

if __name__ == "__main__":
    verify_rag()
