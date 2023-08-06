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
import os
import time
import subprocess
import tarfile
import shutil
from celery.utils.log import get_task_logger
from .celery import app
from .jobs import TerminusJob
from .job_status import JobStatus
from .commons import TerminusCommons, PostProcessingServiceNotFoundError, DataDirectoryNotFoundError, \
                     JobSubmissionError, PostProcessingServiceInfoError, PostProcessingServiceInfoNotFoundError


log = get_task_logger(__name__)


@app.task(bind=True, name='update_server_online', exchange='galactica.status', routing_key="host_online",
          ignore_result=True)
def update_server_online(self, host):
    pass


@app.task(bind=True, exchange='terminus', name='test_terminus_server_is_up', ignore_result=True)
def test_terminus_server_is_up(self, host):
    """Tests whether a Terminus server instance is up"""
    # log.warning("Terminus server '{h:s}' is up !")
    update_server_online.apply_async(args=[host, ])
    return True


def _job_directory_cleanup(jobdir, debug=False):
    # Job directory cleanup
    if jobdir is not None and os.path.isdir(jobdir):
        if not debug:
            # Delete job execution directory
            shutil.rmtree(jobdir)
        else:
            # --------------------- Move the directory to the '__failed' dir ----------------------- #
            cmns = TerminusCommons()
            failed_dir = cmns.failed_jobs_directory
            if not os.path.isdir(failed_dir):  # Create __failed directory if not already created
                os.mkdir(failed_dir)

            # Destination directory in '__failed' dir
            dest_dir = os.path.join(failed_dir, os.path.basename(jobdir))
            if os.path.isdir(dest_dir):  # Possible cleanup
                shutil.rmtree(dest_dir)
            # Move directory
            shutil.move(jobdir, dest_dir)


@app.task(bind=True, exchange='terminus', name='execute_terminus_job', ignore_result=True)
def execute_terminus_job(self, jobid, service_name, cat_alias, proj_alias, exp_alias, data_ref, **serv_kwargs):
    cmns = TerminusCommons()
    data_path = os.path.join(cat_alias, proj_alias, exp_alias)
    log.info("[task.py::execute_terminus_job] Received Terminus job #{jid:d} (service={service_name!s}, data_path={path!s}, "
             "data_reference={dref!s})".format(jid=jobid, service_name=service_name, path=data_path, dref=data_ref))

    # activate or not test mode to probe service 
    test_mode = serv_kwargs.pop("test", False)

    # check that test_mode is a boolean value
    if not isinstance(test_mode, bool):
        log.warning("[task.py::execute_terminus_job] Terminus job #{jid:d} not submitted: test_mode not a boolean error.".format(jid=jobid))
        # Call celery task to update job status on the web server remotely
        update_terminus_job_status.apply_async(args=[jobid, cmns.FAILURE_STATUS,
                                                     "'test_mode' type error: job submission failed"])
        return

    # Create TerminusJob instance
    tjob = TerminusJob(jobid, service_name, serv_kwargs, data_path, data_ref=data_ref, test_mode=test_mode)

    # ------------------------------------------------ Job submission ------------------------------------------------ #
    try:
        tjob.submit()
        log.info("[task.py::execute_terminus_job] Job (#{jid:d}) successfully submitted (pending execution)".format(jid=jobid))
        update_terminus_job_status.apply_async(
            args=[tjob.id, cmns.PENDING_STATUS, "Job successfully submitted (pending execution)"])  # , kwargs={})  # , priority=10)
    except DataDirectoryNotFoundError:  # as err:  # Simulation data directory not found on filesystem
        # Call celery task to update job status on the web server remotely
        log.error("[task.py::execute_terminus_job] Terminus job #{jid:d} not submitted: data directory '{dpath!s}' not "
                 "found".format(jid=jobid, dpath=tjob.data_path))
        msg = "Raw simulation data directory '{dpath!s}' not found.".format(dpath=tjob.data_path)
        update_terminus_job_status.apply_async(args=[tjob.id, cmns.FAILURE_STATUS, msg])  # , kwargs={})  # , priority=10)
        return
    except PostProcessingServiceNotFoundError:  # as err:  # Invalid post-processing  service
        log.error("[task.py::execute_terminus_job] Terminus job #{jid:d} not submitted: post-processing service '{service_name!s}' not "
                 "available".format(jid=jobid, service_name=tjob.service))
        # Call celery task to update job status on the web server remotely
        update_terminus_job_status.apply_async(args=[tjob.id, cmns.FAILURE_STATUS,
                                                     "Post-processing service '{service_name!s}' is not "
                                                     "available.".format(service_name=tjob.service)])  # , kwargs={})  # , priority=10)
        return
    except JobSubmissionError:  # as err:  # An error occurred during job (SLURM) submission
        log.error("[task.py::execute_terminus_job] Terminus job #{jid:d} not submitted: SLURM submission error.".format(jid=jobid))
        # Call celery task to update job status on the web server remotely
        update_terminus_job_status.apply_async(args=[tjob.id, cmns.FAILURE_STATUS,
                                                     "SLURM error : job submission failed"])  # , kwargs={})  # , priority=10)
        _job_directory_cleanup(tjob.find_job_directory(check=False), debug=True)
        return
    except PostProcessingServiceInfoNotFoundError:  # no service.json config file
        log.error("[task.py::execute_terminus_job] Terminus job #{jid:d} not submitted: post-processing service '{service_name!s}' missing"
                 "service.info file".format(jid=jobid, service_name=tjob.service))
        msg = "Service configuration json file 'service.json' not found."
        update_terminus_job_status.apply_async(args=[tjob.id, cmns.FAILURE_STATUS, msg])
        return
    except PostProcessingServiceInfoError:  # problem detected with service.json config file
        log.error("[task.py::execute_terminus_job] Terminus job #{jid:d} not submitted: post-processing service '{service_name!s}' problem detected "
                 "with service.info file".format(jid=jobid, service_name=tjob.service))
        msg = "Service configuration 'service.json' format not correct ."
        update_terminus_job_status.apply_async(args=[tjob.id, cmns.FAILURE_STATUS, msg])
        return
    # ---------------------------------------------------------------------------------------------------------------- #

    # -------------------------------- Job execution handled by the SLURM controller --------------------------------- #
    job_dir = tjob.find_job_directory(check=False)
    job_dir_del_msg = "Job execution directory has been removed by sysadmin during execution."
    last_status_update = None

    # Wait for job status JSON file to be created upon execution of the SLURM job
    while os.path.isdir(job_dir) and not JobStatus.exists(job_dir=job_dir):
        time.sleep(5)

    while True:
        if not JobStatus.exists(job_dir=job_dir):  # Should never happen => job directory removed during execution
            log.error("[task.py::execute_terminus_job] Job (#{jid:d}) execution directory has been deleted !".format(jid=jobid))
            update_terminus_job_status.apply_async(
                args=[tjob.id, cmns.FAILURE_STATUS, job_dir_del_msg])  # , kwargs={})  # , priority=10)
            _job_directory_cleanup(job_dir)
            return

        status = JobStatus.last_updated(last_update_time=last_status_update, job_dir=job_dir)
        if status is None:
            time.sleep(5)  # Status not modified
        else:  # Updated status/message
            last_status_update, new_status, new_message = status
            if new_status == 'running':
                log.info("[task.py::execute_terminus_job] Terminus job #{jid:d} is running !".format(jid=jobid))
                update_terminus_job_status.apply_async(
                    args=[tjob.id, cmns.RUNNING_STATUS, "Job is running."])  # , kwargs={})  # , priority=10)
                time.sleep(5)
                continue
            elif new_status == 'failed':
                log.error("[task.py::execute_terminus_job] Terminus job #{jid:d} stopped. Error: {err!s}.".format(jid=jobid, err=new_message))
                update_terminus_job_status.apply_async(
                    args=[tjob.id, cmns.FAILURE_STATUS, "Job stopped with error message : "
                                                        "'{err_msg!s}'.".format(err_msg=new_message)])  # , kwargs={})  # , priority=10)
                _job_directory_cleanup(job_dir, debug=True)
                return
            elif new_status == 'timed out':
                log.error("[task.py::execute_terminus_job] Terminus job #{jid:d} timed out".format(jid=jobid))
                update_terminus_job_status.apply_async(
                    args=[tjob.id, cmns.TIMED_OUT_STATUS, "Job timed out"])  # , kwargs={})  # , priority=10)
                _job_directory_cleanup(job_dir, debug=True)
                return
            elif new_status == 'completed':
                log.info("[task.py::execute_terminus_job] Terminus job #{jid:d} completed successfully.".format(jid=jobid))
                update_terminus_job_status.apply_async(
                    args=[tjob.id, cmns.SUCCESS_STATUS, "Job completed successfully."])  # , kwargs={})  # , priority=10)
                break
            else:
                time.sleep(5)
    # ---------------------------------------------------------------------------------------------------------------- #

    # ----------------------------------------------- Do not upload in test mode ------------------------------------- #
    if test_mode:
        _job_directory_cleanup(job_dir)
        return
    # ---------------------------------------------------------------------------------------------------------------- #

    # ----------------------------------------------- Data upload ---------------------------------------------------- #
    if os.path.isdir(job_dir):
        output_datadir = os.path.join(job_dir, "out")
    else:
        log.error("[task.py::execute_terminus_job] Job (#{jid:d}) execution directory has been deleted !".format(jid=jobid))
        update_terminus_job_status.apply_async(args=[tjob.id, cmns.FAILURE_STATUS, job_dir_del_msg])  # , kwargs={})  # , priority=10)
        return
    targz_fname = "{job_name!s}.tar.gz".format(job_name=tjob.job_name)
    try:
        # Build compressed archive file (*.tar.gz)
        targz_fpath = os.path.join(job_dir, targz_fname)
        with tarfile.open(name=targz_fpath, mode='w:gz') as tar_file:
            tar_file.add(output_datadir, arcname=tjob.service)
        
        # check tarball size according to Galactica max filesize
        # targz_bsize = float(os.path.getsize(targz_fpath))
        # targz_bsize /= (1024.0*1024.0)  # to Mb (most of services should results in a few Mb tarball)
        # if( targz_bsize > Galactica_max_file_size_gb*1024 ):
        #   raise ResultTarballToBig(job.service)

        # Upload TARGZ file on the Galactica web server
        host = cmns.upload_hostname
        log.info("[task.py::execute_terminus_job] Uploading '{targz_fname!s}' file to Galactica server "
                 "(target: {host:s}.".format(targz_fname=targz_fname, host=host))
        rsync_p = subprocess.Popen(['rsync', '-avP', targz_fpath, "{gal_host!s}:".format(gal_host=host)],
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    except tarfile.TarError as tarerr:
        log.error("[task.py::execute_terminus_job] '{targz_fname!s}' file creation failed: {err!s}".format(targz_fname=targz_fname, err=str(tarerr)))
        msg = "An error occurred during job data tarball file creation."
        update_terminus_job_status.apply_async(args=[tjob.id, cmns.FAILURE_STATUS, msg])  # , kwargs={})  # , priority=10)
        _job_directory_cleanup(job_dir, debug=True)
        return

    while rsync_p.poll() is None:
        log.info("[task.py::execute_terminus_job] : ", rsync_p.stdout.readline())
        # Upload on Galactica server is still pending, wait 5s...
        #time.sleep(5)

    # Upload is finished => update job status in db and clean up file system
    if rsync_p.returncode == 0:  # Upload is finished without error
        # Update job status in Galactica
        log.info("[task.py::execute_terminus_job] '{targz_fname!s}' file upload completed !".format(targz_fname=targz_fname))
        update_terminus_job_status.apply_async(
            args=[tjob.id, cmns.PUBLISHED_STATUS, "Job data tarball successfully uploaded."])  # , kwargs={})  # , priority=10)
        _job_directory_cleanup(job_dir)
    else:  # Upload finished with an error
        # Update job status in Galactica
        log.error("[task.py::execute_terminus_job] '{targz_fname!s}' file upload stopped with error".format(targz_fname=targz_fname))
        msg = "Job execution completed successfully but an error occurred during job data transfer."
        update_terminus_job_status.apply_async(args=[tjob.id, cmns.FAILURE_STATUS, msg])  # , kwargs={})  # , priority=10)
        _job_directory_cleanup(job_dir, debug=True)
    # ---------------------------------------------------------------------------------------------------------------- #


@app.task(exchange='galactica.status', routing_key='galactica.terminus_status', ignore_result=True,
          name='update_terminus_job_status')
def update_terminus_job_status(jobid, status, message):
    pass


__all__ = ['execute_terminus_job', 'update_terminus_job_status']
