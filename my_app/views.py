import requests
import re
from bs4 import BeautifulSoup
from django.shortcuts import render
from urllib.parse import quote_plus
from . import models

BASE_CRAIGSLIST_URL = 'https://losangeles.craigslist.org/search/?query={}'
BASE_IMAGE_URL = 'https://images.craigslist.org/{}_300x300.jpg'

URA_MANJI_IMAGE = 'https://usercontent2.hubstatic.com/4523219_f520.jpg'
CRAIGSLIST_DEFAULT_IMAGE = 'https://craigslist.org/images/peace.jpg'
FREEDOM_EAGLE_IMAGE = "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fyt3.ggpht.com%2Fa-%2FAAuE7mDVwDwSfr2niqzJ-misHtqq6tmPXClXMrT_8A%3Ds900-mo-c-c0xffffffff-rj-k-no&f=1&nofb=1"


def home(request):
    return render(request, 'base.html')


def new_search(request):
    # request.POST returns a dict
    # so using get() to retrieve the element we want
    search = request.POST.get('search')
    models.Search.objects.create(search= search)

    final_url = BASE_CRAIGSLIST_URL.format(quote_plus(search))
    response = requests.get(final_url)
    data = response.text
    soup = BeautifulSoup(data, features='html.parser')

    post_listings = soup.find_all('li', {'class': 'result-row'})

    final_postings = []

    for post in post_listings:
        post_title = post.find(class_= 'result-title').text
        post_url = post.find('a').get('href')
        post_image_url = CRAIGSLIST_DEFAULT_IMAGE

        # get item price if it exists
        if post.find(class_= 'result-price'):
            post_price = post.find(class_= 'result-price').text
        else:
            post_price = 'N/A'


        if post.find(class_='result-image').get('data-ids'):
            ''' 
            If there are images, get the image IDs labeled 'data-ids', formatted as:
                1:(data-id), 1:(data-id), 1:(data-id),
            and give the first one from the list
            '''
            post_image_ids = post.find(class_='result-image').get('data-ids')
            post_image = re.findall("1:(.+?),", post_image_ids)
            if post_image:
                post_image_url = BASE_IMAGE_URL.format(post_image[0])
                print(post_image_url)

        final_postings.append((post_title, post_url, post_price, post_image_url))



    stuff_for_frontend = {
        'search': search,
        'final_postings': final_postings,
    }

    return render(request, 'my_app/new_search.html', stuff_for_frontend)