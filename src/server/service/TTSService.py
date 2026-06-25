import os
import base64
import asyncio
from queue import Queue
from dashscope.audio.qwen_tts_realtime import *
from typing import Any
from dashscope.audio.tts_v2 import VoiceEnrollmentService
from common.utils.OSSUtils import getSystemFileUrl
from common.properties.Voice import voice

class StreamingTTSCallback(QwenTtsRealtimeCallback):
    def __init__(self, q):
        self.q : Queue = q

    def on_open(self) -> None:
        print('ttsModel通信建立')
        pass

    def on_close(self, close_status_code, close_msg) -> None:
        print('ttsModel通信关闭')

    def on_event(self, response: str) -> None:
        try:
            type = response['type']
            if 'session.created' == type:
                print('ttsModel通信开始: session_id={}'.format(response['session']['id']))
            if 'response.audio.delta' == type:
                recv_audio_b64 = response['delta']
                self.q.put(base64.b64decode(recv_audio_b64))
            if 'response.done' == type:
                print(f'ttsModel单次回复完成')
            if 'session.finished' == type:
                self.q.put(None)
                print('ttsModel通信结束')
        except Exception as e:
            print('ttsModel通信错误: {}'.format(e))
            return


class TTSService:
    def __init__(self):
        self.model = os.getenv('TTSMODEL')
        self.url = 'wss://dashscope.aliyuncs.com/api-ws/v1/realtime'


    async def getAudioStream(self, voiceId: str, textStream) -> Any:
        audioQueue = Queue()
        ttsModel = QwenTtsRealtime(
            url=self.url,
            model=self.model,
            callback=StreamingTTSCallback(audioQueue),
        )
        ttsModel.connect()
        ttsModel.update_session(
            voice=voice.voice_id,
            response_format=AudioFormat.PCM_24000HZ_MONO_16BIT,
            mode='server_commit'
        )
        async def audioStream():
            while True:
                audioBytes = await asyncio.to_thread(audioQueue.get)
                if audioBytes is None:
                    break
                yield audioBytes

        async def readTextStream():
            async for text in textStream:
                ttsModel.append_text(text)

        sender = asyncio.create_task(readTextStream())

        async for audio in audioStream():
            yield audio

        await sender

    async def newVoice(self, fileName: str = "LuciaVoice.wav"):
        voiceUrl = getSystemFileUrl(fileName)
        voiceEnrollmentService = VoiceEnrollmentService()
        if self.model is None:
            raise Exception("TTSMODEL 未配置")
        voice_id = voiceEnrollmentService.create_voice(
            target_model=self.model,
            url=voiceUrl,
            prefix=fileName.split('.')[0]
        )
        voice.setVoiceId(voice_id)


ttsService = TTSService()