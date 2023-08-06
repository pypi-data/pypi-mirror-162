# -*- coding: utf-8 -*-
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
"""
@author: Damien CHAPON (damien.chapon@cea.fr)
"""
from celery import Celery
from kombu import Queue, Exchange
from .commons import TerminusCommons


cmns = TerminusCommons()  # debug=True)
app = Celery('Terminus', include=('Terminus.tasks',))

# -------------------------------------- RabbitMQ messaging queues definition ---------------------------------------- #
# Queue to consume messages from to run data processing jobs and monitor data host status
terminus_exchange = Exchange('terminus', type='direct')
job_queue = Queue("{host!s}.terminus_jobs".format(host=cmns.hostname), exchange=terminus_exchange, no_declare=True,
                  routing_key="{host!s}.terminus_job".format(host=cmns.hostname),
                  queue_arguments={'x-max-length': 1024, 'x-overflow': 'reject-publish', 'x-max-priority': 128})
monitor_queue = Queue("{host!s}.monitor".format(host=cmns.hostname), exchange=terminus_exchange, no_declare=True,
                      routing_key="{host!s}.monitoring".format(host=cmns.hostname),
                      queue_arguments={'x-max-length': 32, 'x-overflow': 'reject-publish',
                                       'x-message-ttl': 30000,  # Messages expires after 30 seconds
                                       'x-dead-letter-exchange': 'galactica.status',
                                       'x-dead-letter-routing-key': 'host_down'})


# Exchange to publish job status update/monitoring status update messages to
status_exchange = Exchange('galactica.status', type='direct')
# status_queue = Queue('galactica.status_update', exchange=status_exchange, routing_key='galactica.terminus_status',
#                      no_declare=True, queue_arguments={'x-max-length': 128, 'x-overflow': 'reject-publish'})
# -------------------------------------------------------------------------------------------------------------------- #

# Optional configuration, see the application user guide :
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#configuration
app.conf.update(
    enable_utc=True,
    broker_url=cmns.rabbitmq_url,
    task_create_missing_queues=False,
    task_queues=(job_queue, monitor_queue),
    task_default_queue=job_queue.name,
    task_acks_late=True,           # \_  Priority queue in RabbitMQ message broker
    worker_prefetch_multiplier=1,  # /
    worker_enable_remote_control=False
)


# @app.task(bind=True)
# def debug_task(self):
#     print('Request: {0!r}'.format(self.request))


if __name__ == "__main__":
    app.start()
