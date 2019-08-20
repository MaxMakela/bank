from django.test import TestCase, Client
from card.views import *
from django.contrib.auth import get_user_model


class TestCardProcessing(TestCase):
    
    def setUp(self):
        User = get_user_model()
        self.card = User.objects.create_user(card_id="1234567812345678", password="1234")
    
    def test_pin_valid(self):
        self.assertFalse(pin_valid(""))
        self.assertFalse(pin_valid(""))
        self.assertFalse(pin_valid("123"))
        self.assertFalse(pin_valid("2233"))
        self.assertFalse(pin_valid("2234"))
        self.assertFalse(pin_valid("1233"))
        self.assertFalse(pin_valid("____"))
        self.assertFalse(pin_valid("1abc"))
        self.assertTrue(pin_valid("1234"))
    
    def test_login_card(self):
        # c = Client()
        # c.login(card_id="1234567812345678", password="1234")
        #
        # response = self.client.get(reverse('home'))
        # self.assertEquals(response.status_code, 200)
        pass
    
    def test_home(self):
        client = Client()
        client.login(card_id="1234567812345678", password="1234")
        
        response = client.get(reverse('home'))
        
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'card/home.html')

    def test_balance(self):
        client = Client()
        client.login(card_id="1234567812345678", password="1234")
    
        response = client.get(reverse('balance'))
    
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'card/balance.html')