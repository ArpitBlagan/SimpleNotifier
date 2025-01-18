import threading
import time
import requests
import json
import os
import httpx
from asgiref.sync import sync_to_async
from urllib.parse import urlparse
import requests.exceptions
from django_ratelimit.decorators import ratelimit
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework.decorators import api_view

from .models import Website, StatusHistory  # Ensure this imports the models correctly



async def notify_on_discord(website,statusHistory):
    
    payload = {
        "content":f"Status update 👀\n",
            "embeds": [{
            "title": "Alert ‼️",
            "fields": [
                {"name": "Name", "value": website.name},
                {"name": "URL", "value": website.url},
                {"name": "Status", "value": statusHistory.status},
            ]
        }]
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(os.getenv('WEBHOOK_URL'), data=json.dumps(payload), headers=headers)   
            if response.status_code == 204:
                print("Message sent successfully.")
                return True
            else:
                print(f"Failed to send message. Status code: {response.status_code}, Response: {response.text}")
                return False
    except httpx.HTTPError as e:
        print("Something went wrong while sending notification to discrod",e)
        return False
        
        




@api_view(['GET'])
def get_website(request, id):
    try:
        website = Website.objects.get(id=id)
        # Serialize the website data
        website_data = {
            'id': website.id,
            'url': website.url,
            'created_at': website.created_at,
            # Add other fields as necessary
        }
        return Response(website_data, status=200)
    except Website.DoesNotExist:
        return Response({"message": "Website with the given ID is not found :("}, status=404)



@api_view(['GET'])
def get_websites(request):
    websites=list(Website.objects.all().values())
    return Response(websites,status=200)


@api_view(['GET'])
def get_histories(request):
    websites=list(StatusHistory.objects.select_related('website').all().values(
        'website__name',  # Include the website name
        'website__url',   # Include the website URL
        'status',         # Include the status from StatusHistory
        'checked_at' 
    ))
    
    return Response(websites,status=200)    

@ratelimit(key='ip', rate='5/m')
@api_view(['POST'])
def add_website(request):
    body = json.loads(request.body)
    #validate the body's url
    parsed_url = urlparse(body['url'])
    if not all([parsed_url.scheme, parsed_url.netloc]):
        print(f"Invalid URL: {website.url}")
        return Response({"message":"Ivalid url please provide a valid one :("},status=400)
    try:
        # Check if the website already exists
        website, created = Website.objects.get_or_create(url=body['url'], defaults={'name': body['name']})
        
        if not created:
            return Response({"message": "Website already exists"}, status=401)

        # Start the thread to begin monitoring the site status
        start_monitoring(website)
        return Response({"message": "Website added successfully :)"}, status=201)

    except Exception as e:
        print(e)
        return Response({"message": "Internal server error"}, status=500)

@ratelimit(key='ip', rate='5/m')
@api_view(['DELETE'])
def delete_website(request, id):
    try:
        website = Website.objects.get(id=id)
        
        # Set the stop flag to signal the monitoring thread to stop
        website.stop_monitoring = True  # Assuming you have a field for this in your model
        website.save()  # Save the change before deletion
        
        website.delete()  # Delete the website
        
        return JsonResponse({"message": "Website deleted successfully :)"}, status=200)
    
    except Website.DoesNotExist:
        return JsonResponse({"error": "Website not found"}, status=404)

import httpx
import asyncio
from asgiref.sync import sync_to_async
from .models import StatusHistory  # Adjust based on your project structure

async def monitor_website(website):
    previous_status = None
    max_retries = 3  # Maximum number of retries for failed requests
    
    while not website.stop_monitoring:  # Check the stop flag
        print("Polling the website :)")
        current_status = None
        
        async with httpx.AsyncClient() as client:
            for attempt in range(max_retries):
                try:
                    response = await client.get(website.url, timeout=5)
                    print(response)
                    current_status = 'up' if response.status_code == 200 else 'down'
                    break  # Exit the retry loop if successful
                
                except httpx.RequestError as e:
                    print(f"Attempt {attempt + 1} failed: {e}")
                    current_status = 'down'
                    await asyncio.sleep(2)  # Non-blocking sleep before retrying

        # If we exhausted all attempts and still got an error
        if current_status == 'down' and attempt == max_retries - 1:
            print(f"Failed to reach {website.url} after {max_retries} attempts.")
        
        # Check if status has changed
        if current_status != previous_status:
            statusHistory = await sync_to_async(StatusHistory.objects.create)(website=website, status=current_status)
            previous_status = current_status
            
            sent = False
            count = 0
            
            while count < 3 and not sent:
                sent = await notify_on_discord(website, statusHistory)
                count += 1
            
            if sent:
                print("Discord notification sent successfully :)")

        await asyncio.sleep(60)  # Non-blocking sleep before the next polling
  # Wait before the next polling


def start_monitoring(website):
    print("start_monitoring function got triggered :)")

    # Define a wrapper function to run the async function in an event loop
    def run_monitor():
        asyncio.run(monitor_website(website))  # Run the async function

    # Create and start the thread
    thread = threading.Thread(target=run_monitor)
    thread.daemon = True  # Allow thread to exit when main program does
    thread.start()
