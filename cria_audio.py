from gtts import gTTS
from subprocess import call

def cria_audio(audio):
    tts = gTTS(audio, lang='pt-br')
    tts.save('audios/tchau.mp3')
    call(['mpg123', 'audios/tchau.mp3'])

cria_audio('Até mais')