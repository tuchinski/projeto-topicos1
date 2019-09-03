from gtts import gTTS
from subprocess import call

def cria_audio(audio):
    tts = gTTS(audio, lang='pt-br')
    tts.save('audios/comando_invalido.mp3')
    call(['mpg123', 'audios/comando_invalido.mp3'])

cria_audio('Puts kkk')