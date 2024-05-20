from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager, User,AbstractUser
from django.contrib.auth import get_user_model
from django.conf import settings 
from datetime import date, timedelta
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_date
from config.settings import AUTH_USER_MODEL
# Create your models here.
class CustomUser(AbstractUser):
    # Adicione campos personalizados, se necessário
    pass

class Disciplina(models.Model):
    nome = models.CharField(max_length=100)
    def __str__(self):
        return self.nome
    
    
class Turma(models.Model):
    nome = models.CharField(max_length=30)
    imagem = models.ImageField(upload_to="images/turmas/", blank=True, null=True)
    alunos = models.ManyToManyField('Aluno', related_name='turmas')
    classes = [
        ('10ª classe','10ª Classe'),
        ('11ª classe','11ª Classe'),
        ('12ª classe','12ª Classe'),
        ('13ª classe','13ª Classe')
    ]
    classe = models.CharField(choices=classes, max_length=30)
   

    def __str__(self):
        return self.nome
class TurmaDisciplina(models.Model):
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE)
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE)
    
class EstatisticaTurma(models.Model):
    turma = models.OneToOneField(Turma, on_delete=models.CASCADE)
    total_alunos = models.PositiveIntegerField(default=0)
    media_notas = models.FloatField(default=0.0)
    
    
class Professor(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    conteudos_educacionais = models.ManyToManyField('ConteudoEducacional', blank=True, related_name='conteudo')

    email = models.EmailField(unique=True)
    departamento = models.CharField(max_length=100)
    titulacao = models.CharField(max_length=50)
    disciplinas_associadas = models.ManyToManyField(Disciplina)
    turmas_associadas = models.ManyToManyField(Turma,blank=True)
    foto = models.ImageField(upload_to="images/professores/", blank=True, null=True)
    horarios = models.ManyToManyField('Horario', blank=True, related_name='horarios_professor')
        
    def __str__(self):
        return f"{self.nome} - {self.departamento}"

class DisciplinaSelecionada(models.Model):
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE)
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.professor.nome} - {self.disciplina.nome}"
 
    
class ProfessorDisciplina(models.Model):
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE)
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE)
    lecionando = models.BooleanField(default=False)
        
    def __str__(self):
        return f"{self.professor.nome} - {self.disciplina}"

class Curso(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome
    
class Classe(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

class Alerta(models.Model):
    aluno  = models.ForeignKey("app.Aluno", on_delete=models.CASCADE, blank=True, null=True)
    descricao = models.TextField(max_length =5000)
    MONTH_CHOICES = [
        (1, 'Janeiro'),
        (2, 'Fevereiro'),
        (3, 'Março'),
        (4, 'Abril'),
        (5, 'Maio'),
        (6, 'Junho'),
        (7, 'Julho'),
        (8, 'Agosto'),
        (9, 'Setembro'),
        (10, 'Outubro'),
        (11, 'Novembro'),
        (12, 'Dezembro'),
    ]
    mes = models.IntegerField(choices=MONTH_CHOICES)
    
    def __str__(self):
        return self.descricao

class Alerta2(models.Model):
    aluno  = models.ForeignKey("app.Aluno", on_delete=models.CASCADE, blank=True, null=True)
    descricao = models.TextField(max_length =5000)
    MONTH_CHOICES = [
        (1, 'Janeiro'),
        (2, 'Fevereiro'),
        (3, 'Março'),
        (4, 'Abril'),
        (5, 'Maio'),
        (6, 'Junho'),
        (7, 'Julho'),
        (8, 'Agosto'),
        (9, 'Setembro'),
        (10, 'Outubro'),
        (11, 'Novembro'),
        (12, 'Dezembro'),
    ]
    mes = models.IntegerField(choices=MONTH_CHOICES)
    
    def __str__(self):
        return self.descricao
class Aluno(models.Model):
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE, blank=True, null=True)
    
    #escola = models.ForeignKey('Escola', on_delete=models.CASCADE)
    nome = models.CharField(max_length=100, null=True, blank=True)
    turma = models.ForeignKey(Turma, on_delete=models.SET_NULL, null=True, blank=True)
    profissao_encarregado = models.CharField(max_length=100)
    data_nascimento = models.DateField()
    foto = models.ImageField(upload_to="images/alunos/", blank=True, null=True)
    tipo_sexo = [
        ('Masculino', 'masculino'),
        ('Feminino', 'feminino'),
    ]

    sexo = models.CharField(choices=tipo_sexo, max_length=30)
    classes = [
        ('10ª classe','10ª Classe'),
        ('11ª classe','11ª Classe'),
        ('12ª classe','12ª Classe'),
        ('13ª classe','13ª Classe')
    ]
    Classe = models.CharField(choices=classes, max_length=30)
    encarregado_nome = models.CharField(max_length=100, null=True, blank=True)
    encarregado_numero = models.CharField(max_length=20, null=True, blank=True)

    @property
    def idade(self):
        hoje = date.today()
        nascimento = self.data_nascimento
        idade_calculada = hoje.year - nascimento.year - ((hoje.month, hoje.day) < (nascimento.month, nascimento.day))
        return idade_calculada

    def get_divida_total(self):
        propinas = self.propina_set.filter(pago=False)
        divida_total = sum(propina.valor for propina in propinas)
        return divida_total
    def __str__(self):
        turma_nome = self.turma.nome if self.turma else "Sem turma"
        return f"{self.nome} - Idade: {self.idade} - Turma: {turma_nome}"


class ComunicadoEnc(models.Model):
    titulo = models.CharField(max_length=100)
    mensagem = models.TextField()
    data_publicacao = models.DateTimeField(auto_now_add=True)
    professor_autor = models.ForeignKey('Professor', on_delete=models.CASCADE)
    turmas_destino = models.ManyToManyField('Turma', blank=True)  # Turmas para as quais o comunicado será enviado

    def __str__(self):
        return self.titulo
    
class InformacoesAcademicas(models.Model):
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='informacoes_academicas')
    desempenho_academico = models.TextField(verbose_name='Desempenho Acadêmico')
    frequencia_escolar = models.CharField(max_length=100, verbose_name='Frequência Escolar')
    horario_aulas = models.CharField(max_length=100, verbose_name='Horário das Aulas')

    def __str__(self):
        return f'Informações Acadêmicas - {self.pk}'
    
class Comportamento(models.Model):
    aluno = models.OneToOneField(Aluno, on_delete=models.CASCADE)
    descricao = models.TextField()
    ausencias_nao_justificadas = models.IntegerField(default=0)
    comportamento = models.CharField(max_length=100)

    def __str__(self):
        return f"Comportamento de {self.aluno.nome}"
    
class Nota(models.Model):
    TIPO_CHOICES = [
        ('Prova', 'Prova'),
        ('Trabalho', 'Trabalho'),
        ('Projeto', 'Projeto'),
        ('Participação', 'Participação'),
        ('Tarefa', 'Tarefa'),
        ('Apresentação', 'Apresentação'),
        ('Exercício', 'Exercício'),
        ('Avaliação Oral', 'Avaliação Oral'),
        ('Outro', 'Outro'),
        
    ]
    
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE)
    disciplina = models.ForeignKey(ProfessorDisciplina, on_delete=models.CASCADE)
    trimestre = models.IntegerField(choices=((1, '1º Trimestre'), (2, '2º Trimestre'), (3, '3º Trimestre')))
    tipo = models.CharField(max_length=100, choices=TIPO_CHOICES)
    nota = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.aluno} - {self.disciplina} (Trimestre {self.trimestre}) - {self.tipo}: {self.nota}"

       

class Aula(models.Model):
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE)
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE)
    data = models.DateField(auto_now_add=True)
    Tema = models.CharField( max_length=500)
    objectivo = models.TextField( max_length=1000)
    inicio = models.TimeField()
    fim = models.TimeField()
    status_aula = [
        ('Em_andamento','Em_andamento'),
        ('Finalizada', 'Finalizada'),
        ('Pendente', 'Pendente'),
    ]
    tipo_status = models.CharField(max_length=255, choices=status_aula)

    def __str__(self):
        return f'{self.disciplina} - Turma: {self.turma} - Data: {self.data} - Início: {self.inicio} - {self.tipo_status}'




class Presenca(models.Model):
    PRESENCA_CHOICES = [
        ('P', 'Presente'),
        ('A', 'Ausente'),
        ('T', 'Atrasado'),
        ('J', 'Justificado'),
    ]
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE)
    aula = models.ForeignKey(Aula, on_delete=models.CASCADE)
    data = models.DateField()
    presente = models.CharField(max_length=1, choices=PRESENCA_CHOICES, default='A')
    nota = models.FloatField(default=0.0)
    justificativa = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.aluno.nome} - {self.aula} - {self.data} - {self.get_presente_display()}'

    def get_status_class(self):
        """
        Returns a CSS class based on the presence status for table styling.
        """
        if self.presente == 'P':
            return 'presente'  # Green for presence
        elif self.presente == 'A':
            return 'ausente'  # Red for absence
        elif self.presente == 'T':
            return 'atrasado'  # Yellow for tardiness (optional)
        else:
            return ''

    def get_justificativa(self):
        """
        Returns the justification if present, otherwise returns None.
        """
        if hasattr(self, 'justificativa'):
            return self.justificativa
        return None
 # Default for other cases

    
# class Presenca(models.Model):
#     aluno = models.ForeignKey('Aluno', on_delete=models.CASCADE)
#     aula = models.ForeignKey(Aula, on_delete=models.CASCADE)
#     presente = models.BooleanField(default=True)
#     data_registro = models.DateTimeField(auto_now_add=True)
#     observacoes = models.TextField(blank=True, null=True)
#     motivo_falta = models.CharField(max_length=255, blank=True, null=True)
#     justificativa = models.TextField(blank=True, null=True)
#     tipo_falta = models.CharField(max_length=50, blank=True, null=True)

#     def _str_(self):
#         return f"{self.aluno}-{self.aula}"

#     class Meta:
#         unique_together = ('aluno', 'aula')

class Propina(models.Model):
    aluno = models.ForeignKey(Aluno, on_delete=models.SET_NULL, null=True, blank=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    data_pagamento = models.DateField()
    detalhes_fatura = models.TextField()

    MONTH_CHOICES = [
        (1, 'Janeiro'),
        (2, 'Fevereiro'),
        (3, 'Março'),
        (4, 'Abril'),
        (5, 'Maio'),
        (6, 'Junho'),
        (7, 'Julho'),
        (8, 'Agosto'),
        (9, 'Setembro'),
        (10, 'Outubro'),
        (11, 'Novembro'),
        (12, 'Dezembro'),
    ]

    DEFAULT_DIVIDA = 14000.00  # Definindo o valor padrão da dívida

    divida = models.DecimalField(max_digits=10, decimal_places=2, default=DEFAULT_DIVIDA)

    mes = models.IntegerField(choices=MONTH_CHOICES)
    pago = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.aluno} - {self.data_pagamento} - {self.pago}"  

    def save(self, *args, **kwargs):
        # Verificar se o valor está vazio ou None
        if self.valor is None or self.valor == '':
            self.valor = self.divida  # Define o valor como a dívida padrão
        super().save(*args, **kwargs)

    def calcular_status_propina(self):
        hoje = timezone.now().date()
        if self.data_pagamento > hoje:
            return 'A Pagar'
        elif self.pago:
            return 'Pago'
        else:
            return 'Em Dívida'

    def get_divida_mes(self):
        if not self.pago:
            return self.valor
        return 0
    

   
class Publicidade(models.Model):
    titulo = models.CharField(max_length=255)
    conteudo = models.TextField()
    imagem = models.ImageField(upload_to='publicidades/', null=True, blank=True)

    def __str__(self):
        return self.titulo

class Story(models.Model):
    autor = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    imagem = models.ImageField(upload_to="images/stories/")
    titulo = models.CharField(max_length=100)
    descricao = models.TextField()
    data_publicacao = models.DateTimeField(auto_now_add=True)
    visualizacoes = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.titulo

    def incrementar_visualizacao(self):
        self.visualizacoes += 1
        self.save()
        
def apagar_stories_antigos():
    # Calcule a data limite para manter os stories
    data_limite = timezone.now() - timedelta(seconds=3)  # Por exemplo, 30 dias

    # Apague os stories mais antigos que a data limite
    Story.objects.filter(data_publicacao__lte=data_limite).delete()
        
class Encarregado(models.Model):
    user = models.OneToOneField(AUTH_USER_MODEL, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=20)
    profissao = models.CharField(max_length=100)
    alunos_associados = models.ManyToManyField(Aluno,blank=True)
    foto = models.ImageField(upload_to="images/encarregados/", blank=True, null=True)
    
    def __str__(self):
        return f"{self.nome} - {self.telefone}"
    

class Feedback(models.Model):
    comentario = models.TextField()
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback {self.id}"

class Pesquisa(models.Model):
    # Adicione campos relevantes para a pesquisa aqui
    pergunta_1 = models.CharField(max_length=100)
    pergunta_2 = models.CharField(max_length=100)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pesquisa {self.id}"
    
class Comunicado(models.Model):
    titulo = models.CharField(max_length=100)
    mensagem = models.TextField()
    data_publicacao = models.DateTimeField(auto_now_add=True)
    encarregado_destino = models.ForeignKey('Encarregado', on_delete=models.CASCADE, blank=True, null=True)
    enviar_para_todos = models.BooleanField(default=False)  # Campo para indicar se o comunicado será enviado para todos os encarregados
    requerido_pagamento = models.BooleanField(default=False)

    def __str__(self):
        return self.titulo
    
# class Horario(models.Model):
#     DIA_CHOICES = [
#         ('Segunda', 'Segunda-feira'),
#         ('Terca', 'Terça-feira'),
#         ('Quarta', 'Quarta-feira'),
#         ('Quinta', 'Quinta-feira'),
#         ('Sexta', 'Sexta-feira'),
#     ]

#     dia_semana = models.CharField(choices=DIA_CHOICES, max_length=10)
#     hora_inicio = models.TimeField()
#     hora_fim = models.TimeField()
#     turma = models.ForeignKey(Turma, on_delete=models.CASCADE)
#     professor = models.ForeignKey(Professor, on_delete=models.CASCADE)
#     aulas = models.ManyToManyField(Aula, blank=True, related_name='horarios_aulas')

#     def __str__(self):
#         return f"{self.dia_semana} - {self.hora_inicio}"

class Horario(models.Model):
    DIA_CHOICES = [
        ('Segunda', 'Segunda-feira'),
        ('Terca', 'Terça-feira'),
        ('Quarta', 'Quarta-feira'),
        ('Quinta', 'Quinta-feira'),
        ('Sexta', 'Sexta-feira'),
    ]
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE)
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE)
    dia_semana = models.CharField(choices=DIA_CHOICES, max_length=10)
    hora_inicio = models.TimeField()
    hora_termino = models.TimeField()
    sala_aula = models.CharField(max_length=50)
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE)

    # turma = models.ForeignKey(Turma, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.disciplina} - {self.dia_semana} - {self.hora_inicio} às {self.hora_termino}"


class ConteudoEducacional(models.Model):
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=100)
    descricao = models.TextField()
    data_publicacao = models.DateField(auto_now_add=True)
    arquivo = models.FileField(upload_to='arquivos_conteudos/', blank=True, null=True)

    def __str__(self):
        return self.titulo
    
class Evento(models.Model):
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=255)
    descricao = models.TextField()
    data = models.DateField()
    hora_inicio = models.TimeField()
    hora_fim = models.TimeField()

    def __str__(self):
        return self.titulo
    
class MensagemSMS(models.Model):
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE, related_name='mensagens_enviadas')
    encarregado = models.ForeignKey(Encarregado, on_delete=models.CASCADE, related_name='mensagens_recebidas')
    mensagem_respondida = models.BooleanField(default=False)
    resposta = models.TextField(blank=True, null=True)
    resposta_professor = models.TextField(blank=True, null=True)
    mensagem = models.TextField()
    data_envio = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.professor.nome} para {self.encarregado.nome} - {self.data_envio}"

class Boletim(models.Model):
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE)
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE)
    nota = models.DecimalField(max_digits=5, decimal_places=2)
    conceito = models.CharField(max_length=20)  # Excelente, Bom, Suficiente, Insuficiente, etc.
    faltas = models.IntegerField(default=0)
    observacoes = models.TextField(blank=True)

    def __str__(self):
        return f"Boletim de {self.aluno.nome} em {self.disciplina.nome}"
    

class Pagamento(models.Model):
    TIPO_CHOICES = [
        ('Folha de Prova', 'Folha de Prova'),
        ('Passe', 'Passe'),
        ('Propina', 'Propina'),
        ('Dívida', 'Dívida'),
        ('Material Escolar', 'Material Escolar'),
        ('Atividade Extracurricular', 'Atividade Extracurricular'),
        ('Uniforme Escolar', 'Uniforme Escolar'),
        ('Taxa de Matrícula', 'Taxa de Matrícula'),
        ('Lanche', 'Lanche'), 
        ('Excursão', 'Excursão'),
        # Adicione quantos tipos de pagamento desejar
    ]
    
    encarregado = models.ForeignKey(Encarregado, on_delete=models.CASCADE)
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=100, choices=TIPO_CHOICES)
    outro_tipo = models.CharField(max_length=100, blank=True, null=True)  # Novo campo para outro tipo de pagamento
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    comprovativo = models.ImageField(upload_to='comprovativos_pagamento/')
    data_pagamento = models.DateField(auto_now_add=True)
    aprovado = models.BooleanField(default=False)

    def __str__(self):
        return f"Pagamento de {self.aluno} - {self.tipo} - {self.valor} - {self.data_pagamento} - {self.aprovado}" 

    
# class Escola(models.Model):
#     nome = models.CharField(max_length=100)
#     endereco = models.CharField(max_length=200)
#     cidade = models.CharField(max_length=100)
#     estado = models.CharField(max_length=50)
#     cep = models.CharField(max_length=10)
#     telefone = models.CharField(max_length=20)
#     email = models.EmailField()
#     diretor = models.CharField(max_length=100)
#     # Outros campos relevantes para a escola

#     def __str__(self):
#         return self.nome

class Eventos(models.Model):
    TIPO_EVENTO_CHOICES = [
        ('Aula', 'Aula'),
        ('Reunião', 'Reunião'),
        ('Prova', 'Prova'),
        ('Atividade Extracurricular', 'Atividade Extracurricular'),
        # Adicione mais tipos de evento conforme necessário
    ]

    id = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=255, verbose_name="Título")
    descricao = models.TextField(verbose_name="Descrição", blank=True)
    data_hora_inicio = models.DateTimeField(verbose_name="Data e Hora de Início")
    data_hora_fim = models.DateTimeField(verbose_name="Data e Hora de Término", blank=True, null=True)
    local = models.CharField(max_length=255, verbose_name="Local")
    cor = models.CharField(max_length=6, verbose_name="Cor", blank=True)
    tipo_evento = models.CharField(max_length=50, verbose_name="Tipo de Evento")
    professor = models.ForeignKey('Professor', on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Professor")
    turma = models.ForeignKey('Turma', on_delete=models.CASCADE, verbose_name="Turma")
    arquivo = models.FileField(upload_to='calendarios/', blank=True, verbose_name="Arquivo")
    recorrencia = models.CharField(max_length=20, verbose_name="Recorrência", blank=True)
    link_externo = models.URLField(blank=True, verbose_name="Link Externo")
    visibilidade = models.CharField(max_length=10, default="Público", verbose_name="Visibilidade") 
    data_publicacao = models.DateTimeField(default=timezone.now)


    def __str__(self):
        return self.titulo