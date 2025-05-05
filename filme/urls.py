from django.urls import path # type: ignore
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('film/<int:film_id>/', views.detalii_film, name='detalii_film'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('favorite/', views.lista_favorite, name='lista_favorite'),
    path('film/<int:film_id>/adauga-favorit/', views.adauga_favorit, name='adauga_favorit'),
    path('film/<int:film_id>/elimina-favorit/', views.elimina_favorit, name='elimina_favorit'),
    path('istoric/', views.istoric_vizionari, name='istoric_vizionari'),
]