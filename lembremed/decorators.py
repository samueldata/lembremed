from functools import wraps
from lembremed.models import Profissional, Instituicao

def adiciona_contexto(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        #Cria a variavel com valor padrao
        contexto = {'usuario': {'nome': '-usuario-'}}

        #Verifica se o usuario estah logado
        if (request.user.is_authenticated):
            #verifica se o usuario eh profissional
            profissional = Profissional.objects.filter(usuario=request.user).first()
            if (profissional):
                contexto = {'usuario': profissional}
            else:
                instituicao = Instituicao.objects.filter(usuario=request.user).first()
                if (instituicao):
                    contexto = {'usuario': instituicao}
        
        # Chame a função original da view e adicione o contexto
        return func(request, *args, contexto_padrao=contexto, **kwargs)
    return wrapper
