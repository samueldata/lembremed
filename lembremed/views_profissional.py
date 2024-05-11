from django.http import HttpResponse
from django.shortcuts import render
from lembremed.models import Profissional
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.auth.decorators import permission_required
from lembremed.decorators import adiciona_contexto

#Pagina principal dos profissionais
#Lista todos os profissionais
@adiciona_contexto
@permission_required('lembremed.pode_gerenciar_profissional')
def profissional_listar(request, contexto_padrao):
    #Somente instituicoes cadastram profissionais
    profissionais = Profissional.objects.filter(instituicao=contexto_padrao['usuario'])
    context = {'lista_profissionais': profissionais}
    
    return render(request, 'profissional/index.html', {**context, **contexto_padrao})


@permission_required('lembremed.pode_gerenciar_profissional')
def profissional_editar(request, pcpf):
    profissional = Profissional.objects.filter(cpf=pcpf)[0]
    context = {
        'profissional': profissional,
        'usuario': profissional.usuario,
        }
    return render(request, 'profissional/cadastro.html', context)


@permission_required('lembremed.pode_gerenciar_profissional')
def profissional_cadastrar(request):
    context = {}
    return render(request, 'profissional/cadastro.html', context)


@adiciona_contexto
@permission_required('lembremed.pode_gerenciar_profissional')
def profissional_salvar(request, contexto_padrao):
    if request.method == 'POST':
        # Pegando a variável POST
        pcpf = request.POST.get('cpf')
        pnome = request.POST.get('nome')
        pemail = request.POST.get('email')
        pcoren = request.POST.get('coren')
        #pcnpj_instituicao = request.POST.get('cnpj_instituicao')
        psenha = request.POST.get('senha')

        #Verifica se estah editando
        if (request.POST.get('edit')):
            profissional = Profissional.objects.get(cpf=pcpf)
            profissional.nome = pnome
            profissional.coren = pcoren
            #profissional.cnpj_instituicao = pcnpj_instituicao
            profissional.save()

            usuario = profissional.usuario
            usuario.email = pemail
            if (psenha):
                usuario.set_password(psenha)
            usuario.save()

        else:
            usuario = get_user_model().objects.create_user(username=pcpf, email=pemail, password=psenha)
            usuario.user_permissions.add(Permission.objects.get(codename='pode_gerenciar_morador'))
            usuario.user_permissions.add(Permission.objects.get(codename='pode_medicar_morador'))
            usuario.save()

            profissional = Profissional.objects.create(cpf=pcpf, nome=pnome, instituicao=contexto_padrao['usuario'], coren=pcoren, usuario=usuario)
            
        return HttpResponse("profissional salvo com sucesso")
    else:
        return HttpResponse("erro por GET no salvar")


@permission_required('lembremed.pode_gerenciar_profissional')
def profissional_excluir(request, pcpf):
    #Verifica se o cpf existe
    profissional = Profissional.objects.get(cpf=pcpf)
    if (profissional):
        profissional.delete()

        profissional.user.delete()
        
        return HttpResponse("excluido com sucesso")
    else:
        return HttpResponse("Erro ao localizar cpf")