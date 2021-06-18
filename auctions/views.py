from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.contrib.auth.decorators import login_required
import datetime
from django.utils import timezone

from .models import User
from .models import *

class CreateProduct(forms.Form):
    productTitle = forms.CharField(label='productTitle')
    productDesc = forms.CharField(widget=forms.Textarea, label='productDesc')
    productPrice = forms.FloatField(label='productPrice')
    productLink = forms.CharField(label='productLink', required=False)
    productCategory = forms.CharField(label="productCategory")

# -------------------------- login - regiser block ---------------------------------------
def login_view(request):
    if request.method == "POST":

        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


# -------------------------- new product block-------------------------------------------------------------------------------

@login_required(login_url='/login')
def newProduct(request):
    categories = Category.objects.all()

    if request.method == "POST":
        seller = request.user
        title = request.POST.get('productTitle')
        description = request.POST.get('productDesc')
        price_start = request.POST.get('productPrice')
        current_price = price_start
        user_close = True

        p_category = int(request.POST.get('category'))
        category = Category.objects.get(pk = p_category)

        if request.user.is_authenticated :
            product.in_watchlist = product in request.user.watchlist.all()
        
        if request.POST.get('productLink'):
            image_link = request.POST.get('productLink')
        else:
            image_link = "https://st4.depositphotos.com/2381417/26959/i/600/depositphotos_269592716-stock-photo-no-thumbnail-images-placeholder-for.jpg"
        
        # saving the data into the database
        l = Product(
                title = title, 
                description = description, 
                price_start = price_start ,
                current_price = current_price,
                image_link = image_link, 
                seller = seller,
                category = category
        )
        l.save()

        now = datetime.datetime.now()

        return render(request, "auctions/product.html", {
            "title": title,
            "description": description,
            "price_start": price_start,
            "img": image_link,
            "seller": seller,
            "date": l.date.now(),
            "category": category,
            "id": l.id,
            "current_price": current_price,
            "user_close": user_close,
            "in_watchlist": product.in_watchlist
        })
    else:
        return render(request, "auctions/newProduct.html", {
            "CreateProductForm": CreateProduct(),
            "categories": categories
        })   


# ---------------------- active listingS block----------------------------
def index(request):
    products = Product.objects.filter(is_closed = False)
    return render(request, "auctions/index.html", {
        "products": products
    })


# ---------------------- product block --------------------------------
def product(request, product_id):
    product = Product.objects.get(pk = product_id)

    bids = product.all_bids_to_this_product.all()
    
    if not product.is_closed and product.seller == request.user:
        user_close = True
    else:
        user_close = False

    if request.user.is_authenticated :
        product.in_watchlist = product in request.user.watchlist.all()

        return render(request, "auctions/product.html", 
        {
            "title": product.title,
            "description": product.description,
            "price_start": product.price_start,
            "current_price": product.current_price,
            "img": product.image_link,
            "seller": product.seller,
            "date": product.date,
            "category": product.category,
            "id": product.id,
            "bids": bids,
            "comments": product.all_comments_to_product.all(),
            "in_watchlist": product.in_watchlist,
            "user_close": user_close
        })
    else: 
        return render(request, "auctions/product.html", 
        {
            "title": product.title,
            "description": product.description,
            "price_start": product.price_start,
            "current_price": product.current_price,
            "img": product.image_link,
            "comments": product.all_comments_to_product.all()
        })


# --------------------------- new bid ---------------------------------
@login_required(login_url='/login')
def new_bid(request, product_id):
    product = Product.objects.get(pk = product_id)
    
    if not product.is_closed and product.seller == request.user:
        user_close = True
    else:
        user_close = False

    message1 = False
    message2 = False

    if request.user.is_authenticated :
        product.in_watchlist = product in request.user.watchlist.all()

    
    if request.POST['bid'] == '':
        bid = 0
    else:
        bid = float(request.POST.get('bid'))
    #proverka stavka ne <0 
    if bid <= 0:
        message1 = True
        
    b = Bid()
    b.product_id = product.id

    if bid <= product.current_price: 
        message2 = True 

    else:
        product.current_price = bid
        product.winner = request.user
        product.save()

        b.new_price = bid
        b.date = datetime.datetime.now()
        b.user = request.user
        b.products = product
        b.save()

    bids = product.all_bids_to_this_product.all()

    if request.method == "POST":
        return render(request, "auctions/product.html", {
            "title": product.title,
            "description": product.description,
            "price_start": product.price_start,
            "current_price": product.current_price,
            "img": product.image_link,
            "seller": product.seller,
            "date": product.date,
            'bid1': bid,
            "id": product.id,
            "message1": message1,
            "message2": message2,
            "category": product.category,
            "bids": bids,
            "comments": product.all_comments_to_product.all(),
            "in_watchlist": product.in_watchlist,
            "user_close": user_close
        })


# -------------------------- commentS block ----------------------------------
@login_required(login_url='/login')
def comment(request, product_id):
    product = Product.objects.get(pk = product_id)

    if not product.is_closed and product.seller == request.user:
        user_close = True
    else:
        user_close = False

    if request.user.is_authenticated :
        product.in_watchlist = product in request.user.watchlist.all()

        comment = request.POST.get('comment')
        c = Comment(
            user = request.user, 
            date=datetime.datetime.now(), 
            content = comment, 
            product_comment = product)
        c.save()

    if request.method == "POST" and not product.is_closed:

        return render(request, "auctions/product.html", {
            
            "id": product.id,
            "comments": product.all_comments_to_product.all(),
            "title": product.title,
            "description": product.description,
            "price_start": product.price_start,
            "current_price": product.current_price,
            "img": product.image_link,
            "seller": product.seller,
            "date": product.date,
            # 'bid': p_bid,
            "id": product.id,
            "category": product.category,
            "bids": product.all_bids_to_this_product.all(),
            "in_watchlist": product.in_watchlist,
            "user_close": user_close
        })
    else:
        return render(request, 'auctions/closed_product.html', {
            "title": product.title,
            "description": product.description,
            "final_price": product.current_price,
            "img": product.image_link,
            "seller": product.seller,
            "category": product.category,
            "id": product.id,
            "comments": product.all_comments_to_product.all(),
            "watchlist": request.user.watchlist.all(),
            "product": product,
            "in_watchlist": product.in_watchlist,
            "winner": product.winner
    })


# -------------------------------- categories block ----------------------------------------------
@login_required(login_url='/login')
def categories(request):
    categories = Category.objects.all()

    return render(request, "auctions/categories.html",{
        "categories": categories
    })


# view to display all the active listings in that category
@login_required(login_url='/login')
def category(request, category):
    category_products = Product.objects.filter(category__category=category)
    category_products = category_products.filter(is_closed = False)

    empty = False
    if len(category_products) == 0:
        empty = True
    return render(request, "auctions/category.html", {
        "category": category,
        "empty": empty,
        "products": category_products
    })


# ---------------------------------- watchlist block ---------------------------------
@login_required
def watchlist(request):
    user_owner = request.user
    print(user_owner.watchlist.all() )
    return render(request, 'auctions/watchlist.html', {
         'watchlist': user_owner.watchlist.all() 
         })

@login_required
def watchlist_add(request, product_id):
    user_owner = request.user

    product = Product.objects.get(pk = product_id)
    user_owner.watchlist.add(product)
    product.in_watchlist = True
    
    if not product.is_closed and product.seller == request.user:
        user_close = True
    else:
        user_close = False
    return render(request, 'auctions/product.html', {
            "title": product.title,
            "description": product.description,
            "price_start": product.price_start,
            "current_price": product.current_price,
            "img": product.image_link,
            "seller": product.seller,
            "date": product.date,
            "category": product.category,
            "id": product.id,
            "bids": product.all_bids_to_this_product.all(),
            "comments": product.all_comments_to_product.all(),
            "watchlist": user_owner.watchlist.all(),
            "product": product,
            "in_watchlist": product.in_watchlist,
            "user_close": user_close
    })    


@login_required
def watchlist_remove(request, product_id):
    user_owner = request.user
    product = Product.objects.get(pk = product_id)
    user_owner.watchlist.remove(product)
    product.in_watchlist = False

    if not product.is_closed and product.seller == request.user:
        user_close = True
    else:
        user_close = False

    return render(request, 'auctions/product.html', {
            "title": product.title,
            "description": product.description,
            "price_start": product.price_start,
            "current_price": product.current_price,
            "img": product.image_link,
            "seller": product.seller,
            "date": product.date,
            "category": product.category,
            "id": product.id,
            "bids": product.all_bids_to_this_product.all(),
            "comments": product.all_comments_to_product.all(),
            "watchlist": user_owner.watchlist.all(),
            "product": product,
            "in_watchlist": product.in_watchlist,
            "user_close": user_close
    })


# ------------------------ closed block --------------------------------------
def closed_item(request, product_id):
    product = Product.objects.get(pk = product_id)
    product.in_watchlist = False
    bid = Bid.objects.filter(product_id = product.id)

    if request.user.is_authenticated :
        product.in_watchlist = product in request.user.watchlist.all()

    if request.user == product.seller:
        product.is_closed = True
        product.save()

    return render(request, 'auctions/closed_product.html', {
            "title": product.title,
            "description": product.description,
            "final_price": product.current_price,
            "img": product.image_link,
            "seller": product.seller,
            "category": product.category,
            "id": product.id,
            "comments": product.all_comments_to_product.all(),
            "watchlist": request.user.watchlist.all(),
            "product": product,
            "in_watchlist": product.in_watchlist,
            "winner": product.winner
    })

def closed_items(request):
    products = Product.objects.filter(is_closed = True)
    return render(request, "auctions/closed_products.html", {
        "products": products
    })
