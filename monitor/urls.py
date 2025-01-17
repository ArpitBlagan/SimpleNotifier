from django.urls import path
from . import views
urlpatterns = [
    path('add/', views.add_website, name='addWebsite'),
    path('all/', views.get_websites, name='getWebsites'),
    path('notify/', views.notify_on_discord, name='notify'),
    path('all/history/', views.get_histories, name='getHistories'),
    path('get/<int:id>/',views.get_website,name="getWebsite"),
    path('delete/<int:id>/', views.delete_website, name='deleteWebsite'),

]