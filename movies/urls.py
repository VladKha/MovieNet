from django.conf.urls import url
from . import views

app_name = 'movies'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^simple_search/$', views.simple_search, name='simple-search'),
    url(r'^complex_search/$', views.complex_search, name='complex-search'),

    url(r'^sort=(?P<field>[a-zA-Z_]+)&(?P<sort_direction>[a-z]+)/$', views.sort, name='sort'),
    url(r'^(?P<movie_id>[0-9]+)/$', views.movie_detail, name='movie-detail'),
    url(r'^genre=(?P<genre_id>[0-9]+)/$', views.genre_search, name='genre-search'),
    url(r'^year=(?P<year>(\d)+)/$', views.year_search, name='year-search'),
    url(r'^country=(?P<country_id>[0-9]+)/$', views.country_search, name='country-search'),
    url(r'^person=(?P<person_id>[0-9]+)/$', views.person_detail, name='person-detail'),
    url(r'^register/$', views.register, name='register'),
    url(r'^login_user/$', views.login_user, name='login-user'),
    url(r'^logout_user/$', views.logout_user, name='logout-user'),
    url(r'^profile=(?P<user_id>[0-9]+)/$', views.user_profile, name='user-profile'),
    url(r'^recommendations/$', views.recommendations, name='recommendations'),


    url(r'^like_movie/$', views.like_movie, name='like-movie'),
    url(r'^dislike_movie/$', views.dislike_movie, name='dislike-movie'),
    url(r'^add_to_favourites/$', views.add_to_favourites, name='add-to-favourites'),
    url(r'^remove_from_favourites/$', views.remove_from_favourites, name='remove-from-favourites'),
    url(r'^add_to_watch_list/$', views.add_to_watch_list, name='add-to-watch-list'),
    url(r'^remove_from_watch_list/$', views.remove_from_watch_list, name='remove-from-watch-list'),
]
