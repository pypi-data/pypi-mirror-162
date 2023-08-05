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

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pathlib              import Path
from ietfdata.datatracker import *
from ietfdata.rfcindex    import *

dt = DataTracker()

#for st in dt.document_state_types():
#    print(f"{st.slug} {st.label}")


#    candidat     Candidate RG Document
#    active       Active RG Document
#    parked       Parked RG Document
#    rg-lc        In RG Last Call
#    sheph-w      Waiting for Document Shepherd
#    chair-w      Waiting for IRTF Chair
#    irsg-w       Awaiting IRSG Reviews
#    irsg_review  IRSG Review
#    irsgpoll     In IRSG Poll
#    iesg-rev     In IESG Review

#    rfc-edit     Sent to the RFC Editor
#    pub          Published RFC
#    iesghold     Document on Hold Based On IESG Request
#    dead         Dead IRTF Document
#    repl         Replaced
#
#    candidat --> active --> rg-lc --> sheph-w --> chair-w --> irsg-w
#                  |  ^        |         ^            |          |
#                  |  |        |         |            |          |
#              +---+  +--------+         +------------+          v
#              |   |  |                                      irsg_review
#              |   v  |                                          |
#              |  parked                                         |
#              |    |                                            v
#              |    |                                         irsgpoll
#              |    v                                            |
#              +-> dead                                          |
#                                                                v
#                                                             iesg-rev
#                                                                 


stream = dt.document_state_type_from_slug("draft-stream-irtf")
for s in dt.document_states(stream):
    print(f"{s.slug:12} {s.name}")
    for next_uri in s.next_states:
        next = dt.document_state(next_uri)
        print(f" - {next.slug}")

