from django.urls import path

from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('history',views.history,name='history'),
    # path('logout', views.logout,name='logout'),
    # path('new_epipen/', views.add_epipen, name='new_epipen'),
    # path('edit_profile/', views.edit_profile, name='edit_profile'),
    # path('view_history/', views.emergency_history, name='view_history'),
    ]