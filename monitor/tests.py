from django.test import TestCase
from .models import Website
from django.urls import reverse
# Create your tests here.
class TestModles(TestCase):
    def test_website(self):
        self.website=Website.objects.create(name="For testing..",url="http://localhost:3000")
        self.assertEqual(Website.objects.last().name, "For testing..")
class TestViews(TestCase):
    def test_website_and_check(self):
        response=Website.objects.create(name="Demo2",url="http://localhost:3000")
        print("response",response)
        self.assertEqual(Website.objects.last().name, 'Demo2')