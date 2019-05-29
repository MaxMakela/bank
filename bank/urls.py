from django.contrib import admin
from django.urls import path, include
from card.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', login_card, name='login_card'),
    path('home/', home, name='home'),
    path('logout/', logout_card, name='logout_card'),
    path('balance/', balance, name='balance'),
    path('cash/', top_up, name='cash'),
    path('top_up/', top_up, name='top_up'),
]
