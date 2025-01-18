from django.test import TestCase

from monitor.views import notify_on_discord
from .models import Website,StatusHistory
# from django.urls import reverse
from unittest.mock import patch, AsyncMock
# Create your tests here.
class TestModles(TestCase):
    def test_website(self):
        website = Website.objects.create(name="For testing..", url="http://localhost:3000")

        # Check if the last website's name is correct
        self.assertEqual(Website.objects.last().name, "For testing..")

        # Fetch the created website from the database
        website = Website.objects.get(id=website.id)

        # Delete the website
        website.delete()

        # Ensure the website is deleted by checking the count
        self.assertEqual(Website.objects.count(), 0)

        # Create a new website after deletion (optional)
        Website.objects.create(name="New Website", url="http://new-url.com")
        self.assertEqual(Website.objects.count(), 1)
class TestViews(TestCase):
    def test_website_and_check(self):
        response=Website.objects.create(name="Demo2",url="http://localhost:3000")
        self.assertEqual(Website.objects.last().name, 'Demo2')
    
    @patch('httpx.AsyncClient.post')  # Mock the HTTP POST request
    async def test_notify_on_discord_success(self, mock_post):
        # Set up mock response
        mock_post.return_value = AsyncMock(status_code=204)

        # Create test data
        website = Website(name="Test Website", url="http://example.com")
        status_history = StatusHistory(status="up")

        # Call the function
        result = await notify_on_discord(website, status_history)
        self.assertEqual(result,True)
        # Assertions
        self.assertTrue(result)
        mock_post.assert_called_once() 
