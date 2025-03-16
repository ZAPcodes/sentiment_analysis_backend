from transformers import pipeline

# Load AI models
sentiment_pipeline = pipeline("sentiment-analysis")
emotion_pipeline = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base")

def analyze_sentiment(text):
    result = sentiment_pipeline(text)[0]
    sentiment = result["label"]
    score = result["score"]
    
    emotion_result = emotion_pipeline(text)[0]
    emotion = emotion_result["label"]
    
    return {
        "text": text,
        "sentiment": sentiment,
        "score": round(score, 2),
        "emotion": emotion
    }
