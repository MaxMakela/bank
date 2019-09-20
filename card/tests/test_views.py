from django.test import TestCase, Client
from card.views import *
from django.contrib.auth import get_user_model


class TestCardProcessing(TestCase):
    
    def setUp(self):
        self.user = get_user_model()
        self.card_id = "1234567812345678"
        self.user.objects.create_user(card_id=self.card_id, password="1234")
    
    def test_pin_valid(self):
        self.assertFalse(pin_valid(""))
        self.assertFalse(pin_valid("123"))
        self.assertFalse(pin_valid("2233"))
        self.assertFalse(pin_valid("2234"))
        self.assertFalse(pin_valid("1233"))
        self.assertFalse(pin_valid("____"))
        self.assertFalse(pin_valid("1abc"))
        self.assertTrue(pin_valid("1234"))
    
    def test_login_card(self):
        # Request hasn't method Post
        client = Client()
        response = client.get('/')
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'card/login.html')
        
        # Wrong card ID
        response = client.post('/', {'username': '1234567812345600', 'password': '1234'})
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'card/login.html')
        
        # Wrong pin
        response = client.post('/', {'username': self.card_id, 'password': '1200'})
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'card/login.html')
        
        # Auth success
        response = client.post('/', {'username': self.card_id, 'password': '1234'})
        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))
    
    def test_home(self):
        client = Client()
        
        response = client.get(reverse('home'))
        self.assertEquals(response.status_code, 302)
        
        client.login(card_id=self.card_id, password="1234")
        
        response = client.get(reverse('home'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'card/home.html')
    
    def test_balance(self):
        client = Client()
        
        response = client.get(reverse('balance'))
        self.assertEquals(response.status_code, 302)
        
        client.login(card_id=self.card_id, password="1234")
        
        response = client.get(reverse('balance'))
        
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'card/balance.html')

    def test_correct_pin_change(self):
        client = Client()
    
        response = client.get(reverse('home'))
        self.assertEquals(response.status_code, 302)
    
        client.login(card_id=self.card_id, password="1234")

        card = self.user.objects.get_card(self.card_id)
        print(f"Before changing password {card}")
        self.assertTrue(card.check_password('1234'))
    
        self.assertTrue(self.pin_changing(client, '1235', '1235', '1235'))

    def test_wrong_pin_change(self):
        client = Client()

        response = client.get(reverse('home'))
        self.assertEquals(response.status_code, 302)

        client.login(card_id=self.card_id, password="1234")

        card = self.user.objects.get_card(self.card_id)
        print(f"Before changing password {card}")
        self.assertTrue(card.check_password('1234'))

        # Incorrect confirm
        self.assertTrue(self.pin_changing(client, '1235', '1236', '1234'))

        # The same pin
        self.assertTrue(self.pin_changing(client, '1234', '1236', '1234'))

        # Incorrect pin format
        self.assertTrue(self.pin_changing(client, 'qwer', '1236', '1234'))

    def test_cash(self):
        client = Client()

        response = client.get(reverse('home'))
        self.assertEquals(response.status_code, 302)

        client.login(card_id=self.card_id, password="1234")

        # Default balance equals 1000
        self.assertEquals(self.cash_changing(client, 100), 900)
        self.assertEquals(self.cash_changing(client, 1000), 0)
        self.assertEquals(self.cash_changing(client, -100), 900)
        self.assertEquals(self.cash_changing(client, 'fewfwef'), 1000)
        self.assertEquals(self.cash_changing(client, 1001), 1000)

    def test_refill(self):
        client = Client()

        response = client.get(reverse('home'))
        self.assertEquals(response.status_code, 302)

        client.login(card_id=self.card_id, password="1234")

        # Default balance equals 1000
        self.assertEquals(self.refill_changing(client, 100), 1100)
        self.assertEquals(self.refill_changing(client, 0), 1000)
        self.assertEquals(self.refill_changing(client, -100), 1100)
        self.assertEquals(self.refill_changing(client, 'fewfwef'), 1000)

    def pin_changing(self, client, first_pin, second_pin, current_pin):
        response = client.post(reverse('pin_change'), {'password': first_pin})
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'card/pin_change.html')

        response = client.post(reverse('pin_change'), {'password': second_pin})
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'card/pin_change.html')

        card = self.user.objects.get_card(self.card_id)
        print(f"After changing password {card}")
        return card.check_password(current_pin)

    def cash_changing(self, client, amount):
        card = self.user.objects.get_card(self.card_id)
        card.balance = 1000
        card.save()
        response = client.post(reverse('cash'), {'amount': amount})
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'card/cash.html')
        card = self.user.objects.get_card(self.card_id)
        return card.balance

    def refill_changing(self, client, amount):
        card = self.user.objects.get_card(self.card_id)
        card.balance = 1000
        card.save()
        response = client.post(reverse('refill'), {'amount': amount})
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'card/refill.html')
        card = self.user.objects.get_card(self.card_id)
        return card.balance
