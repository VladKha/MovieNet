import re

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import Movie, Genre, Country, Person
from .forms import UserForm


MOVIES_PER_PAGE = 12


def create_year_periods(movies):
    if movies.count() == 0:
        return []

    ordered_movies = movies.order_by('year')
    period = 10

    first_year = int(ordered_movies.first().year / period) * period
    last_year = ordered_movies.last().year
    year_periods = []
    while True:
        if last_year - first_year < period:
            year_periods.append(str(first_year) + ' - ' + str(last_year))
            break
        year_periods.append(str(first_year) + ' - ' + str(first_year + period))
        first_year += period

    return year_periods


def create_ratings():
    return [str(i) + '+' for i in range(1, 10)]


def make_pagination(request, movies):
    page = request.GET.get('page', 1)
    paginator = Paginator(movies, MOVIES_PER_PAGE)
    try:
        movies = paginator.page(page)
    except PageNotAnInteger:
        movies = paginator.page(1)
    except EmptyPage:
        movies = paginator.page(paginator.num_pages)

    return movies


def index(request, movies=None):
    if not movies:
        movies = Movie.objects.all()

    context = {
        'genres': Genre.objects.all().order_by('name'),
        'year_periods': create_year_periods(movies),
        'ratings': create_ratings()
    }

    simple_query = request.GET.get('q')
    text = request.GET.get('text')
    genre = request.GET.get('genre')
    year_period = request.GET.get('year_period')
    rating = request.GET.get('rating')

    if simple_query:
        movies, query = simple_search(request, simple_query, movies)
        context['query'] = query

    elif text or genre or year_period or rating:
        movies, query = complex_search(request, text, genre, year_period, rating, movies)
        context['query'] = query

    context['movies'] = make_pagination(request, movies)
    return render(request, 'movies/index.html', context)


def sort(request, field, sort_direction):
    direction = '-' if sort_direction == 'desc' else ''
    movies = Movie.objects.order_by(direction + field)
    return index(request, movies)


def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)
    trailer_id = movie.trailer.replace('https://www.youtube.com/watch?v=', '')

    context = {
        'movie': movie,
        'trailer_id': trailer_id,
    }

    if request.user.is_authenticated():
        user = User.objects.get(id=int(request.user.id))

        is_in_favourites = user.profile.favourite_movies.filter(id=movie_id).count() == 1
        is_in_watch_list = user.profile.watch_list.filter(id=movie_id).count() == 1

        context['is_in_favourites'] = is_in_favourites
        context['is_in_watch_list'] = is_in_watch_list

    return render(request, 'movies/movie_detail.html', context)


def simple_search(request, simple_query, movies):
    words = re.split('\\s+', simple_query.strip())
    result = []
    for word in words:
        result = movies.filter(
            Q(title__icontains=word) |
            Q(description__icontains=word) |
            Q(director__last_name__icontains=word) |
            Q(director__first_name__icontains=word) |
            Q(key_actors__first_name__icontains=word) |
            Q(key_actors__last_name__icontains=word)
        ).distinct()

    query = '"' + simple_query + '"'
    return result, query


def complex_search(request, text, genre, year_period, rating, movies):
    result = movies
    q_genre = ''
    q_text = ''
    q_date_period = ''
    q_rating = ''

    if genre:
        result = result.filter(Q(genres__name__icontains=genre)).distinct()
        q_genre = ' genre "' + genre + '"'

    if text:
        words = re.split('\\s+', text.strip())
        for word in words:
            result = result.filter(
                Q(title__icontains=word) |
                Q(description__icontains=word) |
                Q(director__last_name__icontains=word) |
                Q(director__first_name__icontains=word) |
                Q(key_actors__first_name__icontains=word) |
                Q(key_actors__last_name__icontains=word)
            ).distinct()
        q_text = '"' + text + '"'

    if year_period:
        years = year_period.split(' - ')
        result = result.filter(
            Q(year__gte=int(years[0])) & Q(year__lte=int(years[1]))
        ).distinct()
        q_date_period = ' from ' + year_period + ' years'

    if rating:
        lowest_rating = int(rating[:rating.index('+')])
        result = result.filter(
            Q(rating__gte=lowest_rating)
        ).distinct()
        q_rating = ' rating ' + rating

    query = q_text + q_genre + q_rating + q_date_period

    return result, query


def genre_search(request, genre_id):
    movies = Movie.objects.filter(genres__exact=genre_id)
    query = '"' + str(Genre.objects.get(id=genre_id)) + '" movies'

    context = {
        'movies': make_pagination(request, movies),
        'query': query
    }

    return render(request, 'movies/index.html', context)


def year_search(request, year):
    movies = Movie.objects.filter(year=year)
    query = 'movies from ' + str(year) + ' year'

    context = {
        'movies': make_pagination(request, movies),
        'query': query
    }

    return render(request, 'movies/index.html', context)


def country_search(request, country_id):
    movies = Movie.objects.filter(production_countries__id=country_id)
    query = 'movies from ' + str(Country.objects.get(id=country_id))

    context = {
        'movies': make_pagination(request, movies),
        'query': query
    }

    return render(request, 'movies/index.html', context)


def person_detail(request, person_id):
    movies = Movie.objects.filter(
        Q(director__id=person_id) | Q(key_actors__id=person_id)
    ).distinct()

    person = Person.objects.get(id=person_id)
    context = {
        'movies': make_pagination(request, movies),
        'person': person,
        'roles': ', '.join([str(r) for r in person.production_roles.all()])
    }

    return render(request, 'movies/person_detail.html', context)


def logout_user(request):
    logout(request)
    return redirect('movies:index')


def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('movies:index')
            else:
                return render(request, 'movies/login.html', {'error_message': 'Your account has been disabled'})
        else:
            return render(request, 'movies/login.html', {'error_message': 'Invalid login'})
    return render(request, 'movies/login.html')


def register(request):
    form = UserForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user.set_password(password)
        user.save()
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('movies:index')
    context = {
        "form": form,
    }
    return render(request, 'movies/register.html', context)


def user_profile(request, user_id):
    user = User.objects.get(id=user_id)

    if user.is_authenticated:
        liked_movies = user.profile.liked_movies.all()
        favourite_movies = user.profile.favourite_movies.all()
        watch_list = user.profile.watch_list.all()

        context = {
            'user': User.objects.get(id=user_id),
            'liked_movies': make_pagination(request, liked_movies),
            'favourite_movies':  make_pagination(request, favourite_movies),
            'watch_list':  make_pagination(request, watch_list),
        }
        return render(request, 'movies/user_profile.html', context)
    else:
        return redirect('movies:index')


def recommendations(request):
    user = request.user

    if user.is_authenticated:
        movies = user.profile.favourite_movies.all()
        genres_count_map = {}
        for m in movies:
            for g in m.genres.all():
                if g in genres_count_map:
                    genres_count_map[g] += 1
                else:
                    genres_count_map[g] = 1

        if len(genres_count_map) > 0:
            top_genre1, top_genre2 = sorted(genres_count_map, key=genres_count_map.__getitem__, reverse=True)[0:2]

            movies = Movie.objects.filter(
                Q(genres__exact=top_genre1.id) | Q(genres__exact=top_genre2)
            ).distinct()

        return render(request, 'movies/recommendations.html', {'movies': make_pagination(request, movies)})
    else:
        return redirect('movies:index')


# AJAX methods
def like_movie(request):
    user = request.user

    if user.is_authenticated:
        movie_id = int(request.POST.get('movie_id', None))

        likes = 0
        if movie_id:
            movie = Movie.objects.get(id=movie_id)
            if movie is not None:
                if movie not in user.profile.liked_movies.filter(id=movie_id):
                    likes = movie.likes + 1
                    user.profile.liked_movies.add(movie)

                else:
                    likes = movie.likes - 1
                    user.profile.liked_movies.remove(movie)
                movie.likes = likes
                movie.save()

        return HttpResponse(likes)
    else:
        return redirect('movies:index')


def dislike_movie(request):
    user = request.user

    if user.is_authenticated:
        movie_id = int(request.POST.get('movie_id', None))

        dislikes = 0
        if movie_id:
            movie = Movie.objects.get(id=movie_id)
            if movie is not None:
                if movie not in user.profile.disliked_movies.filter(id=movie_id):
                    dislikes = movie.dislikes + 1
                    user.profile.disliked_movies.add(movie)
                else:
                    dislikes = movie.dislikes - 1
                    user.profile.disliked_movies.remove(movie)
                movie.dislikes = dislikes
                movie.save()

        return HttpResponse(dislikes)
    else:
        return redirect('movies:index')


def add_to_favourites(request):
    user = request.user

    if user.is_authenticated:
        movie_id = int(request.POST.get('movie_id', None))

        user.profile.favourite_movies.add(movie_id)

        return HttpResponse()
    else:
        return redirect('movies:index')


def add_to_watch_list(request):
    user = request.user

    if user.is_authenticated:
        movie_id = int(request.POST.get('movie_id', None))

        user.profile.watch_list.add(movie_id)

        return HttpResponse()
    else:
        return redirect('movies:index')


def remove_from_favourites(request):
    user = request.user

    if user.is_authenticated:
        movie_id = int(request.POST.get('movie_id', None))

        user.profile.favourite_movies.remove(movie_id)

        return HttpResponse()
    else:
        return redirect('movies:index')


def remove_from_watch_list(request):
    user = request.user

    if user.is_authenticated:
        movie_id = int(request.POST.get('movie_id', None))

        user.profile.watch_list.remove(movie_id)

        return HttpResponse()
    else:
        return redirect('movies:index')
