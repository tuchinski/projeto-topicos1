import speech_recognition as sr
from subprocess import call
from requests import get
from bs4 import BeautifulSoup
from gtts import gTTS
import webbrowser as browser
import json
from paho.mqtt import publish
#### CONFIGURAÇOES ####
hotword = 'helena'
assunto_atual = ''
qtde_noticias = 1
ultima_cidade = ''
with open('python-assist-260122-c2cabb1fdb47.json') as credenciais_google:
    credenciais_google = credenciais_google.read()


#### FUNÇOES PRINCIPAIS ####
def monitora_audio():   
    microfone = sr.Recognizer()
    with sr.Microphone() as source:
        while True:
            print("Aguardando o comando")
            audio = microfone.listen(source)

            try:
                trigger = microfone.recognize_google_cloud(audio, credentials_json=credenciais_google, language='pt-BR')
                trigger = trigger.lower()
                if hotword in trigger:
                    print('Comando: ', trigger)
                    responde('feedback')
                    executa_comandos(trigger)
                    break

            except sr.UnknownValueError:
                print("Google Cloud Speech could not understand audio")
            except sr.RequestError as e:
                print("Could not request results from Google Cloud Speech service; {0}".format(e))
    return trigger

def responde(arquivo):
    call(['mpg123', 'audios/' + arquivo + '.mp3'])

def executa_comandos(trigger):
    if 'notícias sobre essa cidade' in trigger:
        print('entrou noticias da cidade!@!@!@!@!@!@@!@!@@!@!@')
        ultimas_noticias(trigger,contexto='cidade')
    elif ('notícias' in trigger) or ('notícia' in trigger):
        ultimas_noticias(trigger)
    elif 'toca' in trigger and 'senhora' in trigger:
        playlists('senhora')
    elif 'tempo agora' in trigger:
        print("dfghjkl Tempo agora")
        previsao_temp(True,False,trigger)
    elif 'temperatura hoje' in trigger:
        print("dfghjkl Tempo agora")
        previsao_temp(False,True,trigger)
    elif 'liga a luz' in trigger:
        publica_mqtt('office/iluminacao/status', '1')
    elif 'desativa a luz' in trigger:
        publica_mqtt('office/iluminacao/status', '0')
    elif 'pesquisar' in trigger:
        pesquisa(trigger)
    elif 'tchau' in trigger:
        responde('tchau')
        exit(1)

        
    else:
        mensagem = trigger.strip(hotword)
        cria_audio(mensagem)
        print('Comando invalido', mensagem)
        responde('comando_invalido')


def previsao_temp(tempo=False, minmax=False,trigger=None):
    command = trigger.split(' ')
    count = 0
    print(command)
    for palavra in command:
        if palavra == 'temperatura' or palavra == 'tempo':
            break
        else:
            count = count + 1
    cidade = ' '.join(command[count+3:-1])
    global ultima_cidade
    ultima_cidade = cidade
    print(cidade)
    
    
    # print(command)
    site = get('http://api.openweathermap.org/data/2.5/weather?q=' + cidade + '&APPID=c423254affe44819bcdbd411425bd2bf&units=metric&lang=pt')
    # site = get('https://api.openweathermap.org/data/2.5/weather?id=3467717&APPID=c423254affe44819bcdbd411425bd2bf&units=metric&lang=pt')
    clima = site.json()
    print(clima)
    #print(json.dumps(clima, indent=4))
    temperatura = clima['main']['temp']
    minima = clima['main']['temp_min']
    maxima = clima['main']['temp_max']
    descricao = clima['weather'][0]['description']
    print()
    if tempo:
        mensagem = f'No momento fazem {temperatura} graus com: {descricao} em {cidade}'
        cria_audio(mensagem)
    if minmax:
        mensagem = f'Minima de {minima} e maxima de {maxima} em {cidade}'
        cria_audio(mensagem)
        

def cria_audio(mensagem):
    tts = gTTS(mensagem, lang='pt-br')
    tts.save('audios/mensagem.mp3')
    print('Helena:', mensagem)
    call(['mpg123', 'audios/mensagem.mp3'])
#### FUNÇOES COMANDOS ####

def ultimas_noticias(trigger,contexto = None):
    command = trigger.split(' ')
    count = 0
    global ultima_cidade
    print("city: " + ultima_cidade)
    print(command)
    global qtde_noticias
    global assunto_atual
    
    if contexto == None:
        for palavra in command:
            if palavra == 'notícia' or palavra == 'notícias':
                break
            else:
                count = count + 1
        assunto = ' '.join(command[count+2:-1])
    elif contexto == 'cidade':
        assunto = ultima_cidade
    else:
        assunto = assunto_atual

    print(assunto)
    site = get('https://news.google.com/rss/search?q=' + assunto + '&hl=pt-BR&gl=BR')
    print(site)
    # site = get('https://news.google.com/rss?hl=pt-BR&gl=BR&ceid=BR:pt-419')
    noticias = BeautifulSoup(site.text, 'html.parser')

    for item in noticias.findAll('item')[:qtde_noticias]:
        mensagem = item.title.text
        cria_audio(mensagem)
    qtde_noticias = qtde_noticias + 2

def pesquisa(trigger):
    command = trigger.split(' ')
    if(command[-2] == 'spotify'):
        chave = ' '.join(command[2:-3])
        print(chave)
        responde('pesquisando_spotify')
        browser.open("https://open.spotify.com/search/" + chave)
    elif(command[-2] == 'google'):
        chave = ' '.join(command[2:-3])
        responde('pesquisando_google')
        browser.open('https://www.google.com/search?q=' + chave)
    elif(command[-2] == 'youtube'):
        chave = ' '.join(command[2:-3])
        responde('pesquisando')
        browser.open('https://www.youtube.com/results?search_query=' + chave)


def playlists(album):
    if album == 'senhora':
        browser.open("https://open.spotify.com/track/0TK2YIli7K1leLovkQiNik")

def previsao_tempo(tempo=False, minmax=False):
    site = get('http://api.openweathermap.org/data/2.5/weather?id=3467717&APPID=c423254affe44819bcdbd411425bd2bf&units=metric&lang=pt')
    clima = site.json()
    #print(json.dumps(clima, indent=4))
    temperatura = clima['main']['temp']
    minima = clima['main']['temp_min']
    maxima = clima['main']['temp_max']
    descricao = clima['weather'][0]['description']
    print()
    if tempo:
        mensagem = f'No momento fazem {temperatura} graus com: {descricao}'
        cria_audio(mensagem)
    if minmax:
        mensagem = f'Minima de {minima} e maxima de {maxima}'
        cria_audio(mensagem)

def publica_mqtt(topic, payload):
    publish.single(topic, payload=payload, qos=1, retain=True, hostname="postman.cloudmqtt.com",
    port=12189, client_id="helena", auth={'username': 'xvsizqmq', 'password': '27iCsnbmm1fM'})
    if payload == '1':
        mensagem = 'Luz ligada'
        cria_audio(mensagem)
    elif payload == '0':
        mensagem = 'Luz desligada'
        cria_audio(mensagem)
def main():
    while True:
        monitora_audio()

main()
