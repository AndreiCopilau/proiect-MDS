import requests # type: ignore
from django.conf import settings # type: ignore

def get_filme_populare():
    url = f"https://api.themoviedb.org/3/movie/popular?api_key={settings.TMDB_API_KEY}&language=en-US&page=1"
    response = requests.get(url)
    # return response.json().get('results', [])
    if response.status_code == 200:
        data = response.json()
        return data.get('results', [])
    return []

def get_detalii_film(film_id):
    url = f"https://api.themoviedb.org/3/movie/{film_id}?api_key={settings.TMDB_API_KEY}&language=en-US"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else None