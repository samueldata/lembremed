from django.http import HttpResponse
from django.shortcuts import render
from lembremed.models import Profissional
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.auth.decorators import permission_required

#Pagina principal dos profissionais
#Lista todos os profissionais
@permission_required('lembremed.pode_gerenciar_profissional')
def profissional_listar(request):
    profissionais = Profissional.objects.all()
    context = {'lista_profissionais': profissionais}
    print(profissionais.count())
    return render(request, 'profissional/index.html', context)

def profissional_editar(request, pcpf):
    profissional = Profissional.objects.filter(cpf=pcpf)[0]
    context = {
        'profissional': profissional,
        'user': profissional.user,
        }
    return render(request, 'profissional/cadastro.html', context)

def profissional_cadastrar(request):
    context = {}
    return render(request, 'profissional/cadastro.html', context)

def profissional_salvar(request):
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

            user = profissional.user
            user.email = pemail
            if (psenha):
                user.set_password(psenha)
            user.save()

        else:
            user = get_user_model().objects.create_user(username=pcpf, email=pemail, password=psenha)
            user.user_permissions.add(Permission.objects.get(codename='pode_gerenciar_morador'))
            user.user_permissions.add(Permission.objects.get(codename='pode_medicar_morador'))
            user.save()

            profissional = Profissional.objects.create(cpf=pcpf, nome=pnome, coren=pcoren, user=user)
            
        
        return HttpResponse("profissional salvo com sucesso")
    else:
        return HttpResponse("erro por GET no salvar")


def profissional_excluir(request, pcpf):
    #Verifica se o cpf existe
    profissional = Profissional.objects.get(cpf=pcpf)
    if (profissional):
        profissional.delete()

        profissional.user.delete()
        
        return HttpResponse("excluido com sucesso")
    else:
        return HttpResponse("Erro ao localizar cpf")