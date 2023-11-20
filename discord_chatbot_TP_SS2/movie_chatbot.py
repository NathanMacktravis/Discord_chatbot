# Import the necessary libraries
import requests
from wit import Wit
from io import BytesIO
from autocorrect import Speller



# Token of the API
TMDB_api_key = "9cbc4d8610399f5e4c023fe8a815716c"

# token of the movie bot
#wit_key = "KRRG2KRS6VANQSMMR4GGQVTVEQF3VZIY" #(old)

wit_key = "NATY7CEUZZMENAHA5VTJ2ACTYU4TBXEG" #(new)@
# Discord token
discord_key = "MTE3NDMzNjkwODk3Mzg0MjQ2NA.Gi4UzX.N3YyXMtowF8azl7aSJEZHonPoKPMktJFmaTPHE"

"""# Intents of discord
intents = Intents.default()
intents.message_content = True"""

# Initialization of the wit model
wit_client = Wit(wit_key)

"""# Function to autocorrect user message
def autocorrect_user_input(usr_input):
    spell = Speller()
    return spell(usr_input)
"""

# Function to extract name of the movie in the user message
def extract_movie_names(user_message):
    # user_message = autocorrect_user_input(user_message)
    entity_names = ['movie:movie', 'movieName:movieName']
    nlp_data = wit_client.message(user_message)
    print(nlp_data)
    entities = nlp_data.get('entities', {})
    movie_names = []

    for entity_name in entity_names:
        if entity_name in entities:
            entity_list = entities[entity_name]

            for entity in entity_list:
                confidence = entity.get('confidence', 0)

                if confidence >= 0.4:
                    movie_names.append(entity['value'])

    return movie_names



# Function to get director name from movie ID
def get_director(movie_id):
    tmdb_url = f'https://api.themoviedb.org/3/movie/{movie_id}/credits'
    tmdb_params = {'api_key': TMDB_api_key}
    tmdb_response = requests.get(tmdb_url, params=tmdb_params).json()

    crew = tmdb_response.get('crew', [])
    directors = [member.get('name', 'Unknown') for member in crew if member.get('job') == 'Director']

    return directors


# Function to get genre name from genre ID
def get_genre_name(genre_id):
    tmdb_url = f'https://api.themoviedb.org/3/genre/movie/list'
    tmdb_params = {'api_key': TMDB_api_key}
    tmdb_response = requests.get(tmdb_url, params=tmdb_params).json()

    genres = tmdb_response.get('genres', [])
    genre_names = [genre.get('name', 'Unknown') for genre in genres if genre.get('id') == genre_id]

    return genre_names[0] if genre_names else 'Unknown'



# Function to get movie poster from TMDb API
def get_movie_poster(movie_id):
    tmdb_url = f'https://api.themoviedb.org/3/movie/{movie_id}'
    tmdb_params = {'api_key': TMDB_api_key}
    tmdb_response = requests.get(tmdb_url, params=tmdb_params).json()

    # Use movie specific answer
    poster_path = tmdb_response.get('poster_path')

    if poster_path:
        # Build full movie poster URL
        poster_url = f'https://image.tmdb.org/t/p/original{poster_path}'

        # Download image
        response = requests.get(poster_url)
        poster_image = BytesIO(response.content)

        return poster_image

    return None


def movie_infos(movie_names):
    # List to store answers for each movie
    responses = []
    posters = []

    for movie_name in movie_names:
        # Use TMDB to get movie information
        tmdb_url = f'https://api.themoviedb.org/3/search/movie'
        tmdb_params = {'api_key': TMDB_api_key, 'query': movie_name}
        tmdb_response = requests.get(tmdb_url, params=tmdb_params).json()

        # Retrieving information about the first result (the most likely movie)
        if 'results' in tmdb_response and tmdb_response['results']:
            result = tmdb_response['results'][0]
            title = result.get('title', 'Unknown')
            overview = result.get('overview', 'No overview available')
            release_date = result.get('release_date', 'Unknown')
            genres = result.get('genre_ids', [])
            director = get_director(result.get('id'))

            # Convert genders from their ID to their name
            genre_names = [get_genre_name(genre_id) for genre_id in genres]

            # The function response
            res = f"* {title} is a {', '.join(genre_names)} movie released in {release_date} and directed by {', '.join(director)}."
            res += f"\nThe overview is: {overview}\n"

            responses.append(res)
            poster = get_movie_poster(result.get('id'))
            posters.append(poster)
        else:
            responses.append(f"No information found for {movie_name}.")
            posters.append(None)

    return responses, posters


