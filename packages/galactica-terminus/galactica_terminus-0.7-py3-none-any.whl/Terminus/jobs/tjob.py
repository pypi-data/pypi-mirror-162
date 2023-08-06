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
import re
import os
from Terminus.commons import TerminusCommons
from .slurm_submit import JobSubmitter


class TerminusJob(object):
    def __init__(self, job_id, service, param_values, data_path, data_ref=None, test_mode=False):
        self._id = job_id
        self._service_name = service
        self._param_valdict = param_values
        self._data_path = data_path
        self._data_reference = data_ref
        self._test_mode = test_mode

    @property
    def id(self):
        return self._id

    @property
    def service(self):
        return self._service_name

    @property
    def job_name(self):
        return "{job_id:d}_{service_name!s}".format(job_id=self._id, service_name=self._service_name)

    @property
    def data_path(self):
        return self._data_path

    @property
    def absolute_data_path(self):
        cmns = TerminusCommons()
        return os.path.join(cmns.data_directory_path, self._data_path)

    @property
    def data_reference(self):
        return self._data_reference

    @property
    def param_values_string(self):
        return str(self._param_valdict)

    @property
    def param_value_dict(self):
        return self._param_valdict

    def find_job_directory(self, check=True):
        """
        Find the job directory absolute path from its name. Performs checks if required.

        :param check: Need to perform check ? Default True
        :return: job directory absolute path
        """
        jname = self.job_name
        cmns = TerminusCommons()
        jdir_path = cmns.job_directory_path
        if check and jname not in os.listdir(jdir_path):
            raise AttributeError("job directory '{job_name!s}' was not found in "
                                 "'{job_dir!s}'.".format(job_name=jname, job_dir=jdir_path))

        d = os.path.join(jdir_path, jname)
        if check and not os.path.isdir(d):
            raise AttributeError("job directory '{job_name!s}' is not a valid directory.".format(job_name=jname))

        return d

    def submit(self):
        """
        Tries to submit itself on the SLURM queue

        :return:
        """
        s = JobSubmitter(self._test_mode)
        s.submit(self)


__all__ = ['TerminusJob']
