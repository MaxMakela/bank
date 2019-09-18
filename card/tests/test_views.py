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

    def test_pin_change(self):
        client = Client()
    
        response = client.get(reverse('home'))
        self.assertEquals(response.status_code, 302)
    
        client.login(card_id=self.card_id, password="1234")

        card = self.user.objects.get_card(self.card_id)
        print(f"Before changing password {card}")
        self.assertTrue(card.check_password('1234'))
    
        response = client.post(reverse('pin_change'), {'password': '1235'})
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'card/pin_change.html')
    
        response = client.post(reverse('pin_change'), {'password': '1235'})
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'card/pin_change.html')
        
        card = self.user.objects.get_card(self.card_id)
        print(f"After changing password {card}")
        self.assertTrue(card.check_password('1235'))

    def test_cash(self):
        client = Client()
    
        response = client.get(reverse('home'))
        self.assertEquals(response.status_code, 302)
    
        client.login(card_id=self.card_id, password="1234")

        card = self.user.objects.get_card(self.card_id)
        print(f"Before changing password {card}")
        self.assertTrue(card.check_password('1234'))