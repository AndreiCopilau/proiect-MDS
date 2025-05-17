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

# def cauta_filme_tmdb(query):
#     url = f"https://api.themoviedb.org/3/search/movie?api_key={settings.TMDB_API_KEY}&language=en-US&query={query}"
#     response = requests.get(url)
#     if response.status_code == 200:
#         data = response.json()
#         return data.get('results', [])
#     return []

def cauta_filme_tmdb(query):
    url = 'https://api.themoviedb.org/3/search/movie'
    params = {
        'api_key': '7c4f52f7a9bfd765ee2774bb2c1ca19c',
        'query': query,
        'language': 'ro-RO'
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get('results', [])
    return []

def get_video_film(film_id):
    url = f"https://api.themoviedb.org/3/movie/{film_id}/videos?api_key={settings.TMDB_API_KEY}&language=en-US"
    response = requests.get(url)
    if response.status_code == 200:
        videos = response.json().get('results', [])
        for video in videos:
            if video['site'] == 'YouTube' and video['type'] == 'Trailer':
                return f"https://www.youtube.com/embed/{video['key']}"
    return None
