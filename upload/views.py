from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import JsonResponse
from .forms import DocumentForm
from .models import Document
import os
import socket
import requests
from django.views.decorators.csrf import csrf_exempt

def upload_file(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect(reverse('upload_list'))
    else:
        form = DocumentForm()
    return render(request, 'upload/upload_form.html', {'form': form})

def upload_list(request):
    docs = Document.objects.order_by('-uploaded_at')
    return render(request, 'upload/upload_list.html', {'documents': docs})

def frontend_info(request):
    hostname = socket.gethostname()
    container_id = os.environ.get('HOSTNAME', hostname)
    
    backend_info = None
    try:
        backend_url = 'http://backend:8000/api/backend-info/'
        response = requests.get(backend_url, timeout=5)
        if response.status_code == 200:
            backend_info = response.json()
    except Exception as e:
        backend_info = {'error': str(e)}
    
    return JsonResponse({
        'service': 'frontend',
        'frontend_hostname': hostname,
        'frontend_container_id': container_id,
        'backend_response': backend_info,
        'message': f'Frontend servido pela instância: {container_id}'
    })

@csrf_exempt
def backend_info(request):
    hostname = socket.gethostname()
    container_id = os.environ.get('HOSTNAME', hostname)
    
    return JsonResponse({
        'service': 'backend',
        'backend_hostname': hostname,
        'backend_container_id': container_id,
        'message': f'Backend servido pela instância: {container_id}'
    })
