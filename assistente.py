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

def obter_nome():
    falar("Olá! Como posso te chamar?")
    nome = ouvir()
    return nome

def saudar(nome):
    falar(f"Prazer em te conhecer, {nome}! Como posso te ajudar hoje?")

def perguntar_professor_ou_encarregado():
    falar("Você é professor ou encarregado?")
    resposta = ouvir()
    return resposta

def redirecionar_pagina(resposta, nome):
    if 'professor' in resposta:
        falar(f"Ótimo, {nome}! Vou te redirecionar para a página do professor.")
        # Adicione aqui a lógica para redirecionar o usuário para a página do professor
    elif 'encarregado' in resposta:
        falar(f"Entendido, {nome}! Vou te redirecionar para a página do encarregado.")
        # Adicione aqui a lógica para redirecionar o usuário para a página do encarregado
    else:
        falar(f"Desculpe, {nome}, não entendi. Por favor, repita se é professor ou encarregado.")

def main():
    nome = obter_nome()
    saudar(nome)
    resposta_professor_encarregado = perguntar_professor_ou_encarregado()
    redirecionar_pagina(resposta_professor_encarregado, nome)

if __name__ == "__main__":
    main()
