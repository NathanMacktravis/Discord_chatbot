# Discord Multi-Intent Chatbot

This project is a multi-intent chatbot designed to operate within a Discord server. The bot can respond to user queries related to movies, weather, or general questions using different APIs and machine learning models.

## Features

- **Movie Information:** The bot can provide detailed information about movies, including summaries, ratings, and posters. It uses the TMDB API to fetch movie data and a custom Wit.ai model to detect movie-related intents from user messages.

- **Weather Information:** The bot can provide weather updates based on user queries. It uses a custom Wit.ai model for intent detection and a weather API for fetching current weather conditions.

- **General Chatbot Responses:** For queries that are not related to movies or weather, the bot uses OpenAI's GPT model to generate relevant responses. This feature allows the bot to handle a wide range of conversational topics.

- **Intent Detection:** The bot uses Wit.ai to determine the intent behind user messages, categorizing them as movie-related, weather-related, or general chat.

## Technologies Used

- **Discord.py:** A Python library for interacting with the Discord API, allowing the bot to listen to messages, send responses, and interact with users in real-time.

- **Wit.ai:** A natural language processing service used to detect user intents. Two separate Wit.ai models are used in this project: one for movie-related queries and another for weather-related queries.

- **TMDB API:** The Movie Database (TMDB) API is used to fetch movie details such as summaries, ratings, and posters based on the movie names detected in user queries.

- **Weather API:** This API is used to retrieve current weather data based on the user's input, allowing the bot to provide up-to-date weather information.

- **OpenAI GPT:** OpenAI's GPT model is used for generating responses to queries that do not fall under the movie or weather categories, enabling the bot to handle a wide range of conversational topics.

## Key Files

- **`app.py`:** The main script containing the bot's logic, including intent detection, response generation, and Discord client setup.
- **`weather_chatbot.py`:** Contains the logic for fetching and processing weather data.
- **`GPT_bot.py`:** Handles the interaction with the OpenAI GPT model for generating responses to general queries.
- **`movie_chatbot.py`:** Manages movie-related queries, including API calls to TMDB and poster retrieval.

---

This project is designed to be extensible, allowing for the addition of new intents and functionalities as needed. It leverages the power of natural language processing and various APIs to provide users with a seamless conversational experience within Discord.
