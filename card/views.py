from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.models import AbstractBaseUser
from card.models import LoginInfo, Transaction, PinSaver
from datetime import datetime, timezone, timedelta
from django.db.models import F
from django.utils.timezone import get_current_timezone

User = get_user_model()

# тут все на столько сырое, что скоро выростут грибы


@login_required(redirect_field_name='login_card')
def home(request):
    return render(request, 'card/home.html')


def login_card(request):
    context = {}
    if request.method == "POST":
        card_id = request.POST['username']
        password = request.POST['password']
        if card_id and password:
            card = authenticate(request, card_id=card_id, password=password)
            if card:
                login(request, card)
                return HttpResponseRedirect(reverse('home'))
            else:
                context['error'] = 'Wrong pin or card ID!'
                if User.objects.filter(card_id=card_id).exists():
                    incorrect_pin_try = LoginInfo(card_id=card_id)
                    incorrect_pin_try.save()
                    if len(LoginInfo.objects.filter(card_id=card_id, time__gt=datetime.now(tz=get_current_timezone())-timedelta(minutes=3))) >= 3:
                        card = User.objects.get(card_id=card_id)
                        card.is_active = False
                        card.save()
                        context['error'] = 'Card has been blocked! To unlock, contact the bank employees.'
                    return render(request, 'card/login.html', context)
                return render(request, 'card/login.html', context)
        else:
            context['error'] = 'You need enter the card number and pin!'
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
        if request.POST['amount']:
            amount = int(request.POST['amount'])
            if amount < 0:
                amount *= -1
        else:
            context['comment'] = 'Enter the amount you want to add to your account'
            return render(request, 'card/cash.html', context)
        card = request.user
        card.balance = card.balance+amount
        transact = Transaction(card_id=card, operation=True, value=amount, new_balance=card.balance)
        if card.balance >= 0:
            transact.save()
            card.save()
        context['success'] = 'Success'
        return render(request, 'card/refill.html', context)
    else:
        return render(request, 'card/refill.html', context)


@login_required(redirect_field_name='login_card')
def cash(request):
    context = {}
    if request.method == "POST":
        if request.POST['amount']:
            amount = int(request.POST['amount'])
            if amount < 0:
                amount *= -1
        else:
            context['comment'] = 'Enter the amount you want to withdraw'
            return render(request, 'card/cash.html', context)
        card = request.user
        if card.balance >= amount:
            card.balance = card.balance-amount
            transact = Transaction(card_id=card, operation=False, value=amount, new_balance=card.balance)
            if card.balance >= 0:
                transact.save()
                card.save()
            context['comment'] = 'Success'
            return render(request, 'card/cash.html', context)
        else:
            context['comment'] = 'Insufficient funds on your account!'
            return render(request, 'card/cash.html', context)
    else:
        return render(request, 'card/cash.html', context)


@login_required(redirect_field_name='login_card')
def pin_change(request):
    context = {}
    card = request.user

    if request.method == "POST":

        new_pin = request.POST['password']

        if PinSaver.objects.filter(card_id=card):
            pin_obj_list = PinSaver.objects.filter(card_id=card)
            pin_obj = PinSaver.objects.filter(card_id=card)[len(pin_obj_list)-1]
            if not pin_obj.confirm:
                if pin_obj.new_pin == new_pin:
                    card.set_password(new_pin)
                    card.save()
                    pin_obj.confirm = True
                    pin_obj.save()
                    context['comment'] = 'Your pin was changed'
                    return render(request, 'card/pin_change.html', context)
                else:
                    pin_obj.confirm = True
                    pin_obj.save()
                    context['comment'] = 'Pins do not match. Try again'
                    return render(request, 'card/pin_change.html', context)
            else:
                return render(request, 'card/pin_change.html', current_pin_valid_context(card, new_pin))
        else:
            return render(request, 'card/pin_change.html', current_pin_valid_context(card, new_pin))
        
    else:
        if PinSaver.objects.filter(card_id=card):
            pin_obj_list = PinSaver.objects.filter(card_id=card)
            pin_obj = PinSaver.objects.filter(card_id=card)[len(pin_obj_list) - 1]
            if not pin_obj.confirm:
                    pin_obj.confirm = True
                    pin_obj.save()
        return render(request, 'card/pin_change.html', context)


@login_required(redirect_field_name='login_card')
def logout_card(request):
    logout(request)
    return HttpResponseRedirect(reverse('login_card'))


def pin_valid(pin):
    try:
        return False if len(pin) != 4 or int(pin[0]) == int(pin[1]) or int(pin[2]) == int(pin[3]) else True
    except ValueError:
        return False


def current_pin_valid_context(card, new_pin):
    context = {}
    if not card.check_password(new_pin):
        if pin_valid(new_pin):
            PinSaver(card_id=card, new_pin=new_pin).save()
            context['comment'] = 'Confirm pin'
            return context
        else:
            context['comment'] = 'Incorrect pin format. Try another one'
            return context
    else:
        context['comment'] = 'New pin can not be the same old'
        return context
