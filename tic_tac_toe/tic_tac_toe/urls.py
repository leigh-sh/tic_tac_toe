from django.conf.urls import url
from django.contrib import admin
from django.urls import path

from .views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    url(r'^signin/$',  signin, name='signin'),
    url(r'^game/$',  game, name='game'),
    url(r'^move/$',  make_move, name='move'),
    url(r'^newgame/$',  new_game, name='new_game'),
    url(r'^signout', signout, name='signout'),
    url(r'^signup/$',  signup, name='signup'),
]
