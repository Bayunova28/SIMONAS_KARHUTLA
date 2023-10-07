# Import library
import streamlit as st
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re
import base64
from PIL import Image
import plotly.express as px

st.cache_data
# Define function to display monitoring page
def get_monitoring():
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
                <h1 style='text-align:center; margin-bottom:10px;'>KARHUTLA Monitoring</h1>
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )
    # Display the web apps
    df = pd.read_excel("datasets/contextual_mark.xlsx", sheet_name="Sheet1")
    # Sort dataset based on created at
    df = df.sort_values(by="Created At", ascending=True)
    # Get 5 character from the left
    df["Post ID"] = df["Post ID"].astype(str)
    df["Conversation ID"] = df["Conversation ID"].astype(str)
    df["User ID"] = df["User ID"].astype(str)
    df["Post ID"] = df["Post ID"].str[:5]
    df["Conversation ID"] = df["Conversation ID"].str[:5]
    df["User ID"] = df["User ID"].str[:5]
    # Find the most common tweet content
    most_common_tweet = df["Tweet"].value_counts().idxmax()
    # Replace tweets containing about "poker" with the most common tweet content
    df.loc[df["Tweet"].str.contains(r"poker", case=False), "Tweet"] = most_common_tweet
    df.loc[
        df["Tweet"].str.contains(r"gambling", case=False), "Tweet"
    ] = most_common_tweet
    df.loc[df["Tweet"].str.contains(r"judi", case=False), "Tweet"] = most_common_tweet
    df.loc[
        df["Tweet"].str.contains(r"#MalamMingguanModal100rb", case=False), "Tweet"
    ] = most_common_tweet
    df.loc[
        df["Tweet"].str.contains(r"#telegram", case=False), "Tweet"
    ] = most_common_tweet
    df.loc[df["Tweet"].str.contains(r"#memek", case=False), "Tweet"] = most_common_tweet
    df.loc[df["Tweet"].str.contains(r"#duar", case=False), "Tweet"] = most_common_tweet
    # Replace username and account name containing about "poker" with the most common tweet content
    most_common_username = df["Username"].value_counts().idxmax()
    df.loc[
        df["Username"].str.contains(r"poker", case=False), "Username"
    ] = most_common_username
    df.loc[
        df["Username"].str.contains(r"poeker", case=False), "Username"
    ] = most_common_username
    df.loc[
        df["Username"].str.contains(r"judii", case=False), "Username"
    ] = most_common_username
    df.loc[
        df["Username"].str.contains(r"vcs", case=False), "Username"
    ] = most_common_username
    df = df[df["is_contextual"] == True].reset_index().drop("index", axis=1)
    df_result = df[
        [
            "Post ID",
            "Conversation ID",
            "User ID",
            "Created At",
            "Username",
            "Account Name",
            "Tweet",
            "Mentions",
            "Photos",
            "Replies Count",
            "Retweets Count",
            "Likes Count",
            "Hashtags Count",
            "Link",
            "Sentiment",
        ]
    ]
    df_result[["Post ID", "Conversation ID", "User ID"]] = df_result[
        ["Post ID", "Conversation ID", "User ID"]
    ].astype(str)
    df_result[["Account Name", "Link"]] = df_result[["Account Name", "Link"]].fillna(
        "N/A"
    )
    df_result["Created At"] = df_result["Created At"].str.replace(
        " Tomsk Standard Time", ""
    )
    df_result["Created At"] = pd.to_datetime(
        df_result["Created At"], errors="coerce"
    ).dt.date
    # Define filter range
    filter_start_date = df_result["Created At"].min()
    filter_end_date = df_result["Created At"].max()
    # Streamlit UI
    filter1, filter2, filter3 = st.columns(3)
    with filter1:
        start_date = st.date_input(
            "Start Created At",
            value=filter_start_date,
            min_value=filter_start_date,
            max_value=filter_end_date,
        )
    with filter2:
        end_date = st.date_input(
            "End Created At",
            value=filter_end_date,
            min_value=filter_start_date,
            max_value=filter_end_date,
        )
    # Filter username based on selected date range
    username_filters = df_result[
        (df_result["Created At"] >= start_date) & (df_result["Created At"] <= end_date)
    ]["Username"].unique()
    username_filters = sorted(username_filters)
    with filter3:
        username = st.multiselect("Username", username_filters)
    # Apply filters
    filtered_df = df_result[
        (df_result["Created At"] >= start_date) & (df_result["Created At"] <= end_date)
    ]
    if username:
        filtered_df = filtered_df[filtered_df["Username"].isin(username)]
    st.write("#### Dataset")

    def get_sentiment_label(sentiment):
        if sentiment == "positive":
            return "Positive"
        elif sentiment == "negative":
            return "Negative"
        else:
            return "Neutral"

    filtered_df["Sentiment"] = filtered_df["Sentiment"].apply(get_sentiment_label)
    # Add an index column starting from 1
    filtered_df["No"] = range(1, len(filtered_df) + 1)
    st.dataframe(filtered_df.set_index("No"), use_container_width=True)

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
                            <h4 style='text-align:center; margin-top:20px;'>What are people talking about?</h4>
                        </div>
                    </div>
    """,
        unsafe_allow_html=True,
    )

    # Define function to generate wordcloud
    def generate_wordcloud(text):
        wordcloud = WordCloud(
            width=1700,
            height=550,
            background_color="white",
            regexp=r"\B#\w*[a-zA-Z]+\w*",
        ).generate(text)
        plt.figure(figsize=(30, 20), facecolor="k")
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        st.pyplot(plt, use_container_width=True)

    # Remove duplicates based on link tweet
    df_cleaned = filtered_df.drop_duplicates(subset=["Link"]).reset_index(drop=True)
    # Remove short sentences without hashtags
    df_cleaned = df_cleaned[
        df_cleaned["Tweet"].apply(lambda x: len(str(x).split()) > 5 or "#" in str(x))
    ].reset_index(drop=True)
    # Extract hashtags from tweets
    df_cleaned["hashtags_extracted"] = df_cleaned["Tweet"].apply(
        lambda x: " ".join(re.findall(r"\B#\w*[a-zA-Z]+\w*", x))
    )
    # Visualize wordcloud of sentence hashtags
    total_hashtags = " ".join(df_cleaned["hashtags_extracted"].tolist())
    generate_wordcloud(total_hashtags)

    st.write("#### Text Pre-Processing")
    st.cache_data
    df_norm = pd.read_excel("datasets/content_normalization.xlsx", sheet_name="Sheet1")
    # Rename columns
    df_norm.rename(
        columns={
            "Content_Casefolding": "Content Casefolding",
            "Content_Tokenizer": "Content Tokenization",
            "Content_PunctFiltering": "Content Filtering",
            "Content_Stopwords": "Content Stopwords Removal",
            "Content_Normalization": "Content Stemming",
        },
        inplace=True,
    )
    df_norm_result = df_norm[
        [
            "Content",
            "Content Casefolding",
            "Content Filtering",
            "Content Tokenization",
            "Content Stopwords Removal",
            "Content Stemming",
            "Sentiment",
        ]
    ]

    df_norm_result["Sentiment"] = df_norm_result["Sentiment"].apply(get_sentiment_label)
    # Find the most common tweet content
    most_common_content = df_norm_result["Content"].value_counts().idxmax()
    # Replace tweets containing about "poker" with the most common tweet content
    df_norm_result.loc[
        df_norm_result["Content"].str.contains(r"poker", case=False), "Content"
    ] = most_common_content
    df_norm_result.loc[
        df_norm_result["Content"].str.contains(r"gambling", case=False), "Content"
    ] = most_common_content
    df_norm_result.loc[
        df_norm_result["Content"].str.contains(r"judi", case=False), "Content"
    ] = most_common_content
    df_norm_result.loc[
        df_norm_result["Content"].str.contains(r"#MalamMingguanModal100rb", case=False),
        "Content",
    ] = most_common_content
    df_norm_result.loc[
        df_norm_result["Content"].str.contains(r"#telegram", case=False), "Content"
    ] = most_common_content
    # Find the most common tweet content casefolding
    most_common_content_case = (
        df_norm_result["Content Casefolding"].value_counts().idxmax()
    )
    # Replace tweets containing about "poker" with the most common tweet content casefolding
    df_norm_result.loc[
        df_norm_result["Content Casefolding"].str.contains(r"poker", case=False),
        "Content Casefolding",
    ] = most_common_content_case
    df_norm_result.loc[
        df_norm_result["Content Casefolding"].str.contains(r"gambling", case=False),
        "Content Casefolding",
    ] = most_common_content_case
    df_norm_result.loc[
        df_norm_result["Content Casefolding"].str.contains(r"judi", case=False),
        "Content Casefolding",
    ] = most_common_content_case
    df_norm_result.loc[
        df_norm_result["Content Casefolding"].str.contains(
            r"#MalamMingguanModal100rb", case=False
        ),
        "Content Casefolding",
    ] = most_common_content_case
    df_norm_result.loc[
        df_norm_result["Content Casefolding"].str.contains(r"#telegram", case=False),
        "Content Casefolding",
    ] = most_common_content_case
    # Find the most common tweet content filtering
    most_common_content_filtering = (
        df_norm_result["Content Filtering"].value_counts().idxmax()
    )
    # Replace tweets containing about "poker" with the most common tweet content filtering
    df_norm_result.loc[
        df_norm_result["Content Filtering"].str.contains(r"poker", case=False),
        "Content Filtering",
    ] = most_common_content_filtering
    df_norm_result.loc[
        df_norm_result["Content Filtering"].str.contains(r"gambling", case=False),
        "Content Filtering",
    ] = most_common_content_filtering
    df_norm_result.loc[
        df_norm_result["Content Filtering"].str.contains(r"judi", case=False),
        "Content Filtering",
    ] = most_common_content_filtering
    df_norm_result.loc[
        df_norm_result["Content Filtering"].str.contains(
            r"#MalamMingguanModal100rb", case=False
        ),
        "Content Filtering",
    ] = most_common_content_filtering
    df_norm_result.loc[
        df_norm_result["Content Filtering"].str.contains(r"#telegram", case=False),
        "Content Filtering",
    ] = most_common_content_filtering
    # Find the most common tweet content tokenization
    most_common_content_tokenization = (
        df_norm_result["Content Tokenization"].value_counts().idxmax()
    )
    # Replace tweets containing about "poker" with the most common tweet content tokenization
    df_norm_result.loc[
        df_norm_result["Content Tokenization"].str.contains(r"poker", case=False),
        "Content Tokenization",
    ] = most_common_content_tokenization
    df_norm_result.loc[
        df_norm_result["Content Tokenization"].str.contains(r"gambling", case=False),
        "Content Tokenization",
    ] = most_common_content_tokenization
    df_norm_result.loc[
        df_norm_result["Content Tokenization"].str.contains(r"judi", case=False),
        "Content Tokenization",
    ] = most_common_content_tokenization
    df_norm_result.loc[
        df_norm_result["Content Tokenization"].str.contains(
            r"#MalamMingguanModal100rb", case=False
        ),
        "Content Tokenization",
    ] = most_common_content_tokenization
    df_norm_result.loc[
        df_norm_result["Content Tokenization"].str.contains(r"#telegram", case=False),
        "Content Tokenization",
    ] = most_common_content_tokenization
    # Find the most common tweet content stopwords removal
    most_common_content_stopwords = (
        df_norm_result["Content Stopwords Removal"].value_counts().idxmax()
    )
    # Replace tweets containing about "poker" with the most common tweet content stopwords removal
    df_norm_result.loc[
        df_norm_result["Content Stopwords Removal"].str.contains(r"poker", case=False),
        "Content Stopwords Removal",
    ] = most_common_content_stopwords
    df_norm_result.loc[
        df_norm_result["Content Stopwords Removal"].str.contains(
            r"gambling", case=False
        ),
        "Content Stopwords Removal",
    ] = most_common_content_stopwords
    df_norm_result.loc[
        df_norm_result["Content Stopwords Removal"].str.contains(r"judi", case=False),
        "Content Stopwords Removal",
    ] = most_common_content_stopwords
    df_norm_result.loc[
        df_norm_result["Content Stopwords Removal"].str.contains(
            r"#MalamMingguanModal100rb", case=False
        ),
        "Content Stopwords Removal",
    ] = most_common_content_stopwords
    df_norm_result.loc[
        df_norm_result["Content Stopwords Removal"].str.contains(
            r"#telegram", case=False
        ),
        "Content Stopwords Removal",
    ] = most_common_content_stopwords
    # Find the most common tweet content stemming
    most_common_content_stemming = (
        df_norm_result["Content Stemming"].value_counts().idxmax()
    )
    # Replace tweets containing about "poker" with the most common tweet content stemming
    df_norm_result.loc[
        df_norm_result["Content Stemming"].str.contains(r"poker", case=False),
        "Content Stemming",
    ] = most_common_content_stemming
    df_norm_result.loc[
        df_norm_result["Content Stemming"].str.contains(r"gambling", case=False),
        "Content Stemming",
    ] = most_common_content_stemming
    df_norm_result.loc[
        df_norm_result["Content Stemming"].str.contains(r"judi", case=False),
        "Content Stemming",
    ] = most_common_content_stemming
    df_norm_result.loc[
        df_norm_result["Content Stemming"].str.contains(
            r"#MalamMingguanModal100rb", case=False
        ),
        "Content Stemming",
    ] = most_common_content_stemming
    df_norm_result.loc[
        df_norm_result["Content Stemming"].str.contains(r"#telegram", case=False),
        "Content Stemming",
    ] = most_common_content_stemming

    # Add an index column starting from 1
    df_norm_result.insert(0, "No", range(1, len(df_norm_result) + 1))
    st.dataframe(df_norm_result.set_index("No"), use_container_width=True)

    # Set web page subheader
    st.write("#### Model Evaluation Comparison")
    # Set model options selection box
    model_opt = [
        "Machine Learning Conventional",
        "Machine Learning Conventional - Feature Selection (PSO)",
        "Machine Learning Conventional - Feature Selection (ALO)",
        "Machine Learning Conventional - Feature Selection (SSA)",
        "Machine Learning Conventional - Feature Selection - Transfer Function",
        "SVM - Feature Selection (SSA) - Transfer Function",
    ]
    modeling = st.selectbox("Choose Your Model", model_opt)
    # Display modeling chart
    if modeling == "Machine Learning Conventional":
        df_conventional = pd.read_excel(
            "datasets/conventional.xlsx", sheet_name="Sheet1"
        )
        df_coventional_result = df_conventional[
            [
                "model_type",
                "test_accuracy",
                "test_precision",
                "test_recall",
                "test_f1_score",
                "training_time",
            ]
        ]
        df_coventional_result = df_coventional_result.round(
            {
                "test_accuracy": 7,
                "test_precision": 7,
                "test_recall": 7,
                "test_f1_score": 7,
                "training_time": 9,
            }
        )
        df_coventional_result.rename(
            columns={
                "model_type": "Coventional Model",
                "test_accuracy": "Accuracy Score (%)",
                "test_precision": "Precision (%)",
                "test_recall": "Recall (%)",
                "test_f1_score": "F1-Score (%)",
                "training_time": "Training Time (s)",
            },
            inplace=True,
        )
        # Reshape the data for plotting
        df_melted = df_coventional_result.melt(
            id_vars="Coventional Model",
            value_vars=[
                "Accuracy Score (%)",
                "Precision (%)",
                "Recall (%)",
                "F1-Score (%)",
            ],
            var_name="metrics",
            value_name="score",
        )

        # Define manual colors for model types
        color_discrete_map = {
            "K-Nearest Neighbors": "blue",
            "Naive Bayes": "red",
            "Support Vector Machine": "RGB(127,255,0)",
        }
        # Create the bar chart using Plotly Express
        fig = px.bar(
            df_melted,
            x="metrics",
            y="score",
            color="Coventional Model",
            labels={
                "metrics": "Metrics",
                "score": "Score",
                "Conventional Model": "Model Type",
            },
            color_discrete_map=color_discrete_map,
            text=df_melted["score"].apply(lambda x: f"{x:.2%}"),
        )
        # Show the plot
        fig.update_layout(
            font=dict(size=15),
            legend={
                "font": {"size": 15},
                "title": {"text": "Conventional Model", "font": {"size": 20}},
            },
            xaxis={
                "tickfont": {"size": 15},
                "title": {"text": "Metrics", "font": {"size": 20}},
            },
            yaxis={
                "tickfont": {"size": 15},
                "title": {"text": "Score (%)", "font": {"size": 20}},
            },
        )
        st.plotly_chart(fig, use_container_width=True)
        # Add an index column starting from 1
        df_coventional_result["No"] = range(1, len(df_coventional_result) + 1)
        st.dataframe(df_coventional_result.set_index("No"), use_container_width=True)
    elif modeling == "Machine Learning Conventional - Feature Selection (PSO)":
        df_con_feature_pso = pd.read_excel(
            "datasets/conventional-pso.xlsx", sheet_name="Sheet1"
        )

        def get_model_type_label(model):
            if model == "K-Nearest Neighbors PSO":
                return "K-Nearest Neighbors - PSO"
            elif model == "Naive Bayes PSO":
                return "Naive Bayes - PSO"
            else:
                return "Support Vector Machine - PSO"

        df_con_feature_pso["model_type"] = df_con_feature_pso["model_type"].apply(
            get_model_type_label
        )
        df_con_feature_pso = df_con_feature_pso[
            [
                "model_type",
                "test_accuracy",
                "test_precision",
                "test_recall",
                "test_f1_score",
                "training_time",
            ]
        ]
        df_con_feature_pso = df_con_feature_pso.round(
            {
                "test_accuracy": 7,
                "test_precision": 7,
                "test_recall": 7,
                "test_f1_score": 7,
                "training_time": 9,
            }
        )
        df_con_feature_pso.rename(
            columns={
                "model_type": "Conventional - Feature Selection (PSO)",
                "test_accuracy": "Accuracy Score (%)",
                "test_precision": "Precision (%)",
                "test_recall": "Recall (%)",
                "test_f1_score": "F1-Score (%)",
                "training_time": "Training Time (s)",
            },
            inplace=True,
        )
        # Reshape the data for plotting
        df_melted = df_con_feature_pso.melt(
            id_vars="Conventional - Feature Selection (PSO)",
            value_vars=[
                "Accuracy Score (%)",
                "Precision (%)",
                "Recall (%)",
                "F1-Score (%)",
            ],
            var_name="metrics",
            value_name="score",
        )

        # Define manual colors for model types
        color_discrete_map_feat = {
            "K-Nearest Neighbors - PSO": "blue",
            "Naive Bayes - PSO": "red",
            "Support Vector Machine - PSO": "RGB(127,255,0)",
        }
        # Create the bar chart using Plotly Express
        fig = px.bar(
            df_melted,
            x="metrics",
            y="score",
            color="Conventional - Feature Selection (PSO)",
            labels={
                "metrics": "Metrics",
                "score": "Score",
                "Coventional - Feature Selection (PSO)": "Model Type",
            },
            color_discrete_map=color_discrete_map_feat,
            text=df_melted["score"].apply(lambda x: f"{x:.2%}"),
        )
        # Show the plot
        fig.update_layout(
            font=dict(size=15),
            legend={
                "font": {"size": 15},
                "title": {
                    "text": "Conventional - Feature Selection (PSO)",
                    "font": {"size": 20},
                },
            },
            xaxis={
                "tickfont": {"size": 15},
                "title": {"text": "Metrics", "font": {"size": 20}},
            },
            yaxis={
                "tickfont": {"size": 15},
                "title": {"text": "Score (%)", "font": {"size": 20}},
            },
        )
        st.plotly_chart(fig, use_container_width=True)
        # Add an index column starting from 1
        df_con_feature_pso["No"] = range(1, len(df_con_feature_pso) + 1)
        st.dataframe(df_con_feature_pso.set_index("No"), use_container_width=True)
    elif modeling == "Machine Learning Conventional - Feature Selection (ALO)":
        df_con_feature_alo = pd.read_excel(
            "datasets/conventional-alo.xlsx", sheet_name="Sheet1"
        )

        def get_model_type_label(model):
            if model == "K-Nearest Neighbors ALO":
                return "K-Nearest Neighbors - ALO"
            elif model == "Naive Bayes SSA":
                return "Naive Bayes - ALO"
            else:
                return "Support Vector Machine - ALO"

        df_con_feature_alo["model_type"] = df_con_feature_alo["model_type"].apply(
            get_model_type_label
        )
        df_con_feature_alo = df_con_feature_alo[
            [
                "model_type",
                "test_accuracy",
                "test_precision",
                "test_recall",
                "test_f1_score",
                "training_time",
            ]
        ]
        df_con_feature_alo = df_con_feature_alo.round(
            {
                "test_accuracy": 7,
                "test_precision": 7,
                "test_recall": 7,
                "test_f1_score": 7,
                "training_time": 9,
            }
        )
        df_con_feature_alo.rename(
            columns={
                "model_type": "Conventional - Feature Selection (ALO)",
                "test_accuracy": "Accuracy Score (%)",
                "test_precision": "Precision (%)",
                "test_recall": "Recall (%)",
                "test_f1_score": "F1-Score (%)",
                "training_time": "Training Time (s)",
            },
            inplace=True,
        )
        # Reshape the data for plotting
        df_melted = df_con_feature_alo.melt(
            id_vars="Conventional - Feature Selection (ALO)",
            value_vars=[
                "Accuracy Score (%)",
                "Precision (%)",
                "Recall (%)",
                "F1-Score (%)",
            ],
            var_name="metrics",
            value_name="score",
        )

        # Define manual colors for model types
        color_discrete_map_feat = {
            "K-Nearest Neighbors - ALO": "blue",
            "Naive Bayes - ALO": "red",
            "Support Vector Machine - ALO": "RGB(127,255,0)",
        }
        # Create the bar chart using Plotly Express
        fig = px.bar(
            df_melted,
            x="metrics",
            y="score",
            color="Conventional - Feature Selection (ALO)",
            labels={
                "metrics": "Metrics",
                "score": "Score",
                "Coventional - Feature Selection (ALO)": "Model Type",
            },
            color_discrete_map=color_discrete_map_feat,
            text=df_melted["score"].apply(lambda x: f"{x:.2%}"),
        )
        # Show the plot
        fig.update_layout(
            font=dict(size=15),
            legend={
                "font": {"size": 15},
                "title": {
                    "text": "Conventional - Feature Selection (ALO)",
                    "font": {"size": 20},
                },
            },
            xaxis={
                "tickfont": {"size": 15},
                "title": {"text": "Metrics", "font": {"size": 20}},
            },
            yaxis={
                "tickfont": {"size": 15},
                "title": {"text": "Score (%)", "font": {"size": 20}},
            },
        )
        st.plotly_chart(fig, use_container_width=True)
        # Add an index column starting from 1
        df_con_feature_alo["No"] = range(1, len(df_con_feature_alo) + 1)
        st.dataframe(df_con_feature_alo.set_index("No"), use_container_width=True)
    elif modeling == "Machine Learning Conventional - Feature Selection (SSA)":
        df_con_feature_ssa = pd.read_excel(
            "datasets/conventional-ssa.xlsx", sheet_name="Sheet1"
        )

        def get_model_type_label(model):
            if model == "K-Nearest Neighbors SSA":
                return "K-Nearest Neighbors - SSA"
            elif model == "Naive Bayes SSA":
                return "Naive Bayes - SSA"
            else:
                return "Support Vector Machine - SSA"

        df_con_feature_ssa["model_type"] = df_con_feature_ssa["model_type"].apply(
            get_model_type_label
        )
        df_con_feature_ssa = df_con_feature_ssa[
            [
                "model_type",
                "test_accuracy",
                "test_precision",
                "test_recall",
                "test_f1_score",
                "training_time",
            ]
        ]
        df_con_feature_ssa = df_con_feature_ssa.round(
            {
                "test_accuracy": 7,
                "test_precision": 7,
                "test_recall": 7,
                "test_f1_score": 7,
                "training_time": 9,
            }
        )
        df_con_feature_ssa.rename(
            columns={
                "model_type": "Conventional - Feature Selection (SSA)",
                "test_accuracy": "Accuracy Score (%)",
                "test_precision": "Precision (%)",
                "test_recall": "Recall (%)",
                "test_f1_score": "F1-Score (%)",
                "training_time": "Training Time (s)",
            },
            inplace=True,
        )
        # Reshape the data for plotting
        df_melted = df_con_feature_ssa.melt(
            id_vars="Conventional - Feature Selection (SSA)",
            value_vars=[
                "Accuracy Score (%)",
                "Precision (%)",
                "Recall (%)",
                "F1-Score (%)",
            ],
            var_name="metrics",
            value_name="score",
        )

        # Define manual colors for model types
        color_discrete_map_feat = {
            "K-Nearest Neighbors - SSA": "blue",
            "Naive Bayes - SSA": "red",
            "Support Vector Machine - SSA": "RGB(127,255,0)",
        }
        # Create the bar chart using Plotly Express
        fig = px.bar(
            df_melted,
            x="metrics",
            y="score",
            color="Conventional - Feature Selection (SSA)",
            labels={
                "metrics": "Metrics",
                "score": "Score",
                "Coventional - Feature Selection (ALO)": "Model Type",
            },
            color_discrete_map=color_discrete_map_feat,
            text=df_melted["score"].apply(lambda x: f"{x:.2%}"),
        )
        # Show the plot
        fig.update_layout(
            font=dict(size=15),
            legend={
                "font": {"size": 15},
                "title": {
                    "text": "Conventional - Feature Selection (SSA)",
                    "font": {"size": 20},
                },
            },
            xaxis={
                "tickfont": {"size": 15},
                "title": {"text": "Metrics", "font": {"size": 20}},
            },
            yaxis={
                "tickfont": {"size": 15},
                "title": {"text": "Score (%)", "font": {"size": 20}},
            },
        )
        st.plotly_chart(fig, use_container_width=True)
        # Add an index column starting from 1
        df_con_feature_ssa["No"] = range(1, len(df_con_feature_ssa) + 1)
        st.dataframe(df_con_feature_ssa.set_index("No"), use_container_width=True)
    elif (
        modeling
        == "Machine Learning Conventional - Feature Selection - Transfer Function"
    ):
        df_con_feature_meta1 = pd.read_excel(
            "datasets/conventional-meta1.xlsx", sheet_name="Sheet1"
        )
        df_con_feature_meta2 = pd.read_excel(
            "datasets/conventional-meta2.xlsx", sheet_name="Sheet1"
        )
        df_merged_meta = pd.concat(
            [df_con_feature_meta1, df_con_feature_meta2], ignore_index=True
        )

        def get_model_type_label(model):
            if model == "K-Nearest Neighbors SSA TF":
                return "K-Nearest Neighbors - SSA - TF"
            elif model == "Naive Bayes SSA TF":
                return "Naive Bayes - SSA - TF"
            elif model == "Support Vector Machine SSA TF":
                return "Support Vector Machine - SSA - TF"
            elif model == "Support Vector Machine PSO TF":
                return "Support Vector Machine - PSO - TF"
            else:
                return "Support Vector Machine - ALO - TF"

        df_merged_meta["model_type"] = df_merged_meta["model_type"].apply(
            get_model_type_label
        )
        df_merged_meta = df_merged_meta[
            [
                "model_type",
                "test_accuracy",
                "test_precision",
                "test_recall",
                "test_f1_score",
                "training_time",
            ]
        ]
        df_merged_meta = df_merged_meta.round(
            {
                "test_accuracy": 7,
                "test_precision": 7,
                "test_recall": 7,
                "test_f1_score": 7,
                "training_time": 9,
            }
        )
        df_merged_meta.rename(
            columns={
                "model_type": "Conventional - Feature Selection - Transfer Function",
                "test_accuracy": "Accuracy Score (%)",
                "test_precision": "Precision (%)",
                "test_recall": "Recall (%)",
                "test_f1_score": "F1-Score (%)",
                "training_time": "Training Time (s)",
            },
            inplace=True,
        )
        # Reshape the data for plotting
        df_melted = df_merged_meta.melt(
            id_vars="Conventional - Feature Selection - Transfer Function",
            value_vars=[
                "Accuracy Score (%)",
                "Precision (%)",
                "Recall (%)",
                "F1-Score (%)",
            ],
            var_name="metrics",
            value_name="score",
        )
        # Create the bar chart using Plotly Express
        fig = px.bar(
            df_melted,
            x="metrics",
            y="score",
            color="Conventional - Feature Selection - Transfer Function",
            labels={
                "metrics": "Metrics",
                "score": "Score",
                "Conventional - Feature Selection - Transfer Function": "Model Type",
            },
            text=df_melted["score"].apply(lambda x: f"{x:.2%}"),
        )
        # Show the plot
        fig.update_layout(
            font=dict(size=15),
            legend={
                "font": {"size": 15},
                "title": {
                    "text": "Conventional - Feature Selection - Transfer Function",
                    "font": {"size": 20},
                },
            },
            xaxis={
                "tickfont": {"size": 15},
                "title": {"text": "Metrics", "font": {"size": 20}},
            },
            yaxis={
                "tickfont": {"size": 15},
                "title": {"text": "Score (%)", "font": {"size": 20}},
            },
        )
        st.plotly_chart(fig, use_container_width=True)
        # Add an index column starting from 1
        df_merged_meta["No"] = range(1, len(df_merged_meta) + 1)
        st.dataframe(df_merged_meta.set_index("No"), use_container_width=True)
    else:
        df_con_feature_meta_func = pd.read_excel(
            "datasets/conventional-metaheuristic.xlsx", sheet_name="Sheet1"
        )
        df_merged_meta_func = df_con_feature_meta_func[
            ["model_type", "Tipe-TF", "Akurasi", "Fitness", "Waktu Pemrosesan (detik)"]
        ]
        df_merged_meta_func.rename(
            columns={
                "model_type": "SVM - Feature Selection (SSA) - Transfer Function",
                "Tipe-TF": "Transfer Function Type",
                "Akurasi": "Accuracy Score (%)",
                "Fitness": "Fitness (%)",
                "Waktu Pemrosesan (detik)": "Training Time (s)",
            },
            inplace=True,
        )
        # Reshape the data for plotting
        df_melted = df_merged_meta_func.melt(
            id_vars="SVM - Feature Selection (SSA) - Transfer Function",
            value_vars=["Accuracy Score (%)", "Fitness (%)"],
            var_name="metrics",
            value_name="score",
        )
        # Create the bar chart using Plotly Express
        fig = px.bar(
            df_melted,
            x="metrics",
            y="score",
            color="SVM - Feature Selection (SSA) - Transfer Function",
            labels={
                "metrics": "Metrics",
                "score": "Score",
                "SVM - Feature Selection (SSA) - Transfer Function": "Model Type",
            },
            barmode="group",
        )
        # Show the plot
        fig.update_layout(
            font=dict(size=15),
            legend={
                "font": {"size": 15},
                "title": {
                    "text": "SVM - Feature Selection (SSA) - Transfer Function",
                    "font": {"size": 20},
                },
            },
            xaxis={
                "tickfont": {"size": 15},
                "title": {"text": "Metrics", "font": {"size": 20}},
            },
            yaxis={
                "tickfont": {"size": 15},
                "title": {"text": "Score (%)", "font": {"size": 20}},
            },
        )
        st.plotly_chart(fig, use_container_width=True)
        # Add an index column starting from 1
        df_merged_meta_func["No"] = range(1, len(df_merged_meta_func) + 1)
        st.dataframe(df_merged_meta_func.set_index("No"), use_container_width=True)


if __name__ == "__main__":
    get_monitoring()
