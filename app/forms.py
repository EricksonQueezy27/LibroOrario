from django import forms
from .models import *
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from crispy_forms.bootstrap import Field
from django.forms import formset_factory
from users.models import User
from django.contrib.auth.forms import UserChangeForm

class ConteudoEducacionalForm(forms.ModelForm):
    class Meta:
        model = ConteudoEducacional
        fields = ['titulo', 'descricao', 'arquivo']

class TurmaForm(forms.ModelForm):
    class Meta:
        model = Turma
        fields = ['nome', 'classe']

class TrocaDisciplinaForm(forms.Form):
    disciplinas = forms.ModelChoiceField(queryset=Disciplina.objects.all(), empty_label=None)

    def __init__(self, *args, **kwargs):
        professor = kwargs.pop('professor', None)
        super().__init__(*args, **kwargs)

        if professor:
            self.fields['disciplinas'].queryset = professor.disciplinas_associadas.all()

class PresencaForm(forms.Form):
    def __init__(self, alunos, *args, **kwargs):
        super(PresencaForm, self).__init__(*args, **kwargs)
        for aluno in alunos:
            self.fields[f'presenca_{aluno.id}'] = forms.BooleanField(label=aluno.nome, required=False)

    def save(self, aluno, aula):
        for field_name, value in self.cleaned_data.items():
            if field_name.startswith('presenca_'):
                aluno_id = int(field_name.split('_')[1])
                presenca, created = Presenca.objects.get_or_create(aluno_id=aluno_id, aula=aula)
                presenca.presente = value
                presenca.save()



class EventoForm(forms.ModelForm):
    class Meta:
        model = Evento
        fields = ['titulo', 'descricao', 'data', 'hora_inicio', 'hora_fim']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'titulo',
            'descricao',
            'data',
            'hora_inicio',
            'hora_fim',
            Submit('submit', 'Salvar', css_class='btn btn-primary')
        )


class SMSForm(forms.ModelForm):
    class Meta:
        model = MensagemSMS
        fields = ['encarregado', 'mensagem']

    def __init__(self, professor, *args, **kwargs):
        super(SMSForm, self).__init__(*args, **kwargs)
        turma = professor.turmas_associadas.first()
        
        if turma:
            alunos = turma.alunos.all()
            encarregados = Encarregado.objects.filter(alunos_associados__in=alunos).distinct()
            self.fields['encarregado'].queryset = encarregados
        else:
            # Se o professor não estiver associado a nenhuma turma, evite um possível erro
            self.fields['encarregado'].queryset = Encarregado.objects.none()


class RespostaForm(forms.ModelForm):
    class Meta:
        model = MensagemSMS
        fields = ['resposta_professor']

class RespostaForm(forms.ModelForm):
    class Meta:
        model = MensagemSMS
        fields = ['resposta']

class SelecaoDisciplinaForm(forms.Form):
    disciplina = forms.ModelChoiceField(queryset=None, empty_label="Selecione a disciplina")

    def __init__(self, *args, **kwargs):
        disciplinas = kwargs.pop('disciplinas', None)  # Certifique-se de que disciplinas tenha um valor padrão
        super(SelecaoDisciplinaForm, self).__init__(*args, **kwargs)
        if disciplinas is not None:
            self.fields['disciplina'].queryset = disciplinas
        else:
            raise ValueError("O parâmetro 'disciplinas' não pode ser None.")


class InformacoesAcademicasForm(forms.ModelForm):
    class Meta:
        model = InformacoesAcademicas
        fields = ['desempenho_academico', 'frequencia_escolar', 'horario_aulas']



class InformacoesAcademicasForm(forms.ModelForm):
    class Meta:
        model = InformacoesAcademicas
        fields = ['desempenho_academico', 'frequencia_escolar', 'horario_aulas']

class ComportamentoForm(forms.ModelForm):
    class Meta:
        model = Comportamento
        fields = ['descricao', 'ausencias_nao_justificadas', 'comportamento']

class IniciarAulaForm(forms.ModelForm):
  data = forms.DateField()
  inicio = forms.TimeField()
  fim = forms.TimeField()

class IniciarAulaForm(forms.ModelForm):
    class Meta:
        model = Aula  # Especifique o modelo associado ao formulário
        fields = ['disciplina', 'inicio', 'fim']  



class EditarAulaForm(forms.ModelForm):
    class Meta:
        model = Aula
        fields = '__all__' 

class PagamentoForm(forms.ModelForm):
    class Meta:
        model = Pagamento
        fields = ['tipo', 'outro_tipo', 'valor', 'comprovativo']

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo')
        outro_tipo = cleaned_data.get('outro_tipo')
        
        # Verifica se o campo 'outro_tipo' está preenchido se o tipo selecionado for 'Outro'
        if tipo == 'Outro' and not outro_tipo:
            raise forms.ValidationError("Por favor, especifique o tipo de pagamento.")
        
        return cleaned_data


class EventosForm(forms.ModelForm):
    class Meta:
        model = Eventos
        fields = '__all__'



class CustomUserChangeForm(UserChangeForm):
    password = forms.CharField(label='Nova senha', widget=forms.PasswordInput, required=False)
    password_confirmation = forms.CharField(label='Confirme a nova senha', widget=forms.PasswordInput, required=False)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'bi', 'telefone', 'foto')

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirmation = cleaned_data.get("password_confirmation")

        if password and password_confirmation and password != password_confirmation:
            raise forms.ValidationError("As senhas não coincidem. Por favor, digite novamente.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
            if commit:
                user.save()
        return user
    
class TurmaForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(TurmaForm, self).__init__(*args, **kwargs)
        # Filtra os alunos que ainda não estão associados a uma turma
        alunos_sem_turma = Aluno.objects.filter(turma__isnull=True)
        self.fields['alunos'].queryset = alunos_sem_turma

    alunos = forms.ModelMultipleChoiceField(
        queryset=Aluno.objects.none(), 
        widget=forms.CheckboxSelectMultiple, 
        required=False
    )

    class Meta:
        model = Turma
        fields = ['nome', 'imagem', 'classe', 'alunos']     




        

class PublicidadeForm(forms.ModelForm):
    class Meta:
        model = Publicidade
        fields = ['titulo', 'conteudo', 'imagem']

class ComunicadoForm(forms.ModelForm):
    class Meta:
        model = Comunicado
        fields = ['titulo', 'mensagem', 'encarregado_destino', 'enviar_para_todos', 'requerido_pagamento']
        
class PublicidadeForm(forms.ModelForm):
    class Meta:
        model = Publicidade
        fields = ['titulo', 'conteudo', 'imagem']
        

class AlunoForm(forms.ModelForm):
    class Meta:
        model = Aluno
        fields = ['nome', 'profissao_encarregado', 'data_nascimento', 'foto', 'sexo', 'Classe', 'encarregado_nome', 'encarregado_numero']
   
class ProfForm(forms.ModelForm):
    class Meta:
        model = Professor
        fields = ['user','nome','email','departamento', 'titulacao','foto'] 

class NotaForm(forms.ModelForm):
    class Meta:
        model = Nota
        fields = ['aluno', 'disciplina', 'trimestre', 'tipo', 'nota']
        labels = {
            'aluno': 'Aluno',
            'disciplina': 'Disciplina',
            'trimestre': 'Trimestre',
            'tipo': 'Tipo',
            'nota': 'Nota',
        }

class ProfessorCreationForm(forms.ModelForm):
    username = forms.ModelChoiceField(queryset=User.objects.all(), label='Nome de Usuário')
    email = forms.EmailField(label='Email', max_length=254)

    class Meta:
        model = Professor
        fields = ['username', 'email', 'nome', 'conteudos_educacionais', 'departamento', 'titulacao', 'disciplinas_associadas', 'turmas_associadas', 'foto']

class EncarregadoForm(forms.ModelForm):
    username = forms.ModelChoiceField(queryset=User.objects.all(), label='Nome de Usuário')
    email = forms.EmailField(label='Email', max_length=254)

    class Meta:
        model = Encarregado
        fields = ['username', 'nome', 'email', 'telefone', 'profissao', 'alunos_associados', 'foto']

    def __init__(self, *args, **kwargs):
        super(EncarregadoForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['nome'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['telefone'].widget.attrs.update({'class': 'form-control'})
        self.fields['profissao'].widget.attrs.update({'class': 'form-control'})
        self.fields['alunos_associados'].widget.attrs.update({'class': 'form-control'})
        self.fields['foto'].widget.attrs.update({'class': 'form-control'})

class Encarregado1Form(forms.ModelForm):
    class Meta:
        model = Encarregado
        fields = ['nome', 'email', 'telefone', 'profissao', 'alunos_associados', 'foto']
        


class AlunoForm1(forms.ModelForm):
    class Meta:
        model = Aluno
        fields = ['nome', 'profissao_encarregado', 'data_nascimento', 'foto', 'encarregado_nome', 'encarregado_numero']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalize os widgets, rótulos, etc., conforme necessário    
        

class StoryForm(forms.ModelForm):
    class Meta:
        model = Story
        fields = ['imagem', 'titulo', 'descricao']
        

class FormularioFeedback(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['comentario']

class FormularioPesquisa(forms.ModelForm):
    class Meta:
        model = Pesquisa
        fields = ['pergunta_1', 'pergunta_2']  
