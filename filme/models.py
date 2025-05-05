from django.db import models
from django.contrib.auth.models import User

class Film(models.Model):
    id_tmdb = models.IntegerField(unique=True)  # ID-ul filmului din API-ul TMDB
    titlu = models.CharField(max_length=200)
    poster_path = models.CharField(max_length=200, null=True, blank=True)
    # Alte câmpuri relevante (release_date, overview etc.)

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    film = models.ForeignKey(Film, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'film')  # Un utilizator poate adauga un film o singura data
        
        
        #pana aici tot a fost adaugat de radu