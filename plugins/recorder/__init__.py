#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

import voice_recorder


def run(readable_results, data, rawbuf):
    print(readable_results)

    if(len(readable_results) > 0):
        firstCmd = readable_results[0]
        voice_recorder.handleTerm(firstCmd)
