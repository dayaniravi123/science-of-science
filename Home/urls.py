from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('index/', views.index, name='index'),
    path('submit/', views.submit, name='submit'),
    path('author/', views.author, name='author'),
    path('statistics/', views.statistics, name='statistics'),
    path('authorStatistics/', views.authorStatistics, name='authorStatistics'),
    path('statisticsMostCommonAuthor/', views.statisticsMostCommonAuthor, name='statisticsMostCommonAuthor'),
    path('statisticsLeastCommonAuthor/', views.statisticsLeastCommonAuthor, name='statisticsLeastCommonAuthor'),
    path('statisticsTopCitation/', views.statisticsTopCitation, name='statisticsTopCitation'),
    path('statisticsLastCitation/', views.statisticsLastCitation, name='statisticsLastCitation'),
    path('statisticsPaperTopRows/', views.statisticsPaperTopRows, name='statisticsPaperTopRows'),
    path('statisticsPaperLastRows/', views.statisticsPaperLastRows, name='statisticsPaperLastRows'),

    path('getauthordetails/', views.getauthordetails, name = 'getauthordetails'),
    path('downloadfile/', views.downloadfile, name='downloadfile'),


]