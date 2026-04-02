def analyse_sentiment(text):
    text = text.lower()

    if any(word in text for word in ["good", "happy", "love", "awesome"]):
        return "Positive"

    elif any(word in text for word in ["bad", "sad", "hate", "terrible"]):
        return "Negative"

    else:
        return "Neutral"