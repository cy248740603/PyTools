from aip import AipSpeech
from ffmpy3 import FFmpeg
import pyaudio
import wave
import os
import string
import numpy as np

APP_ID = "17484342"
API_KEY = "pai3Y9zBeFGp4Zd6yZ7jkjzC"
SECRET_KEY = "v9RkUMfqj1zMG692g5Rm5vXPn9eUQpK2"

client = AipSpeech(APP_ID,API_KEY,SECRET_KEY)

# res = client.synthesis("你好,我是小饼",'zh',1,
#     {
#         'vol':100,
#         'spd':4,#0~9
#         'pit':4, #0~9 御姐音 - 萝莉音
#         'per':4 #发音人选择,0女声,1男声,3情感合成-度逍遥,4情感合成-度丫丫
#     }
# )

# print("over")
# with open("mp3/s1.mp3",'wb') as f :
#     f.write(res)
# ff = FFmpeg(
#     inputs={'mp3/s1.mp3': None},
#     outputs={'mp3/output.pcm': '-acodec pcm_s16le -f s16le -ac 1 -ar 16000'}
# )
# ff.cmd
# 'ffmpeg -i mp3/s1.mp3 -acodec pcm_s16le -f s16le -ac 1 -ar 16000 mp3/output.pcm'
# ff.run()

# filePath = 'mp3/output.pcm'
# with open(filePath,'rb') as fp:
#     file_context = fp.read()

# res =client.asr(file_context,'pcm',16000,{
#     'dev_pid':1537,
# }) 
# print(res)

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
RECORD_SECONDS = 1
TIMEOUT_SECONDS = 3
WAVE_OUTPUT_FILENAME = 'mp3/bing.wav'
MP3_OUTPUT_FILENAME = 'mp3/s1.mp3'

def play_mp3(file_name):
    os.system("ffplay -autoexit -nodisp %s"%(file_name))

def rec(file_name):
    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("开始录音,请说话......")

    frames = []
    timeout_count = TIMEOUT_SECONDS + 1
    while(True):
        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)
        audio_data = np.fromstring(data, dtype=np.short)
        large_sample_count = np.sum( audio_data > 800 )
        temp = np.max(audio_data)
        if temp > 800 :
            timeout_count = 0
            print('检测到声音\r\n当前阈值:%s'%temp)
        else:
            if timeout_count < TIMEOUT_SECONDS:
                timeout_count += 1
                print('timeout1 :%d'%timeout_count)
            elif timeout_count == TIMEOUT_SECONDS:
                print('timeout2 :%d'%timeout_count)
                break
            else:
                frames = []

    print("录音结束,请闭嘴!")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(file_name, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

def wav2pcm(wav_file):
    pcm_file = '%s.pcm' % (wav_file.split('.')[0])
    # ff = FFmpeg(
    #     inputs={wav_file: None},
    #     outputs={pcm_file: '-acodec pcm_s16le -f s16le -ac 1 -ar 16000'}
    # )
    # ff.cmd
    # 'ffmpeg -i %s -acodec pcm_s16le -f s16le -ac 1 -ar 16000 %s' % (wav_file,pcm_file)
    # ff.run()

    # 就是此前我们在cmd窗口中输入命令,这里面就是在让Python帮我们在cmd中执行命令
    os.system("ffmpeg -y  -i %s  -acodec pcm_s16le -f s16le -ac 1 -ar 16000 %s"%(wav_file,pcm_file))
    return pcm_file

def asr(pcm_file):
    with open(pcm_file,'rb')as fp:
        file_context = fp.read()    

    res =client.asr(file_context,'pcm',16000,{
        'dev_pid':1537,
    }) 
    print(res)
    if res.get('err_msg') in 'success.' :
        print(res.get('result')[0])
        return res.get('result')[0]
    print(res.get('err_msg'))
    return '不知道你在说什么'

def synth(synth_str):
    synth_context = client.synthesis(synth_str,'zh',1,
        {
            'vol':100,
            'spd':4,#0~9
            'pit':4, #0~9 御姐音 - 萝莉音
            'per':4 #发音人选择,0女声,1男声,3情感合成-度逍遥,4情感合成-度丫丫
        }
    )

    with open(MP3_OUTPUT_FILENAME,'wb') as f :
        f.write(synth_context)
    return synth_context

def faq(q):
    if '你叫什么名字' in q:
        return '我叫小饼'
    else :
        return '你说什么'
while(True):
    rec(WAVE_OUTPUT_FILENAME)

    pcm_file = wav2pcm(WAVE_OUTPUT_FILENAME)

    res_str = asr(pcm_file)

    faq_res = faq(res_str)

    synth(faq_res)

    play_mp3(MP3_OUTPUT_FILENAME)