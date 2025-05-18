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

# inlocuiesc cu cealalta functie ca sa imi poata afisa si celelalte pagini
# def cauta_filme_tmdb(query):
#     url = 'https://api.themoviedb.org/3/search/movie'
#     params = {
#         'api_key': '7c4f52f7a9bfd765ee2774bb2c1ca19c',
#         'query': query,
#         'language': 'ro-RO'
#     }
#     response = requests.get(url, params=params)
#     if response.status_code == 200:
#         return response.json().get('results', [])
#     return []

def cauta_filme_tmdb(query, pagina=1):
    url = 'https://api.themoviedb.org/3/search/movie'
    params = {
        'api_key': settings.TMDB_API_KEY,
        'query': query,
        'language': 'ro-RO',
        'page': pagina
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return {
            'filme': data.get('results', []),
            'pagina_curenta': data.get('page', 1),
            'total_pagini': data.get('total_pages', 1)
        }
    return {'filme': [], 'pagina_curenta': 1, 'total_pagini': 1}


def get_video_film(film_id):
    url = f"https://api.themoviedb.org/3/movie/{film_id}/videos?api_key={settings.TMDB_API_KEY}&language=en-US"
    response = requests.get(url)
    if response.status_code == 200:
        videos = response.json().get('results', [])
        for video in videos:
            if video['site'] == 'YouTube' and video['type'] == 'Trailer':
                return f"https://www.youtube.com/embed/{video['key']}"
    return None

# pentru a face filtrare dupa toate filmele si sa existe paginare
def descopera_filme_tmdb(gen=None, min_rating=None, pagina=1):
    url = 'https://api.themoviedb.org/3/discover/movie'
    params = {
        'api_key': settings.TMDB_API_KEY,
        'language': 'ro-RO',
        'sort_by': 'popularity.desc',
        'page': pagina
    }

    if gen:
        params['with_genres'] = gen
    if min_rating:
        try:
            params['vote_average.gte'] = float(min_rating)
        except ValueError:
            pass

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return {
            'filme': data.get('results', []),
            'pagina_curenta': data.get('page', 1),
            'total_pagini': data.get('total_pages', 1)
        }
    return {'filme': [], 'pagina_curenta': 1, 'total_pagini': 1}

