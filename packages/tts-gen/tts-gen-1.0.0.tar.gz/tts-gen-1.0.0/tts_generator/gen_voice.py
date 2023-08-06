#coding: utf-8

import os.path
import requests
import json
from tqdm import tqdm
from tts_generator import __server_url__

def gen_voice(texts, output_dir, server_url=None, voice_num=None):
    if not server_url:
        server_url = __server_url__
    server_synthesize_url = server_url + '/api/synthesize_multi'
    server_info_url = server_url + '/api/info'

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    headers = {
            'User-Agent'         : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36',
            'Accept-Language'    : 'zh-CN,zh;q=0.9',
            #'Content-Type'       : 'application/json',
            }

    with requests.Session() as session:
        r = session.get(url=server_info_url, headers=headers, verify=False)
        info = json.loads(r.text)
        max_voice_num = info['max_voice_num']
        if not voice_num:
            voice_num = max_voice_num
        total_voice_num = min(max_voice_num, voice_num)

        for text in texts:
            print('generate %s wavs ...' % text)

            text_dir = os.path.join(output_dir, text)
            if not os.path.exists(text_dir):
                os.mkdir(text_dir)

            blk_voice_num = 10 # 分块传输
            for voice_index in tqdm(range(0, total_voice_num, blk_voice_num)):
                data = {
                    'text': text,
                    'voice_index': voice_index,
                    'voice_num': min(blk_voice_num, total_voice_num - voice_index),
                    }
                r = session.post(url=server_synthesize_url, data=data, headers=headers, verify=False)
                #print(r.content)
                #print(r.headers['Content-Type'])
                wav_split_map = json.loads(r.headers['Content-Type'])
                for k, v in wav_split_map.items():
                    begin, end = v[0], v[1]
                    with open('%s' % os.path.join(text_dir, k), 'wb') as f:
                        f.write(r.content[begin:end])
                #print('content len:', len(r.content))


if __name__ == '__main__':
    texts = []
    texts.append('你好小爱')
    texts.append('天猫精灵')
    gen_voice(texts, './wavs')

