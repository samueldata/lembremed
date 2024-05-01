from django.http import HttpResponse
from django.shortcuts import render
from morador.models import Profissional

#pagina inicial do lembremed
def index(request):
    return HttpResponse("index")

#Pagina principal dos profissionais
#Lista todos os profissionais
def profissional_listar(request):
    profissionais = Profissional.objects.all()
    context = {'lista_profissionais': profissionais}
    return render(request, 'profissional/index.html', context)

def profissional_editar(request, pcpf):
    profissional = Profissional.objects.filter(cpf=pcpf)[0]
    #return HttpResponse(profissional.nome)
    context = {'profissional': profissional}
    return render(request, 'profissional/cadastro.html', context)

def profissional_cadastrar(request):
    context = {}
    return render(request, 'profissional/cadastro.html', context)

def profissional_salvar(request):
    if request.method == 'POST':
        # Pegando a variável POST
        pcpf = request.POST.get('cpf')
        pnome = request.POST.get('nome')
        pcoren = request.POST.get('coren')
        #pcnpj_instituicao = request.POST.get('cnpj_instituicao')
        psenha = request.POST.get('senha')

        #Verifica se estah editando
        if (request.POST.get('edit')):
            profissional = Profissional.objects.get(cpf=pcpf)
            profissional.nome = pnome
            profissional.coren = pcoren
            #profissional.cnpj_instituicao = pcnpj_instituicao
            profissional.senha = psenha

        else:
            profissional = Profissional(cpf=pcpf, nome=pnome, coren=pcoren, senha=psenha)

        profissional.save()

        return HttpResponse("profissional salvo com sucesso")
    else:
        return HttpResponse("erro por GET no salvar")


def profissional_excluir(request, pcpf):
    #Verifica se o cpf existe
    profissional = Profissional.objects.get(cpf=pcpf)
    if (profissional):
        profissional.delete()
        return HttpResponse("excluido com sucesso")
    else:
        return HttpResponse("Erro ao localizar cpf")