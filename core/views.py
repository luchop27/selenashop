from django.shortcuts import render


def inicio(request):
    """Renderiza la plantilla inicio.html"""
    return render(request, 'index.html')


def home_02(request):
    """Renderiza la plantilla home-02.html"""
    return render(request, 'home-02.html')

