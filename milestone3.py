import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import Counter

# Data loading and preprocessing function
@st.cache_data  # Use the new caching decorator
def load_data():
    try:
        imdb = pd.read_csv("imdb_all.csv")
        tmdb = pd.read_csv("tmdb_all.csv")
        dbpedia = pd.read_csv("dbpedia_all.csv")

        # Data cleaning
        imdb["user_review"] = imdb["user_review"].fillna("No Review")
        imdb["director"] = imdb["director"].fillna("Unknown")
        imdb["casting"] = imdb["casting"].fillna("Unknown")
        imdb = imdb[imdb["year"].notnull()].reset_index(drop=True)

        tmdb["genre"] = tmdb["genre"].fillna("Unknown")
        tmdb["budget"] = tmdb["budget"].fillna(0)
        tmdb["revenue"] = tmdb["revenue"].fillna(0)
        tmdb = tmdb[tmdb["year"].notnull()].reset_index(drop=True)

        dbpedia["aggregate value"] = dbpedia["aggregate value"].fillna("Unknown")
        dbpedia["director name"] = dbpedia["director name"].fillna("Unknown")
        dbpedia["genre"] = dbpedia["genre"].fillna("Unknown")
        dbpedia["actor name"] = dbpedia["actor name"].fillna("Unknown")
        dbpedia = dbpedia[dbpedia["year"].notnull()].reset_index(drop=True)

        return imdb, tmdb, dbpedia
    except Exception as e:
        st.error(f"An error occurred while loading and processing data: {e}")
        return None, None, None

imdb, tmdb, dbpedia = load_data()

# Page selection
st.sidebar.title("Menu")
page = st.sidebar.radio("Choose a Page", ["Home", "Search Movies", "Data Analysis", "Research Questions", "Data Description"])

if page == "Home":
    st.title("Welcome to My Movie Data Analysis APP")
    st.markdown("""
    <h2 style='text-align: center; color: black; font-size: 24px;'>Project Creator: Shuo Dai</h2>
    """, unsafe_allow_html=True)

    st.header("How to Use This App:")
    st.write("""
    This app aims to provide in-depth analysis of movie data through the following features to facilitate user interaction and data presentation:
    - **Data Analysis Page:** On this page, users can view various types of data analysis views. Select different analysis categories such as highest-grossing movies, annual movie revenue, etc., from a dropdown menu. Each selection will update the charts accordingly to display specific analysis results.
    - **Research Questions Page:** This page provides detailed explanations of the research questions and their answers, including the purpose of the project, the findings, and key insights from the research process.
    - **Search Movies Page:** Users can search for specific movies by entering a movie name. If the movie is available in the database, the app will display detailed information about the movie, including box office, director, and actors.
    - **Data Description Page:** This page provides a summary of the datasets utilized in the application. It includes information about the source of each dataset, the types of data each contains, and the methods used for data collection and preprocessing. This section is designed to give users a clear understanding of the foundational data that supports the analyses presented in the app.
    """)

    st.subheader("Main Issues and Recommendations for Improvement:")
    st.write("""
        - **Loading Time:** Due to the large size of the datasets, loading times for some charts may be long.
        - **Data Accuracy:** The data used in this application comes from varied sources, each with its own set of challenges. IMDB data is acquired through web scraping, which may be affected by changes in the website layout and result in inaccuracies. TMDB data, sourced from an API, is subject to real-time update delays and possible data inconsistencies. DBpedia information, derived from a static dataset, tends to be reliable but may not always reflect the most recent updates. Users should be cautious when making decisions based on this data and consider verifying information from additional sources.
        - **Functionality Enhancement:** Plans to introduce more data sources and analytical dimensions in the future to provide a more comprehensive analysis of the movie market.
        """)


elif page == "Data Analysis":
    st.title("Data Analysis Views")
    try:
        # Allows user to select a type of data analysis to view
        analysis_option = st.selectbox("Choose Analysis View", [
            "Highest Grossing Movies", "Annual Movie Revenue", "IMDB Rating Analysis",
            "Movie Revenue by Genre", "Budget vs Revenue", "Rating vs Revenue",
            "Director vs Revenue", "Actor vs Revenue", "IMDB User Review Word Cloud"])
        explanations = {
            "Highest Grossing Movies": "Displays the highest-grossing movies within a selected time frame, helping identify the most popular and financially successful films.",
            "Annual Movie Revenue": "Shows the total annual revenue of the film industry, allowing observation of growth trends or cyclical changes.",
            "IMDB Rating Analysis": "Provides IMDB ratings for various movies, helping users understand the general audience reception of these films.",
            "Movie Revenue by Genre": "Analyzes box office performance by different genres (e.g., action, comedy, sci-fi), showing which genres attract the most viewers.",
            "Budget vs Revenue": "Compares a movie's production budget with its box office revenue, analyzing the correlation between budget size and market performance.",
            "Rating vs Revenue": "Explores the relationship between movie ratings and box office revenue, assessing whether ratings significantly impact revenue.",
            "Director vs Revenue": "Displays revenue earned by movies directed by different directors, analyzing the market appeal and commercial success of directors.",
            "Actor vs Revenue": "Analyzes box office revenue for movies featuring different actors, assessing the potential impact of an actor's star power on revenue.",
            "IMDB User Review Word Cloud": "Generates a word cloud from keywords extracted from IMDB user reviews, visually presenting the hot topics and sentiments discussed by the audience."
        }

        # Display the explanation for the selected analysis
        if analysis_option in explanations:
            st.markdown(f"**Explanation:** {explanations[analysis_option]}")

        # Execute data analysis based on user selection
        if analysis_option == "Highest Grossing Movies":
            top_revenue = tmdb.sort_values(by="revenue", ascending=False).head(10)
            st.write(top_revenue[["title", "revenue"]])

        elif analysis_option == "Annual Movie Revenue":
            revenue_by_year = tmdb.groupby('year')['revenue'].sum()
            st.line_chart(revenue_by_year)

        elif analysis_option == "IMDB Rating Analysis":
            rate_by_year = imdb.groupby('year')['rate'].mean()
            st.line_chart(rate_by_year)

        elif analysis_option == "Movie Revenue by Genre":
            genre_revenue = tmdb.explode('genre').groupby('genre')['revenue'].sum().sort_values(ascending=False)
            st.bar_chart(genre_revenue)

        elif analysis_option == "Budget vs Revenue":
            budget_revenue = tmdb[tmdb['budget'] > 0]
            fig, ax = plt.subplots()
            ax.scatter(budget_revenue['budget'], budget_revenue['revenue'], alpha=0.5)
            ax.set_xscale('log')
            ax.set_yscale('log')
            ax.set_xlabel('Budget (Log Scale)')
            ax.set_ylabel('Revenue (Log Scale)')
            st.pyplot(fig)

        elif analysis_option == "Rating vs Revenue":
            rate_revenue = tmdb[['rate', 'revenue']].dropna()
            fig, ax = plt.subplots()
            ax.scatter(rate_revenue['rate'], rate_revenue['revenue'], alpha=0.5)
            ax.set_yscale('log')
            ax.set_xlabel('Rating')
            ax.set_ylabel('Revenue (Log Scale)')
            st.pyplot(fig)

        elif analysis_option == "Director vs Revenue":
            # Merge data from IMDB and TMDB datasets using movie titles
            combined_data = imdb[['title', 'director']].merge(tmdb[['title', 'revenue']], on='title', how='inner')
            director_revenue = combined_data.groupby('director')['revenue'].sum().sort_values(ascending=False)
            st.subheader("Director vs Revenue")
            st.bar_chart(director_revenue)

        elif analysis_option == "Actor vs Revenue":
            # Analyze revenue contribution by different actors
            combined_data = imdb[['title', 'casting']].merge(tmdb[['title', 'revenue']], on='title', how='inner')
            actor_revenue = combined_data.explode('casting').groupby('casting')['revenue'].sum().sort_values(ascending=False)
            st.bar_chart(actor_revenue)

        elif analysis_option == "IMDB User Review Word Cloud":
            # Generate a word cloud from IMDB user reviews
            user_reviews = " ".join(imdb['user_review'].dropna().tolist())
            wordcloud = WordCloud(width=800, height=400).generate(user_reviews)
            fig, ax = plt.subplots()
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis('off')
            st.pyplot(fig)
    except Exception as e:
        # Handle any exceptions by showing an error message
        st.error(f"An error occurred while processing data: {e}")


elif page == "Research Questions":
    st.title("Research Question Answers")
    # Display answers to research questions
    st.markdown("""
    **Research Questions and Their Answers:**
    1. **What did you set out to study?**
       - At the project's outset, my goal was to explore the correlation between viewership ratings, box office revenue, and discussions on social media. However, after preliminary data analysis, I realized that obtaining social media data was challenging and insufficient to support in-depth analysis.
       - Therefore, I shifted my focus to more specific and data-supported questions: Are there noticeable differences in commercial success and public acceptance among different types or genres of movies? How do factors such as director, main actors, and production costs affect a movie's overall rating and market performance?

    2. **What did you Discover/what were your conclusions?**
       - **Are there noticeable differences in commercial success and public acceptance among different movie genres?**
       - The "Movie Revenue by Genre" chart shows that action and adventure movies far outperform other genres, such as documentaries and independent films in box office revenue. However, this is not necessarily reflected in IMDb ratings, which suggests that ratings may reflect artistic value and critics' opinions more than commercial success.
       - **How do factors such as director, main actors, and production costs affect a movie's overall rating and market performance?**
       - The "Budget vs Revenue" chart clearly demonstrates that higher production budgets are usually positively correlated with higher box office revenues. Additionally, the "Director vs Revenue" and "Actor vs Revenue" charts further confirm the significant impact of well-known directors and actors' brand effects on box office success.
       - **Conclusions:**
       - These findings not only confirmed some initial assumptions but also revealed new insights, especially in terms of the relationship between the commercial success of movie genres and their ratings. Commercial success does not necessarily coincide with high ratings, which could influence producers' decisions on movie genre selection and budget allocation. Moreover, the importance of star directors and actors provides significant strategic guidance for movie marketing.

    3. **What difficulties did you have in completing the project?**
       - In this project, I faced several practical challenges. Initially, I encountered strict rate limits when retrieving data from movie database APIs, which significantly slowed down data collection. When attempting to use web scraping techniques to extract data from websites, the complex web structures and anti-scraping techniques also posed technical difficulties, often requiring adjustments to the scraping scripts due to minor changes in site structure. In terms of data processing, the inconsistency and missing values in the raw data necessitated extensive data cleaning efforts, which was not only time-consuming but also complex.

    4. **What skills did you wish you had while you were doing the project?**
       - During this movie data analysis project, I realized that enhancing certain practical skills could significantly improve the efficiency and quality of the project's outputs. Although I already used Pandas for data handling and analysis, I wished to further deepen my understanding and master its more advanced data manipulation features, such as complex data aggregation and time series analysis, to more effectively manage and interpret large datasets. Additionally, improving application development skills in Streamlit, particularly learning how to optimize data loading and enhance application responsiveness, were critical aspects of improving user experience. By enhancing these skills, I could more effectively drive project progress, enhance the depth and breadth of data analysis, and achieve higher research outcomes.

    5. **What would you do “next” to expand or augment the project?**
       - Building on the current project, I plan to expand and enhance several key aspects of the project next. First, I intend to introduce more dimensions of data, such as audience social media feedback and more detailed information on movie production backgrounds, to help us more comprehensively understand the multifaceted impacts on movie success. Next, I plan to apply machine learning techniques to predict movie commercial success, by developing more complex predictive models to analyze how different variables such as director, actors, budget, and movie genre influence box office and audience ratings. Additionally, considering the continuous growth in data volume, I will explore using more efficient data storage and processing technologies, such as cloud computing services and big data platforms, to improve the speed and efficiency of data processing. Finally, I aim to enhance the current Streamlit application by adding more interactive features and user customization options to make the application more user-friendly and better serve data presentation and user analysis needs. Through these expansions and enhancements, the project will not only offer deeper insights but also enhance its practicality and scientific value.
    """)


elif page == "Search Movies":
    st.title("Search Movies")
    # Prompt user to input a movie name
    movie_name = st.text_input("Enter a movie name:", "")
    if movie_name:
        try:
            # Filter each dataframe for entries that contain the search query in the 'title' column
            imdb_result = imdb[imdb['title'].str.contains(movie_name, case=False, na=False)]
            tmdb_result = tmdb[tmdb['title'].str.contains(movie_name, case=False, na=False)]
            dbpedia_result = dbpedia[dbpedia['title'].str.contains(movie_name, case=False, na=False)]
            
            # Check if any results were found in any of the datasets
            if not imdb_result.empty or not tmdb_result.empty or not dbpedia_result.empty:
                if not imdb_result.empty:
                    st.subheader("Information from the IMDB dataset")
                    st.dataframe(imdb_result)
                if not tmdb_result.empty:
                    st.subheader("Information from the TMDB dataset")
                    st.dataframe(tmdb_result)
                if not dbpedia_result.empty:
                    st.subheader("Information from the DBpedia dataset")
                    st.dataframe(dbpedia_result)
            else:
                # Display an error message if no data was found
                st.error("Sorry, we could not find any information about this movie. Please try searching for another movie.")
        except Exception as e:
            # Handle exceptions by showing an error message
            st.error(f"An error occurred while searching for movies: {e}")

elif page == "Data Description":
    st.title("Data Description")
    st.write("""
    **IMDb Internet Movie Database:**
    IMDb is the world's leading database of movie, TV, and celebrity information, offering a vast array of movie-related data, including ratings, user reviews, cast lists, directors, release dates, and genres. Utilizing web crawling techniques, I systematically access and crawl specific movie pages on IMDb to gather pertinent data. This involves scripting to analyze page structures and extract requisite information. With this dataset, I aim to analyze rating distributions across genres, delve into audience review sentiments, and explore the correlations between directors/actors and movie ratings. This analysis seeks to uncover the pivotal factors influencing a movie's commercial success and audience ratings.

    **TMDb API (The Movie Database API):**
    The TMDb API is a public API offering information on movies, TV shows, and celebrities. Developers can access data such as titles, synopses, ratings, cast lists, posters, and background images. Registration is required to obtain an API key for data retrieval. With comprehensive documentation and diverse endpoints, this API facilitates access to various data types. For instance, I utilize this API to retrieve movie data, which, when combined with IMDb data, enables detailed movie trend analysis and rating pattern research.

    **DBpedia:**
    Originally intending to utilize Twitter data, I switched to DBpedia, a repository of structured information extracted from Wikipedia. This dataset comprises movie titles, cast names, director names, release years, movie genres, and an 'aggregate value' column summarizing key information for each movie. Integrated with IMDb and TMDb data, this dataset enriches movie metadata, enabling comprehensive analyses such as trend insights, impact assessments of cast and crew, and genre reach studies.
    
    **Stopwords for IMDB User Review Word Cloud:**
    Stopwords are common words that are often filtered out before or after processing of natural language data. They carry little to no meaning and are usually removed to focus on meaningful words. The stopwords used for generating the IMDB user review word cloud are stored in the stopwords.txt file.
    """)


st.sidebar.info("This app uses Streamlit to display various movie data analyses.")
