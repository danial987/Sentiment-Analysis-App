from textblob import TextBlob
import nltk
import pandas as pd

# Ensure you have downloaded the necessary corpora
nltk.download('punkt')

def analyze_sentiment(text):
    blob = TextBlob(text)
    sentiments = []
    for sentence in blob.sentences:
        sentiment_score = sentence.sentiment.polarity
        if sentiment_score > 0:
            sentiment_label = 'Positive'
        elif sentiment_score < 0:
            sentiment_label = 'Negative'
        else:
            sentiment_label = 'Neutral'
        sentiments.append({
            'text': str(sentence),
            'score': sentiment_score,
            'label': sentiment_label
        })
    
    # Overall sentiment
    overall_sentiment_score = blob.sentiment.polarity
    if overall_sentiment_score > 0:
        overall_sentiment_label = 'Positive'
    elif overall_sentiment_score < 0:
        overall_sentiment_label = 'Negative'
    else:
        overall_sentiment_label = 'Neutral'
    
    return overall_sentiment_label, overall_sentiment_score * 100, sentiments

def get_sentiment_summary(text):
    blob = TextBlob(text)
    positive, negative, neutral = 0, 0, 0
    for sentence in blob.sentences:
        if sentence.sentiment.polarity > 0:
            positive += 1
        elif sentence.sentiment.polarity < 0:
            negative += 1
        else:
            neutral += 1
    return positive, negative, neutral

def get_top_words(text):
    blob = TextBlob(text)
    words = blob.words
    positive_words, negative_words, neutral_words = [], [], []
    for word in words:
        word_blob = TextBlob(word)
        sentiment_score = word_blob.sentiment.polarity
        if sentiment_score > 0:
            positive_words.append(word)
        elif sentiment_score < 0:
            negative_words.append(word)
        else:
            neutral_words.append(word)
    return positive_words, negative_words, neutral_words

def get_word_frequencies(text):
    blob = TextBlob(text)
    word_counts = blob.word_counts.items()
    word_freq_df = pd.DataFrame(word_counts, columns=['Word', 'Frequency'])
    word_freq_df = word_freq_df.sort_values(by='Frequency', ascending=False).head(10)
    return word_freq_df

def get_sentiment_timeline(text):
    blob = TextBlob(text)
    sentiment_timeline = []
    for i, sentence in enumerate(blob.sentences):
        sentiment_timeline.append({'Position': i, 'Sentiment': sentence.sentiment.polarity})
    return pd.DataFrame(sentiment_timeline)

def get_sentiment_distribution(text):
    positive, negative, neutral = get_sentiment_summary(text)
    return positive, negative, neutral

def extract_key_phrases(text):
    blob = TextBlob(text)
    phrases = blob.noun_phrases
    phrase_sentiments = []
    for phrase in phrases:
        phrase_blob = TextBlob(phrase)
        sentiment_score = phrase_blob.sentiment.polarity
        if sentiment_score > 0:
            sentiment_label = 'Positive'
        elif sentiment_score < 0:
            sentiment_label = 'Negative'
        else:
            sentiment_label = 'Neutral'
        phrase_sentiments.append({
            'phrase': phrase,
            'score': sentiment_score,
            'label': sentiment_label
        })
    return phrase_sentiments

def get_heatmap_data(text):
    blob = TextBlob(text)
    heatmap_data = []
    for i, sentence in enumerate(blob.sentences):
        heatmap_data.append([i, sentence.sentiment.polarity])
    return pd.DataFrame(heatmap_data, columns=['Segment', 'Sentiment'])

def analyze_emotions(text):
    blob = TextBlob(text)
    emotions = {'Joy': 0, 'Anger': 0, 'Sadness': 0, 'Fear': 0, 'Surprise': 0, 'Disgust': 0}
    for sentence in blob.sentences:
        sentiment_score = sentence.sentiment.polarity
        if sentiment_score > 0.5:
            emotions['Joy'] += 1
        elif sentiment_score < -0.5:
            emotions['Anger'] += 1
        elif sentiment_score < 0:
            emotions['Sadness'] += 1
        elif 'fear' in sentence.lower():
            emotions['Fear'] += 1
        elif 'surprise' in sentence.lower():
            emotions['Surprise'] += 1
        elif 'disgust' in sentence.lower():
            emotions['Disgust'] += 1
    return emotions
