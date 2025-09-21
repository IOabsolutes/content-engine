from django.urls import path
from items import views

urlpatterns = [
    path("create/", views.item_create_view, name="item-create"),
]
