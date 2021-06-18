from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    watchlist = models.ManyToManyField('Product', null=True, blank=True)

class Product(models.Model):
    title = models.CharField(max_length = 100)
    description = models.TextField()
    seller = models.ForeignKey(User, related_name="product_user", on_delete=models.CASCADE, blank=True)
    price_start = models.FloatField()
    current_price = models.FloatField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    image_link = models.URLField(null=True, blank=True, help_text="Enter bid's image URL optional")
    category = models.ForeignKey('Category', related_name = "products_with_category", on_delete=models.CASCADE, blank=True, null=True)
    is_closed = models.BooleanField(default= False)
    winner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    
    def __str__(self):
        return self.title

class Bid(models.Model):
    product_id = models.IntegerField()
    new_price = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, related_name="bid_user", on_delete=models.CASCADE, blank=True)
    products = models.ForeignKey(Product, related_name = "all_bids_to_this_product", on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return str(f"{self.new_price} made {self.user} for product {self.products}")

class Comment(models.Model):
    user = models.ForeignKey(User, related_name="comment_user", on_delete=models.CASCADE, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    # comment_id = models.IntegerField()
    product_comment = models.ForeignKey(Product, related_name = "all_comments_to_product", on_delete=models.CASCADE, blank=True)

    def __str__(self):
        return str(f"{self.user} for {self.product_comment}")

class Category(models.Model):
    category = models.CharField(max_length = 20)
    # products = models.ForeignKey(Product, related_name = "all_categ_to_this_product",  blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.category)