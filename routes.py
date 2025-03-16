from fastapi import APIRouter, Form, UploadFile, File, HTTPException
import pandas as pd
import io
from models import analyze_sentiment
from utils import extract_keywords, generate_ai_recommendations
from collections import Counter, defaultdict
from pathlib import Path

router = APIRouter()

sentiment_storage = {"Positive": 0, "Negative": 0, "Neutral": 0}  # Store counts

@router.post("/api/analyze")
async def analyze_text(data: dict):
    if "text" not in data:
        raise HTTPException(status_code=400, detail="Missing 'text' field")

    result = analyze_sentiment(data["text"])

    # Ensure the sentiment exists in sentiment_storage before updating it
    if result["sentiment"] not in sentiment_storage:
        sentiment_storage[result["sentiment"]] = 0  

    sentiment_storage[result["sentiment"]] += 1  # Track counts for graph
    return result


# API: Bulk CSV Sentiment Analysis
@router.post("/api/analyze_csv")
async def analyze_csv(file: UploadFile = File(...), column_name: str = Form("")):
    contents = await file.read()
    print("File read successfully!")

    df = pd.read_csv(io.StringIO(contents.decode("utf-8")))
    print("CSV Columns:", df.columns.tolist())

    # If column_name is empty, auto-detect text-based columns
    if not column_name:
        possible_text_columns = [col for col in df.columns if df[col].dtype == 'object']
        if not possible_text_columns:
            raise HTTPException(status_code=400, detail="No text-based columns found in CSV.")
        column_name = possible_text_columns[0]  # Pick the first text column automatically

    if column_name not in df.columns:
        raise HTTPException(status_code=400, detail=f"Column '{column_name}' not found in CSV.")

    # Initialize sentiment counts
    sentiment_counts = defaultdict(int)

    # Perform sentiment analysis and normalize sentiments
    df["sentiment"] = df[column_name].apply(lambda x: analyze_sentiment(str(x))["sentiment"].upper())

    # Debugging: Print unique sentiment values
    print("Unique Sentiments in DataFrame:", df["sentiment"].unique())

    # Count occurrences of each sentiment and store it in sentiment_counts
    for sentiment in df["sentiment"]:
        sentiment_counts[sentiment] += 1

    print("Sentiment Counts:", dict(sentiment_counts))  # Debugging

    # Extract keywords
    df["keywords"] = df[column_name].apply(lambda x: extract_keywords(x) if pd.notna(x) else "")

    # Save results to CSV
    output_dir = Path("static")
    output_dir.mkdir(exist_ok=True)  # Ensure directory exists
    output_path = output_dir / "sentiment_results.csv"
    df.to_csv(output_path, index=False)

    # AI Recommendations
    ai_recommendations = generate_ai_recommendations(sentiment_counts)

    return {
        "message": "Analysis complete",
        "download_url": f"/static/{output_path.name}",
        "sentiment_distribution": dict(sentiment_counts),  # Now correctly populated
        "ai_recommendations": ai_recommendations
    }



# API: Get Sentiment Distribution for Graphs
@router.get("/api/sentiment_distribution")
async def get_sentiment_distribution():
    return sentiment_storage

# API: Get Trending Keywords
@router.get("/api/get_keywords")
async def get_keywords():
    sample_texts = ["The service was great!", "Terrible customer support.", "Loved the experience."]
    keywords = extract_keywords(sample_texts)
    return {"keywords": keywords}

# API: Download Processed CSV
@router.get("/api/download_csv")
async def download_csv():
    return {"download_url": "/static/sentiment_results.csv"}
