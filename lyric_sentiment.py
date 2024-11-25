from transformers import pipeline

def analyze_sentiment(text):
    # Initialize the sentiment analysis pipeline
    sentiment_analyzer = pipeline(
        "sentiment-analysis",
        model="siebert/sentiment-roberta-large-english",
        return_all_scores=True
    )
    
    # Get the sentiment scores
    results = sentiment_analyzer(text)
    
    # Return the results for the first input (results[0] contains list of sentiments)
    return results[0]

def main():
    # Get input from user
    print("Enter the lyrics to analyze (press Enter twice to finish):")
    lines = []
    while True:
        line = input()
        if line:
            lines.append(line)
        else:
            break
    
    lyrics = " ".join(lines)
    
    # Analyze the sentiment
    sentiment_scores = analyze_sentiment(lyrics)
    
    # Display results
    print("\nSentiment Analysis Results:")
    for score in sentiment_scores:
        print(f"{score['label']}: {score['score']:.3f}")

if __name__ == "__main__":
    main()
