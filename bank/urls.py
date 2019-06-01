from django.contrib import admin
from django.urls import path, include
from card.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', login_card, name='login_card'),
    path('home/', home, name='home'),
    path('balance/', balance, name='balance'),
    path('cash/', cash, name='cash'),
    path('refill/', refill, name='refill'),
    path('pin_change', pin_change, name='pin_change')
]
