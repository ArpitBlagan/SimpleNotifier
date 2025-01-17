import threading
import time
import requests
import json
import os
from django_ratelimit.decorators import ratelimit
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework.decorators import api_view

from .models import Website, StatusHistory  # Ensure this imports the models correctly


@api_view(['POST'])
def notify_on_discord(request):
    body=json.loads(request.body)
    payload = {
        "content": body['message']  # The message you want to send
    }
    
    headers = {
        "Content-Type": "application/json"
    }

    responsse = requests.post(os.getenv('WEBHOOK_URL'), data=json.dumps(payload), headers=headers)

    if responsse.status_code == 204:
        print("Message sent successfully.")
        return Response({"message":"Successfully sent :)"},status=200)
    else:
        print(f"Failed to send message. Status code: {responsse.status_code}, Response: {responsse.text}")
        return Response({"message":"something went wrong :("},status=500)
        




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


@csrf_exempt
@api_view(['GET'])
def get_websites(request):
    websites=list(Website.objects.all().values())
    return Response(websites,status=200)

@csrf_exempt
@api_view(['GET'])
def get_histories(request):
    websites=list(StatusHistory.objects.all().values())
    return Response(websites,status=200)

@ratelimit(key='ip', rate='1/m')
@csrf_exempt
@api_view(['POST'])
def add_website(request):
    body = json.loads(request.body)
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

@ratelimit(key='ip', rate='1/m')
@csrf_exempt
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

def monitor_website(website):
    previous_status = None
    
    while not website.stop_monitoring:  # Check the stop flag
        print("Pooling the website :)")
        try:
            response = requests.get(website.url, timeout=5)
            current_status = 'up' if response.status_code == 200 else 'down'
        except requests.RequestException:
            current_status = 'down'

        if current_status != previous_status:
            StatusHistory.objects.create(website=website, status=current_status)
            # Uncomment to send Discord notifications if implemented
            # send_discord_notification(website, current_status)
            previous_status = current_status

        time.sleep(60)  # Sleep for a defined interval before checking again

def start_monitoring(website):
    print("start_monitoring function got triggered :)")
    thread = threading.Thread(target=monitor_website, args=(website,))
    thread.daemon = True  # Allow thread to exit when main program does
    thread.start()
