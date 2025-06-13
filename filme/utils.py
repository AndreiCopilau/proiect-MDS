import requests
from collections import Counter
from django.conf import settings

from .models import Film, ViewHistory


"""
Saves a movie from TMDB to the database if it does not already exist.
Updates genres if missing.
"""
def save_movie_tmdb_if_not_exists(film_dict):
    id_tmdb = film_dict.get('id')
    if not id_tmdb:
        return None

    movie, created = Film.objects.get_or_create(
        id_tmdb=id_tmdb,
        defaults={
            'titlu': film_dict.get('title'),
            'poster_path': film_dict.get('poster_path'),
            'genre_ids': film_dict.get('genre_ids', [])
        }
    )

    # if movie exists but has no genres, update them
    if not created and not movie.genre_ids and film_dict.get('genre_ids'):
        movie.genre_ids = film_dict['genre_ids']
        movie.save()

    return movie


"""
Fetches popular movies from TMDB and saves them in the database.
Returns the list of movies fetched.
"""
def get_popular_movies():
    url = f"https://api.themoviedb.org/3/movie/popular?api_key={settings.TMDB_API_KEY}&language=en-US&page=1"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        movies = data.get('results', [])

        for movie in movies:
            save_movie_tmdb_if_not_exists(movie)

        return movies  
    
    return []


"""
Get detailed information about a specific movie by its TMDB ID.
"""
def get_movie_details(film_id):
    url = f"https://api.themoviedb.org/3/movie/{film_id}?api_key={settings.TMDB_API_KEY}&language=en-US"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else None


"""
Search for movies on TMDB based on a query string. Save found movies in the database.
Returns a dictionary with the list of movies, current page, and total pages.
"""
def search_movies_tmdb(query, page=1):
    url = 'https://api.themoviedb.org/3/search/movie'
    params = {
        'api_key': settings.TMDB_API_KEY,
        'query': query,
        'language': 'ro-RO',
        'page': page
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        movies = data.get('results', [])

        # save movies in DB
        for movie in movies:
            save_movie_tmdb_if_not_exists(movie)

        return {
            'movies': data.get('results', []),
            'current_page': data.get('page', 1),
            'total_pages': data.get('total_pages', 1)
        }
        
    return {'movies': [], 'current_page': 1, 'total_pages': 1}


"""
#Get the YouTube trailer embed URL for a movie by its TMDB ID.
"""
def get_movie_video(film_id):
    url = f"https://api.themoviedb.org/3/movie/{film_id}/videos?api_key={settings.TMDB_API_KEY}&language=en-US"
    response = requests.get(url)
    
    if response.status_code == 200:
        videos = response.json().get('results', [])
        for video in videos:
            if video['site'] == 'YouTube' and video['type'] == 'Trailer':
                return f"https://www.youtube.com/embed/{video['key']}"
            
    return None


"""
Discover movies on TMDB filtered by genre and minimum rating with pagination. 
Save discovered movies in the database and returns a paginated list.
"""
def discover_movies_tmdb(genre=None, min_rating=None, page=1):
    url = 'https://api.themoviedb.org/3/discover/movie'
    params = {
        'api_key': settings.TMDB_API_KEY,
        'language': 'ro-RO',
        'sort_by': 'popularity.desc',
        'page': page
    }

    if genre:
        params['with_genres'] = genre
    if min_rating:
        try:
            params['vote_average.gte'] = float(min_rating)
        except ValueError:
            pass

    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        movies = data.get('results', [])

        # save movies in DB
        for movie in movies:
            save_movie_tmdb_if_not_exists(movie)

        return {
            'movies': movies,
            'current_page': data.get('page', 1),
            'total_pages': data.get('total_pages', 1)
        }
        
    return {'movies': [], 'current_page': 1, 'total_pages': 1}


"""
Generate movie recommendations based on the user's viewing history and favorite genres.
"""	
def recommendations_by_genres(user, top_n=3, movies_per_genre=3):
    watched  = ViewHistory.objects.filter(user=user).select_related('film')
    watched_movie_ids = set(v.film.id_tmdb for v in watched)
    all_genres = []

    for view in watched:
        all_genres.extend(view.film.genre_ids)

    favorite_genres = [genre for genre, _ in Counter(all_genres).most_common(top_n)]

    recommendations  = []
    recommended_movie_ids  = set()

    for genre_id in favorite_genres:
        result = discover_movies_tmdb(genre=genre_id)
        if result and 'movies' in result:
            for movie in result['movies']:
                if movie['id'] not in watched_movie_ids and movie['id'] not in recommended_movie_ids:
                    recommendations.append(movie)
                    recommended_movie_ids.add(movie['id'])
                    if len(recommendations) >= top_n * movies_per_genre:
                        break

    return recommendations


"""
For movies in the database without genres, fetch and update their genres from TMDB.
"""
def fill_movie_genres():
    base_url = "https://api.themoviedb.org/3/movie/"
    headers = {"Accept": "application/json"}
    movies_without_genres  = Film.objects.filter(genre_ids=[])

    for movie in movies_without_genres:
        url = f"{base_url}{movie.id_tmdb}"
        params = {
            "api_key": settings.TMDB_API_KEY,
            "language": "ro-RO"  
        }

        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                data = response.json()
                genres = data.get("genres", [])
                ids = [g["id"] for g in genres]
                movie.genre_ids = ids
                movie.save()
                print(f"✔ Genuri completate pentru: {movie.titlu}")
            else:
                print(f"✖ Eroare la {movie.titlu} (status {response.status_code})")
        except Exception as e:
            print(f"✖ Eroare la {movie.titlu}: {e}")
