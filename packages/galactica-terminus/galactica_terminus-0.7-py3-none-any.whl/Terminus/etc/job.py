#!__TERMINUS_python_interpreter__
# -*- coding: utf-8 -*-
#SBATCH --job-name=__TERMINUS_job_name__   # job name
#SBATCH -N __TERMINUS_job_nnodes__                               # number of nodes
#SBATCH -n __TERMINUS_job_ncores__                               # number of cores
#SBATCH --mem 2048                         # memory pool for per node (MB)
#SBATCH --time=__TERMINUS_job_timeout__                    # time (DD-HH:MM)
#SBATCH --output=log_%j.out                # STDOUT
#SBATCH --error=log_%j.err                 # STDERR

# This software is part of the Terminus software project.
#
# Copyright © Commissariat a l'Energie Atomique et aux Energies Alternatives (CEA)
#
#  FREE SOFTWARE LICENCING
#  -----------------------
# This software is governed by the CeCILL license under French law and abiding by the rules of distribution of free
# software. You can use, modify and/or redistribute the software under the terms of the CeCILL license as circulated by
# CEA, CNRS and INRIA at the following URL: "http://www.cecill.info". As a counterpart to the access to the source code
# and rights to copy, modify and redistribute granted by the license, users are provided only with a limited warranty
# and the software's author, the holder of the economic rights, and the successive licensors have only limited
# liability. In this respect, the user's attention is drawn to the risks associated with loading, using, modifying
# and/or developing or reproducing the software by the user in light of its specific status of free software, that may
# mean that it is complicated to manipulate, and that also therefore means that it is reserved for developers and
# experienced professionals having in-depth computer knowledge. Users are therefore encouraged to load and test the
# software's suitability as regards their requirements in conditions enabling the security of their systems and/or data
# to be ensured and, more generally, to use and operate it in the same conditions as regards security. The fact that
# you are presently reading this means that you have had knowledge of the CeCILL license and that you accept its terms.
#
#
# COMMERCIAL SOFTWARE LICENCING
# -----------------------------
# You can obtain this software from CEA under other licencing terms for commercial purposes. For this you will need to
# negotiate a specific contract with a legal representative of CEA.
#

from __future__ import unicode_literals, absolute_import

import signal
import sys
import os
import time
from datetime import datetime
import json

# debug
import logging
from logging import handlers

log = logging.getLogger("job")  # nom Terminus.job
log.addHandler(logging.handlers.RotatingFileHandler("out/job.log"))

# Import local job_status module
import_retries = 1

#prevent issue job_status not found if cwd || "./" is not in path
sys.path.append(os.getcwd())
while True:
    try:
        log.warning("Try to import 'job_status' module (test #{itry:d}/20)".format(itry=import_retries))
        from job_status import JobStatus
        break
    except ImportError as exc:
        if import_retries >= 20:
            raise IOError("Service module could not be imported after 60 seconds filesystem cache sync. timeout")
        log.warn("'job_status' module cannot be imported... Wait 3 seconds")
        import_retries += 1
        time.sleep(3)  # Wait 3 seconds to sync filesystem cache

log.warning("Imported 'job_status' module.")

# Import local service module
import_retries = 1
while True:
    try:
        log.warning("Try to import run from __TERMINUS_service_name__ (test #{itry:d}/12)".format(itry=import_retries))
        from __TERMINUS_service_name__ import run
        break
    except ImportError as exc:
        if import_retries >= 12:
            JobStatus.update('failed', str(exc))
            raise IOError("Service module could not be imported after 1 minute filesystem cache sync. timeout")
        log.warn("Service module cannot be imported... Wait 5 seconds")
        import_retries += 1
        time.sleep(5)  # Wait 5 seconds to sync filesystem cache
    except Exception as exc:
        JobStatus.update('failed', str(exc))
        sys.exit(1)

log.warning("Imported run from __TERMINUS_service_name__")

job_name = "__TERMINUS_job_name__"
datapath = "__TERMINUS_data_path__"
data_ref = "__TERMINUS_data_ref__"
func_kwargs = __TERMINUS_func_kwargs__


# ---------- Define SIGTERM signal handler (sent shortly before job timeout, SIGKILL is sent upon timeout) ----------- #
def signal_term_handler(sig, frame):
    JobStatus.update('timed out', "job timed out.")
    sys.exit(1)
signal.signal(signal.SIGTERM, signal_term_handler)
# -------------------------------------------------------------------------------------------------------------------- #

log.warning("signal_term_handler defined")

# Publish message to set job status as RUNNING before running the job
JobStatus.update('running', "job is running")

log.warning("Job is running ... ")

# Start time
str_beg = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

try:
    run(datapath, data_ref, **func_kwargs)
    log.warn("Job launched from run function ... ")

except Exception as exc:
    # Publish message to set job status as ERROR if job failed
    JobStatus.update('failed', str(exc))

    log.warning("Job failed ... ")

    sys.exit(1)


# Stop time
str_end = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

log.warning("Job finished successfully ... ")

# --------------------------- Save run info in JSON config file (documentation) ---------------------------------- #
# Get simulation data path relative to base data directory (in 'TERMINUS_DATA_DIR' env. variable)
d = {'service_name': '__TERMINUS_service_name__',
     'host': "__TERMINUS_host_name__",
     'data': {'data_path': '__TERMINUS_data_path__', 'data_reference': data_ref},
     'run_parameters': func_kwargs,
     'time_info': {'job_start': str_beg, 'job_finished': str_end},
}

with open(os.path.join("out", "processing_config.json"), 'w') as f:
    json.dump(d, f, indent=4)
# ---------------------------------------------------------------------------------------------------------------- #

log.warning("Json file created ! ")

# Publish message to set job status as COMPLETED if job succeeded
JobStatus.update('completed', "job executed successfully")

log.warning("Job completed ! ")

sys.exit(0)
