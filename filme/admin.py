from django.contrib import admin  # Acesta este importul crucial
from .models import Film, Favorite  # Importă modelele tale

# Înregistrează modelele pentru a fi vizibile în admin
admin.site.register(Film)
admin.site.register(Favorite)