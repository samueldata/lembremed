from django.http import HttpResponse
from django.shortcuts import render
from .models import Morador
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.auth.decorators import permission_required

#Pagina principal dos moradores
#Lista todos os moradores
@permission_required('lembremed.pode_gerenciar_morador')
def morador_listar(request):
    moradores = Morador.objects.all()
    context = {'lista_moradores': moradores}
    return render(request, 'morador/index.html', context)


@permission_required('lembremed.pode_gerenciar_morador')
def morador_editar(request, pcpf):
    morador = Morador.objects.filter(cpf=pcpf)[0]
    #return HttpResponse(morador.nome)
    context = {'morador': morador}
    return render(request, 'morador/cadastro.html', context)


@permission_required('lembremed.pode_gerenciar_morador')
def morador_cadastrar(request):
    context = {}
    return render(request, 'morador/cadastro.html', context)


@permission_required('lembremed.pode_gerenciar_morador')
def morador_salvar(request):
    if request.method == 'POST':
        # Pegando a variável POST
        pcpf = request.POST.get('cpf')
        pnome = request.POST.get('nome')
        pdt_nascimento = request.POST.get('dt_nascimento')

        #Verifica se estah editando
        if (request.POST.get('edit')):
            morador = Morador.objects.get(cpf=pcpf)
            morador.nome = pnome
            morador.dt_nascimento = pdt_nascimento

        else:
            morador = Morador(cpf=pcpf, nome=pnome, dt_nascimento=pdt_nascimento)

        morador.save()

        return HttpResponse("morador salvo com sucesso")
    else:
        return HttpResponse("erro por GET no salvar")


@permission_required('lembremed.pode_gerenciar_morador')
def morador_excluir(request, pcpf):
    #Verifica se o cpf existe
    morador = Morador.objects.get(cpf=pcpf)
    if (morador):
        morador.delete()
        return HttpResponse("excluido com sucesso")
    else:
        return HttpResponse("Erro ao localizar cpf")