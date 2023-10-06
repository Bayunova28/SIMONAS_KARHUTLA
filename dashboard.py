# Import library
import streamlit as st
import datetime
from wordcloud import WordCloud
import pandas as pd
import re
from PIL import Image
import matplotlib.pyplot as plt
import plotly.express as px
import base64
import plotly.graph_objects as go

st.cache_data
# Define function to generate dashboard
def get_dashboard():
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
                <h1 style='text-align:center; margin-bottom:10px;'>KARHUTLA: Sentiment Analysis Dashboard</h1>
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )
    # Display the web apps
    df = pd.read_excel("datasets/contextual_mark.xlsx", sheet_name="Sheet1")
    df = df[df["is_contextual"] == True].reset_index().drop("index", axis=1)
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
    body1, body2, body3 = st.columns(3)
    with body1:
        st.markdown(
            "<div style='margin-top: 20px; border: 1px; border-radius: 5px; padding: 10px; background-color: #00FFFF;'>"
            "<h4 style='text-align: center; font-weight: bold;'>No of Dataset</h4>"
            "</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<div style='border: 1px; border-radius: 5px; padding: 40px; background-color: #ADD8E6;'>"
            f"<h2 style='text-align: center; padding-top: 25px; color: #0000FF; height: 105px; font-weight: bold;'>{filtered_df.shape[0]:,}</h2>"
            "</div>",
            unsafe_allow_html=True,
        )
    with body2:
        st.markdown(
            "<div style='margin-top: 20px; border: 1px; border-radius: 5px; padding: 10px; background-color: #FF69B4;'>"
            "<h4 style='text-align: center; font-weight: bold;'>Overall Sentiments</h4>"
            "</div>",
            unsafe_allow_html=True,
        )

        # Define function to display emoticon in sentiment labels
        def display_emoticon_stats(
            emoticon_path, sentiment_label, bg_color, sentiment, filtered_df, df
        ):
            with open(emoticon_path, "rb") as f:
                img_data = f.read()
                img_base64 = base64.b64encode(img_data).decode()

            sentiment_count = filtered_df[filtered_df["Sentiment"] == sentiment].shape[
                0
            ]
            all_sentiment = filtered_df.shape[0]

            if all_sentiment > 0:
                sentiment_percentage = (sentiment_count / all_sentiment) * 100
            else:
                sentiment_percentage = 0.00

            st.markdown(
                f"<div style='background-color: #{bg_color}; border-radius: 5px;'>"
                f"<div style='{border_box_style}'>"
                f"<img src='data:image/png;base64,{img_base64}' width='90'>"
                f"<div style='display: flex; flex-direction: column; align-items: center;'>"
                f"<h4>{sentiment_label}</h4>"
                f"<h4 style='margin-top: -26px; padding-left: 10px;'>{sentiment_percentage:.2f}%</h4>"
                "</div>"
                "</div>"
                "</div>",
                unsafe_allow_html=True,
            )

        emoticon1, emoticon2, emoticon3 = st.columns(3)
        border_box_style = "border: 1px; padding: 10px; text-align: center; margin-top: 5px; height: 180px;"
        with emoticon1:
            display_emoticon_stats(
                "assets/smile.png", "Positive", "CCFB5D", "positive", filtered_df, df
            )
        with emoticon2:
            display_emoticon_stats(
                "assets/neutral.png", "Neutral", "E5E4E2", "neutral", filtered_df, df
            )
        with emoticon3:
            display_emoticon_stats(
                "assets/sad.png", "Negative", "FF8674", "negative", filtered_df, df
            )
    with body3:
        st.markdown(
            "<div style='margin-top: 20px; border: 1px; border-radius: 5px; padding: 10px; background-color: #FFE87C;'>"
            "<h4 style='text-align: center; font-weight: bold;'>Mentions</h4>"
            "</div>",
            unsafe_allow_html=True,
        )

        # Extract hashtags from tweets
        def extract_hashtags(tweet):
            hashtags = re.findall(r"#\w+", tweet)
            return hashtags

        filtered_df["Hashtags"] = filtered_df["Tweet"].apply(extract_hashtags)
        # Create a new DataFrame with hashtag data
        hashtag_data = []
        for index, row in filtered_df.iterrows():
            for hashtag in row["Hashtags"]:
                hashtag_data.append({"Tweet": row["Tweet"], "Hashtag": hashtag})
        df_hashtags = pd.DataFrame(hashtag_data)
        # Replace values
        df_hashtags[df_hashtags["Hashtag"] == "#saveindonesia"] = "#saveriau"
        # Group by hashtag and sum mentions
        df_hashtag_mentions = (
            df_hashtags.groupby("Hashtag")["Tweet"].count().reset_index()
        )
        df_hashtag_mentions.rename(columns={"Tweet": "Mentions"}, inplace=True)
        # Select top 7 hashtags
        df_top_hashtags = df_hashtag_mentions.nlargest(5, "Mentions")
        # Shorten hashtag names for legend
        hashtag_names_short = [
            tag[:15] + "..." if len(tag) > 18 else tag
            for tag in df_top_hashtags["Hashtag"]
        ]
        # Create the pie chart
        fig = px.pie(
            df_top_hashtags,
            values="Mentions",
            names=hashtag_names_short,
            hover_data=["Mentions"],
            labels={"Mentions": "Total Mentions"},
        )
        # Adjusting the size of the pie chart (layout)
        fig.update_layout(
            height=265,  # This makes the chart responsive
            margin=dict(t=10),
            legend={
                "font": {"size": 15},
                "title": {"text": "Hashtags", "font": {"size": 20}},
            },
            font=dict(size=15),
            hoverlabel=dict(font_size=15),
        )
        st.plotly_chart(fig, use_container_width=True)
    # Adding chart title
    st.markdown(
        "<div style='margin-top: -65px; margin-bottom: 10px; border: 1px; border-radius: 5px; padding: 5px; background-color: #FFFDD0;'>"
        "<h4 style='text-align: center; font-weight: bold;'>What are people talking about?</h4>"
        "</div>",
        unsafe_allow_html=True,
    )

    # Define function to generate wordcloud
    def get_wordcloud(text):
        wordcloud = WordCloud(
            width=1700,
            height=550,
            background_color="white",
            regexp=r"\B#\w*[a-zA-Z]+\w*",
        ).generate(text)
        plt.figure(figsize=(30, 20), facecolor="k")
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        st.pyplot(plt)

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
    get_wordcloud(total_hashtags)
    # Adding chart title
    st.markdown(
        "<div style='margin-top: 20px; margin-bottom: 10px; border: 1px; border-radius: 5px; padding: 5px; background-color: #00FFFF;'>"
        "<h4 style='text-align: center; font-weight: bold;'>Sentiment by Features</h4>"
        "</div>",
        unsafe_allow_html=True,
    )
    # Calculate sentiment counts based on the original DataFrame
    sentiment_counts = filtered_df["Sentiment"].value_counts(ascending=False)

    # Create a list to store DataFrames for each sentiment category
    dfs_per_sentiment = []

    # Group the DataFrame by sentiment and select top 10 tweets for each sentiment
    for sentiment in sentiment_counts.index:
        top_tweets = filtered_df[filtered_df["Sentiment"] == sentiment].nlargest(
            10, "Hashtags Count"
        )
        dfs_per_sentiment.append(top_tweets)

    # Concatenate the DataFrames
    top_tweets_per_sentiment = pd.concat(dfs_per_sentiment)

    # Abbreviate long tweet content for better visualization
    max_tweet_length = 20
    top_tweets_per_sentiment["Abbreviated Hashtags"] = [
        " ".join(re.findall(r"#\w+", tweet))[:max_tweet_length] + "..."
        if len(" ".join(re.findall(r"#\w+", tweet))) > max_tweet_length
        else " ".join(re.findall(r"#\w+", tweet))
        for tweet in top_tweets_per_sentiment["Tweet"]
    ]

    # Create a horizontal stacked bar chart for sentiment counts
    sentiment_colors = {
        "positive": "#CCFB5D",
        "neutral": "#E5E4E2",
        "negative": "#FF8674",
    }
    fig = go.Figure()

    for sentiment, color in sentiment_colors.items():
        filtered_sentiment = top_tweets_per_sentiment[
            top_tweets_per_sentiment["Sentiment"] == sentiment
        ]
        trace = go.Bar(
            y=filtered_sentiment["Abbreviated Hashtags"],
            x=filtered_sentiment["Hashtags Count"].sort_values(ascending=True),
            name=sentiment.capitalize(),
            orientation="h",
            marker=dict(color=color),
        )
        fig.add_trace(trace)

    # Create layout for the figure
    fig.update_layout(
        barmode="stack",
        margin=dict(t=10),
        height=650,
        legend={
            "font": {"size": 15},
            "title": {"text": "Sentiment", "font": {"size": 20}},
        },
        xaxis={
            "tickfont": {"size": 15},
            "title": {"text": "No of Records", "font": {"size": 20}},
        },
        yaxis={
            "tickfont": {"size": 15},
            "title": {"text": "Aspect", "font": {"size": 20}},
        },
    )

    # Streamlit UI
    st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    get_dashboard()
