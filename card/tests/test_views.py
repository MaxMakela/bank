from django.test import TestCase, Client
from card.views import *
from django.contrib.auth import get_user_model


class TestCardProcessing(TestCase):
    
    def setUp(self):
        User = get_user_model()
        self.card = User.objects.create_user(card_id="1234567812345678", password="1234")
    
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
        response = client.post('/', {'username': '1234567812345678', 'password': '1200'})
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'card/login.html')
        
        # Auth success
        response = client.post('/', {'username': '1234567812345678', 'password': '1234'})
        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))
    
    def test_home(self):
        client = Client()
        
        response = client.get(reverse('home'))
        self.assertEquals(response.status_code, 302)
        
        client.login(card_id="1234567812345678", password="1234")
        
        response = client.get(reverse('home'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'card/home.html')
    
    def test_balance(self):
        client = Client()
        
        response = client.get(reverse('balance'))
        self.assertEquals(response.status_code, 302)
        
        client.login(card_id="1234567812345678", password="1234")
        
        response = client.get(reverse('balance'))
        
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'card/balance.html')
