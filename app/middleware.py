from .models import Propina, Aluno, Alerta, Alerta2, Encarregado
from datetime import datetime
from .utils import sms



class PropinaMiddlewareVerification:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        mes_actual = datetime.now().month
        dia = datetime.now().day

        mapper = [
            {"titulo": "Janeiro", "value": 1},
            {"titulo": "Fevereiro", "value": 2},
            {"titulo": "Março", "value": 3},
            {"titulo": "Abril", "value": 4},
            {"titulo": "Maio", "value": 5},
            {"titulo": "Junho", "value": 6},
            {"titulo": "Julho", "value": 7},
            {"titulo": "Agosto", "value": 8},
            {"titulo": "Setembro", "value": 9},
            {"titulo": "Outubro", "value": 10},
            {"titulo": "Novembro", "value": 11},
            {"titulo": "Dezembro", "value": 12},
        ]
        
        
        #VERIFICAR DIA
        
        
        
        
        
        for mes in mapper:
            if mes["value"] == mes_actual:
                propinas = Propina.objects.all()
                alunos = Aluno.objects.all()
                
                for alunoData in alunos:
                    encarregados = Encarregado.objects.all()
                    for encarregado in encarregados:
                        alunos_associados = encarregado.alunos_associados.all()
                        for aluno in alunos_associados:
                            pagamento = Propina.objects.filter(aluno=aluno, pago=True, mes= mes_actual)
                            alerta = Alerta.objects.filter(aluno=aluno, mes=mes_actual)
                            if not pagamento and not alerta:
                                message = (f'Caro encarregado, Ainda não fez o pagamento do mês de  {mes["titulo"]} para o(a) Estudante {aluno.nome}!')
                                # sms.enviar_mensagem(encarregado.user.telefone, message)
                                
                                alerta = Alerta()
                                alerta.aluno = aluno
                                alerta.mes = mes_actual
                                alerta.descricao = message
                                alerta.save()
                            
        for mes in mapper:
            if mes["value"] == mes_actual and dia == 8:
                propinas = Propina.objects.all()
                alunos = Aluno.objects.all()
                
                for alunoData in alunos:
                    encarregados = Encarregado.objects.all()
                    for encarregado in encarregados:
                        alunos_associados = encarregado.alunos_associados.all()
                        for aluno in alunos_associados:
                            pagamento = Propina.objects.filter(aluno=aluno, pago=True, mes= mes_actual)
                            alerta = Alerta2.objects.filter(aluno=aluno, mes=mes_actual)
                            if not pagamento and not alerta:
                                message = (f'Caro encarregado, Ainda não fez o pagamento do mês de  {mes["titulo"]} para o(a) Estudante {aluno.nome}')
                                # sms.enviar_mensagem(encarregado.user.telefone, message)
                                
                                alerta = Alerta2()
                                alerta.aluno = aluno
                                alerta.mes = mes_actual
                                alerta.descricao = message
                                alerta.save()
                            
                            


                
                    
                    

        return response
