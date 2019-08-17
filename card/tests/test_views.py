from django.test import SimpleTestCase
from card.views import pin_valid


class TestCardProcessing(SimpleTestCase):
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
