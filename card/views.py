from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from card.models import CardInfo

#тут все на столько сырое, что скоро выростут грибы

@login_required(redirect_field_name='login_card')
def home(request):
    context = {}
    return render(request, 'card/home.html', context)


def login_card(request):
    logout(request)
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


@login_required(redirect_field_name='login_card')
def balance(request):
    return render(request, 'card/balance.html')


@login_required(redirect_field_name='login_card')
def refill(request):
    context = {}
    if request.method == "POST":
        summ = int(request.POST['summ'])
        card = request.user
        card.balance=card.balance+summ
        card.save()
        context['success'] = 'Operation done successful'
        return render(request, 'card/refill.html', context)
    else:
        return render(request, 'card/refill.html', context)


@login_required(redirect_field_name='login_card')
def cash(request):
    context = {}
    if request.method == "POST":
        summ = int(request.POST['summ'])
        card = request.user
        if card.balance >= summ:
            card.balance=card.balance-summ
            card.save()
            context['comment'] = 'Operation done successful'
            return render(request, 'card/cash.html', context)
        else:
            context['comment'] = 'Insufficient funds in your account!'
            return render(request, 'card/cash.html', context)

    else:
        return render(request, 'card/cash.html', context)

