from functools import wraps
from lembremed.models import Profissional, Instituicao

def adiciona_contexto(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):

        #Cria a variavel com valor padrao
        contexto_padrao = {'usuario': {'nome': '-usuario-'}}

        #Verifica se o usuario estah logado
        if (request.user.is_authenticated):
            #verifica se o usuario eh profissional
            usuario = Profissional.objects.filter(usuario=request.user).first()
            if (usuario):
                contexto_padrao = {'usuario': usuario}
            else:
                usuario = Instituicao.objects.filter(usuario=request.user).first()
                if (usuario):
                    contexto_padrao = {'usuario': usuario}
        
        
        # Chame a função original da view e adicione o contexto
        return func(request, contexto_padrao=contexto_padrao, *args, **kwargs)
    return wrapper
