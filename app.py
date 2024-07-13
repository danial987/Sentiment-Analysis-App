import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from sentiment_analysis import analyze_sentiment, get_sentiment_summary, get_top_words, get_word_frequencies, get_sentiment_timeline, get_sentiment_distribution, extract_key_phrases, get_heatmap_data, analyze_emotions
import pandas as pd
import PyPDF2
import docx
import io
import networkx as nx

def load_css():
    with open('static/style.css') as f:
        css_code = f.read()
    st.markdown(f'<style>{css_code}</style>', unsafe_allow_html=True)

# Initialize session state to store history and user input
if 'history' not in st.session_state:
    st.session_state.history = []

if 'user_input' not in st.session_state:
    st.session_state.user_input = ""

def read_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ''
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        text += page.extract_text()
    return text

def read_docx(file):
    doc = docx.Document(file)
    text = ''
    for para in doc.paragraphs:
        text += para.text + '\n'
    return text

def draw_hierarchical_tree():
    # Create a directed graph
    G = nx.DiGraph()

    # Add nodes and edges
    G.add_edges_from([
        ("Bad Writing", "Negative"),
        ("Bad Writing", "Neutral"),
        ("Bad Writing", "Positive"),
        ("Negative", "Bad"),
        ("Negative", "Horrible"),
        ("Bad", "Toilet"),
        ("Neutral", "Detective Story"),
        ("Positive", "Effective Start")
    ])

    pos = nx.spring_layout(G)  # positions for all nodes
    plt.figure(figsize=(10, 6))
    nx.draw(G, pos, with_labels=True, arrows=False, node_shape="o", node_size=3000, font_size=10, font_weight='bold')
    plt.title("Hierarchical Tree Visualization")
    st.pyplot(plt)

def input_page():
    load_css()
    st.title("Sentiment Analysis App")
    
    with st.container(border=True):
        input_tabs = st.tabs(["Enter Text", "Upload File"])
        
        with input_tabs[0]:
            st.write("Enter the text you want to analyze for sentiment:")
            with st.container(border=True):
                st.session_state.user_input = st.text_area("Input Text", height=200)
        
        with input_tabs[1]:
            st.write("Upload a file to analyze for sentiment:")
            with st.container(border=True):
                uploaded_file = st.file_uploader("Upload a PDF, Word, or TXT file", type=["pdf", "docx", "txt"])
                if uploaded_file is not None:
                    if uploaded_file.type == "application/pdf":
                        st.session_state.user_input = read_pdf(uploaded_file)
                    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                        st.session_state.user_input = read_docx(uploaded_file)
                    else:
                        st.session_state.user_input = uploaded_file.getvalue().decode("utf-8")

        if st.button("Analyze Sentiment"):
            if st.session_state.user_input:
                st.session_state.sentiment, st.session_state.confidence, st.session_state.detailed_sentiments = analyze_sentiment(st.session_state.user_input)
                # Store in history
                st.session_state.history.append({
                    'Text': st.session_state.user_input, 
                    'Sentiment': st.session_state.sentiment, 
                    'Confidence': st.session_state.confidence
                })
                st.session_state.analysis_done = True
                st.session_state.page = "results"
                st.experimental_rerun()
            else:
                st.write("Please enter text to analyze or upload a file.")

def results_page():
    load_css()
    st.title("Sentiment Analysis Results")
    
    if 'analysis_done' in st.session_state and st.session_state.analysis_done:
        if st.button("Back"):
            st.session_state.page = "input"
            st.experimental_rerun()
        
        with st.container(border=True):
            tabs = st.tabs(["Results", "Visualizations", "Detailed Breakdown", "Top Words by Sentiment", "Historical Analysis", "Emotion Analysis"])
            
            with tabs[0]:
                with st.container(border=True):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric(label="Sentiment Result", value=st.session_state.sentiment)
                    
                    with col2:
                        st.metric(label="Confidence Score", value=f"{st.session_state.confidence:.2f}%")
                
                with st.container(border=True):
                    st.subheader("Sentiment Summary")
                    positive_count, negative_count, neutral_count = get_sentiment_summary(st.session_state.user_input)
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric(label="Positive Words", value=positive_count)
                    
                    with col2:
                        st.metric(label="Negative Words", value=negative_count)
                    
                    with col3:
                        st.metric(label="Neutral Words", value=neutral_count)
            
            with tabs[1]:
                st.header("Visualizations")
                
                with st.container(border=True):
                    vis_tabs = st.tabs(["Sentiment Distribution", "Word Cloud", "Interactive Word Cloud", "Sentiment Heatmap", "Sentiment Timeline", "Treemap", "Hierarchical Tree"])
                    
                    with vis_tabs[0]:
                        st.subheader("Sentiment Distribution")
                        positive_count, negative_count, neutral_count = get_sentiment_distribution(st.session_state.user_input)
                        labels = ['Positive', 'Negative', 'Neutral']
                        values = [positive_count, negative_count, neutral_count]
                        
                        fig = px.pie(names=labels, values=values, title="Sentiment Distribution", 
                                     color=labels, color_discrete_map={'Positive':'green', 'Negative':'red', 'Neutral':'gray'})
                        st.plotly_chart(fig)
                    
                    with vis_tabs[1]:
                        st.subheader("Word Cloud")
                        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(st.session_state.user_input)
                        fig, ax = plt.subplots()
                        ax.imshow(wordcloud, interpolation='bilinear')
                        ax.axis('off')  # Hide the axes
                        st.pyplot(fig)

                    with vis_tabs[2]:
                        st.subheader("Interactive Word Cloud")
                        word_freq = get_word_frequencies(st.session_state.user_input)
                        fig = px.bar(word_freq, x='Word', y='Frequency', title='Top 10 Most Frequent Words')
                        st.plotly_chart(fig)

                    with vis_tabs[3]:
                        st.subheader("Sentiment Heatmap")
                        heatmap_data = get_heatmap_data(st.session_state.user_input)
                        fig = px.density_heatmap(heatmap_data, x="Segment", y="Sentiment", title="Sentiment Heatmap")
                        st.plotly_chart(fig)

                    with vis_tabs[4]:
                        st.subheader("Sentiment Timeline")
                        timeline = get_sentiment_timeline(st.session_state.user_input)
                        fig = px.line(timeline, x='Position', y='Sentiment', title='Sentiment Timeline')
                        st.plotly_chart(fig)

                    with vis_tabs[5]:
                        st.subheader("Treemap")
                        word_freq = get_word_frequencies(st.session_state.user_input)
                        fig = px.treemap(word_freq, path=['Word'], values='Frequency', title='Word Frequency Treemap')
                        st.plotly_chart(fig)

                    with vis_tabs[6]:
                        st.subheader("Hierarchical Tree")
                        draw_hierarchical_tree()
            
            with tabs[2]:
                st.header("Detailed Breakdown")
                detailed_sentiments = st.session_state.detailed_sentiments
                
                with st.container(border=True):
                    breakdown_tabs = st.tabs(["Sentiment Score Trend", "Detailed Sentiment Scores"])

                    with breakdown_tabs[0]:
                        st.subheader("Sentiment Score Trend")
                        sentiment_scores = [sentiment['score'] for sentiment in detailed_sentiments]
                        sentence_positions = list(range(len(sentiment_scores)))
                        fig = px.line(x=sentence_positions, y=sentiment_scores, title='Sentiment Score Trend')
                        st.plotly_chart(fig)
                    
                    with breakdown_tabs[1]:
                        st.subheader("Detailed Sentiment Scores")
                        for i, sentiment in enumerate(detailed_sentiments):
                            sentiment_color = "green" if sentiment['label'] == "Positive" else "red" if sentiment['label'] == "Negative" else "gray"
                            st.markdown(f"<span style='color:{sentiment_color}'>{i + 1}. {sentiment['text']} - {sentiment['label']} ({sentiment['score']:.2f})</span>", unsafe_allow_html=True)

            with tabs[3]:
                st.header("Top Words by Sentiment")
                positive_words, negative_words, neutral_words = get_top_words(st.session_state.user_input)
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.write("**Positive Words**")
                    st.write(positive_words)

                with col2:
                    st.write("**Negative Words**")
                    st.write(negative_words)

                with col3:
                    st.write("**Neutral Words**")
                    st.write(neutral_words)

            with tabs[4]:
                st.header("Historical Analysis")
                with st.container(border=True):
                    history_df = pd.DataFrame(st.session_state.history)
                    st.dataframe(history_df)

                with st.container(border=True):
                    st.subheader("Overall Sentiment Distribution")
                    overall_positive = history_df[history_df['Sentiment'] == 'Positive'].shape[0]
                    overall_negative = history_df[history_df['Sentiment'] == 'Negative'].shape[0]
                    overall_neutral = history_df[history_df['Sentiment'] == 'Neutral'].shape[0]
                    overall_distribution = pd.DataFrame({
                        'Sentiment': ['Positive', 'Negative', 'Neutral'],
                        'Count': [overall_positive, overall_negative, overall_neutral]
                    })
                    fig = px.bar(overall_distribution, x='Sentiment', y='Count', title='Overall Sentiment Distribution')
                    st.plotly_chart(fig)

            with tabs[5]:
                st.header("Emotion Analysis")
                emotions = analyze_emotions(st.session_state.user_input)
                emotion_labels = list(emotions.keys())
                emotion_values = list(emotions.values())
                fig = px.bar(x=emotion_labels, y=emotion_values, title="Emotion Analysis")
                st.plotly_chart(fig)

    else:
        st.write("No analysis done yet. Please go to the 'Input' page to analyze text or upload a file.")

# Page navigation logic
def main():
    if 'page' not in st.session_state:
        st.session_state.page = "input"
    
    page = st.session_state.page
    
    if page == "input":
        input_page()
    elif page == "results":
        results_page()

if __name__ == "__main__":
    main()
