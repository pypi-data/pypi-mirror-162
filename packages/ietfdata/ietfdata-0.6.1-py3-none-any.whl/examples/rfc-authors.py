# Copyright (C) 2021 University of Glasgow
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

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pathlib              import Path
from ietfdata.datatracker import *
from ietfdata.rfcindex    import *

# =============================================================================

dt = DataTracker()
ri = RFCIndex()

affiliations_for_rfc = {}
affiliations = []

for rfc in ri.rfcs():
    print(f"{rfc.doc_id} -> {rfc.draft}")
    if rfc.draft is not None:
        draft = dt.document_from_rfc(rfc.doc_id)
        if draft is not None:
            for author in dt.document_authors(draft):
                person = dt.person(author.person)
                print(f"  {person.name}, {author.affiliation}")
                if author.affiliation != "":
                    if author.affiliation not in affiliations:
                        affiliations.append(author.affiliation)
                    if rfc.doc_id not in affiliations_for_rfc:
                        affiliations_for_rfc[rfc.doc_id] = [author.affiliation]
                    else:
                        if author.affiliation not in affiliations_for_rfc[rfc.doc_id]: 
                            affiliations_for_rfc[rfc.doc_id].append(author.affiliation)

with open("affiliations_for_rfc.json", "w") as outf:
    print(json.dumps(affiliations_for_rfc, indent = 4), file = outf)

with open("affiliations.json", "w") as outf:
    print(json.dumps(affiliations, indent = 4), file = outf)

