# Copyright (C) 2022 University of Glasgow
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import email.header
import email.utils
import json
import os
import re
import string
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dataclasses          import dataclass, field
from pathlib              import Path
from ietfdata.datatracker import *
from ietfdata.mailarchive import *

dt      = DataTracker()
archive = MailArchive()
lists   = list(archive.mailing_list_names())
addrs   = {}
lists_for_addr = {}
list_totals = {}
total_2021  = 0
msgs_per_list = {}

index = 1
for ml_name in lists:
    print(F"{index:5d} /{len(lists):5d} {ml_name:40}", end="")
    index += 1
    failed = 0
    total_list  = 0
    ml = archive.mailing_list(ml_name)
    ml.update()
    msgs_per_list[ml_name] = {}
    for msg in ml.messages():
        msg822 = msg.rfc822_message()
        date_str = msg822.get("Date")
        date = email.utils.parsedate_to_datetime(date_str)
        year = date.timetuple().tm_year
        if year == 2021:
            total_list += 1
            total_2021 += 1
            n, e = email.utils.parseaddr(msg822.get("From"))
            if e != "":
                if e not in addrs:
                    addrs[e] = n

                if e not in lists_for_addr:
                    lists_for_addr[e] = [ml_name]
                else:
                    if ml_name not in lists_for_addr[e]:
                        lists_for_addr[e].append(ml_name)

                if e not in msgs_per_list[ml_name]:
                    msgs_per_list[ml_name][e] = 1
                else:
                    msgs_per_list[ml_name][e] += 1
                

    list_totals[ml_name] = total_list
    print(F"   {total_list:6}")

results = {}
results["num_msgs_in_total"] = total_2021
results["num_msgs_per_list"] = list_totals
results["addrs"]             = addrs
results["lists_for_addr"]    = lists_for_addr
results["msgs_per_list"]     = msgs_per_list

with open(Path("emails-2021.json"), "w") as outf:
    json.dump(results, outf, sort_keys=True, indent=2)

# =============================================================================
