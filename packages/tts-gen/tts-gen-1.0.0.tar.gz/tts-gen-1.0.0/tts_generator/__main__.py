#!/usr/bin/env python

import sys
import argparse
from tts_generator import __version__, __server_url__
from tts_generator.gen_voice import gen_voice

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='tts_gen', description='TTS Generator')
    parser.add_argument('-V', '--version', action='version', version='tts_gen %s' % __version__)
    parser.add_argument('-f', '--file', help='tts keywords file, one keyword per line')
    parser.add_argument('-o', '--output', help='output wavs directory')
    parser.add_argument('-n', '--num', type=int, help='number of wavs to be generated per keyword (default: max)')
    parser.add_argument('-u', '--url', help='url of tts server (default: %s)' % __server_url__)
    args = parser.parse_args()
    if args.file and args.output:
        texts = []
        for line in open(args.file, 'r'):
            line = line.strip(' ').strip('\t').strip('\n')
            if line:
                texts.append(line)
        gen_voice(texts, args.output, server_url=args.url, voice_num=args.num)
    else:
        parser.print_help()
        sys.exit(0)
