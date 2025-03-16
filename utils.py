import nltk
from nltk.corpus import stopwords
from collections import Counter

nltk.download("stopwords")

def extract_keywords(texts):
    words = " ".join(texts).lower().split()
    words = [word for word in words if word not in stopwords.words("english")]
    common_words = Counter(words).most_common(10)
    return [word[0] for word in common_words]

def generate_ai_recommendations(sentiments):
    if sentiments["Negative"] > sentiments["Positive"]:
        return [
            {"message": "Users express concern about response times", "priority": "High"},
            {"message": "Consider improving customer service quality", "priority": "Medium"}
        ]
    return [
        {"message": "Product features are generally well-received", "priority": "Low"}
    ]
