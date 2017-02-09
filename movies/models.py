from django.db import models
from django_countries.fields import CountryField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Genre(models.Model):
    name = models.CharField(max_length=30, unique=True)

    class Meta:
        db_table = 'genre'
        verbose_name_plural = 'genres'
        ordering = ['name']

    def __str__(self):
        return self.name


class ProductionRole(models.Model):
    title = models.CharField(max_length=30, unique=True)

    class Meta:
        db_table = 'production_role'

    def __str__(self):
        return self.title


class Country(models.Model):
    country = CountryField(unique=True)

    class Meta:
        db_table = 'country'
        verbose_name_plural = 'countries'
        ordering = ['country']

    def __str__(self):
        return str(self.country.name)


class Person(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    date_of_birth = models.DateField(help_text="Please use the following format: <em>YYYY-MM-DD</em>.")
    date_of_death = models.DateField(
        null=True,
        blank=True,
        help_text="Please use the following format: <em>YYYY-MM-DD</em>."
    )
    photo = models.ImageField(
        null=True,
        blank=True
    )

    country = models.ForeignKey(
        Country,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='people',
        verbose_name='represented country'
    )
    production_roles = models.ManyToManyField(
        ProductionRole,
        blank=True,
        related_name='people',
        verbose_name='role in movie production'
    )

    class Meta:
        db_table = 'person'
        verbose_name_plural = 'people'
        ordering = ['last_name']

    def __str__(self):
        return self.last_name + ' ' + self.first_name + ', ' + str(self.date_of_birth.year)


class Movie(models.Model):
    title = models.CharField(max_length=50)
    year = models.IntegerField(
        validators=[MinValueValidator(0)]
    )
    description = models.TextField(
        null=True,
        blank=True
    )
    rating = models.FloatField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(10)]
    )
    trailer = models.URLField()
    cover = models.ImageField()
    link_to_watch = models.URLField(
        null=True,
        blank=True
    )
    date_added = models.DateField(auto_now_add=True)
    duration = models.DurationField(help_text='Format HH:MM:SS')

    likes = models.IntegerField(default=0, blank=True)
    dislikes = models.IntegerField(default=0, blank=True)

    director = models.ForeignKey(
        Person,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='directed_movies',
        # limit_choices_to={'production_roles': ProductionRole.objects.filter(title='Director').get().pk},
        verbose_name='director'
    )
    production_countries = models.ManyToManyField(
        Country,
        related_name='movies',
        verbose_name='production countries'
    )
    genres = models.ManyToManyField(
        Genre,
        blank=True,
        related_name='movies',
        verbose_name='genres'
    )
    key_actors = models.ManyToManyField(
        Person,
        blank=True,
        # limit_choices_to={'production_roles': ProductionRole.objects.filter(title='Actor').get().pk},
        related_name='acted_movies',
        verbose_name='list of key actors',
    )

    class Meta:
        db_table = 'movie'
        ordering = ['-date_added']

    def __str__(self):
        return self.title + ', ' + str(self.year)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    liked_movies = models.ManyToManyField(
        Movie,
        blank=True,
        related_name='users_liked',
        verbose_name='liked movies'
    )
    disliked_movies = models.ManyToManyField(
        Movie,
        blank=True,
        related_name='users_disliked',
        verbose_name='disliked movies'
    )
    favourite_movies = models.ManyToManyField(
        Movie,
        blank=True,
        related_name='users_favourite',
        verbose_name='favourite movies'
    )
    watch_list = models.ManyToManyField(
        Movie,
        blank=True,
        related_name='users_added_watch_list',
        verbose_name='watch list'
    )

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()

    class Meta:
        db_table = 'profile'
