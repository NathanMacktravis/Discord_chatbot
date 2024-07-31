# Import the necessary libraries to preprocesses the input of the user

import requests
import re
import spacy  # To extract city name from text
from nltk.corpus import wordnet
from autocorrect import Speller  # To correct the input of the user
from datetime import datetime
from timezonefinder import TimezoneFinder  # To obtain the time of a city in function of the coordonates
import pytz  # To convert the current time using the obtained timezone
from geopy.geocoders import Nominatim


# Function to autocorrect user input
def autocorrect_user_input(usr_input):
    spell = Speller()
    return spell(usr_input)


# We define a function to built our list of keywords from intent
def get_keywords(word):
    list_syn = {}
    # for word in list_words:
    synonyms = []
    for syn in wordnet.synsets(word):
        for lem in syn.lemmas():
            # Remove any special characters from synonym strings
            lem_name = re.sub('[^a-zA-Z0-9 \n\.]', ' ', lem.name())
            synonyms.append(lem_name)
    list_syn[word] = set(synonyms)
    return list_syn


# We built a function to have the keywords dictionary with synonyms of keywords formatted with RegEx metacharacters
def get_intent_keyword(list_intents):
    # Building dictionary of Intents & Keywords
    keywords = {}
    keywords_dict = {}
    for word in list_intents:
        # Defining a new key in the keywords dictionary
        keywords[word] = []

        # Populating the values in the keywords dictionary with synonyms of keywords formatted with RegEx metacharacters
        for synonym in list(get_keywords(word)[word]):
            keywords[word].append('.*\\b' + synonym + '\\b.*')

    # We get our intents
    for intent, keys in keywords.items():
        # Joining the values in the keywords dictionary with the OR (|) operator updating them in keywords_dict dictionary
        keywords_dict[intent] = re.compile('|'.join(keys))

    return keywords_dict


# Function to give the local city of the user
def get_city_from_ip():
    try:
        response = requests.get('https://ipinfo.io')  # Using of a request https to have our city
        data = response.json()
        return data.get('city')
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


# Function to extract city name from text
nlp = spacy.load("en_core_web_sm")


def extract_city_from_text(text):
    doc = nlp(text)
    cities = [entity.text for entity in doc.ents if entity.label_ == "GPE"]
    return cities


# Function to get coords from city name
def get_coords_from_city(city_name):
    geolocator = Nominatim(user_agent="geoapiExercises")
    location = geolocator.geocode(city_name)
    if location:
        return location.latitude, location.longitude
    else:
        print("Coordinates not found for the given city.")
        return None, None


# Function to get coords from city extracted in the text
def get_city_coords_from_text(input_text):
    extracted_city_list = extract_city_from_text(input_text)
    coords_list = []
    for city in extracted_city_list:
        coords_list.append(get_coords_from_city(city))
    return coords_list


# Function to get the weather of the city
def get_weather_info(lat, lon, hourly=True):
    try:
        # We define a condition if we want hourly data
        if hourly:
            url = f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,weather_code'
        # If we want daily data
        else:
            url = f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,weather_code&timezone=Europe/Paris'

        # We make a GET request to the URL and save it as json()
        response = requests.get(url)
        data = response.json()

        if hourly:
            return data["hourly"]  # For hourly data
        else:
            return data["daily"]  # For daily data
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


# Function to get weather code
def get_weather_type(weather_code):
    weather_mapping = {
        0: 'Clear sky',
        (1, 2, 3): 'Cloud',
        (45, 48): 'Fog',
        (51, 53, 55): 'Drizzle',
        (56, 57): 'Freezing Drizzle',
        (61, 63, 65): 'Rain',
        (66, 67): 'Freezing Rain',
        (71, 73, 75): 'Snow fall',
        77: 'Snow grains',
        (80, 81, 82): 'Rain showers',
        (85, 86): 'Snow showers',
        95: 'Thunderstorm',
        (96, 99): 'Thunderstorm with slight and heavy hail'
    }

    for key, value in weather_mapping.items():
        if isinstance(key, int):
            if weather_code == key:
                return value
        elif isinstance(key, tuple):
            if weather_code in key:
                return value

    return 'Unknown weather type'


# We create a regex function to have a hour index
def get_hour_index(text):
    regex_pattern = r'\b(?:[1-9]|1[0-2])\s*[ap](?:m)?\b'

    match = re.search(regex_pattern, text, re.IGNORECASE)

    if match:
        matched_text = match.group(0).lower()
        # Extract the numeric hour from the matched text
        numeric_hour_match = re.search(r'(?:[1-9]|1[0-9]|20)', matched_text)
        if numeric_hour_match:
            numeric_hour_text = numeric_hour_match.group(0).lower()
            return matched_text, int(numeric_hour_text)

    # Return -1 if no match is found
    return None, -1


# Function to get the index of the day

def get_day_index(text):
    regex_pattern = r'\b(?:today|tomorrow|day(?:\safter)?\stomorrow|(?:[1-7]|one|two|three|four|five|six|seven)\s*day)\b'

    match = re.search(regex_pattern, text, re.IGNORECASE)

    if match:
        matched_text = match.group(0).lower()
        if "today" in matched_text:
            return matched_text, 0
        elif "day after tomorrow" in matched_text:
            return matched_text, 2
        elif "tomorrow" in matched_text:
            return matched_text, 1
        else:
            # Extract the numeric day from the matched text
            numeric_day_match = re.search(r'\b(?:[1-7]|one|two|three|four|five|six|seven)\b', matched_text,
                                          re.IGNORECASE)
            if numeric_day_match:
                numeric_day_text = numeric_day_match.group(0).lower()
                try:
                    # Try to convert to an integer
                    numeric_day = int(numeric_day_text)
                    # Check if the integer is within the specified range
                    if numeric_day in [1, 2, 3, 4, 5, 6, 7]:
                        return matched_text, numeric_day
                except ValueError:
                    pass
                numeric_mapping = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6, 'seven': 7}
                return matched_text, numeric_mapping[numeric_day_text]

    # Return -1 if no match is found
    return None, -1


# A function to have the time of city
def get_gmt_time(latitude, longitude):
    try:
        # Get the timezone from the geographical coordinates
        tf = TimezoneFinder()
        timezone_str = tf.timezone_at(lat=latitude, lng=longitude)

        if timezone_str:
            # Convert the current time using the obtained timezone
            local_time = datetime.now(pytz.timezone(timezone_str))

            # Convert local time to GMT
            gmt_time = local_time.astimezone(pytz.timezone("GMT"))

            return gmt_time.strftime("%Y-%m-%d %H:%M:%S GMT")
        else:
            return "Unable to determine the timezone."
    except Exception as e:
        return f"An error occurred: {e}"


# We define a function to have a comment of the weather

def comment_temperature(temperature):
    if temperature <= 10:
        return "It's sooooo cold, put a jacket on 🥶"
    elif temperature >= 10 and temperature <= 20:
        return "It's temperate 😉"
    elif temperature >= 20:
        return "It's hot, time to party 😎"
    else:
        return "Error 404, no temperature 😑"


# We Built a dictionary of responses
responses_chatbot = {
    'hello': "Hello, I'm a wheather chatbot! How can I help you?",
    'time': 'The time ',
    'weather': 'The weather in',
    'love': 'For sure, we love that !',
    'fallback': 'I dont quite understand. Could you repeat that?',
}




# Function to get a weather response about a weather
def response_for_weather(key, user_input, hourly):
    # If it's a keyword weather matches, the fallback intent is replaced by the matched intent as the key for the responses dictionary
    if key == 'weather':
        input_cities = extract_city_from_text(user_input)
        if input_cities:
            city_coords = get_coords_from_city(input_cities[0])
            city = input_cities[0]
        else:
            city = get_city_from_ip()
            city_coords = get_coords_from_city(city)

        matched_text_hour, matched_hour_input = get_hour_index(user_input)
        matched_text_day, matched_day_input = get_day_index(user_input)

        if matched_text_day:
            hourly = False
        weather_response = get_weather_info(city_coords[0], city_coords[1], hourly=hourly)

        if matched_text_day:
            temperature = weather_response["temperature_2m_max"][matched_day_input]
            weather_code = weather_response["weather_code"][matched_day_input]

        elif matched_text_hour:
            temperature = weather_response["temperature_2m"][matched_hour_input]
            weather_code = weather_response["weather_code"][matched_hour_input]

        else:
            temperature = weather_response["temperature_2m"][0]
            weather_code = weather_response["weather_code"][0]
        weather_message = get_weather_type(weather_code)
        res = responses_chatbot['weather'] + " " + city
        if matched_text_hour:
            res += " at " + matched_text_hour + " will be "
        elif matched_text_day:
            if matched_text_day not in ["today", "tomorrow", "day after tomorrow"]:
                res += " in"
            res += " " + matched_text_day + " will be "
        else:
            res += " is "
        res += str(temperature) + " °C, " + "with " + weather_message + ". " + comment_temperature(temperature)

    return res


# Function to get a time response about a weather
def response_for_time(key, user_input, hourly):
    # If it's a keyword time, the fallback intent is replaced by the matched intent as the key for the responses dictionary
    if key == 'time':
        input_cities = extract_city_from_text(user_input)
        if input_cities:
            city_coords = get_coords_from_city(input_cities[0])
            city = input_cities[0]
        else:
            city = get_city_from_ip()
            city_coords = get_coords_from_city(city)
        res = responses_chatbot['time'] + " in " + city + " is " + get_gmt_time(city_coords[0], city_coords[1])

    return res



# we define the main_chatbot function (match_pattern function)
def main_chatbot_weather(input_message):
    hourly = True
    main_intent = ['hello', 'time', 'greetings', 'love', 'color', 'happy', 'weather']

    # Takes the user input and converts all characters to lowercase
    user_input = autocorrect_user_input(input_message.lower())
    matched_intent = None

    for intent, pattern in get_intent_keyword(main_intent).items():
        # Using the regular expression search function to look for keywords in user input
        if re.search(pattern, user_input):
            # if a keyword matches, select the corresponding intent from the keywords_dict dictionary
            matched_intent = intent
    # The fallback intent is selected by default
    key = 'fallback'

    if matched_intent in responses_chatbot:
        # If a keyword matches, the fallback intent is replaced by the matched intent as the key for the responses dictionary
        key = matched_intent

    if key == 'weather':

        return response_for_weather(key, user_input, hourly)


    elif key == 'time':
        return response_for_time(key, user_input, hourly)

    else:
        # The chatbot prints the response that matches the selected intent
        return responses_chatbot[key]
