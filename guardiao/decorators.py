from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def nivel_acesso_minimo(nivel_requerido):
    """
    Decorador para restringir acesso com base no nível do operador.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            operador = getattr(request.user, 'operador', None)
            if not operador or operador.nivel_acesso < nivel_requerido:
                messages.error(
                    request, "Você não tem permissão para acessar esta página.")
                return redirect('pronto_armamento')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
