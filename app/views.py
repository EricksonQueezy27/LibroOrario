import calendar
import logging
from typing import Counter
from django.shortcuts import render, redirect
from django.views import View
from .models import *
from django.db import IntegrityError
from datetime import datetime, time
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseNotFound
from django.utils import timezone
from django.http import Http404

from .forms import *
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import user_passes_test
from math import ceil
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# from django_sendsms.backends.base import BaseSmsBackend
import speech_recognition as sr
import pyttsx3

def ouvir():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Diga algo:")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        texto = recognizer.recognize_google(audio, language='pt-PT')  # Português do Brasil
        return texto.lower()
    except sr.UnknownValueError:
        return "Não entendi."
    except sr.RequestError:
        return "Erro de conexão com a API."

def falar(texto):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    for voice in voices:
        if "brazil" in voice.name.lower():  # Procurar voz em português do Brasil
            engine.setProperty('voice', voice.id)
            break
    engine.setProperty('rate', 150)  # Ajusta a velocidade da fala
    engine.say(texto)
    engine.runAndWait()

def index(request):
    if request.method == 'POST':
        # Receber dados do formulário (se houver)
        nome = request.POST.get('nome')
        resposta = request.POST.get('resposta')
        if not nome:
            nome = "usuário"
        
        # Interagir com o assistente de voz
        falar(f"Prazer em te conhecer, {nome}! Como posso te ajudar hoje?")
        resposta_professor_encarregado = ouvir()
        if 'professor' in resposta_professor_encarregado:
            falar(f"Ótimo, {nome}! Estou abrindo o sistema do professor para você.")
            # Redirecionar para a página do professor
            return render(request, 'Professor.html', {'mensagem': f'Olá, {nome}! Você é professor.'})
        elif 'encarregado' in resposta_professor_encarregado:
            falar(f"Entendido, {nome}! Estou abrindo o sistema do encarregado para você.")
            # Redirecionar para a página do encarregado
            return render(request, 'Encarregado.html', {'mensagem': f'Olá, {nome}! Você é encarregado.'})
        else:
            falar(f"Desculpe, {nome}, não entendi. Por favor, repita se é professor ou encarregado.")
            return render(request, 'index.html', {'mensagem': f"Desculpe, {nome}, não entendi. Por favor, repita se é professor ou encarregado."})

    return render(request, 'index.html')

def librooraio(request):
    
    return render(request, 'site.html')



@login_required
def turmas(request):

    professor = Professor.objects.get(user=request.user)
    turmas_do_professor = Turma.objects.filter(professor=professor)
    turmas = professor.turmas_associadas.all()
    numt = professor.turmas_associadas.count()

    context = {
        "professor": professor,
        "turmas_do_professor": turmas_do_professor,
        "turmas_associados": turmas,
        "numt": numt,
    }

    return render(request, "turmas.html", context)
    # return render(request, 'turmas.html', {'turmas': turmas})


# def turmas(request):
#     professor = Professor.objects.get(user=request.user)

#     turmas_do_professor = Turma.objects.filter(professor=professor)
#     turmas_associadas = professor.turmas_associadas.all()


#     context = {
#         'professor': professor,
#         'turmas_do_professor': turmas_do_professor,
#         'turmas_associados': turmas_associadas,

#     }

#     return render(request, 'turmas.html', context)

# @login_required
# def detalhes_turma(request, turma_id):
#     turma = get_object_or_404(Turma, id=turma_id)
#     alunos_relacionados = turma.alunos.all()
#     hora_atual = datetime.now().time()
#     professor = Professor.objects.all()

#     # Corrija a busca da aula atual usando o objeto Horario
#     horario_atual = Horario.objects.filter(
#         turma=turma,
#         hora_inicio__lte=hora_atual,
#         hora_fim__gt=hora_atual
#     ).first()

#     # Verifique se há uma aula atual no horário
#     if horario_atual:
#         aula_atual = horario_atual.aula_set.first()
#     else:
#         aula_atual = None

#     context = {'turma': turma,
#                'alunos_relacionados': alunos_relacionados,
#                'aula_atual': aula_atual,
#                'professor': professor,
#                }
#     return render(request, 'detalhes_turma.html', context)


# Lógica para o caso em que turma_id não é fornecido
# @login_required
# def lista_turmas(request):
#     try:
#         professor = Professor.objects.get(user=request.user)
#     except Professor.DoesNotExist:
#         raise Http404("Professor não encontrado.")

#     turmas_do_professor = professor.turmas_associadas.all()

#     context = {
#         'professor': professor,
#         'turmas_do_professor': turmas_do_professor,
#     }

#     return render(request, 'lista_turmas.html', context)


@login_required
def listar_alunos(request):
    alunos = Aluno.objects.all()
    context = {"alunos": alunos}
    return render(request, "detalhes_turma.html", context)


@login_required
def presencas_disciplina(request, disciplina_id):
    # Obter a disciplina do professor
    disciplina = get_object_or_404(ProfessorDisciplina, id=disciplina_id, professor=request.user.professor)

    # Obter todas as presenças dos alunos nesta disciplina
    presencas = Presenca.objects.filter(aula__disciplina=disciplina.disciplina)

    # Passar os dados para o template
    context = {
        'disciplina': disciplina,
        'presencas': presencas,
    }

    return render(request, 'presencas_disciplina.html', context)

@login_required
def detalhes_aluno(request, aluno_id):
    aluno = get_object_or_404(Aluno, id=aluno_id)
    disciplina_professor = Disciplina.objects.filter(professor=request.user.professor).first()  # Supondo que o usuário logado seja um professor
    presencas_aluno = Presenca.objects.filter(aluno=aluno, aula__disciplina=disciplina_professor)

    # Restante do código...

    context = {
        "aluno": aluno,
        "presencas_aluno": presencas_aluno,
        # Outras variáveis de contexto...
    }
    return render(request, 'detalhes_aluno.html', context)
@login_required
def detalhes_aluno(request, aluno_id):
    aluno = get_object_or_404(Aluno, id=aluno_id)
    informacoes_academicas = InformacoesAcademicas.objects.filter(aluno=aluno)
    disciplina_professor = Disciplina.objects.filter(professor=request.user.professor).first()  # Supondo que o usuário logado seja um professor
    presencas_aluno = Presenca.objects.filter(aluno=aluno, aula__disciplina=disciplina_professor)
    if request.method == "GET":
        form = InformacoesAcademicasForm(request.GET)
        if form.is_valid():
            informacoes_academicas = form.save(commit=False)
            informacoes_academicas.aluno = aluno
            informacoes_academicas.save()
            return redirect("detalhes_aluno", aluno_id=aluno_id)
    else:
        form = InformacoesAcademicasForm()

    presenca_aluno = Presenca.objects.filter(aluno=aluno).exists()

    if request.method == "GET" and "comportamento" in request.GET:
        form_comportamento = ComportamentoForm(request.GET)
        if form_comportamento.is_valid():
            comportamento = form_comportamento.save(commit=False)
            comportamento.aluno = aluno
            comportamento.save()
            return redirect("detalhes_aluno", aluno_id=aluno_id)
    else:
        form_comportamento = ComportamentoForm()

    comportamento_aluno = Comportamento.objects.filter(aluno=aluno).first()

    context = {
        "aluno": aluno,
        "tem_presenca": presenca_aluno,
        "form": form,
        "informacoes_academicas": informacoes_academicas,
        "form_comportamento": form_comportamento,
        "comportamento_aluno": comportamento_aluno,
        "presencas_aluno": presencas_aluno,
        'disciplina_professor':disciplina_professor,
    }
    return render(request, 'detalhes_aluno.html', context)


def get_dynamic_text():
    current_time = datetime.now().time()
    current_weekday = datetime.now().weekday()

    if current_time.hour < 12:
        greeting = "Bom dia, Professor(a)!"
    elif current_time.hour < 18:
        greeting = "Boa tarde, Professor(a)!"
    else:
        greeting = "Boa noite, Professor(a)!"

    if current_weekday < 5:  # Segunda a sexta-feira
        if current_time.hour < 8:
            schedule_text = "Bom dia! Hora de se preparar para as aulas do dia."
        elif current_time.hour < 10:
            schedule_text = "Hora de começar as aulas. Mantenha o foco!"
        elif current_time.hour < 12:
            schedule_text = "Aulas em andamento. Esteja disponível para ajudar os alunos."
        elif current_time.hour < 14:
            schedule_text = "Hora do intervalo. Aproveite para descansar um pouco."
        elif current_time.hour < 16:
            schedule_text = "Retorno das aulas. Continue inspirando seus alunos."
        elif current_time.hour < 18:
            schedule_text = "Aulas do dia encerradas. Hora de preparar o material para amanhã."
        else:
            schedule_text = "Seu dia como professor acabou. Recarregue suas energias!"

    else:  # Fim de semana
        if current_time.hour < 10:
            schedule_text = "Bom dia! Aproveite o fim de semana para recarregar as energias."
        elif current_time.hour < 12:
            schedule_text = "Um novo dia. Que tal revisar seu plano de aulas?"
        elif current_time.hour < 14:
            schedule_text = "Hora do almoço. Descanse e relaxe um pouco."
        elif current_time.hour < 16:
            schedule_text = "Tarde tranquila. Dedique um tempo para sua paixão pela educação."
        elif current_time.hour < 18:
            schedule_text = "Fim de tarde. Reflita sobre seus objetivos como educador."
        else:
            schedule_text = "Boa noite, Professor! Amanhã é um novo dia cheio de oportunidades."

    return greeting, schedule_text

# Exemplo de uso:
for _ in range(6):
    greeting, schedule_text = get_dynamic_text()
    print(greeting)
    print(schedule_text)
    print("-----------------")
    
    
@login_required
def prof(request):
    professor = get_object_or_404(Professor, user=request.user)
    numero_de_turmas = professor.turmas_associadas.count()
    numero_de_disciplinas = professor.disciplinas_associadas.count()
    turmas_associadas = professor.turmas_associadas.all()
    disciplinas_associadas = professor.disciplinas_associadas.all()
    publicidade = Publicidade.objects.all()
    alunos = Aluno.objects.all()
    alunos_relacionados = turmas_associadas.count()
    greeting, schedule_text = get_dynamic_text()

    # Mensagens não respondidas pelo professor
    mensagens_nao_respondidas = MensagemSMS.objects.filter(
        professor=professor, resposta_professor__isnull=True
    )

    # Mensagens respondidas pelo professor
    mensagens_respondidas = MensagemSMS.objects.filter(professor=professor).exclude(
        resposta_professor__isnull=True
    )

    # Contar o número de mensagens respondidas
    numero_mensagens_respondidas = mensagens_respondidas.count()

    # Definir os formulários fora do bloco else
    evento_form = EventoForm()
    sms_form = SMSForm(professor)

    resposta_form = RespostaForm()
    horarios = Horario.objects.filter(professor=professor)
    info_horario = False
    horarios_proximos = {}
    horarios_vencido = {}
    for horarioIndex in horarios:
        curr_date = date.today()
        print(calendar.day_name[curr_date.weekday()])
        print(horarioIndex.dia_semana)
        print(horarioIndex.hora_inicio)

        # Obtendo a data e hora atual
        now = datetime.now()
        horario_inicio = datetime.combine(now.date(), horarioIndex.hora_inicio)
        if (
            calendar.day_name[curr_date.weekday()] == "Monday"
            and horarioIndex.dia_semana == "Segunda"
        ):
            tempo_restante = (horario_inicio - now).total_seconds() / 3600

            # if tempo_restante <= 0:
            #     print("Faltam mais de 2 horas para o início do horário")
            #     info_horario = True
            #     horas = ceil(tempo_restante)
            #     horarios_vencido = {
            #         "id": horarioIndex.id,
            #         "turma": horarioIndex.turma,
            #         "disciplina": horarioIndex.disciplina,
            #         "hora_inicio": horarioIndex.hora_inicio,
            #         "tempo_restante": horas,
            #     }
            #     print(now, "rwerw")

            if tempo_restante <= 2:
                print("Faltam menos de 2 horas para o início do horário")
                info_horario = True
                horas = ceil(tempo_restante)

                horarios_proximos = {
                    "id": horarioIndex.id,
                    "turma": horarioIndex.turma,
                    "disciplina": horarioIndex.disciplina,
                    "hora_inicio": horarioIndex.hora_inicio,
                    "tempo_restante": horas,
                }
            else:
                print(f"Faltam {tempo_restante:.2f} horas para o início do horário")
        if (
            calendar.day_name[curr_date.weekday()] == "Tuesday"
            and horarioIndex.dia_semana == "Terca"
        ):
            tempo_restante = (horario_inicio - now).total_seconds() / 3600
            print("tempo_restante", tempo_restante)
            # if tempo_restante <= 0:
            #     print("Faltam mais de 2 horas para o início do horário")
            #     info_horario = True
            #     horas = ceil(tempo_restante)
            #     horarios_vencido = {
            #         "id": horarioIndex.id,
            #         "turma": horarioIndex.turma,
            #         "disciplina": horarioIndex.disciplina,
            #         "hora_inicio": horarioIndex.hora_inicio,
            #         "tempo_restante": horas,
            #     }
            #     print(now, "rwerw")

            if tempo_restante <= 2:
                print("Faltam menos de 2 horas para o início do horário")
                info_horario = True
                horas = ceil(tempo_restante)

                horarios_proximos = {
                    "id": horarioIndex.id,
                    "turma": horarioIndex.turma,
                    "disciplina": horarioIndex.disciplina,
                    "hora_inicio": horarioIndex.hora_inicio,
                    "tempo_restante": horas,
                }
            else:
                print(f"Faltam {tempo_restante:.2f} horas para o início do horário")
                
                #quarta-feira
        if (
            calendar.day_name[curr_date.weekday()] == "Wednesday"
            and horarioIndex.dia_semana == "Quarta"
        ):
            tempo_restante = (horario_inicio - now).total_seconds() / 3600
            print("tempo_restante", tempo_restante)
            # if tempo_restante <= 0:
            #     print("Faltam mais de 2 horas para o início do horário")
            #     info_horario = True
            #     horas = ceil(tempo_restante)
            #     horarios_vencido = {
            #         "id": horarioIndex.id,
            #         "turma": horarioIndex.turma,
            #         "disciplina": horarioIndex.disciplina,
            #         "hora_inicio": horarioIndex.hora_inicio,
            #         "tempo_restante": horas,
            #     }
            #     print(now, "rwerw")

            if tempo_restante <= 2:
                print("Faltam menos de 2 horas para o início do horário")
                info_horario = True
                horas = ceil(tempo_restante)

                horarios_proximos = {
                    "id": horarioIndex.id,
                    "turma": horarioIndex.turma,
                    "disciplina": horarioIndex.disciplina,
                    "hora_inicio": horarioIndex.hora_inicio,
                    "tempo_restante": horas,
                }
            else:
                print(f"Faltam {tempo_restante:.2f} horas para o início do horário")
                
                #quinta-feira
        if (
            calendar.day_name[curr_date.weekday()] == "Thursday "
            and horarioIndex.dia_semana == "Quinta"
        ):
            tempo_restante = (horario_inicio - now).total_seconds() / 3600
            print("tempo_restante", tempo_restante)
            # if tempo_restante <= 0:
            #     print("Faltam mais de 2 horas para o início do horário")
            #     info_horario = True
            #     horas = ceil(tempo_restante)
            #     horarios_vencido = {
            #         "id": horarioIndex.id,
            #         "turma": horarioIndex.turma,
            #         "disciplina": horarioIndex.disciplina,
            #         "hora_inicio": horarioIndex.hora_inicio,
            #         "tempo_restante": horas,
            #     }
            #     print(now, "rwerw")

            if tempo_restante <= 2:
                print("Faltam menos de 2 horas para o início do horário")
                info_horario = True
                horas = ceil(tempo_restante)

                horarios_proximos = {
                    "id": horarioIndex.id,
                    "turma": horarioIndex.turma,
                    "disciplina": horarioIndex.disciplina,
                    "hora_inicio": horarioIndex.hora_inicio,
                    "tempo_restante": horas,
                }
            else:
                print(f"Faltam {tempo_restante:.2f} horas para o início do horário")

        
        if (
            calendar.day_name[curr_date.weekday()] == "Friday  "
            and horarioIndex.dia_semana == "Sexta"
        ):
            tempo_restante = (horario_inicio - now).total_seconds() / 3600
            print("tempo_restante", tempo_restante)
            # if tempo_restante <= 0:
            #     print("Faltam mais de 2 horas para o início do horário")
            #     info_horario = True
            #     horas = ceil(tempo_restante)
            #     horarios_vencido = {
            #         "id": horarioIndex.id,
            #         "turma": horarioIndex.turma,
            #         "disciplina": horarioIndex.disciplina,
            #         "hora_inicio": horarioIndex.hora_inicio,
            #         "tempo_restante": horas,
            #     }
            #     print(now, "rwerw")

            if tempo_restante <= 2:
                print("Faltam menos de 2 horas para o início do horário")
                info_horario = True
                horas = ceil(tempo_restante)

                horarios_proximos = {
                    "id": horarioIndex.id,
                    "turma": horarioIndex.turma,
                    "disciplina": horarioIndex.disciplina,
                    "hora_inicio": horarioIndex.hora_inicio,
                    "tempo_restante": horas,
                }
            else:
                print(f"Faltam {tempo_restante:.2f} horas para o início do horário")
                
                
    # Filtrar disciplinas associadas ao professor
    disciplinas_associadas_professor = professor.disciplinas_associadas.all()

    selecao_disciplina_form = SelecaoDisciplinaForm(
        disciplinas=disciplinas_associadas_professor
    )

    if request.method == "POST":
        if "selecionar_disciplina" in request.POST:
            selecao_disciplina_form = SelecaoDisciplinaForm(
                request.POST, disciplinas=disciplinas_associadas_professor
            )
            if selecao_disciplina_form.is_valid():
                disciplina_id = selecao_disciplina_form.cleaned_data["disciplina"]
                # redirecione para uma página para iniciar a aula
                return redirect("iniciar_aula", disciplina_id=disciplina_id)

        # Restante do código para processar outros formulários...

    context = {
        'professor': professor,
        'evento_form': evento_form,
        'sms_form': sms_form,
        'publicidade': publicidade,
        'turmas_associados': turmas_associadas,
        'numero_de_turmas': numero_de_turmas,
        'horarios_proximos': horarios_proximos,
        'horarios_vencido': horarios_vencido, 
        'numero_de_disciplinas': numero_de_disciplinas,
        'disciplinas_associadas': disciplinas_associadas,
        'alunos_relacionados': alunos_relacionados,
        'alunos': alunos,
        'mensagens_respondidas': mensagens_respondidas,
        'mensagens_nao_respondidas': mensagens_nao_respondidas,
        'resposta_form': resposta_form,
        'numero_mensagens_respondidas': numero_mensagens_respondidas,
        'selecao_disciplina_form': selecao_disciplina_form,  # Adicione o formulário de seleção de disciplina ao contexto
        'greeting': greeting,
        'schedule_text': schedule_text,
    }

    return render(request, "professor.html", context)

@login_required
def enc(request):
    try:
        encarregado = Encarregado.objects.get(user=request.user)
    except Encarregado.DoesNotExist:
        return HttpResponse("Encarregado não encontrado.")

    publicidade = Publicidade.objects.all()

    # Get students associated with the encarregado
      # Passo 2: Obter os alunos associados ao encarregado
    alunos_associados = encarregado.alunos_associados.all()
    
    # Passo 3: Identificar a aula atual
    # Vamos assumir que a aula atual é identificada por data e hora (isso pode variar dependendo de como você define "aula atual")
    agora = timezone.now().date()
    
    # Passo 4: Filtrar as presenças desses alunos na aula atual
    presencas = Presenca.objects.filter(aluno__in=alunos_associados, data=agora)

    # Renderizar os resultados na template
    context = {
        'encarregado': encarregado,
        'presencas': presencas,
        'publicidade':publicidade,
    }
    return render(request, 'encarregado.html', context)


def aluno_pagou_mes(aluno, mes):
    return Propina.objects.filter(aluno=aluno, mes=mes, pago=True).exists()

@login_required
def historico_pagamentos(request, encarregado_id):
    if request.user.is_authenticated:
        if request.user.encarregado.id != encarregado_id:
            return redirect("pagina_de_erro")

        encarregado = Encarregado.objects.get(id=encarregado_id)
        alunos = encarregado.alunos_associados.all()
        comunicados_pagamento = Comunicado.objects.filter(
            encarregado_destino=encarregado, requerido_pagamento=True
        )

        context = {
            "encarregado": encarregado,
            "alunos": alunos,
            "comunicados_pagamento": comunicados_pagamento,
        }

        return render(request, "historico_pagamentos.html", context)
    else:
        return redirect("login")
@login_required
def historico_pagamentos_aluno(request, aluno_id):
    aluno = Aluno.objects.get(pk=aluno_id)
    
    # Pagamentos de propina do aluno
    propinas_aluno = Propina.objects.filter(aluno=aluno)
    meses_com_status = []
    for month, month_name in Propina.MONTH_CHOICES:
        propina_mes = propinas_aluno.filter(mes=month).first()
        if propina_mes:
            if propina_mes.pago:
                status = 'Pago'
                valor = propina_mes.valor
                icone = 'fa-check-circle text-success'  # Ícone de marcação de verificação verde
            else:
                status = 'A Pagar'
                valor = propina_mes.valor
                icone = 'fa-times-circle text-danger'  # Ícone de marcação de cruz vermelha
        else:
            status = 'A Pagar'
            valor = 0
            icone = 'fa-times-circle text-danger'  # Ícone de marcação de cruz vermelha

        meses_com_status.append({
            'mes': month_name,
            'status': status,
            'valor': valor,
            'icone': icone,
        })

    # Outros pagamentos do aluno
    outros_pagamentos = Pagamento.objects.filter(aluno=aluno, aprovado=True)  # Apenas pagamentos aprovados

    context = {
        'aluno': aluno,
        'meses_com_status': meses_com_status,
        'outros_pagamentos': outros_pagamentos,
    }

    return render(request, 'historico_pagamentos_aluno.html', context)


@login_required
def visualizar_educandos(request, encarregado_id):
    encarregado = get_object_or_404(Encarregado, pk=encarregado_id)
    alunos_associados = encarregado.alunos_associados.all()

    informacoes_academicas_por_aluno = []
    for aluno in alunos_associados:
        informacoes_academicas = InformacoesAcademicas.objects.filter(aluno=aluno)
        boletim = Boletim.objects.filter(
            aluno=aluno
        )  # Supondo que você tenha um modelo Boletim

        informacoes_academicas_por_aluno.append(
            {
                "aluno": aluno,
                "informacoes_academicas": informacoes_academicas,
                "boletim": boletim,  # Adicionando o boletim ao contexto
            }
        )

    context = {
        "encarregado": encarregado,
        "alunos_associados": informacoes_academicas_por_aluno,
    }
    return render(request, "educandos.html", context)

@login_required
def editar_informacao_academica(request, informacao_academica_id):
    informacao_academica = get_object_or_404(
        InformacoesAcademicas, pk=informacao_academica_id
    )

    if request.method == "POST":
        form = InformacoesAcademicasForm(request.POST, instance=informacao_academica)
        if form.is_valid():
            form.save()
            # Redirecionar para a página de detalhes do aluno após a edição
            aluno_id = informacao_academica.aluno.id
            return redirect(reverse("detalhes_aluno", args=[aluno_id]))
    else:
        form = InformacoesAcademicasForm(instance=informacao_academica)

    return render(request, "editar_informacao_academica.html", {"form": form})

@login_required
def excluir_informacao_academica(request, informacao_academica_id):
    informacao_academica = get_object_or_404(
        InformacoesAcademicas, pk=informacao_academica_id
    )

    if request.method == "POST":
        informacao_academica.delete()
        # Redirecionar para a página de detalhes do aluno após a exclusão
        return redirect(reverse("detalhes_aluno", args=[informacao_academica.aluno.id]))
    else:
        # Lógica para renderizar um formulário de confirmação de exclusão
        pass

@login_required
def horario_professor(request, turma_id):
    turma = Turma.objects.get(pk=turma_id)
    horarios = Horario.objects.filter(turma=turma)
    return render(
        request, "detalhes_turma.html", {"turma": turma, "horarios": horarios}
    )


# def visualizar_educandos(request, encarregado_id):
#     encarregado = get_object_or_404(Encarregado, pk=encarregado_id)
#     alunos_associados = encarregado.alunos_associados.all()

#     informacoes_academicas_por_aluno = {}
#     for aluno in alunos_associados:
#         informacoes_academicas_por_aluno[aluno] = InformacoesAcademicas.objects.filter(aluno=aluno)

#     context = {
#         'encarregado': encarregado,
#         'alunos_associados': alunos_associados,
#         'informacoes_academicas_por_aluno': informacoes_academicas_por_aluno,
#     }
#     return render(request, 'educandos.html', context)
# Função auxiliar para obter presenças da aula atual para um aluno específico


def get_presencas_aula_atual(aula_atual):
    presencas_aula_atual = Presenca.objects.filter(aula=aula_atual)
    return presencas_aula_atual


def login(request):
    user_type = request.GET.get("user_type")
    if user_type == "professor":
        welcome_message = "Seja Bem-Vindo Professor!"
    elif user_type == "encarregado":
        welcome_message = "Seja Bem-Vindo Encarregado!"
    else:
        welcome_message = "Voçê não tem permissão para estar nesta pagina"
        return render(
            request,
            "login.html",
            {"welcome_message": welcome_message, "user_type": user_type},
        )


# @login_required
# def perfilenc(request):
#     user_instance = request.user
#     encarregado = get_object_or_404(Encarregado, user=user_instance)
#     if request.method == 'POST':
#         user_form = UserForm(request.POST, instance=user_instance)
#         encarregado_form = EncarregadoForm2(request.POST, request.FILES, instance=encarregado)
#         if user_form.is_valid() and encarregado_form.is_valid():
#             user_instance = user_form.save(commit=False)  # Salvar o usuário separadamente
#             user_instance.set_password(user_form.cleaned_data['password'])  # Definir a senha
#             user_instance.save()  # Salvar o usuário
#             encarregado_form.save()  # Salvar o encarregado
#             return redirect('perfilenc')  # Redirecionar para a mesma página após salvar
#     else:
#         user_form = UserForm(instance=user_instance)
#         encarregado_form = EncarregadoForm2(instance=encarregado)
#     return render(request, 'perfilenc.html', {'user_form': user_form, 'encarregado_form': encarregado_form, 'encarregado': encarregado})

@login_required
def perfilenc(request):
    user_instance = request.user
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user_instance)
        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data['password']
            if password:  # Se uma nova senha foi fornecida, atualize-a
                user.set_password(password)
            user.save()
            return redirect('perfilenc')  # Redirecionar para a página de perfil após salvar
    else:
        form = UserForm(instance=user_instance)
    return render(request, 'perfilenc.html', {'form': form})

@login_required
def editar_encarregado2(request, encarregado_id):
    encarregado = get_object_or_404(Encarregado, pk=encarregado_id)
    if request.method == 'POST':
        form = EncarregadoForm2(request.POST, request.FILES, instance=encarregado)
        if form.is_valid():
            form.save()
              # Redirecionar para a página de perfil ou outra página desejada
    else:
        form = EncarregadoForm2(instance=encarregado)
    return render(request, 'editar_encarregado1.html', {'form': form})

@login_required
def perfilpro(request):
    professor = get_object_or_404(Professor, user=request.user)
    prof = Professor.objects.filter(user=request.user)
    disciplinas = professor.disciplinas_associadas.all() 
    if request.method == "POST":
        form = ProfForm(request.POST, request.FILES, instance=professor)
        if form.is_valid():
            form.save()
        return redirect(perfilpro)
    else:
        form = ProfForm(instance=professor)
    
    context = {
        "professo": professor,
        "disciplinas": disciplinas,
        "form": form,
        "prof": prof,
    }
    return render(request, "perfilpro.html", context)


# @login_required
# def encperf(request):
#     encarregado = get_object_or_404(Encarregado, user=request.user)

#     context = {
#         'encarregado': encarregado,
#         }
#     return render(request, 'encperf.html', context)

# @property
# def idade(self):
#     hoje = date.today()
#     nascimento = self.data_nascimento
#     idade_calculada = hoje.year - nascimento.year - ((hoje.month, hoje.day) < (nascimento.month, nascimento.day))
#     return idade_calculada

@login_required
def listar_turmas(request):
    turmas = Turma.objects.all()
    context = {"turmas": turmas}
    return render(request, "listar_turmas.html", context)

@login_required
def listar_aulas(request):
    aulas = Aula.objects.all()
    context = {"aulas": aulas}
    return render(request, "listar_aulas.html", context)

@login_required
def detalhes_aula(request, aula_id):
    aula = get_object_or_404(Aula, id=aula_id)
    presencas = aula.presenca_set.all()

    if request.method == "POST":
        if "excluir_aula" in request.POST:
            aula.delete()
            messages.success(request, "Aula excluída com sucesso!")
            return redirect("detalhes_turma")

    context = {
        "aula": aula,
        "presencas": presencas,
    }

    return render(request, "detalhes_aula.html", context)

@login_required
def avalicao(request):

    return render(request, "avalicao.html")


@login_required
def detalhes_turma(request, turma_id):
    turma = get_object_or_404(Turma, id=turma_id)
    alunos_relacionados = turma.alunos.all().order_by('nome')
    hora_atual = datetime.now().time()
    professor_instance = Professor.objects.filter(user=request.user)
    disciplinas = ProfessorDisciplina.objects.filter(professor=professor_instance.get())
    professor_id = request.user.professor.id
    horarios = Horario.objects.filter(turma=turma, professor=professor_id)

    # Obtenha a disciplina selecionada
    # disciplina_selecionada = request.GET.get("disciplina")
    # if disciplina_selecionada:
    #     disc = Disciplina.objects.filter(id=disciplina_selecionada).get()
    #     disciplina_selecionada_instance = ProfessorDisciplina.objects.filter(disciplina=disc).get()
    # else:
    #     disciplina_selecionada_instance = disciplinas[0]

    # Lógica para lidar com a troca de disciplina
    troca_disciplina_form = TrocaDisciplinaForm()
    if request.method == "POST":
        troca_disciplina_form = TrocaDisciplinaForm(request.POST)
        if troca_disciplina_form.is_valid():
            disciplina_selecionada = troca_disciplina_form.cleaned_data["disciplinas"]

    if request.method == "POST":
        # Passe os dados do aluno para o formulário NotaForm
        nota_form = NotaForm(request.POST)
        if nota_form.is_valid():
            # Salve a nota no banco de dados
            nota_form.save()
            # Redirecione de volta para a página de detalhes da turma após salvar a nota
            return redirect("detalhes_turma", turma_id=turma_id)
    else:
        # Se o método não for POST, crie uma instância do formulário NotaForm sem dados
        nota_form = NotaForm()

    context = {
        "turma": turma,
        "alunos_relacionados": alunos_relacionados,
        "horarios": horarios,
        "troca_disciplina_form": troca_disciplina_form,
        #'nova_disciplina': disciplina_selecionada,
        "disciplinas": disciplinas,
        #'disciplinaData': disciplina_selecionada_instance,
        "nota_form": nota_form,  # Adicionando o formulário de lançamento de notas ao contexto
    }

    return render(request, "detalhes_turma.html", context)
@login_required
def ver_horarios_professor(request):
    # Recupere todos os horários relacionados ao professor logado
    professor = request.user.professor  # Supondo que o professor esteja associado ao usuário
    horarios = Horario.objects.filter(professor=professor)

    context = {
        'horarios': horarios
    }

    return render(request, 'ver_horarios_professor.html', context)
@login_required
def aula(request, aula_id):
    aula = Aula.objects.get(id=aula_id)
    turma_aula = aula.turma
    alunos_turma = turma_aula.alunos.all().order_by('nome')
    context = {
        'aula': aula,
        'turma_aula': turma_aula,
        'alunos_turma': alunos_turma,
    }
    return render(request, "aula.html", context=context)

def registrar_presenca(request, aluno_id, aula_id):
    # Verifica se a requisição é do tipo POST
    if request.method == 'POST':
        # Verifica se já existem duas entradas de presença para o aluno e aula específicos
        presencas = Presenca.objects.filter(aluno_id=aluno_id, aula_id=aula_id)

        # Se já existirem duas entradas, retorna um erro 403 (proibido)
        if presencas.count() >= 2:
            return HttpResponseForbidden("Você já registrou a presença duas vezes.")

        # Se houver uma ou nenhuma entrada de presença para o aluno e aula específicos
        # verifica se a presença está sendo registrada como presente ou ausente
        if 'presenca' in request.POST:
            presente = request.POST['presenca']
            if presente == 'P' or presente == 'A':
                # Se já existir uma entrada de presença, atualiza o valor de presente
                presenca = presencas.first() if presencas.exists() else None
                if presenca:
                    presenca.presente = presente
                    presenca.save()
                else:
                    # Se não existir, cria uma nova entrada de presença
                    Presenca.objects.create(
                        aluno_id=aluno_id,
                        aula_id=aula_id,
                        data=date.today(),
                        presente=presente
                    )

    # Redireciona para a página anterior
    return redirect(request.META.get('HTTP_REFERER', ''))






@login_required
def iniciar_aula_turma(request, turma_id):
    horario_data = Horario.objects.filter(turma=turma_id)
    date = datetime.now()
    print(horario_data)
    context = {}
    if horario_data:
        context = {"horario": horario_data.get(),"date": date }
        print(date)
        if request.method == 'POST':
            data = request.POST
            disciplina_selecionada = Disciplina.objects.get(id=horario_data.get().disciplina_id)
            turmaObj = Turma.objects.get(id=horario_data.get().turma_id)
            tema = data["Tema"]
            objectivos = data["objectivos"]
            dateFim = data["dateFim"]
            dateInicio = data["dateInicio"]
            aula = Aula()
            
            aula.turma=turmaObj
            aula.Tema=tema
            aula.objectivo=objectivos
            aula.disciplina=disciplina_selecionada
            aula.inicio=dateInicio
            aula.fim=dateFim
            aula.save()
            return redirect("aula", aula.id)

    else:
        context = {"error": "Erro ao buscar dados!"}

    return render(request, "iniciar_aula.html", context=context)

@login_required
def iniciar_aula(request):
    if request.method == "POST":
        professor = request.user.professor
        # Filtrar por professor e lecionando (se o campo existir)
        if hasattr(ProfessorDisciplina, "lecionando"):
            disciplinas_lecionando = ProfessorDisciplina.objects.filter(
                professor=professor, lecionando=True
            )
        else:
            disciplinas_lecionando = ProfessorDisciplina.objects.filter(
                professor=professor
            )
        disciplina_id = request.POST["disciplina"]
        disciplina_selecionada = Disciplina.objects.get(pk=disciplina_id)
        turma = disciplina_selecionada.turma
        data = request.POST["data"]
        inicio = request.POST["inicio"]
        fim = request.POST["fim"]
        aula = Aula(
            turma=turma,
            disciplina=disciplina_selecionada,
            data=data,
            inicio=inicio,
            fim=fim,
        )
        aula.save()
        # Redirecionar para página de sucesso ou detalhes da aula
        return redirect("detalhes_aula", aula.id)
    else:
        professor = request.user.professor
        # Filtrar por professor e lecionando (se o campo existir)
        if hasattr(ProfessorDisciplina, "lecionando"):
            disciplinas_lecionando = ProfessorDisciplina.objects.filter(
                professor=professor, lecionando=True
            )
        else:
            disciplinas_lecionando = ProfessorDisciplina.objects.filter(
                professor=professor
            )
        form = IniciarAulaForm(
            initial={"disciplina": disciplinas_lecionando.first().id}
        )  # Selecionar a primeira disciplina por padrão
    return render(
        request,
        "iniciar_aula.html",
        {"form": form, "disciplinas": disciplinas_lecionando},
    )

@login_required
def editar_aula(request, pk):
    aula = Aula.objects.get(pk=pk)
    form = EditarAulaForm(instance=aula)
    if request.method == "POST":
        form = EditarAulaForm(request.POST, instance=aula)
        if form.is_valid():
            form.save()
            return redirect("detalhes_aula", pk=aula.id)
    context = {
        "form": form,
        "aula": aula,
    }
    return render(request, "editar_aula.html", context)

@login_required
def excluir_aula(request, pk):
    if request.method == "POST":
        aula = Aula.objects.get(pk=pk)
        aula.delete()
        return redirect("prof")
    return render(request, "detalhes_aula.html", {"aula": Aula.objects.get(pk=pk)})


# def registrar_presenca(request, aula_id):
#     aula = get_object_or_404(Aula, pk=aula_id)  # Retrieve Aula by ID
#     turma = aula.turma  # Assuming a relationship between Aula and Turma models

#     if request.method == "POST":
#         alunos = turma.alunos.all()  # Fetch all students in the turma
#         for aluno in alunos:
#             presente = request.POST.get(f"presente_{aluno.id}", False)
#             aluno.presente_aula(aula, presente)  # Call the method on each Aluno

#         # Handle successful registration (e.g., redirect to success page)
#         return redirect(
#             "detalhes_aula", aula_id=aula.id
#         )  # Assuming a details_aula view

#     context = {
#         "aula": aula,
#         "alunos": alunos,
#     }

#     return render(request, "registrar_presenca.html", context)

@login_required
def lancar_notas(request, pk):
    aula = Aula.objects.get(pk=pk)
    turma = aula.turma
    alunos = turma.aluno_set.all()
    if request.method == "POST":
        for aluno in alunos:
            nota = request.POST.get(f"nota_{aluno.id}", None)
            aluno.lancar_nota(aula, nota)
        return redirect("detalhes_aula", pk=aula.id)
    context = {
        "aula": aula,
        "alunos": alunos,
    }
    return render(request, "avaliacao.html", context)

@login_required
def visualizar_boletim(request, aluno_id):
    aluno = get_object_or_404(Aluno, pk=aluno_id)
    boletim = Boletim.objects.filter(aluno=aluno)

    context = {
        "aluno": aluno,
        "boletim": boletim,
    }
    return render(request, "visualizar_boletim.html", context)

@login_required
def finalizar_aula(request):
    aula = Aula.objects.get(fim__isnull=True)
    aula.fim = timezone.now()
    aula.save()
    messages.success(request, "Aula finalizada com sucesso!")
    return redirect("/")


@login_required
def estatisticas_turma(request, turma_id):
    turma = get_object_or_404(Turma, id=turma_id)
    estatistica_turma = EstatisticaTurma.objects.get_or_create(turma=turma)[0]
    alunos_relacionados = turma.alunos.count()
    alunos_associados_professor = turma.alunos.count()

    context = {
        "turma": turma,
        "estatistica_turma": estatistica_turma,
        "alunos_associados": turma.alunos,
        "alunos_relacionados": alunos_relacionados,
        "alunos_associados_professor": alunos_associados_professor,
    }

    return render(request, "estatisticas_turma.html", context)

registros = EstatisticaTurma.objects.all()

# Exclui todos os registros
registros.delete()

@login_required
def avaliacoes_turma(request, turma_id):
    professor = Professor.objects.get(user=request.user)
    turma = get_object_or_404(Turma, id=turma_id)
    alunos_associados = turma.alunos.all()
    # avaliacoes_turma = Avaliacao.objects.filter(aluno__turma=turma)
    # #disciplinas = professor.disciplinas_associadas()  # Obtendo disciplinas associadas ao professor

    # if request.method == 'POST':
    #     # Lógica para processar o envio de uma avaliação individual, se necessário
    #     pass

    # # Consulta para obter todas as avaliações (substitua por sua lógica de consulta)
    # avaliacoes_individuais = Avaliacao.objects.all()

    # Consulta para calcular a média por disciplina (substitua por sua lógica de consulta)
    media_por_disciplina = (
        {}
    )  # Dicionário onde a chave é a disciplina e o valor é a média

    context = {
        "titulo": "Avaliações",
        #'avaliacoes_individuais': avaliacoes_individuais,
        "media_por_disciplina": media_por_disciplina,
        "turma": turma,
        #'avaliacoes_turma': avaliacoes_turma,
        "alunos_associados": alunos_associados,
        #'disciplinas': disciplinas,
    }
    return render(request, "avaliacoes.html", context)


logger = logging.getLogger(__name__)
@login_required
def realizar_pagamento(request, aluno_id):
    aluno = get_object_or_404(Aluno, id=aluno_id)
    encarregado = Encarregado.objects.get(user=request.user)
    alunos_associados = encarregado.alunos_associados.all()

    if request.method == "POST":
        form = PagamentoForm(request.POST, request.FILES, initial={"aluno": aluno})
        if form.is_valid():
            pagamento = form.save(commit=False)
            pagamento.aluno = aluno  # Definindo o aluno manualmente
            pagamento.encarregado = encarregado
            pagamento.save()
            return redirect("pagamento_realizado")
    else:
        form = PagamentoForm(initial={"aluno": aluno})

    return render(request, "realizar_pagamento.html", {"form": form, "aluno": aluno})

@login_required
def pagamento_realizado(request):
    return render(request, "pagamento_realizado.html")

@login_required
def comunicado(request):

    return render(request, "comunicado.html")

def pagina_de_erro(request):

    return render(request, "pagina_de_erro.html")


# Define a função que verifica se o usuário é superusuário
def is_superuser(user):
    return user.is_authenticated and user.is_superuser


@user_passes_test(is_superuser)# Aplica o decorator à sua view
def cadashorario(request):
    if request.method == 'POST':
        form = HorarioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('iadmin')  # Redirecione para a lista de horários ou outra página
    else:
        form = HorarioForm()
    return render(request, 'cadastrar_horario.html', {'form': form})

@user_passes_test(is_superuser)
def lista_adiciona_disciplinas(request):
    if request.method == 'POST':
        form = DisciplinaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_adiciona_disciplinas')
    else:
        form = DisciplinaForm()
    
    disciplinas = Disciplina.objects.all()
    return render(request, 'lista_adiciona_disciplinas.html', {'form': form, 'disciplinas': disciplinas})


@user_passes_test(is_superuser)
def excluir_disciplina(request, disciplina_id):
    disciplina = get_object_or_404(Disciplina, pk=disciplina_id)
    disciplina.delete()
    return redirect('lista_adiciona_disciplinas')

@user_passes_test(is_superuser)
def editar_disciplina(request, disciplina_id):
    disciplina = Disciplina.objects.get(pk=disciplina_id)
    data = {
        'id': disciplina.id,
        'nome': disciplina.nome,
        # Adicione mais campos conforme necessário
    }
    return JsonResponse(data)

@user_passes_test(is_superuser)
def iadmin(request):
    # Conta o número de turmas
    numero_de_turmas = Turma.objects.count()
    publicidades = Publicidade.objects.all()
    # Conta o número de alunos
    numero_de_alunos = Aluno.objects.count()

    # Conta o número de professores
    numero_de_professores = Professor.objects.count()

    # Conta o número de encarregados
    numero_de_encarregados = Encarregado.objects.count()
    numero_de_solicitacoes = Pagamento.objects.filter(aprovado=False).count()
    
    # Recupera o usuário atualmente autenticado
    user = request.user

    # Acessa as informações do usuário
    username = user.username
    first_name = user.first_name
    last_name = user.last_name
    email = user.email
    bi = user.bi
    telefone = user.telefone
    foto = user.foto
    horarios = Horario.objects.all()
    # Define o contexto com as informações do usuário e os números contados
    context = {
        "username": username,
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "bi": bi,
        "telefone": telefone,
        "foto": foto,
        "numero_de_turmas": numero_de_turmas,
        "numero_de_alunos": numero_de_alunos,
        "numero_de_professores": numero_de_professores,
        "numero_de_encarregados": numero_de_encarregados,
        "publicidades": publicidades,
        'numero_de_solicitacoes': numero_de_solicitacoes,
        'horarios':horarios,
    }

    # Renderiza a página 'admin.html' passando o contexto para o template
    return render(request, "admin.html", context)

def processar_pagamento_e_gerar_pdf(request):
    if request.method == 'POST':
        # Obter dados do formulário
        tipo_pagamento = request.POST.get('tipo')
        outro_tipo = request.POST.get('outro_tipo')
        valor = request.POST.get('valor')
        comprovativo = request.FILES.get('comprovativo')

        # Aqui você pode processar os dados e fazer o que for necessário para gerar o comprovativo em PDF
        # Por exemplo, você pode usar a biblioteca ReportLab para criar o PDF

        # Criar o PDF usando ReportLab
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="comprovativo.pdf"'

        # Criar um objeto PDF Canvas
        buffer = response.content
        c = canvas.Canvas(buffer, pagesize=letter)

        # Adicionar conteúdo ao PDF
        c.drawString(100, 750, f'Tipo de Pagamento: {tipo_pagamento}')
        c.drawString(100, 730, f'Outro Tipo: {outro_tipo}')
        c.drawString(100, 710, f'Valor: {valor}')

        # Salvar o PDF
        c.save()
        return response
    else:
        # Se não for uma solicitação POST, retorne uma resposta de erro
        return HttpResponse(status=405)

@user_passes_test(is_superuser)
def edit_profile(request):
    if request.method == "POST":
        form = CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(
                form.cleaned_data["password"]
            )  # Define a senha com a senha fornecida no formulário
            user.save()
            # Adicione instruções de depuração para verificar se os dados estão sendo salvos corretamente
            print("Informações do perfil atualizadas com sucesso!")
            return redirect("iadmin")  # Redireciona para a página inicial após salvar
        else:
            # Adicione instruções de depuração para verificar quaisquer erros de validação
            print("Erros de validação no formulário:", form.errors)
    else:
        form = CustomUserChangeForm(instance=request.user)
    return render(request, "perfilsuper.html", {"form": form})


@user_passes_test(is_superuser)
def verturmas(request):
    # Recupera todas as turmas do banco de dados
    turmas = Turma.objects.all()
    context = {"turmas": turmas}
    return render(request, "verturmas.html", context)


@user_passes_test(is_superuser)
def visualizar_turma(request, turma_id):
    turma = get_object_or_404(Turma, id=turma_id)
    return render(request, "visualizar_turma.html", {"turma": turma})


@user_passes_test(is_superuser)
def detalhes_aluno1(request, aluno_id):
    aluno = get_object_or_404(Aluno, id=aluno_id)
    return render(request, "detalhe_aluno.html", {"aluno": aluno})


@user_passes_test(is_superuser)
def adicionar_aluno(request):
    if request.method == "POST":
        # Obtenha os dados do formulário do pedido POST
        nome = request.POST["nome"]
        profissao_encarregado = request.POST["profissao_encarregado"]
        data_nascimento = request.POST["data_nascimento"]
        foto = request.FILES.get("foto", None)
        sexo = request.POST["sexo"]
        Classe = request.POST["Classe"]
        encarregado_nome = request.POST["encarregado_nome"]
        encarregado_numero = request.POST["encarregado_numero"]

        # Verifique se o campo 'turma' está presente nos dados do request
        if "turma" in request.POST:
            turma_id = request.POST[
                "turma"
            ]  # Obtenha o ID da turma selecionada no formulário
            turma = Turma.objects.get(id=turma_id)  # Obtenha a turma com base no ID
        else:
            turma = None  # Se nenhum turma foi selecionada, defina como None

        # Crie uma instância do aluno com os dados fornecidos
        aluno = Aluno.objects.create(
            nome=nome,
            profissao_encarregado=profissao_encarregado,
            data_nascimento=data_nascimento,
            foto=foto,
            sexo=sexo,
            Classe=Classe,
            encarregado_nome=encarregado_nome,
            encarregado_numero=encarregado_numero,
            turma=turma,  # Associe a turma ao aluno
        )
        return redirect("criar_turma")

    # Obtém todas as turmas para passar para o template
    turmas = Turma.objects.all()

    # Retorna o formulário renderizado com o contexto das turmas
    return render(request, "adicionar_aluno.html", {"turmas": turmas})


@user_passes_test(is_superuser)
def criar_turma(request):
    if request.method == "POST":
        form = TurmaForm(request.POST, request.FILES)
        if form.is_valid():
            turma = form.save(
                commit=False
            )  # Salva o formulário, mas não no banco de dados ainda
            turma.save()  # Salva a turma no banco de dados para que possamos associar os alunos
            # Se houver alunos selecionados, adicione-os à turma
            alunos_selecionados = form.cleaned_data["alunos"]
            if alunos_selecionados:
                turma.alunos.add(*alunos_selecionados)
            return redirect("verturmas")
    else:
        form = TurmaForm()

    return render(request, "criar_turma.html", {"form": form})


@user_passes_test(is_superuser)
def editar_turma(request, turma_id):
    turma = get_object_or_404(Turma, id=turma_id)
    if request.method == "POST":
        form = TurmaForm(request.POST, request.FILES, instance=turma)
        if form.is_valid():
            form.save()
            return redirect("verturmas")
    else:
        form = TurmaForm(instance=turma)
    context = {
        "form": form,
        "turma": turma,
    }
    return render(request, "editar_turma.html", context)


@user_passes_test(is_superuser)
def ver_professores(request):
    professores = Professor.objects.all()
    return render(request, "ver_professores.html", {"professores": professores})

@user_passes_test(is_superuser)
def ver_encarregado(request, encarregado_id):
    encarregado = get_object_or_404(Encarregado, pk=encarregado_id)
    
    query = request.GET.get('q')
    if query:
        alunos = encarregado.alunos_associados.filter(nome__icontains=query).order_by('nome')
    else:
        alunos = encarregado.alunos_associados.all().order_by('nome')

    return render(request, "ver_encarregado.html", {
        "encarregado": encarregado,
        "alunos": alunos,
        "query": query,
    })
  


@user_passes_test(is_superuser)
def ver_alunos(request):
    query = request.GET.get('q')
    if query:
        alunos = Aluno.objects.filter(nome__icontains=query).order_by('nome')
    else:
        alunos = Aluno.objects.all().order_by('nome')
    context = {
        "alunos": alunos,
        "query": query,
    }
    return render(request, "ver_alunos.html", context)

@user_passes_test(is_superuser)
def licitacoes_pendentes(request):
    pagamentos_pendentes = Pagamento.objects.filter(aprovado=False)
    return render(request, 'licitacoes_pendentes.html', {'pagamentos_pendentes': pagamentos_pendentes})
@user_passes_test(is_superuser)
def aprovar_pagamento(request, pagamento_id):
    pagamento = Pagamento.objects.get(pk=pagamento_id)
    pagamento.aprovado = True
    pagamento.save()
    return redirect('listar_licitacoes_pendentes')

@user_passes_test(is_superuser)
def reprovar_pagamento(request, pagamento_id):
    pagamento = get_object_or_404(Pagamento, id=pagamento_id)
    
    # Excluir o pagamento
    pagamento.delete()

    messages.success(request, f'O pagamento de {pagamento.aluno} foi reprovado e removido com sucesso.')
    
    return redirect('listar_licitacoes_pendentes')
@login_required
def meu_horario(request, professor_id):
    professor = get_object_or_404(Professor, id=professor_id)
    
    context = {
        'professor': professor,
    }
    return render(request, 'meu_horario.html', context)

@user_passes_test(is_superuser)
def cadastrar_publicidade_comunicado(request):
    if request.method == "POST":
        publicidade_form = PublicidadeForm(
            request.POST, request.FILES, prefix="publicidade"
        )
        comunicado_form = ComunicadoForm(request.POST, prefix="comunicado")

        if "submit_publicidade" in request.POST and publicidade_form.is_valid():
            publicidade_form.save()
            return redirect(
                "iadmin"
            )  # Redirecionar para a página inicial após o cadastro da publicidade

        elif "submit_comunicado" in request.POST and comunicado_form.is_valid():
            comunicado_form.save()
            return redirect(
                "iadmin"
            )  # Redirecionar para a página inicial após o cadastro do comunicado
    else:
        publicidade_form = PublicidadeForm(prefix="publicidade")
        comunicado_form = ComunicadoForm(prefix="comunicado")

    publicidades = Publicidade.objects.all()

    context = {
        "publicidade_form": publicidade_form,
        "comunicado_form": comunicado_form,
        "publicidades": publicidades,
    }

    return render(request, "cadastrar_publicidade_comunicado.html", context)


@user_passes_test(is_superuser)
def editar_publicidade(request, publicidade_id):
    publicidade = get_object_or_404(Publicidade, pk=publicidade_id)

    if request.method == "POST":
        form = PublicidadeForm(request.POST, request.FILES, instance=publicidade)
        if form.is_valid():
            form.save()
            return redirect("cadastrar_publicidade_comunicado")
    else:
        form = PublicidadeForm(instance=publicidade)

    return render(request, "editar_publicidade.html", {"form": form})


@user_passes_test(lambda u: u.is_superuser)
def editar_aluno(request, id):
    aluno = get_object_or_404(Aluno, id=id)
    if request.method == "POST":
        form = AlunoForm(request.POST, request.FILES, instance=aluno)
        if form.is_valid():
            form.save()
            return redirect("ver_alunos")
    else:
        form = AlunoForm(instance=aluno)
    return render(request, "editar_aluno.html", {"form": form})


@user_passes_test(is_superuser)
def excluir_publicidade(request, publicidade_id):
    publicidade = get_object_or_404(Publicidade, pk=publicidade_id)
    publicidade.delete()
    return redirect("cadastrar_publicidade_comunicado")


@user_passes_test(is_superuser)
def atribuir_turmas_horarios(request, professor_id):
    professor = get_object_or_404(Professor, id=professor_id)
    turmas = Turma.objects.all()
    horarios = Horario.objects.all()

    if request.method == "POST":
        turmas_selecionadas = request.POST.getlist("turmas")
        horarios_selecionados = request.POST.getlist("horarios")

        # Atribuir turmas selecionadas ao professor
        professor.turmas_associadas.set(turmas_selecionadas)

        # Atribuir horários selecionados ao professor
        professor.horarios.set(horarios_selecionados)

        # Redirecionar para a página de detalhes do professor após a atribuição
        return redirect("detalhes_professor", professor_id=professor_id)

    return render(
        request,
        "atribuir_turmas_horarios.html",
        {"professor": professor, "turmas": turmas, "horarios": horarios},
    )


@user_passes_test(is_superuser)
def detalhes_professor(request, professor_id):
    professor = get_object_or_404(Professor, id=professor_id)
    horarios = Horario.objects.filter(professor=professor)
    # Adicione outras informações relevantes aqui, se necessário
    context =  {"professor": professor, "horarios": horarios}

    return render(request, "detalhes_professor.html",context)

@user_passes_test(is_superuser)
def editar_professor(request, professor_id):
    professor = get_object_or_404(Professor, id=professor_id)
    if request.method == 'POST':
        form = ProfessorForm(request.POST, instance=professor)
        if form.is_valid():
            form.save()
            return redirect('detalhes_professor', professor_id=professor.id)
    else:
        form = ProfessorForm(instance=professor)
    return render(request, 'editar_professor.html', {'form': form})

@user_passes_test(is_superuser)  # Restringe acesso somente a superusuários
def sigup(request):
    if request.method == "GET":
        # Renderiza o formulário de inscrição em solicitações GET
        return render(request, "cadastro.html", {"form": UserCreationForm()})
    else:  # Processa o envio do formulário (POST)
        if request.POST["password1"] == request.POST["password2"]:
            try:
                # Cria um novo usuário com senhas validadas
                user = User.objects.create_user(
                    username=request.POST["username"],
                    password=request.POST["password1"],
                )

                # Redireciona para a visualização "ver_professores" após inscrição bem-sucedida
                return redirect("cadastrar_professor")
            except IntegrityError:
                # Trata o erro de usuário já existente
                return render(
                    request,
                    "cadastro.html",
                    {"form": UserCreationForm(), "error": "Usuário já existe!"},
                )
            except Exception as e:
                # Captura outros erros inesperados
                return render(
                    request,
                    "cadastro.html",
                    {"form": UserCreationForm(), "error": str(e)},
                )
        else:
            # Exibe mensagem de erro para senhas diferentes
            return render(
                request,
                "cadastro.html",
                {"form": UserCreationForm(), "error": "Senhas diferentes!"},
            )


@user_passes_test(is_superuser)
def cadastrar_professor(request):
    if request.method == "POST":
        form = ProfessorCreationForm(request.POST, request.FILES)
        if form.is_valid():
            # Salvar o professor e associar ao usuário selecionado
            professor = form.save(commit=False)
            professor.user = form.cleaned_data[
                "username"
            ]  # Corrigido para 'username' ao invés de 'user'
            professor.save()
            print("Professor salvo com sucesso!")
            return redirect(
                "ver_professores"
            )  # Redirecionar para uma página de sucesso
        else:
            print("Formulário inválido:", form.errors)
    else:
        form = ProfessorCreationForm()
    print("Renderizando o formulário de cadastro de professor")
    return render(request, "cadastrar_professor.html", {"form": form})


@user_passes_test(lambda u: u.is_superuser)
def cadastrar_encarregado(request):
    if request.method == "POST":
        form = EncarregadoForm(request.POST, request.FILES)
        if form.is_valid():
            # Salvar o encarregado e associar ao usuário selecionado
            encarregado = form.save(commit=False)
            encarregado.user = form.cleaned_data[
                "username"
            ]  # Corrigido para 'username' ao invés de 'user'
            encarregado.save()
            print("Encarregado salvo com sucesso!")
            return redirect(
                "encarregado_list"
            )  # Redirecionar para uma página de sucesso
        else:
            print("Formulário inválido:", form.errors)
    else:
        form = EncarregadoForm()
    print("Renderizando o formulário de cadastro de encarregado")
    return render(request, "cadastrar_encarregado.html", {"form": form})


@user_passes_test(is_superuser)
def encarregado_list_view(request):
    query = request.GET.get('q')
    if query:
        encarregados = Encarregado.objects.filter(nome__icontains=query).order_by('nome')
    else:
        encarregados = Encarregado.objects.all().order_by('nome')
    
    return render(request, "encarregado_list.html", {
        "encarregados": encarregados,
        "query": query,
    })

def handler400(request, exception):
    return render(request, '400.html', status=400)

def handler404(request, exception):
    return render(request, '404.html', status=404)

def handler500(request):
    return render(request, '500.html', status=500)

def handler405(request, exception):
    # Renderiza o template personalizado para o erro 405
    return render(request, '405.html', status=405)

@user_passes_test(is_superuser)  # Restringe acesso somente a superusuários
def enca(request):
    if request.method == "GET":
        # Renderiza o formulário de inscrição em solicitações GET
        return render(request, "cadastroenc.html", {"form": UserCreationForm()})
    else:  # Processa o envio do formulário (POST)
        if request.POST["password1"] == request.POST["password2"]:
            try:
                # Cria um novo usuário com senhas validadas
                user = User.objects.create_user(
                    username=request.POST["username"],
                    password=request.POST["password1"],
                )

                # Redireciona para a visualização "ver_professores" após inscrição bem-sucedida
                return redirect("cadastrar_encarregado")
            except IntegrityError:
                # Trata o erro de usuário já existente
                return render(
                    request,
                    "cadastroenc.html",
                    {"form": UserCreationForm(), "error": "Usuário já existe!"},
                )
            except Exception as e:
                # Captura outros erros inesperados
                return render(
                    request,
                    "cadastroenc.html",
                    {"form": UserCreationForm(), "error": str(e)},
                )
        else:
            # Exibe mensagem de erro para senhas diferentes
            return render(
                request,
                "cadastroenc.html",
                {"form": UserCreationForm(), "error": "Senhas diferentes!"},
            )


@user_passes_test(is_superuser)
def editar_encarregado(request, id):
    encarregado = get_object_or_404(Encarregado, id=id)
    if request.method == "POST":
        form = Encarregado1Form(request.POST, request.FILES, instance=encarregado)
        if form.is_valid():
            form.save()
            return redirect(
                "encarregado_list"
            )  # Redirecione para a visualização de encarregados após salvar com sucesso
    else:
        form = Encarregado1Form(instance=encarregado)
    return render(request, "editar_encarregado.html", {"form": form})


@user_passes_test(is_superuser)
def eliminar_turma(request, turma_id):
    turma = get_object_or_404(Turma, id=turma_id)
    if request.method == "POST":
        turma.delete()
        return redirect(
            "verturmas"
        )  # Substitua 'pagina_de_turmas' pelo nome da sua página de turmas
    return render(request, "eliminar_turma.html", {"turma": turma})


@user_passes_test(is_superuser)
def eliminar_professor(request, professor_id):
    professor = get_object_or_404(Professor, id=professor_id)
    if request.method == "POST":
        professor.delete()
        return redirect("ver_professores")
    return render(
        request, "confirmar_eliminar_professor.html", {"professor": professor}
    )


@user_passes_test(is_superuser)
def eliminar_aluno(request, id):
    aluno = get_object_or_404(Aluno, id=id)
    if request.method == "POST":
        aluno.delete()
        return redirect("ver_alunos")
    return render(request, "confirmar_eliminar_aluno.html", {"aluno": aluno})


@login_required
def perfil_alunos(request, encarregado_id):
    encarregado = get_object_or_404(Encarregado, pk=encarregado_id)
    alunos_associados = encarregado.alunos_associados.all()

    context = {
        "encarregado": encarregado,
        "alunos_associados": alunos_associados,
    }
    return render(request, "alunosp.html", context)


@login_required
def alunoed(request, aluno_id):
    aluno = get_object_or_404(Aluno, pk=aluno_id)
    if request.method == "POST":
        form = AlunoForm1(request.POST, request.FILES, instance=aluno)
        if form.is_valid():
            form.save()
            # Redirecione para a visualização do perfil do encarregado associado ao aluno
            return redirect("perfilalunos", encarregado_id=request.user.encarregado.id)
    else:
        form = AlunoForm1(instance=aluno)
    return render(request, "alunoed.html", {"form": form})


@login_required
def feed_noticias(request):
    publicidade = Publicidade.objects.all()
    storys = Story.objects.all()
    context = {
        "publicidade": publicidade,
        "storys": storys,
    }
    return render(request, "feed_noticias.html", context)


@login_required
def incrementar_visualizacao(request, story_id):
    if request.method == "POST" and request.is_ajax():
        story = Story.objects.get(pk=story_id)
        story.visualizacoes += 1
        story.save()
        return JsonResponse({"visualizacoes": story.visualizacoes})
    return JsonResponse(
        {"error": "Método inválido ou requisição não é AJAX."}, status=400
    )


@login_required
def publicar_story(request):
    if request.method == "POST":
        form = StoryForm(request.POST, request.FILES)
        if form.is_valid():
            story = form.save(commit=False)
            story.autor = (
                request.user
            )  # Define o autor como o usuário atual (encarregado)
            story.save()
            return redirect("feed_noticias")
    else:
        form = StoryForm()
    return render(request, "publicar_story.html", {"form": form})


def enviar_feedback(request):
    if request.method == "POST":
        formulario = FormularioFeedback(request.POST)
        if formulario.is_valid():
            formulario.save()
            return redirect(
                "sucesso_feedback"
            )  # Redireciona para uma página de sucesso após enviar o feedback
    else:
        formulario = FormularioFeedback()
    return render(request, "feed_noticias.html", {"formulario": formulario})


def enviar_pesquisa(request):
    if request.method == "POST":
        formulario = FormularioPesquisa(request.POST)
        if formulario.is_valid():
            formulario.save()
            return redirect(
                "sucesso_pesquisa"
            )  # Redireciona para uma página de sucesso após enviar a pesquisa
    else:
        formulario = FormularioPesquisa()
    return render(request, 'feed_noticias.html', {'formulario': formulario})

def chat(request):
    
    return render(request, 'chat.html')


def help_page(request):
    
    
    return render(request, 'help.html')

from django.db.models import Prefetch
class PresencasAlunoView(View):
    def get(self, request, aluno_id):
        try:
            aluno = Aluno.objects.get(pk=aluno_id)
            presencas = Presenca.objects.filter(aluno=aluno).prefetch_related(
            Prefetch('aula', queryset=Aula.objects.select_related('disciplina')))  # Optimize query for discipline name
            
            # Conta o número total de presenças, ausências e justificações
            status_counter = Counter(presenca.presente for presenca in presencas)

            total_presencas = status_counter['P']
            total_ausencias = status_counter['A']
            total_justificacoes = status_counter['J']

        except Aluno.DoesNotExist:
            # Handle case where aluno_id is not found (e.g., display error message)
            context = {'error_message': 'Aluno não encontrado.'}
            return render(request, 'presencas.html', context)

        context = {
            'aluno': aluno,
            'presencas': presencas,
            'total_presencas': total_presencas,
            'total_ausencias': total_ausencias,
            'total_justificacoes': total_justificacoes,
        }
        return render(request, 'presencas.html', context)