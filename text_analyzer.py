# Import library
import streamlit as st
import PyPDF2
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from docx import Document
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
import io
from io import BytesIO
from textblob import TextBlob
from googletrans import Translator
import nltk
import xlsxwriter
import base64
from PIL import Image
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
nltk.download("punkt")
nltk.download("stopwords")

st.cache_data
# Define function to generate text analyzer
def get_text_analyzer():
    # Create selection sidebar
    serv_opt = ["Document Uploader", "Text Sentiment"]
    services = st.sidebar.selectbox("Choose Your Service", serv_opt)
    # Load image
    with open("assets/ipb_icon.png", "rb") as f:
        img_data = f.read()
        img_base64 = base64.b64encode(img_data).decode()
    # Adding title web page
    st.markdown(
        f"""
        <style>
            .centered-text {{
                display: flex;
                justify-content: center;
                align-items: center;
                margin-top: -25px;
                font-size: 24px;
            }}
            .body {{
                margin-bottom: 15px;
            }}
            .title-container {{
                display: flex;
                justify-content: center;
                align-items: center;
            }}
        </style>
        <div class='centered-text body'>
            <div class='title-container'>
                <img src="data:image/png;base64,{img_base64}" alt="Emoticon" width='90'>
                <h1 style='text-align:center; margin-bottom:10px;'>KARHUTLA Text Sentiment</h1>
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )
    if services == "Document Uploader":
        # Set subheader web page
        st.write("#### Document Uploader")

        # Define function to extract pdf file format
        def extract_pdf_format(pdf_bytes):
            pdf_text = ""
            pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_bytes))
            for page in pdf_reader.pages:
                pdf_text += page.extract_text()
            return pdf_text

        # Define function to extract docx file format
        def extract_docx_format(docx_bytes):
            docx = Document(BytesIO(docx_bytes))
            docx_text = []
            for paragraph in docx.paragraphs:
                docx_text.append(paragraph.text)
            return "\n".join(docx_text)
            # Define function to generate wordcloud

        def get_wordcloud(text):
            wordcloud = WordCloud(
                width=1700, height=550, background_color="white"
            ).generate(text)
            plt.figure(figsize=(30, 20), facecolor="k")
            plt.imshow(wordcloud, interpolation="bilinear")
            plt.axis("off")
            st.pyplot(plt)

        # Define function to generate sentiment labels
        def sentiment_labels(polarity):
            if polarity > 0:
                return "Positive"
            elif polarity < 0:
                return "Negative"
            else:
                return "Neutral"

        # Define function to generate text pre-processing
        def preprocess_text(text):
            content = text.split("\n")
            content_cleaned = [line.strip() for line in content if line.strip()]
            casefolding_cleaned = [line.lower() for line in content_cleaned]
            formatted_content = [word_tokenize(line) for line in casefolding_cleaned]
            stop_words = set(stopwords.words("english"))
            filtered_content = [
                [token for token in line_tokens if token.lower() not in stop_words]
                for line_tokens in formatted_content
            ]
            stemmer = PorterStemmer()
            stemmed_content = [
                [stemmer.stem(token) for token in line_tokens]
                for line_tokens in filtered_content
            ]
            return (
                content_cleaned,
                casefolding_cleaned,
                formatted_content,
                filtered_content,
                stemmed_content,
            )

        uploaded_file = st.file_uploader(
            "Upload Your Document", type=["txt", "pdf", "docx"]
        )
        if uploaded_file is not None:
            file_contents = uploaded_file.read()
            file_extension = uploaded_file.name.split(".")[-1].lower()
            if file_extension == "txt":
                # Adding title web page
                st.markdown(
                    """
                    <style>
                        .centered-text{
                            display:flex;
                            justify-content:center;
                            align-items:center;
                            margin-top:-25px;
                            font-size:24px; 
                        }
                        .title-container{
                            display:flex;
                            justify-content:center;
                        }
                    </style>
                    <div class='centered-text body'>
                        <div class='title-container'>
                            <h4 style='text-align:center; margin-top:20px;'>What are Contents Talking About?</h4>
                        </div>
                    </div>
                """,
                    unsafe_allow_html=True,
                )
                get_wordcloud(file_contents.decode("utf-8"))
                st.write("#### Text Pre-processing")
                (
                    content_cleaned,
                    casefolding_cleaned,
                    formatted_content,
                    filtered_content,
                    stemmed_content,
                ) = preprocess_text(file_contents.decode("utf-8"))

                sentiments = []
                polarities = []
                subjectivities = []

                for line in casefolding_cleaned:
                    blob = TextBlob(line)
                    sentiments.append(blob.sentiment.polarity)
                    polarities.append(blob.sentiment.polarity)
                    subjectivities.append(blob.sentiment.subjectivity)

                data = {
                    "No": range(1, len(content_cleaned) + 1),
                    "Content": content_cleaned,
                    "Content Casefolding": casefolding_cleaned,
                    "Content Tokenization": [
                        ", ".join(tokens)
                        for tokens in [
                            ["[{}]".format(token) for token in line_tokens]
                            for line_tokens in formatted_content
                        ]
                    ],
                    "Content Stopword Removal": [
                        ", ".join(tokens)
                        for tokens in [
                            ["[{}]".format(token) for token in line_tokens]
                            for line_tokens in filtered_content
                        ]
                    ],
                    "Content Stemming": [
                        ", ".join(tokens)
                        for tokens in [
                            ["[{}]".format(token) for token in line_tokens]
                            for line_tokens in stemmed_content
                        ]
                    ],
                    "Polarity": polarities,
                    "Subjectivity": subjectivities,
                }

                df = pd.DataFrame(data)
                df["No"] = range(1, len(df) + 1)
                df["Sentiment"] = df["Polarity"].apply(sentiment_labels)
                st.dataframe(df.set_index("No"), use_container_width=True)

                # Add a download button
                def download_excel(dataframe):
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                        dataframe.to_excel(writer, sheet_name="Sheet1", index=False)
                    output.seek(0)
                    return output

                st.download_button(
                    label="Download",
                    data=download_excel(df),
                    file_name="data.xlsx",
                    key="download-xlsx",
                )
            elif file_extension == "pdf":
                # Assuming 'file_contents' contains the PDF content
                pdf_text = extract_pdf_format(file_contents)
                # Adding title web page
                st.markdown(
                    """
                    <style>
                        .centered-text{
                            display:flex;
                            justify-content:center;
                            align-items:center;
                            margin-top:-25px;
                            font-size:24px; 
                        }
                        .title-container{
                            display:flex;
                            justify-content:center;
                        }
                    </style>
                    <div class='centered-text body'>
                        <div class='title-container'>
                            <h4 style='text-align:center; margin-top:20px;'>What are Contents Talking About?</h4>
                        </div>
                    </div>
                """,
                    unsafe_allow_html=True,
                )
                get_wordcloud(pdf_text)
                st.write("#### Text Pre-processing")
                (
                    content_cleaned,
                    casefolding_cleaned,
                    formatted_content,
                    filtered_content,
                    stemmed_content,
                ) = preprocess_text(pdf_text)

                sentiments = []
                polarities = []
                subjectivities = []

                for line in casefolding_cleaned:
                    blob = TextBlob(line)
                    sentiments.append(blob.sentiment.polarity)
                    polarities.append(blob.sentiment.polarity)
                    subjectivities.append(blob.sentiment.subjectivity)

                data = {
                    "No": range(1, len(content_cleaned) + 1),
                    "Content": content_cleaned,
                    "Content Casefolding": casefolding_cleaned,
                    "Content Tokenization": [
                        ", ".join(tokens)
                        for tokens in [
                            ["[{}]".format(token) for token in line_tokens]
                            for line_tokens in formatted_content
                        ]
                    ],
                    "Content Stopword Removal": [
                        ", ".join(tokens)
                        for tokens in [
                            ["[{}]".format(token) for token in line_tokens]
                            for line_tokens in filtered_content
                        ]
                    ],
                    "Content Stemming": [
                        ", ".join(tokens)
                        for tokens in [
                            ["[{}]".format(token) for token in line_tokens]
                            for line_tokens in stemmed_content
                        ]
                    ],
                    "Polarity": polarities,
                    "Subjectivity": subjectivities,
                }

                df = pd.DataFrame(data)
                df["No"] = range(1, len(df) + 1)
                df["Sentiment"] = df["Polarity"].apply(sentiment_labels)
                st.dataframe(df.set_index("No"), use_container_width=True)

                def download_excel(dataframe):
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                        dataframe.to_excel(writer, sheet_name="Sheet1", index=False)
                    output.seek(0)
                    return output

                st.download_button(
                    label="Download",
                    data=download_excel(df),
                    file_name="data.xlsx",
                    key="download-xlsx",
                )
            elif file_extension == "docx":
                # Assuming 'file_contents' contains the DOCX content
                docx_text = extract_docx_format(file_contents)
                # Adding title web page
                st.markdown(
                    """
                    <style>
                        .centered-text{
                            display:flex;
                            justify-content:center;
                            align-items:center;
                            margin-top:-25px;
                            font-size:24px; 
                        }
                        .title-container{
                            display:flex;
                            justify-content:center;
                        }
                    </style>
                    <div class='centered-text body'>
                        <div class='title-container'>
                            <h4 style='text-align:center; margin-top:20px;'>What are Contents Talking About?</h4>
                        </div>
                    </div>
                """,
                    unsafe_allow_html=True,
                )
                get_wordcloud(docx_text)
                st.write("#### Text Pre-processing")
                (
                    content_cleaned,
                    casefolding_cleaned,
                    formatted_content,
                    filtered_content,
                    stemmed_content,
                ) = preprocess_text(docx_text)

                sentiments = []
                polarities = []
                subjectivities = []

                for line in casefolding_cleaned:
                    blob = TextBlob(line)
                    sentiments.append(blob.sentiment.polarity)
                    polarities.append(blob.sentiment.polarity)
                    subjectivities.append(blob.sentiment.subjectivity)

                data = {
                    "No": range(1, len(content_cleaned) + 1),
                    "Content": content_cleaned,
                    "Content Casefolding": casefolding_cleaned,
                    "Content Tokenization": [
                        ", ".join(tokens)
                        for tokens in [
                            ["[{}]".format(token) for token in line_tokens]
                            for line_tokens in formatted_content
                        ]
                    ],
                    "Content Stopword Removal": [
                        ", ".join(tokens)
                        for tokens in [
                            ["[{}]".format(token) for token in line_tokens]
                            for line_tokens in filtered_content
                        ]
                    ],
                    "Content Stemming": [
                        ", ".join(tokens)
                        for tokens in [
                            ["[{}]".format(token) for token in line_tokens]
                            for line_tokens in stemmed_content
                        ]
                    ],
                    "Polarity": polarities,
                    "Subjectivity": subjectivities,
                }

                df = pd.DataFrame(data)
                df["No"] = range(1, len(df) + 1)
                df["Sentiment"] = df["Polarity"].apply(sentiment_labels)
                st.dataframe(df.set_index("No"), use_container_width=True)

                def download_excel(dataframe):
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                        dataframe.to_excel(writer, sheet_name="Sheet1", index=False)
                    output.seek(0)
                    return output

                st.download_button(
                    label="Download",
                    data=download_excel(df),
                    file_name="data.xlsx",
                    key="download-xlsx",
                )
            else:
                st.warning(
                    "Unsupported file format. Please upload a .txt, .pdf, or .docx file."
                )
    else:
        # Set web page subheader
        st.write("#### Text Sentiment")

        # Define function to translate
        def translate_text(input_text, source_lang, target_lang):
            if source_lang != "en":
                translator = Translator()
                translated_text = translator.translate(
                    input_text, src=source_lang, dest=target_lang
                ).text
            else:
                translated_text = input_text
            return translated_text

        # Define function to analyze sentiment using VADER
        def analyze_sentiment_vader(text):
            analyzer = SentimentIntensityAnalyzer()
            sentiment_scores = analyzer.polarity_scores(text)
            compound_score = sentiment_scores["compound"]

            if compound_score >= 0.05:
                sentiment = "Positive 🙂"
            elif compound_score <= -0.05:
                sentiment = "Negative 😠"
            else:
                sentiment = "Neutral 😐"

            return sentiment, compound_score

        # Setup source and destination languages
        source_lang = "auto"
        target_lang = "en"

        # Get user input
        input_text = st.text_area("Input Text Here", key="text_sentiment")

        if st.button("Analyze"):
            if input_text:
                translated_text = translate_text(
                    input_text, source_lang, target_lang
                ).capitalize()
                vader_sentiment, sentiment_score = analyze_sentiment_vader(
                    translated_text
                )

                st.write("#### Result")
                st.write(f"##### Sentiment: {vader_sentiment}")
                st.write(f"##### Compound Score: {sentiment_score:.2%}")
            else:
                st.write("Please enter some text for analysis.")


if __name__ == "__main__":
    get_text_analyzer()
