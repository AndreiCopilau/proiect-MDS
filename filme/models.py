from django.db import models
from django.conf import settings 

class Film(models.Model):
    id_tmdb = models.IntegerField(unique=True)
    titlu = models.CharField(max_length=200)
    poster_path = models.CharField(max_length=200, null=True, blank=True)
    # Alte câmpuri relevante

class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # <-- modificare
    film = models.ForeignKey(Film, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'film')

class ViewHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # <-- modificare
    film = models.ForeignKey(Film, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-viewed_at']


from django.contrib.auth.models import AbstractUser

class UserCustom(AbstractUser):
    telefon = models.CharField(max_length=15, blank=True, verbose_name="Telefon")
    data_nasterii = models.DateField(blank=True, null=True, verbose_name="Data nasterii")
    gen = models.CharField(
        max_length=10,
        choices=[('M', 'Masculin'), ('F', 'Feminin')],
        blank=True,
        verbose_name="Gen"
    )
    ocupatie = models.CharField(max_length=50, blank=True, verbose_name="Ocupatie")
    cod = models.CharField(max_length=100, null=True, blank=True, verbose_name="Cod de confirmare")
    email_confirmat = models.BooleanField(default=False, verbose_name="Email confirmat")

    def __str__(self):
        return self.username
