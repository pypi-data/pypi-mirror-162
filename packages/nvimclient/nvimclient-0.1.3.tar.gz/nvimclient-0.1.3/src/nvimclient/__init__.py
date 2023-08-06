# -*- coding: utf-8 -*-
# @Auther: Verf
# @Emal: verf@protonmail.com
import os
import sys
import time
import argparse
import subprocess
import importlib.metadata

import pynvim

__version__ = importlib.metadata.version('nvimclient')


def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v',
                        '--version',
                        help='print version info',
                        action='store_true')
    parser.add_argument('-s',
                        '--server',
                        help='neovim server address',
                        type=str)
    parser.add_argument('-g',
                        '--gui',
                        help='open nvim in provided gui if not exist',
                        type=str)
    parser.add_argument('path', nargs='*', help='file path to open')
    args = parser.parse_args()

    if args.version:
        print('nvimclient {}'.format(__version__))
        sys.exit()

    if args.server:
        addr = args.server
    elif os.getenv('NVIM_LISTEN_ADDRESS'):
        addr = os.getenv('NVIM_LISTEN_ADDRESS')
    else:
        sys.stderr.write('Cannot find neovim server address.')
        sys.exit(-1)

    nvim = None
    # try attach to exist neovim instance
    try:
        nvim = pynvim.attach("socket", path=addr)
        isattach = True
    except FileNotFoundError:
        isattach = False

    # if not exist instance, open new instance
    if not isattach:
        try:
            if args.gui:
                subprocess.Popen(args.gui)
            else:
                subprocess.call(['nvim', *args.path], shell=True)
                sys.exit()
        except FileNotFoundError:
            sys.stderr.write('Cannot open new neovim instance')
            sys.exit(-1)
        # try attach to new instance
        for _ in range(25):
            try:
                nvim = pynvim.attach("socket", path=addr)
                isattach = True
                break
            except FileNotFoundError:
                time.sleep(0.2)

    if not isattach:
        sys.stderr.write('Cannot attach to neovim instance')
        sys.exit(-1)

    if args.path:
        for path in args.path:
            path = os.path.abspath(path)
            if os.path.isdir(path):
                nvim.command(':cd {}'.format(path))
            else:
                nvim.command(':e {}'.format(path))
    nvim.close()
    sys.exit()
