from django.shortcuts import render, redirect


def home(request):
    """Dashboard/panel principal - requiere sesión (el middleware lo controla)."""
    if not request.session.get('usuario_id'):
        return redirect('login')
    return render(request, 'index.html')