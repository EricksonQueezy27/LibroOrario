from django.contrib import admin
from .models import *

# Register your models here.
admin.site.site_header = "LibroOraio"
admin.site.site_title = "Gerenciador"
admin.site.index_title = "Sistema Escolar LibroOrarrio"
admin.site.site_url = "http://192.168.8.116:3000"
admin.site.name  = "LibroOrario"
# admin.site.register(Notificacao)
admin.site.register(Publicidade)
# admin.site.register(Propina)
admin.site.register(Presenca)
admin.site.register(Aluno)
admin.site.register(Nota)
#admin.site.register(Avaliacao)
admin.site.register(Propina)
admin.site.register(Professor)
admin.site.register(Encarregado)
admin.site.register(Disciplina)
admin.site.register(Aula)
admin.site.register(Turma)
admin.site.register(Curso)
admin.site.register(Classe)
admin.site.register(Horario)
admin.site.register(ConteudoEducacional)
admin.site.register(ProfessorDisciplina)
admin.site.register(Evento)
# admin.site.register(Lembrete)
admin.site.register(MensagemSMS)
admin.site.register(TurmaDisciplina)
admin.site.register(EstatisticaTurma)
admin.site.register(DisciplinaSelecionada)
admin.site.register(InformacoesAcademicas)
admin.site.register(Comportamento)
admin.site.register(Boletim)
admin.site.register(Pagamento)
admin.site.register(Eventos)
admin.site.register(Story)
admin.site.register(Feedback)
admin.site.register(Pesquisa)

class ComunicadoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'data_publicacao', 'destino', 'requerido_pagamento')
    list_filter = ('requerido_pagamento',)
    search_fields = ('titulo', 'mensagem', 'encarregado_destino__nome')
    actions = ['enviar_comunicado']

    def destino(self, obj):
        if obj.enviar_para_todos:
            return "Para todos os encarregados"
        else:
            return obj.encarregado_destino.nome if obj.encarregado_destino else ""

    def enviar_comunicado(self, request, queryset):
        for comunicado in queryset:
            if comunicado.enviar_para_todos:
                # Enviar comunicado para todos os encarregados
                encarregados = Encarregado.objects.all()
                for encarregado in encarregados:
                    Comunicado.objects.create(
                        titulo=comunicado.titulo,
                        mensagem=comunicado.mensagem,
                        encarregado_destino=encarregado,
                        requerido_pagamento=comunicado.requerido_pagamento
                    )
                self.message_user(request, "Comunicado de pagamento enviado para todos os encarregados.")
            else:
                # Enviar comunicado para o encarregado específico
                Comunicado.objects.create(
                    titulo=comunicado.titulo,
                    mensagem=comunicado.mensagem,
                    encarregado_destino=comunicado.encarregado_destino,
                    requerido_pagamento=comunicado.requerido_pagamento
                )
                self.message_user(request, f"Comunicado de pagamento enviado para {comunicado.encarregado_destino.nome}.")

    enviar_comunicado.short_description = "Enviar comunicado de pagamento"

admin.site.register(Comunicado, ComunicadoAdmin)