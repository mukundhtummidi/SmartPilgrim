from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import json

# Locally-owned chatbot behavior as asset system (no API key dependency)
CHATBOT_KB = {
    'hello': 'Hello! I am Pilgrim Bot. How can I assist your temple visit today?',
    'hi': 'Hi there! Ask me about temple bookings, crowd-safety, or donation options.',
    'booking': 'You can book darshan slots in the Bookings section. Would you like me to guide you?',
    'crowd': 'For crowd forecasts check the Home section, and use off-peak timings for a smoother visit.',
    'donation': 'Donate securely using the Contributions section, and get instant receipts via email.',
    'sos': 'If you are in an emergency, use the Safety > SOS page or contact temple officials immediately.',
}


def chatbot_view(request):
    return render(request, 'crowd_ai/chatbot.html')


@csrf_exempt
def chatbot_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
    except Exception:
        return JsonResponse({'error': 'Invalid JSON payload'}, status=400)

    if not user_message:
        return JsonResponse({'reply': 'Please send a question to the chatbot.'})

    lower_msg = user_message.lower()
    for key, answer in CHATBOT_KB.items():
        if key in lower_msg:
            return JsonResponse({'reply': answer})

    # Fallback answer as local asset knowledge
    return JsonResponse({'reply': 'I am an in-system assistant. Ask about bookings, crowd, donations, or SOS.'})
