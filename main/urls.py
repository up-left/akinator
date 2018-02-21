from django.urls import path

from . import views


urlpatterns = [
    path(r'play/', views.play, name='play'),
    path(r'guesses/', views.GuessList.as_view(), name='guesses'),
    path(r'questions/', views.QuestionList.as_view(), name='questions'),
]
