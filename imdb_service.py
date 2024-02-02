import requests

def get_omdb_rating(movie_title):
    api_key = "8338ec7b"
    search_url = "https://www.omdbapi.com/"

    # Отправляем GET-запрос на поиск фильма
    response = requests.get(search_url, params={"apikey": api_key, "t": movie_title})

    if response.status_code == 200:
        data = response.json()
        if data["Response"] == "True":
            rating = data["imdbRating"]
            return rating

    return None
