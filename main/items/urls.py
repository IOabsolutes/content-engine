from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.item_create_view, name='item_create'),
    path('', views.item_list_view, name='item_list'),
    path('<int:id>/', views.item_detail_view, name='item_detail'),
]