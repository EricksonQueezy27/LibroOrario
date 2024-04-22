from django.urls import path,include
from .views import *
from django.contrib.admin.views.decorators import staff_member_required

urlpatterns = [
    path("", index, name="index"),
    path("login/", login, name="login"),
    path('professor/', prof, name='prof'),
    path('perfilpro/', perfilpro, name='perfilpro'),
    #path('encperf/', encperf, name='encperf'),
    path('turmas/', turmas, name='turmas'),
    path('perfilenc/', perfilenc, name='perfilenc'),
    path('turma/<int:turma_id>/', detalhes_turma, name='detalhes_turma'),
    path('detalhes_turma/<int:turma_id>/', detalhes_turma, name='detalhes_turma'),
    #path('perfilenc/<int:perfilenc_id>/',perfilenc, name='perfilenc'),
    path('alunos/', listar_alunos, name='listar_alunos'),
    path('alunos/<int:aluno_id>/', detalhes_aluno, name='detalhes_aluno'),
    #path('adicionar-comportamento/<int:aluno_id>/', adicionar_comportamento, name='adicionar_comportamento'),
    path('encarregado/', enc, name='encarregado'),
    path('turmas/', turmas, name='turmas'),
    path('listar_turmas/', listar_turmas, name='listar_turmas'),
    path('detalhes_turma/<int:turma_id>/', detalhes_turma, name='detalhes_turma'),
    path('listar_aulas/', listar_aulas, name='listar_aulas'),
    path('detalhes_aula/<int:aula_id>/', detalhes_aula, name='detalhes_aula'),
    path('estatisticas_turma/<int:turma_id>/', estatisticas_turma, name='estatisticas_turma'),
    path('avaliacoes/turma/<int:turma_id>/', avaliacoes_turma, name='avaliacoes_turma'),
    #path('selecionar-aula/', selecionar_aula, name='selecionar_aula'),
    path('historico-pagamentos/<int:encarregado_id>/', historico_pagamentos, name='historico_pagamentos'),
    path('visualizar_educandos/<int:encarregado_id>/', visualizar_educandos, name='visualizar_educandos'),
   path('editar-informacao-academica/<int:informacao_academica_id>/', editar_informacao_academica, name='editar_informacao_academica'),
   path('excluir-informacao-academica/<int:informacao_academica_id>/', excluir_informacao_academica, name='excluir_informacao_academica'),
   path('professor/horario/', horario_professor, name='horario_professor'),
   # path('turma/<int:turma_id>/horario/', horario_turma, name='horario_turma'),
    path('iniciar-aula/', iniciar_aula, name='iniciar_aula'),
    path('finalizar-aula/', finalizar_aula, name='finalizar_aula'),
    path('excluir_aula/<int:pk>/', excluir_aula, name='excluir_aula'),
    path('editar_aula/<int:pk>/', editar_aula, name='editar_aula'),
    path('registrar_presenca/<int:pk>/', registrar_presenca, name='registrar_presenca'),
    path('lancar_notas/<int:pk>/', lancar_notas, name='lancar_notas'),
    path('visualizar_boletim/<int:aluno_id>/', visualizar_boletim, name='visualizar_boletim'),
    path('realizar-pagamento/<int:aluno_id>/', realizar_pagamento, name='realizar_pagamento'),
    path('pagamento_realizado/',  pagamento_realizado, name='pagamento_realizado'),
    path('comunicado/',  comunicado, name='comunicado'),
    path('pagina_de_erro/', pagina_de_erro, name='pagina_de_erro'),
    path('iadmin/',iadmin, name='iadmin' ), 
    path('edit_profile/', edit_profile, name='edit_profile'),
      path('verturmas/', verturmas, name='verturmas'),
    path('visualizar_turma/<int:turma_id>/', visualizar_turma, name='visualizar_turma'),
    path('detalhes_aluno/<int:aluno_id>/', detalhes_aluno1, name='detalhes_aluno1'),
    path('adicionar_aluno/', adicionar_aluno, name='adicionar_aluno'),
    path('criar_turma/', criar_turma, name='criar_turma'),
    path('editar_turma/<int:turma_id>/', editar_turma, name='editar_turma'),
     path('ver_professores/', ver_professores, name='ver_professores'),
    path('ver_encarregado/<int:encarregado_id>/', ver_encarregado, name='ver_encarregado'),
    path('ver_alunos/', ver_alunos, name='ver_alunos'),
    path('cadastrar_publicidade_comunicado/', cadastrar_publicidade_comunicado, name='cadastrar_publicidade_comunicado'),
    path('atribuir_turmas_horarios/<int:professor_id>/', atribuir_turmas_horarios, name='atribuir_turmas_horarios'),
    path('detalhes_professor/<int:professor_id>/', detalhes_professor, name='detalhes_professor'),
    path('excluir_publicidade/<int:publicidade_id>/', excluir_publicidade, name='excluir_publicidade'),
    path('editar_publicidade/<int:publicidade_id>/', editar_publicidade, name='editar_publicidade'),  
    # Outras URLs...







 
]
