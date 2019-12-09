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
with open('python-assist-73999abe1178.json') as credenciais_google:
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
    if 'notícias' in trigger:
        ultimas_noticias()
    elif 'toca' in trigger and 'senhora' in trigger:
        playlists('senhora')
    elif 'tempo agora' in trigger:
        previsao_tempo(tempo=True)
    elif 'temperatura hoje' in trigger:
        previsao_tempo(minmax=True)
    elif 'liga a luz' in trigger:
        publica_mqtt('office/iluminacao/status', '1')
    elif 'desativa a luz' in trigger:
        publica_mqtt('office/iluminacao/status', '0')
    elif 'pesquisar' in trigger:
        pesquisa(trigger)
    else:
        mensagem = trigger.strip(hotword)
        cria_audio(mensagem)
        print('Comando invalido', mensagem)
        responde('comando_invalido')


def cria_audio(mensagem):
    tts = gTTS(mensagem, lang='pt-br')
    tts.save('audios/mensagem.mp3')
    print('Helena:', mensagem)
    call(['mpg123', 'audios/mensagem.mp3'])
#### FUNÇOES COMANDOS ####

def ultimas_noticias():
    site = get('https://news.google.com/rss?hl=pt-BR&gl=BR&ceid=BR:pt-419')
    noticias = BeautifulSoup(site.text, 'html.parser')
    for item in noticias.findAll('item')[:2]:
        mensagem = item.title.text
        cria_audio(mensagem)

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
