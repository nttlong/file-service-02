from captcha.audio import AudioCaptcha
from captcha.image import ImageCaptcha

audio = AudioCaptcha(voicedir='/path/to/voices')
image = ImageCaptcha(fonts=['/path/A.ttf', '/path/B.ttf'])

data = audio.generate('1234')
audio.write('1234', 'out.wav')

data = image.generate('1234')
image.write('1234', 'out.png')