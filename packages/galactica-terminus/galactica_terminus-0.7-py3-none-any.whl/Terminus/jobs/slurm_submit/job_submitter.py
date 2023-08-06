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
import stat
import json
import time
import re
import shutil
import subprocess
from Terminus.commons import TerminusCommons, PostProcessingServiceNotFoundError, DataDirectoryNotFoundError,\
    JobSubmissionError, PostProcessingServiceInfoNotFoundError, PostProcessingServiceInfoError

from celery.utils.log import get_task_logger

log = get_task_logger(__name__)


class JobSubmitter(object):
    """
    Job submission class
    """
    JOB_PYTHON_FILENAME = "job.py"
    DIGIT_STARTING_SERVICE_MODULE = re.compile("^[0-9].*$")

    def __init__(self, test_mode=False):
        self._commons = TerminusCommons()
        self._test_mode = test_mode

    @property
    def service_list(self):
        """
        Get the list of installed services
        """
        services = {}
        for d in os.listdir(self._commons.service_directory_path):
            p = os.path.join(self._commons.service_directory_path, d)
            if os.path.isdir(p):
                services[d] = p
        return services

    def _check_service_json(self, file_path):
        """
        Check the content of the json service.json file.
        """
        _available_job_type = ["python"]  # extend to "bash" someday ?
        _first_level_keys = ["job"]
        _second_level_keys = ["type", "interpreter", "n_nodes", "n_cores", "timout_mn"]

        if not os.path.isfile(file_path):
            raise IOError()
        
        # read json info file
        with open(file_path, "r") as info_file:
            service_info = json.load(info_file)
      
        # check that it's a dict
        if not isinstance(service_info, dict):
            raise PostProcessingServiceInfoError(file_path)
      
        # only available key for now is "job"
        if len(service_info.keys()) == 0 or len(service_info.keys()) > 1:
            raise PostProcessingServiceInfoError(file_path)
      
        # check dict keys
        for k in _first_level_keys:
            if k not in service_info:
                raise PostProcessingServiceInfoError(file_path)

            # for now it must be a dict too
            if not isinstance(service_info[k], dict):
                raise PostProcessingServiceInfoError(file_path)
        
            for kk in _second_level_keys:
                if kk not in service_info[k]:
                    if kk in ["n_nodes", "n_cores", "timout_mn"]:
                        # These are optional, it's ok...
                        pass
                    else:
                        raise PostProcessingServiceInfoError(file_path)

        # check keys values
        if service_info["job"]["type"] not in _available_job_type:
            raise PostProcessingServiceInfoError(file_path)
      
        # check interpreter path
        if not os.path.isfile(service_info["job"]["interpreter"].strip()):
            raise PostProcessingServiceInfoError(file_path)

        # Check number of nodes value
        if "n_nodes" in service_info["job"]:
            try:
                n_nodes = int(service_info["job"]["n_nodes"])
            except:
                raise PostProcessingServiceInfoError(file_path)

        # Check number of nodes value
        if "n_cores" in service_info["job"]:
            try:
                n_cores = int(service_info["job"]["n_cores"])
            except:
                raise PostProcessingServiceInfoError(file_path)

        # Check job timout (minutes)
        if "timout_mn" in service_info["job"]:
            try:
                timeout_mn = int(service_info["job"]["timout_mn"])

            except:
                raise PostProcessingServiceInfoError(file_path)
        return service_info

    def submit(self, job):
        """
        Job submission method

        Parameters
        ----------
        job: ``TerminusJob``
            post-processing job instance
        """
        template_dir = os.path.join(self._commons.terminus_root_directory, "etc")

        # Check job service exists on the server
        sdict = self.service_list
        if job.service not in sdict:
            raise PostProcessingServiceNotFoundError(job.service)
        # job_script_base = os.path.join(self._commons.service_directory_path, JobSubmitter.JOB_PYTHON_FILENAME)
        job_script_base = os.path.join(template_dir, JobSubmitter.JOB_PYTHON_FILENAME)

        module_file = os.path.join(sdict[job.service], "{service_name!s}.py".format(service_name=job.service))
        if not os.path.isfile(job_script_base) or not os.path.isfile(module_file):
            raise PostProcessingServiceNotFoundError(job.service)

        # Check data directory exists on the server
        abs_data_path = job.absolute_data_path
        if not os.path.isdir(abs_data_path):
            raise DataDirectoryNotFoundError(job.data_path)

        # Clear/create job run directory
        job_dir = job.find_job_directory(check=False)
        if os.path.isdir(job_dir):
            shutil.rmtree(job_dir, ignore_errors=True)
        os.makedirs(os.path.join(job_dir, "out"))

        # Deprecated --------------------------------------------------------------------
        #
        # read python.info from service directory. This file has to be created 
        # by the user that create the service
        # 
        # python_info_path = os.path.join(sdict[job.service], "python.info")
        # job_custom_python_interp_path = ""
        # try:
        #     with open(python_info_path, 'r') as python_infofile:
        #         for line in python_infofile:
        #             if "PYTHON=" in line or "python=" in line:
        #                 job_custom_python_interp_path = line.replace("\n", "").split("=")[1]
        # except IOError as e:
        #     raise JobSubmissionError(str(e))

        # this replace the old python.info by a json file containing
        # information about the job type and interpreter, this file is mandatory
        service_info_path = os.path.join(sdict[job.service], "service.json")
        try:
            service_info = self._check_service_json(service_info_path)
        except IOError:
            raise PostProcessingServiceInfoNotFoundError(job.service)

        log.info("[job_submitter.py::submit] Job #{jid:d} type : {job_type:s} !".format(jid=job.id,job_type=service_info["job"]["type"]))
        log.info("[job_submitter.py::submit] Job #{jid:d} interpreter : {interpreter:s} !".format(jid=job.id, interpreter=service_info["job"]["interpreter"]))
        job_nnodes = int(service_info["job"].get("n_nodes", 1))
        log.info("[job_submitter.py::submit] Job #{jid:d} nodes: {nn:d} !".format(jid=job.id, nn=job_nnodes))
        job_ncores = int(service_info["job"].get("n_cores", 8))
        log.info("[job_submitter.py::submit] Job #{jid:d} cores : {nc:d} !".format(jid=job.id, nc=job_ncores))
        job_timeout = int(service_info["job"].get("timout_mn", 30))
        log.info("[job_submitter.py::submit] Job #{jid:d} timeout  : {to:d} minutes!".format(jid=job.id, to=job_timeout))
        to_days = job_timeout // (60*24)
        job_timeout -= to_days * 24 * 60
        to_hrs = job_timeout // 60
        to_mns = job_timeout % 60
        job_timeout = "{days:02d}-{hrs:02d}:{mins:02d}".format(days=to_days, hrs=to_hrs, mins=to_mns)
        job_custom_python_interp_path = service_info["job"]["interpreter"].strip()

        # copy the params of the services and add test value 
        copy_job_parameters = job.param_value_dict.copy()
        copy_job_parameters["test"] = self._test_mode
        copy_job_parameters_string = str(copy_job_parameters)
        
        log.info("[job_submitter.py::submit] Job #{jid:d} Galactica parameters : {pvs:s} ".format(jid=job.id, pvs=job.param_values_string))
        log.info("[job_submitter.py::submit] Job #{jid:d} run parameters : {pvs:s} ".format(jid=job.id, pvs=copy_job_parameters_string))

        # Copy main service module file + job_status module + job submission script in job run directory
        if JobSubmitter.DIGIT_STARTING_SERVICE_MODULE.match(job.service) is None:
            job_module_file = job.service
        else:
            job_module_file = "script_{job_service!s}".format(job_service=job.service)
        shutil.copy(module_file, os.path.join(job_dir, "{job_modfile!s}.py".format(job_modfile=job_module_file)))
        job_status_module_file = os.path.join(self._commons.terminus_root_directory, "job_status.py")
        shutil.copy(job_status_module_file, os.path.join(job_dir, "job_status.py"))
        job_script = os.path.join(job_dir, JobSubmitter.JOB_PYTHON_FILENAME)
        try:
            lines = []
            with open(job_script_base, 'r') as base_jobfile:
                for line in base_jobfile:
                    line = line.replace("__TERMINUS_job_nnodes__", str(job_nnodes))
                    line = line.replace("__TERMINUS_job_ncores__", str(job_ncores))
                    line = line.replace("__TERMINUS_job_timeout__", job_timeout)
                    line = line.replace("__TERMINUS_python_interpreter__", job_custom_python_interp_path)
                    line = line.replace("__TERMINUS_job_name__", job.job_name)
                    line = line.replace("__TERMINUS_data_path__", abs_data_path)
                    line = line.replace("__TERMINUS_data_ref__", job.data_reference)
                    line = line.replace("__TERMINUS_host_name__", self._commons.hostname)
                    line = line.replace("__TERMINUS_service_name__", job_module_file)
                    line = line.replace("__TERMINUS_func_kwargs__", copy_job_parameters_string)
                    lines.append(line)

            with open(job_script, 'w') as jobfile:
                for line in lines:
                    jobfile.write(line)
        except IOError as e:
            raise JobSubmissionError(str(e))

        log.info("[job_submitter.py::submit] Job # {jid:d} job.py reading for submission ".format(jid=job.id))

        # set chmod on job_script - BUG in daemonization if not
        os.chmod(job_script, stat.S_IXUSR | stat.S_IXGRP | stat.S_IRUSR | stat.S_IRGRP)

        # Let the filesystem cache refresh so job_status and service Python modules are visible
        time.sleep(10)

        if not self._commons.use_slurm:
            log.info("[job_submitter.py::submit] Job # {jid:d} running job.py".format(jid=job.id))
            p = subprocess.Popen([job_custom_python_interp_path, job_script], cwd=job_dir, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)

        else:  # submit SLURM job in batch mode using 'sbatch'
            p = subprocess.Popen(['sbatch', job_script], cwd=job_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            log.info("[job_submitter.py::submit] Job # {jid:d} submitted to slurm queue".format(jid=job.id))

        # if p.wait() != 0:
        #     # TODO Handle job submission errors
        #     log.warning("A job submission error occured with file %s !" % job_script)
        #     pass


__all__ = ["JobSubmitter"]
