from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.models import AbstractBaseUser


# тут все на столько сырое, что скоро выростут грибы


@login_required(redirect_field_name='login_card')
def home(request):
	context = {}
	if request.session.get('new_pin'):
		del request.session['new_pin']
	return render(request, 'card/home.html', context)


def login_card(request):
	context = {}
	if request.method == "POST":
		cardID = request.POST['username']
		password = request.POST['password']
		if cardID and password:
			User = get_user_model()
			card = authenticate(request, cardID=cardID, password=password)
			if card:
				login(request, card)
				return HttpResponseRedirect(reverse('home'))
			else:
				if User.objects.filter(cardID=cardID).exists():
					context['error'] = 'Wrong pin!'
					if cardID in request.session:
						request.session[cardID] += 1
					else:
						request.session[cardID] = 1
					request.session.modified = True
					if request.session.get(cardID) >= 3:
						card = User.objects.get(cardID=cardID)
						card.is_active = False
						card.save()
						context['error'] = 'Card has been blocked! To unlock, contact the bank employees.'
					return render(request, 'card/login.html', context)
				context['error'] = 'Wrong card ID!'
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
		if request.POST['summ']:
			summ = int(request.POST['summ'])
		else:
			context['comment'] = 'Enter the amount you want to add to your account'
			return render(request, 'card/cash.html', context)
		card = request.user
		card.balance = card.balance+summ
		card.save()
		context['success'] = 'Operation done successful'
		return render(request, 'card/refill.html', context)
	else:
		return render(request, 'card/refill.html', context)


@login_required(redirect_field_name='login_card')
def cash(request):
	context = {}
	if request.method == "POST":
		if request.POST['summ']:
			summ = int(request.POST['summ'])
		else:
			context['comment'] = 'Enter the amount you want to withdraw'
			return render(request, 'card/cash.html', context)
		card = request.user
		if card.balance >= summ:
			card.balance = card.balance-summ
			card.save()
			context['comment'] = 'Operation done successful'
			return render(request, 'card/cash.html', context)
		else:
			context['comment'] = 'Insufficient funds in your account!'
			return render(request, 'card/cash.html', context)

	else:
		return render(request, 'card/cash.html', context)


@login_required(redirect_field_name='login_card')
def pin_change(request):
	context = {}
	if request.method == "POST":
		
		card = request.user
		new_pin = request.POST['password']
		
		if request.session.get('new_pin'):
			if request.session.get('new_pin') == new_pin:
				card.set_password(new_pin)
				card.save()
				del request.session['new_pin']
				context['comment'] = 'Your pin was changed'
				return render(request, 'card/pin_change.html', context)
			else:
				del request.session['new_pin']
				context['comment'] = 'Pins do not match. Try again'
				return render(request, 'card/pin_change.html', context)
		
		if not card.check_password(new_pin):
			if pin_valid(new_pin):
				request.session['new_pin'] = new_pin
				context['comment'] = 'Confirm pin'
				return render(request, 'card/pin_change.html', context)
			else:
				context['comment'] = 'Incorrect pin format. Try another one'
				return render(request, 'card/pin_change.html', context)
		else:
			context['comment'] = 'New pin can not be the same old'
			return render(request, 'card/pin_change.html', context)
	else:
		return render(request, 'card/pin_change.html', context)


@login_required(redirect_field_name='login_card')
def logout_card(request):
	logout(request)
	return HttpResponseRedirect(reverse('login_card'))


def pin_valid(pin):
	return False if len(pin) != 4 or pin[0] == pin[1] or pin[2] == pin[3] else True


