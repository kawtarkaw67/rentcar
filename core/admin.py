from django.contrib import admin
from .models import Voiture, Client, Reservation, Categorie, Paiement, Historique, Notification

admin.site.register(Voiture)
admin.site.register(Client)
admin.site.register(Reservation)
admin.site.register(Categorie)
admin.site.register(Paiement)
admin.site.register(Historique)
admin.site.register(Notification)
