from django.http import HttpResponse
from django.shortcuts import render
from lembremed.models import Estoque, Medicamento, Administra, Morador, Profissional
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.auth.decorators import permission_required
from datetime import datetime

#Pagina principal dos medicamentos
#Lista todos os medicamentos
def medicamento_listar(request, pcpf):
    estoques = Estoque.objects.filter(morador=pcpf)

    estoques_administrados = []
    for estoque in estoques:
        ultima_administracao = Administra.objects.filter(estoque=estoque).order_by('-dthr_administracao').first()
        estoques_administrados.append({ #Cria o objeto com o estoque e sua ultima administracao
            'estoque': estoque,
            'ultima_administracao': ultima_administracao,
            'duracao': estoque.qtd_disponivel / (estoque.frequencia * estoque.prescricao)
        })

    context = {'lista_estoques': estoques_administrados}
    
    return render(request, 'medicamento/index.html', context)


def medicamento_editar(request, pcpf, pcodigo):
    estoque = Estoque.objects.get(codigo=pcodigo, morador__cpf=pcpf)

    arr_medicamentos = Medicamento.objects.all().order_by('principio')
    tipos_apresentacao = Estoque.tipos_apresentacao

    context = {
        'estoque': estoque,
        'arr_medicamentos': arr_medicamentos,
        'tipos_apresentacao': tipos_apresentacao,
        }
    return render(request, 'medicamento/cadastro.html', context)


def medicamento_cadastrar(request, pcpf):
    arr_medicamentos = Medicamento.objects.all().order_by('principio')
    tipos_apresentacao = Estoque.tipos_apresentacao

    context = {
        'cpf': pcpf,
        'arr_medicamentos': arr_medicamentos,
        'tipos_apresentacao': tipos_apresentacao,
        }
    return render(request, 'medicamento/cadastro.html', context)


def medicamento_salvar(request, pcpf):
    if request.method == 'POST':
        # Pegando a variável POST
        pcodigo = request.POST.get('codigo')
        pcodigo_medicamento = request.POST.get('codigo_medicamento')
        papresentacao = request.POST.get('apresentacao')
        pconcentracao = request.POST.get('concentracao')
        pprescricao = request.POST.get('prescricao')
        pfrequencia = request.POST.get('frequencia')
        phorarios = request.POST.get('horarios')
        pqtd_disponivel = request.POST.get('qtd_disponivel')

        #Verifica se estah editando
        if (request.POST.get('edit')):
            estoque = Estoque.objects.get(codigo=pcodigo)
            estoque.medicamento = Medicamento.objects.get(codigo=pcodigo_medicamento)
            estoque.apresentacao = papresentacao
            estoque.concentracao = pconcentracao
            estoque.prescricao = pprescricao
            estoque.frequencia = pfrequencia
            estoque.horarios = phorarios
            estoque.qtd_disponivel = pqtd_disponivel
            estoque.save()

        else:
            Estoque.objects.create(
                morador = Morador.objects.get(cpf=pcpf),
                medicamento = Medicamento.objects.get(codigo=pcodigo_medicamento),
                apresentacao = papresentacao,
                concentracao = pconcentracao,
                prescricao = pprescricao,
                frequencia = pfrequencia,
                horarios = phorarios,
                qtd_disponivel = pqtd_disponivel,
            )
                

        # Após criar o usuário, atribua o papel associado

        return HttpResponse("medicamento salvo com sucesso")
    else:
        return HttpResponse("erro por GET no salvar")


def medicamento_excluir(request, pcpf, pcodigo):
    #Verifica se o estoque existe para o cpf
    estoque = Estoque.objects.get(codigo=pcodigo, morador__cpf=pcpf)
    if (estoque):
        #Exclui as administracoes deste estoque
        Administra.objects.filter(estoque=estoque).delete()

        #Exclui o estoque
        estoque.delete()

        return HttpResponse("Administração cadastrada com sucesso!")
    
    else:
        return HttpResponse("Erro ao localizar estoque")
    

def medicamento_administrar(request, pcpf, pcodigo):
    #Verifica se o estoque existe para o cpf
    estoque = Estoque.objects.get(codigo=pcodigo, morador__cpf=pcpf)
    if (estoque):
        #Atualiza o estoque
        estoque.qtd_disponivel -= estoque.prescricao
        estoque.save()

        #Registra a administracao
        Administra.objects.create(
            profissional = Profissional.objects.get(user=request.user),
            morador = estoque.morador,
            estoque = estoque,
            dthr_administracao = datetime.now(),
        )
        return HttpResponse("Administração cadastrada com sucesso!")
    
    else:
        return HttpResponse("Erro ao localizar estoque")
    