#!/usr/bin/env python
#
# Copyright (C) 2016 The CyanogenMod Project
# Copyright (C) 2017-2020 The LineageOS Project
#
# SPDX-License-Identifier: Apache-2.0
#

import os
import sys
from hashlib import sha1

DEVICE = 'whyred'
VENDOR = 'xiaomi'
VENDOR_PATH = os.path.join(
    *['..', '..', '..', 'vendor', VENDOR, DEVICE, 'proprietary'])


class Updater:
    def __init__(self, filename):
        self.filename = filename
        with open(self.filename, 'r') as f:
            self.lines = f.read().splitlines()

    def write(self):
        with open(self.filename, 'w') as f:
            f.write('\n'.join(self.lines) + '\n')

    def cleanup(self):
        for index, line in enumerate(self.lines):
            # Skip empty or commented lines
            if len(line) == 0 or line[0] == '#' or '|' not in line:
                continue

            # Drop SHA1 hash, if existing
            self.lines[index] = line.split('|')[0]

        self.write()

    def update(self):
        need_sha1 = False
        for index, line in enumerate(self.lines):
            # Skip empty lines
            if len(line) == 0:
                continue

            # Check if we need to set SHA1 hash for the next files
            if line[0] == '#':
                need_sha1 = (' - from' in line)
                continue

            if need_sha1:
                # Remove existing SHA1 hash
                line = line.split('|')[0]

                file_path = line.split(';')[0].split(':')[-1]
                if file_path[0] == '-':
                    file_path = file_path[1:]

                with open(os.path.join(VENDOR_PATH, file_path), 'rb') as f:
                    hash = sha1(f.read()).hexdigest()

                self.lines[index] = '{}|{}'.format(line, hash)

        self.write()


for file in ['proprietary-files.txt']:
    updater = Updater(file)
    if len(sys.argv) == 2 and sys.argv[1] == '-c':
        updater.cleanup()
    else:
        updater.update()
