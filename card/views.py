from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse


@login_required(redirect_field_name='login_card')
def home(request):
    context = {}
    return render(request, 'card/home.html', context)


def login_card(request):
    context = {}
    if request.method == "POST":
        cardID = request.POST['username']
        password = request.POST['password']
        card = authenticate(request, cardID=cardID, password=password)
        if card:
            login(request, card)
            return HttpResponseRedirect(reverse('home'))
        else:
            context['error'] = 'Wrong card data!'
            return render(request, 'card/login.html', context)
    else:
        return render(request, 'card/login.html', context)


def logout_card(request):
    return HttpResponseRedirect(reverse('login_card'))