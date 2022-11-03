import json

from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from django_telethon.models import App, ClientSession, Login, LoginStatus


def _get_data(request):
    if 'application/json' in request.META.get('CONTENT_TYPE', ''):
        data = request.body.decode('utf-8')
        data = json.loads(data)
    else:
        data = request.POST
    return data


@csrf_exempt
def send_code_request_view(request):
    data = _get_data(request)
    phone_number = data.get('phone_number', None)
    client_session_name = data.get('client_session_name', None)
    if not App.objects.all().exists():
        return JsonResponse({'error': 'No app found'}, status=400)

    if not phone_number or not client_session_name:
        return JsonResponse({'error': 'Missing phone number or client session name'}, status=400)
    client_session, is_created = ClientSession.objects.get_or_create(name=client_session_name)

    if client_session.login_status != LoginStatus.LOGIN_REQUIRED:
        return JsonResponse({'error': 'Client session is not in login required status'}, status=400)

    if Login.objects.filter(client_session=client_session).have_to_send_code().exists():
        return JsonResponse({'error': 'Client session is already waiting for send code.'}, status=400)

    login = Login.objects.create(client_session=client_session, phone_number=phone_number, have_to_send_code=True)
    return JsonResponse({'login_id': login.id}, status=200)


@csrf_exempt
def login_user_view(request):
    data = _get_data(request)
    client_session_name = data.get('client_session_name', None)
    phone_number = data.get('phone_number', None)
    code = data.get('code', None)
    password = data.get('password', None)

    if not App.objects.all().exists():
        return JsonResponse({'error': 'No app found'}, status=400)

    if not phone_number or not client_session_name or not code:
        return JsonResponse({'error': 'Missing phone number or client session name or code'}, status=400)
    try:
        client_session = ClientSession.objects.get(name=client_session_name)
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'Client session does not exists'}, status=400)

    if client_session.login_status != LoginStatus.LOGIN_REQUIRED:
        return JsonResponse({'error': 'Client session is not in login required status'}, status=400)

    if not password:
        password = None
    if (
        login := Login.objects.filter(have_to_send_code=False, client_session=client_session)
        .order_by('-created_at')
        .first()
    ):
        login.code = code
        login.passcode = password
        login.save()
    return JsonResponse({}, status=200)


@csrf_exempt
def login_bot_view(request):
    data = _get_data(request)
    client_session_name = data.get('client_session_name', None)
    bot_token = data.get('bot_token', None)

    if not App.objects.all().exists():
        return JsonResponse({'error': 'No app found'}, status=400)

    if not bot_token or not client_session_name:
        return JsonResponse({'error': 'Missing bot token or client session name or code'}, status=400)

    client_session, _ = ClientSession.objects.get_or_create(name=client_session_name)

    if client_session.login_status != LoginStatus.LOGIN_REQUIRED:
        return JsonResponse({'error': 'Client session is not in login required status'}, status=400)

    login = Login.objects.create(client_session=client_session, bot_token=bot_token, have_to_send_code=False)
    return JsonResponse({'login_id': login.id}, status=200)
