from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("newProduct", views.newProduct, name="newProduct"),
    path("categories", views.categories, name="categories"),
    path("category/<str:category>", views.category, name="category"),
    path("product/<int:product_id>", views.product, name="product"),
    path("product/<int:product_id>/new_bid", views.new_bid, name="new_bid"),
    path("product/<int:product_id>/comment", views.comment, name="comment"),
    path("watchlist/", views.watchlist, name="watchlist"),
    path("product/<int:product_id>/add", views.watchlist_add, name="watchlist_add"),
    path("product/<int:product_id>/remove", views.watchlist_remove, name="watchlist_remove"),
    path("product/<int:product_id>/closed_item", views.closed_item, name="closed_item"),
    path("product/closed_items", views.closed_items, name="closed_items")
]
