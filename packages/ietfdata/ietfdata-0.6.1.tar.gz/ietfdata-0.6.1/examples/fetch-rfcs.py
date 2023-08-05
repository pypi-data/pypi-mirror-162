#!/usr/bin/env python3.8
#
# Copyright (c) 2022 Colin Perkins
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import requests
import sys
import time

from pathlib              import Path
from ietfdata.rfcindex    import *
from ietfdata.datatracker import *

def save_url(url, outfile):
    retry = True
    retry_time = 1
    while retry:
        try:
            response = http.get(url, verify=True)
            if response.status_code == 200:
                retry = False
                retry_time = 1
                with open(outfile, "wb") as outf:
                    outf.write(response.content)
            else:
                print(f"  error {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"  error connection failed: retry in {retry_time}")
            http.close()
            time.sleep(retry_time)
            retry_time *= 2
            retry = True

def fetch_rfcs():
    print("Fetching RFCs:")
    for rfc in reversed(list(ri.rfcs())):
        rfc_dir = Path(f"data/rfc/{rfc.doc_id.lower()}")

        if not rfc_dir.exists():
            print(f"  mkdir {rfc_dir}")
            rfc_dir.mkdir(parents=True)

        if not rfc_dir.is_dir():
            print(f"error {rfc_dir} exists but is not a directory")
            sys.exit(1)

        for fmt in rfc.formats:
            # `fmt` will be done of ASCII, PDF, PS, HTML, XML, TEXT.
            # TEXT is plain text generated from an RFC-XML v3 format.
            # ASCII is the original textual RFC format (which is not,
            # despite the name, always ASCII format).
            if fmt in ["XML", "TEXT", "ASCII"]:
                rfc_url  = rfc.content_url(fmt)
                rfc_file = Path(f"{rfc_dir}/{rfc.doc_id}.{fmt}".lower())
                if not rfc_file.exists():
                    print(f"  fetch {str(rfc_file):30} ({rfc_url})")
                    save_url(rfc_url, rfc_file)


dt   = DataTracker()
ri   = RFCIndex()
http = requests.Session()

fetch_rfcs()

