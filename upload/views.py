from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import DocumentForm
from .models import Document

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
