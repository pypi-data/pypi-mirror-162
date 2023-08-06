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
@author: Loic STRAFELLA (loic.strafella@cea.fr)
"""
import sys
import stat
import os
import shutil
import socket
import getpass
import argparse
from datetime import datetime
import readline
import glob
import re
import subprocess
import json
from Terminus.commons import TerminusCommons


def _fpath_auto_complete(text, state):
    if text.startswith("~"):
        search_path = os.path.expanduser(text)
    elif text.startswith("$"):
        search_path = os.path.expandvars(text)
    else:
        search_path = text
    return (glob.glob(search_path+'*')+[None])[state]


# Set filepath auto completion for input() calls
readline.set_completer_delims(' \t\n;')
readline.parse_and_bind("tab: complete")
readline.set_completer(_fpath_auto_complete)


class TerminusConfigManager(object):
    IP_ADDR_REGEXP = re.compile("^((25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]\\d|\\d)\\.){3}"
                                "(25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]\\d|\\d)$")
    _RABBITMQ_SECRET_FILE = "rabbitmq_server_pwd"
    _RABBITMQ_SECRET_DIR = "_secret"

    TERMINUS_SERVICE_FILE = "terminus.service"
    CELERY_DEAMON_NNODES = "CELERYD_NODES"
    CELERY_DAEMON_OPTIONS = "CELERYD_OPTS"

    # _terminus_env_pythonpath = ""
    _job_scheduler_slurm = 0
    
    # config parameters
    terminus_parameters = {TerminusCommons.ENVVAR_TERMINUS_HOSTNAME: "", TerminusCommons.ENVVAR_DOT_DIR: "",
                           TerminusCommons.ENVVAR_DATA_DIR: "", TerminusCommons.ENVVAR_JOBRUNS_DIR: "",
                           TerminusCommons.ENVVAR_ROOT_DIR: "", TerminusCommons.ENVVAR_SERVICE_DIR: "",
                           "User": "''", "Group": "''", TerminusCommons.ENVVAR_UPLOAD_HOST: "Galactica_storage",
                           TerminusCommons.ENVVAR_TERMINUS_USE_SLURM: "", TerminusCommons.ENVVAR_RABBITMQ_USER: "",
                           TerminusCommons.ENVVAR_RABBITMQ_HOST: "", TerminusCommons.ENVVAR_RABBITMQ_PORT: "",
                           TerminusCommons.ENVVAR_RABBITMQ_VIRTUAL_HOST: ""}

    terminus_parameters_works = {TerminusCommons.ENVVAR_DATA_DIR: False, TerminusCommons.ENVVAR_JOBRUNS_DIR: False,
                                 TerminusCommons.ENVVAR_SERVICE_DIR: False}

    # list of warning for path
    path_warning = []

    _terminus_celery_nodes = 2
    _terminus_celery_concurrency = 2

    def __init__(self, read_only=False):
        self._read_only = read_only
        self._home_dir = os.path.expanduser("~")
        self._dot_terminus_path = os.path.join(self._home_dir, TerminusCommons.Default_dot_terminus_dir)

        self._terminus_root_dir = os.path.dirname(os.path.abspath(__file__))

        # Terminus template directory that contains terminus.env and terminus.service template files
        self._terminus_template_dir = os.path.join(self._terminus_root_dir, "etc")

        self.terminus_parameters[TerminusCommons.ENVVAR_ROOT_DIR] = self._terminus_root_dir

        # This makes great bug in case of Python 2 job script 
        #
        # get PYTHONPATH from user env
        # 
        # try:
        #     self._terminus_env_pythonpath = os.environ['PYTHONPATH']
        # except KeyError:
        #     self._terminus_env_pythonpath = ""
        
        # self._terminus_env_pythonpath += ":" + self._terminus_root_dir

        # Get 'celery' executable path to set CELERY_BIN environment variable correctly.
        celery_name = {'linux': 'celery', 'win32': 'celery.exe'}[sys.platform]
        self._terminus_celery_path = os.path.join(os.path.dirname(sys.executable), celery_name)
        if not os.path.isfile(self._terminus_celery_path):
            print("\n\t'{cpath:s}' executable not found...".format(cpath=self._terminus_celery_path))
            if sys.platform == "linux":
                self._terminus_celery_path = subprocess.run(['which', celery_name],
                                                            stdout=subprocess.PIPE).stdout.decode("utf-8").strip("\n")
                if os.path.isfile(self._terminus_celery_path):
                    print("'celery' executable found at {cpath:s}, setting CELERY_BIN env. "
                          "variable".format(cpath=self._terminus_celery_path))
                else:
                    print("Please install Celery and rerun 'terminus_config' CLI.")
            else:
                print("Please install Celery and rerun 'terminus_config' CLI.")
        else:
            print("'celery' executable found at {cpath:s}, setting CELERY_BIN env. "
                  "variable".format(cpath=self._terminus_celery_path))
            
        # this supposes that terminus.env and terminus.service are in .terminus directory which is supposed
        # to be at ~/.terminus
        self._terminus_env_file_path = os.path.join(self._dot_terminus_path, TerminusCommons.Terminus_dot_env_fname)
        self._terminus_serv_file_path = os.path.join(self._dot_terminus_path, self.TERMINUS_SERVICE_FILE)
        self._rabbitmq_secret_path = os.path.join(self._dot_terminus_path, self._RABBITMQ_SECRET_DIR)
        
        # Check ~/.terminus directory
        if not os.path.isdir(self._dot_terminus_path):
            print("\n\t> Creating '%s' directory into the '%s' directory." % (self._dot_terminus_path, self._home_dir))
            os.makedirs(self._dot_terminus_path)  # Create `~/.terminus` directory
        else:
            print("\nFound a '.terminus' directory into the home directory\n")

        # Check ~/.terminus/_secret
        if not os.path.isdir(self._rabbitmq_secret_path):
            # self._rabbitmq_secret_path = os.path.join(self._dot_terminus_path, self._RABBITMQ_SECRET_DIR)
            print("\t> Creating '%s' directory into the '%s' directory." % (self._RABBITMQ_SECRET_DIR,
                                                                            self._dot_terminus_path))
            os.makedirs(self._rabbitmq_secret_path)  # Create `~/.terminus/_secret` directory

        to_file = os.path.join(self._home_dir, self._dot_terminus_path)
        if not os.path.isfile(os.path.join(to_file, self.TERMINUS_SERVICE_FILE)):
            # ~/.terminus/terminus.service not found => copy terminus.service template to .terminus directory
            from_file = os.path.join(self._terminus_template_dir, self.TERMINUS_SERVICE_FILE)
            shutil.copy2(from_file, to_file)

        if not os.path.isfile(os.path.join(to_file, TerminusCommons.Terminus_dot_env_fname)):
            # ~/.terminus/terminus.env file not found => copy terminus.env template to .terminus directory
            from_file = os.path.join(self._terminus_template_dir, TerminusCommons.Terminus_dot_env_fname)
            shutil.copy2(from_file, to_file)
            self.set_default_parameters()
        else:
            self.load_terminus_config()

    @property
    def template_dir(self):
        return self._terminus_template_dir

    def set_default_parameters(self):
        """
        Set default parameters for terminus_parameters
        """
        
        self.terminus_parameters[TerminusCommons.ENVVAR_TERMINUS_HOSTNAME] = (socket.gethostname()).lower()
        self.terminus_parameters[TerminusCommons.ENVVAR_DOT_DIR] = self._dot_terminus_path

        # self.terminus_parameters["TERMINUS_WORKDIR"] = self._home_dir

        self.terminus_parameters[TerminusCommons.ENVVAR_DATA_DIR] = self._home_dir
        self.terminus_parameters[TerminusCommons.ENVVAR_JOBRUNS_DIR] = self._home_dir
        self.terminus_parameters[TerminusCommons.ENVVAR_SERVICE_DIR] = self._home_dir

        self.terminus_parameters[TerminusCommons.ENVVAR_TERMINUS_USE_SLURM] = 0  # False by default

        self.terminus_parameters["User"] = getpass.getuser()
        self.terminus_parameters["Group"] = self.terminus_parameters["User"]
        self.terminus_parameters[TerminusCommons.ENVVAR_UPLOAD_HOST] = "Galactica_storage"

        # Default values
        self._terminus_celery_nodes = 2
        self._terminus_celery_concurrency = 2

    def load_terminus_config(self):
        """ 
        Load a terminus configuration file from home directory
        """
        # check if there is a terminus.env file in .terminus directory
        if not os.path.isfile(self._terminus_env_file_path):
            print("> No '%s' file found, create a new one from terminus template.\n" % self._terminus_env_file_path)

            # copy terminus.env template to .terminus directory
            from_file = os.path.join(self._terminus_template_dir, TerminusCommons.Terminus_dot_env_fname)
            to_file = os.path.join(self._home_dir, self._dot_terminus_path)
            shutil.copy2(from_file, to_file)

            self.set_default_parameters()

        elif not self._read_only:
            # datetime object containing current date and time
            now = datetime.now()
            # dd/mm/YY H:M:S
            dt_string = now.strftime("%d-%m-%Y-%H-%M-%S")

            # save current terminus.env by copying it to terminus.env.date and
            # we'll override the terminus.env file
            from_file = self._terminus_env_file_path
            to_file = from_file + "." + dt_string

            shutil.copy2(from_file, to_file)
            print("> '{tef:s}' configuration file found !".format(tef=TerminusCommons.Terminus_dot_env_fname))
            print("\t> backup to : '%s' \n" % to_file)
        
        # check if there is a terminus.service file in .terminus directory
        if not os.path.isfile(self._terminus_serv_file_path):
            print("> No '{tsfp:s}' file found, create a new one from terminus "
                  "template.\n".format(tsfp=self._terminus_serv_file_path))

            # copy terminus.service template to .terminus directory
            from_file = os.path.join(self._terminus_template_dir, self.TERMINUS_SERVICE_FILE)
            to_file = os.path.join(self._home_dir, self._dot_terminus_path)
            shutil.copy2(from_file, to_file)

            return
        elif not self._read_only:
            # datetime object containing current date and time
            now = datetime.now()
            # dd/mm/YY H:M:S
            dt_string = now.strftime("%d-%m-%Y-%H-%M-%S")

            # save current terminus.env by copying it to terminus.env.date and we'll override the terminus.env file
            from_file = self._terminus_serv_file_path
            to_file = from_file + "." + dt_string

            shutil.copy2(from_file, to_file)
            print("> terminus.service configuration file found !")
            print("\t> backup to : '%s' \n" % to_file)
        
        # open terminus.env file if it exists
        try:
            lines = []
            with open(self._terminus_env_file_path, "r") as f:
                lines = f.readlines()
        except IOError:
            print("Error trying to open '{tef:s}' file".format(tef=TerminusCommons.Terminus_dot_env_fname))

        for tmp in lines:
            # let suppose the user use CELERY_NODES=n and not CELERY_NODES="w1@machine w2@machine w3@machine"
            if TerminusConfigManager.CELERY_DEAMON_NNODES in lines and not lines.startswith("#"):
                CN_str = tmp.replace("\n", "").split("=")[1]
                try:
                    self._terminus_celery_nodes = int(CN_str)  # Deprecated terminus config
                except ValueError:
                    # 1 node is reserved for monitoring, all the other celery nodes handle job requests
                    self._terminus_celery_nodes = len(CN_str.split(" ")) - 1
            
            elif TerminusConfigManager.CELERY_DAEMON_OPTIONS in lines:  # CELERYD_OPTS=--concurrency=XXX -c:5 1 -Q anais.terminus_jobs -Q:5 anais.monitor
                CO_str = tmp.replace("\n", "").split("=")[2].split(" ")[0]  # => XXX
                self._terminus_celery_concurrency = int(CO_str)

            else:
                for k in self.terminus_parameters.keys():
                    if k == TerminusCommons.ENVVAR_ROOT_DIR:
                        # Skip Terminus root directory definition
                        continue
                    if k in tmp:
                        self.terminus_parameters[k] = tmp.replace("\n", "").split("=")[1].replace("\"", "")
        
        self.terminus_parameters[TerminusCommons.ENVVAR_TERMINUS_USE_SLURM] = int(self.terminus_parameters[TerminusCommons.ENVVAR_TERMINUS_USE_SLURM])

        # should do better than that
        if self.terminus_parameters[TerminusCommons.ENVVAR_DOT_DIR] == "__empty__":
            self.terminus_parameters[TerminusCommons.ENVVAR_DOT_DIR] = self._dot_terminus_path

        # open terminus.service file
        try:
            lines = []
            with open(self._terminus_serv_file_path, "r") as f:
                lines = f.readlines()
        except IOError:
            print("Error trying to open terminus.service file")

        for tmp in lines:
            for k in self.terminus_parameters.keys():
                if k in tmp:
                    self.terminus_parameters[k] = tmp.replace("\n", "").split("=")[1]
        
        if self.check_terminus_config():
            print("Problem in terminus environment variables")

        # But we'll lose previous configuration if user cancel unless we read a
        # temrinus.env.date file
        #
        # this fix the ugly bug of having old var defined in existed terminus.env file
        # and allow to use always the last version of terminus.env template.
        #
        # copy terminus.env template to .terminus directory
        from_file = os.path.join(self._terminus_template_dir, TerminusCommons.Terminus_dot_env_fname)
        to_file = os.path.join(self._home_dir, self._dot_terminus_path)
        shutil.copy2(from_file, to_file)

        # this fix the ugly bug of having old var defined in existed terminus.service file
        # and allow to use always the last version of terminus.service template.
        #
        # copy terminus.service template to .terminus directory
        from_file = os.path.join(self._terminus_template_dir, self.TERMINUS_SERVICE_FILE)
        to_file = os.path.join(self._home_dir, self._dot_terminus_path)
        shutil.copy2(from_file, to_file)

        print("\nTerminus configuration loaded, ready to update.\n")

    def configure_terminus(self):
        """
        Configure terminus environment variables. In case of "enter hit" a defaut value
        """
        # self.terminus_parameters["TERMINUS_HOSTNAME"] = input("Enter a terminus host name (current %s): " %
        # self.terminus_parameters["TERMINUS_HOSTNAME"])
        tmp = input("Enter a terminus host name (current '%s'): " % self.terminus_parameters[TerminusCommons.ENVVAR_TERMINUS_HOSTNAME])
        if not tmp.replace(" ", ""):
            # small trick to be sure the HOSTNAME is not in MAJ
            self.terminus_parameters[TerminusCommons.ENVVAR_TERMINUS_HOSTNAME] = self.terminus_parameters[TerminusCommons.ENVVAR_TERMINUS_HOSTNAME].lower()
            print("\t> Default value used\n")
        else:
            self.terminus_parameters[TerminusCommons.ENVVAR_TERMINUS_HOSTNAME] = tmp.lower()

        # tmp = input("Enter a terminus work directory (current %s): " % self.terminus_parameters["TERMINUS_WORKDIR"])
        # if ( not tmp.replace(" ", "") ):
        #     print("\t> Default value used")
        # else:
        #     self.terminus_parameters["TERMINUS_WORKDIR"] = tmp
        
        # tmp = input("Enter a terminus data directory (current '%s'): " % self.terminus_parameters[TerminusCommons.ENVVAR_DATA_DIR"])
        # if not tmp.replace(" ", ""):
        #     print("\t> Default value used\n")
        # else:
        #     self.terminus_parameters[TerminusCommons.ENVVAR_DATA_DIR"] = tmp
        self.ask_path(TerminusCommons.ENVVAR_DATA_DIR, "terminus data directory")

        # tmp = input("Enter a terminus job directory (current '%s'): " % self.terminus_parameters[TerminusCommons.ENVVAR_JOBRUNS_DIR])
        # if not tmp.replace(" ", ""):
        #     print("\t> Default value used\n")
        # else:
        #     self.terminus_parameters[TerminusCommons.ENVVAR_JOBRUNS_DIR] = tmp
        self.ask_path(TerminusCommons.ENVVAR_JOBRUNS_DIR, "terminus job directory")
        
        # tmp = input("Enter a terminus service directory (current "
        #             "'{curr_serv_dir:s}'): ".format(curr_serv_dir=self.terminus_parameters[TerminusCommons.ENVVAR_SERVICE_DIR]))
        # if not tmp.replace(" ", ""):
        #     print("\t> Default value used\n")
        # else:
        #     self.terminus_parameters[TerminusCommons.ENVVAR_SERVICE_DIR] = tmp
        self.ask_path(TerminusCommons.ENVVAR_SERVICE_DIR, "terminus service directory")

        # Do not let the user the possibility to choose the User and Group for systemd
        # because the .terminus/ is created @ ${HOME}

        # tmp = input("Enter a terminus systemd user (current %s): " % self.terminus_parameters["User"])
        # if ( not tmp.replace(" ","") ):
        #     print("\t> Default value used")
        # else:
        #     self.terminus_parameters["User"] = tmp
        
        # tmp = input("Enter a terminus systemd group (current %s): " % self.terminus_parameters["Group"])
        # if ( not tmp.replace(" ","") ):
        #     print("\t> Default value used")
        # else:
        #     self.terminus_parameters["Group"] = tmp

        tmp = input("Enter a terminus number of nodes (current %s): " % self._terminus_celery_nodes)
        if not tmp.replace(" ", ""):
            print("\t> Default value used\n")
        else:
            self._terminus_celery_nodes = int(tmp)

        tmp = input("Enter a terminus number of concurrency/node (current %s): " % self._terminus_celery_concurrency)
        if not tmp.replace(" ", ""):
            print("\t> Default value used\n")
        else:
            self._terminus_celery_concurrency = int(tmp)

        tmp = input("Enter a Galactica server SSH target name (configured in your local ~/.ssh/config file) (current '%s'): " % self.terminus_parameters[TerminusCommons.ENVVAR_UPLOAD_HOST])
        if not tmp.replace(" ", ""):
            print("\t> Current value used\n")
        else:
            self.terminus_parameters[TerminusCommons.ENVVAR_UPLOAD_HOST] = tmp

        val = 'N'
        val_int = 0
        if self.terminus_parameters[TerminusCommons.ENVVAR_TERMINUS_USE_SLURM] > 0:
            val = 'Y'
            val_int = 1
        
        tmp = input("Use SLURM for job submission ? (Y/n) (current %s): " % val)
        tmp = tmp.replace(" ", "")

        if not tmp:
            print("\t> Default value used\n")
            self.terminus_parameters[TerminusCommons.ENVVAR_TERMINUS_USE_SLURM] = val_int
        else:
            if tmp == 'Y' or tmp == 'y':
                self.terminus_parameters[TerminusCommons.ENVVAR_TERMINUS_USE_SLURM] = 1
            else:
                self.terminus_parameters[TerminusCommons.ENVVAR_TERMINUS_USE_SLURM] = 0

        print("\n------------------ RabbitMQ configuration ---------------\n")
        
        tmp = input("Enter a rabbitmq username (current '%s'): " % self.terminus_parameters[TerminusCommons.ENVVAR_RABBITMQ_USER])
        if not tmp.replace(" ", ""):
            print("\t> Current value used\n")
        else:
            self.terminus_parameters[TerminusCommons.ENVVAR_RABBITMQ_USER] = tmp

        while True:
            tmp = input("Enter a rabbitmq host IP (current '%s'): " % self.terminus_parameters[TerminusCommons.ENVVAR_RABBITMQ_HOST])
            if not tmp.replace(" ", ""):
                print("\t> Current value used\n")
                break
            else:
                if self.IP_ADDR_REGEXP.match(tmp) is not None:
                    self.terminus_parameters[TerminusCommons.ENVVAR_RABBITMQ_HOST] = tmp
                    break
                else:
                    print("\tInvalid IP address (format required: 'xxx.xxx.xxx.xxx').\n")
        
        tmp = input("Enter a rabbitmq port (current '%s'): " % self.terminus_parameters[TerminusCommons.ENVVAR_RABBITMQ_PORT])
        if not tmp.replace(" ", ""):
            print("\t> Current value used\n")
        else:
            self.terminus_parameters[TerminusCommons.ENVVAR_RABBITMQ_PORT] = tmp
        
        tmp = input("Enter a rabbitmq virtual host (current "
                    "'{rmq_vhost:s}'): ".format(rmq_vhost=self.terminus_parameters[TerminusCommons.ENVVAR_RABBITMQ_VIRTUAL_HOST]))
        if not tmp.replace(" ", ""):
            print("\t> Current value used\n")
        else:
            self.terminus_parameters[TerminusCommons.ENVVAR_RABBITMQ_VIRTUAL_HOST] = tmp
        
        rabbitmq_pwd_file_path = os.path.join(self._rabbitmq_secret_path, self._RABBITMQ_SECRET_FILE)
        
        # Attempt to create file for rabbitmq password
        if not os.path.isfile(rabbitmq_pwd_file_path):
            with open(rabbitmq_pwd_file_path, "w") as tempo:
                tempo.write("__DUMMY_PASSWD__")
            print("\n> Now add the given RabbitMQ server password in this file: %s" % rabbitmq_pwd_file_path)

        # Set sensitive information file permission to read|write for the user only.
        os.chmod(rabbitmq_pwd_file_path, stat.S_IREAD | stat.S_IWRITE)  # chmod 600 _secret/rabbitmq_server_pwd

        print("\n----------- RabbitMQ configuration completed -------------")
        
        print("\n> Configured User: %s" % self.terminus_parameters["User"])
        print("> Configured Group: %s\n" % self.terminus_parameters["Group"])

        # check for warning
        if len(self.path_warning) != 0:
            for k in self.path_warning:
                print("\t> Directory '%s' does not exist. This directory must be created before launching Terminus !\n"\
                        % (self.terminus_parameters[k]) )


        # if self.check_terminus_config():
        #     print("Problem in terminus environment variables, check your path !")
        #     return False
        # else:
        #     print("Path checked successfuly !")
        while True:
            tmp = input("Save configuration ? [Y/n]: ")
            tmp = tmp.replace(" ", "").lower()
            if tmp == 'n':
                print("Aborting.")

                # not really awesome but works
                self.load_terminus_config()
                return False
            elif tmp == "y" or tmp == "":
                if not self.write_terminus_config():
                    print("Error while writting terminus_config file !")
                    return False
                else:
                    print("Terminus configuration file written successfully.")
                    break
            else:
                print("Invalid option. Please select 'y' or 'n'.")
                continue

        return True
    
    def ask_path(self, terminus_var, user_text):
        """
        Ask for a 'terminus_var' which must be a path. Display 'user_text' in prompt.
        Test if directory provided by user exist and if not propose to create it.
        """
        while True:
            tmp = input("Enter a %s (current '%s'): " % (user_text, self.terminus_parameters[terminus_var]))

            if not tmp.replace(" ", "") and self.terminus_parameters[terminus_var] != "__empty__":
                print("\t> Default value used\n")
                break
            else:
                self.terminus_parameters[terminus_var] = tmp

            if not os.path.isdir(tmp):
                rst = input("\t> Directory '%s' does not exist. Create directory ? (Y/n) : " % tmp)
                if rst.replace("\n", "").replace(" ", "").lower() == "y":
                    try:
                        os.makedirs(tmp)
                    except OSError:
                        print ("Creation of the directory %s failed" % tmp)
                    else:
                        print ("\t> Successfully created the directory '%s'. \n" % tmp)
                        break
                else:
                    # user says thanks, but no thanks for directory creation
                    self.path_warning.append(terminus_var)
                    break
            else:
                break

    def check_terminus_config(self):
        """
        Check terminus environment variables that are path to directory
        """
        problem = False

        for k in self.terminus_parameters.keys():
            if os.path.isdir(self.terminus_parameters[k]):
                self.terminus_parameters_works[k] = True

        for k in self.terminus_parameters_works.keys():
            if not self.terminus_parameters_works[k]:
                print("Error with '%s' for key '%s', directory does not exist !"%(self.terminus_parameters[k], k))
                problem = True
        
        # check that user and group match, if not fix them
        tmp = getpass.getuser()
        if getpass.getuser() != self.terminus_parameters["User"]:
            print("\t> Warning configured 'User' and 'Group' from terminus.service does not match current user !")
            self.terminus_parameters["User"] = tmp
            self.terminus_parameters["Group"] = tmp

        return problem

    def write_terminus_config(self):
        """
        Write terminus.env and terminus.service file in home directory with modified parameters
        """
        if self._read_only:  # Must not write in read-only mode
            return False

        # For the terminus.env file
        if self._terminus_env_file_path is None:
            print("Error something went wrong, there is no _terminus_env_file_path set ! ")
            return False

        with open(self._terminus_env_file_path, "r") as f:
            lines = f.readlines()

        # print("TERMINUS_ROOT = " , self.terminus_parameters["TERMINUS_ROOT"])

        for i in range(0, len(lines)):
            if "CELERYD_PID_FILE" in lines[i]:
                lines[i] = "CELERYD_PID_FILE=" + os.path.join(self._dot_terminus_path, "pids", "%n.pid") + "\n"
            elif "CELERYD_LOG_FILE" in lines[i]:
                lines[i] = "CELERYD_LOG_FILE=" + os.path.join(self._dot_terminus_path, "logs", "%n.log") + "\n"
            elif "CELERY_BIN" in lines[i]:
                lines[i] = "CELERY_BIN=\"" + self._terminus_celery_path + "\"\n"
            elif TerminusConfigManager.CELERY_DEAMON_NNODES in lines[i] and not lines[i].startswith("#"):
                worker_list = ["job_worker{iw:d}@{h:s}.terminus".format(iw=iworker,
                                                                        h=self.terminus_parameters[TerminusCommons.ENVVAR_TERMINUS_HOSTNAME])
                               for iworker in range(1, self._terminus_celery_nodes+1)]
                worker_list.append("monitor@{h:s}.terminus".format(h=self.terminus_parameters[TerminusCommons.ENVVAR_TERMINUS_HOSTNAME]))

                lines[i] = "{k:s}={wl:s}\n".format(k=TerminusConfigManager.CELERY_DEAMON_NNODES,
                                                   wl=" ".join(worker_list))
            elif TerminusConfigManager.CELERY_DAEMON_OPTIONS in lines[i]:
                # Here, set the concurrency to self._terminus_celery_concurrency for the workers 1-n dedicated to
                # the 'host.terminus_jobs' Queue, and concurreny to 1 for the monitor worker dedicated to the
                # 'host.monitor' Queue
                lines[i] = "{k:s}=\"--concurrency={nth:d} -Q {host:s}.terminus_jobs -c:{mnw:d} 1 -Q:{mnw:d} " \
                           "{host:s}.monitor\"" \
                           "\n".format(k=TerminusConfigManager.CELERY_DAEMON_OPTIONS,
                                       nth=self._terminus_celery_concurrency,
                                       host=self.terminus_parameters[TerminusCommons.ENVVAR_TERMINUS_HOSTNAME],
                                       mnw=self._terminus_celery_nodes+1)
            else:
                for k in self.terminus_parameters.keys():
                    if k in lines[i]:
                        lines[i] = k + "=\"" + str(self.terminus_parameters[k]) + "\"\n"
        
        with open(self._terminus_env_file_path, "w") as f:
            for tmp in lines:
                f.write(tmp)
        
        # For the terminus.service file
        if self._terminus_serv_file_path is None:
            print("Error something went wrong, there is no _terminus_serv_file_path set ! ")
            return False

        lines = []
        with open(self._terminus_serv_file_path, "r") as f:
            lines = f.readlines()

        for i in range(0, len(lines)):
            if "EnvironmentFile" in lines[i]:
                lines[i] = "EnvironmentFile=" + self._terminus_env_file_path + "\n"
            elif "WorkingDirectory" in lines[i]:
                lines[i] = "WorkingDirectory=" + self.terminus_parameters[TerminusCommons.ENVVAR_JOBRUNS_DIR] + "\n"
            else:
                for k in self.terminus_parameters.keys():
                    if k in lines[i]:
                        lines[i] = k + "=" + self.terminus_parameters[k] + "\n"
        
        with open(self._terminus_serv_file_path, "w") as f:
            for tmp in lines:
                f.write(tmp)

        return True


def check_current_config(tcm):
    """
    Check the current config file

    Parameters
    ----------
    tcm: TerminusConfigManager object
    """
    env_fpath = os.path.join(tcm.template_dir, TerminusCommons.Terminus_dot_env_fname)
    try:
        lines = []
        with open(env_fpath, "r") as f:
            lines = f.readlines()
    except IOError:
        print("Error with file {evfp:s} ".format(evfp=env_fpath))

    for tmp in lines:
        for k in tcm.config_parameters.keys():
            if k in tmp:
                tcm.config_parameters[k] = tmp.replace("\n", "").split("=")[1]


def server_config(args=None):
    """The main routine."""
    if args is None:
        args = sys.argv[1:]

    print("\n# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #")
    print("# ~~~~~~~~~~~~~~~~~~~~~~ Terminus server configuration helper ~~~~~~~~~~~~~~~~~~~~~~~ #")
    print("# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #\n")
    config_manager = TerminusConfigManager()
    # Do argument parsing here (eg. with argparse) and anything else
    # you want your project to do. Return values are exit codes.

    # parser = argparse.ArgumentParser(description="Run on-demand data post-processing server for the Galactica "
    #                                              "astrophysical simulation database")
    # parser.add_argument('--debug', dest='debug', action='store_true', help='Run in debug mode')
    # pargs = parser.parse_args()
    # is_debug = pargs.debug

    while True:
        try:
            res = handle_action(config_manager)
            if not res:
                break
        except KeyboardInterrupt:

            # save current state of configuration
            config_manager.write_terminus_config()

            print("\nCanceled...\n"
                  "# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #")
            break
    return 0


def handle_action(cfg_manager: TerminusConfigManager):
    """
    Handle user command-line interaction

    Parameters
    ----------
    cfg_manager: :class:`Terminus.TerminusConfigManager`
    """
    print("Select an option :\n"
          " - [1] Configure Terminus \n"
          " - [2] Quit ")
    
    try:
        option = int(input("\nYour choice ? : "))
        if option not in [1, 2]:
            print("Error: Valid choices are [1, 2]")
            return True
    except SyntaxError:
        option = 1

    if option == 2:
        print("\nDone...\n"
              "# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #")
        return False

    else:  # if option == 1:
        print("Configuration of Terminus")
        is_ok = cfg_manager.configure_terminus()

        if not is_ok:
            return True


def datasource_dir_config(args=None, test_mode=False):
    """Datasource directory path definition method from a JSON file sent by Galactica to the Terminus server admin."""

    parser = argparse.ArgumentParser(description="Configure datasource directory path definitions from a JSON file.")
    parser.add_argument("json_file", help="JSON-formatted file sent to the Terminus server admin.")
    pargs = parser.parse_args(args=args)

    print("\n"
          "# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #\n"
          "# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Terminus datasource directory definitions ~~~~~~~~~~~~~~~~~~~~~~~~ #\n"
          "# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #")

    if not os.path.isfile(pargs.json_file):
        print("Error : cannot find file '{f:s}' !".format(f=pargs.json_file))
        return 1

    with open(pargs.json_file, 'r') as jf:
        ddd_dict = json.load(jf)

    # Get Terminus install data root directory
    if test_mode:
        terminus_data_dir_root = os.environ[TerminusCommons.ENVVAR_DATA_DIR]
        if not os.path.isdir(terminus_data_dir_root):
            os.makedirs(terminus_data_dir_root)
    else:
        config_manager = TerminusConfigManager(read_only=True)
        terminus_data_dir_root = config_manager.terminus_parameters[TerminusCommons.ENVVAR_DATA_DIR]

    # Build project category directory, if required
    if "category" not in ddd_dict or ddd_dict["category"] == "":
        raise ValueError("Undefined project category.")
    cat_dir = os.path.join(terminus_data_dir_root, ddd_dict["category"])
    if not os.path.isdir(cat_dir):
        os.makedirs(cat_dir)
        print("Project category directory '{cd:s}' created.".format(cd=cat_dir))
    else:
        print("Project category directory '{cd:s}' already exists.".format(cd=cat_dir))

    # Build project directory, if required
    proj_dict = ddd_dict["project"]
    if "alias" not in proj_dict or proj_dict["alias"] == "":
        raise ValueError("Project alias is not defined.")
    proj_dir = os.path.join(cat_dir, proj_dict["alias"])
    if not os.path.isdir(proj_dir):
        os.makedirs(proj_dir)
        print(" -> Project directory '{pd:s}' created.".format(pd=proj_dir))
    else:
        print(" -> Project directory '{pd:s}' already exists.".format(pd=proj_dir))

    # Build simulation directories, if required
    if "children" not in ddd_dict:
        raise ValueError("Missing project's 'children' simulation definition.")
    for simu in ddd_dict["children"]:
        if "alias" not in simu:
            raise ValueError("Undefined simulation 'alias'")
        simu_dir = os.path.join(proj_dir, simu["alias"])
        if not os.path.isdir(simu_dir):
            os.makedirs(simu_dir)
            print("     * Simulation directory '{sd:s}' created.".format(sd=simu_dir))
        else:
            print("     * Simulation directory '{sd:s}' already exists.".format(sd=simu_dir))

        user_input = None
        # Build snapshots symbolic links
        if "children" not in simu:
            raise ValueError("Missing simulation's 'children' snapshot definition.")
        for snapshot in simu["children"]:
            snapshot_dir_abspath = snapshot["directory_path"]
            # Get directory basename to replicate it in the job directory
            sn_dirname = os.path.basename(snapshot_dir_abspath)
            sn_lnk = os.path.join(simu_dir, sn_dirname)
            create_symlink = False

            if os.path.islink(sn_lnk):
                # Symbolic link already exists => What do we do ?
                old_link_target = os.readlink(sn_lnk)
                if old_link_target == snapshot_dir_abspath:
                    # Unchanged symlink => do nothing
                    print("        - Snapshot data symbolic link unchanged : '{dest:s}' => "
                          "'{src:s}'".format(src=snapshot_dir_abspath, dest=sn_lnk))
                    continue

                # Symlink to modify ?
                if user_input not in ["a", "x"]:
                    while True:
                        try:
                            # Ask user input to overwrite symbolic link pointing to a different target
                            option = input("        - Snapshot data symlink '{snl:s}' has changed:"
                                           "            + old target : '{ot:s}'."
                                           "            + new target : '{nt:s}'."
                                           "          Overwrite (y='yes', n='no', a='yes to all', x='no to all', q='quit') "
                                           "[Y] ? ".format(snl=sn_lnk, ot=old_link_target,
                                                           nt=snapshot_dir_abspath)).lower()
                            if option not in ["y", "a", "n", "x", "q"]:
                                print("Invalid option")
                                continue
                            break
                        except SyntaxError:
                            option = "n"
                            break
                    if option == "q":
                        break
                    elif option == "n":
                        continue
                    elif option == "y":
                        create_symlink = True
                    elif option == "a":
                        user_input = "a"
                        create_symlink = True
                    elif option == "x":
                        user_input = "x"
                        # create_symlink = False
                        continue
                elif user_input == "x":
                    continue
                elif user_input == "a":
                    create_symlink = True

                if create_symlink:  # Remove old symbolic link first
                    os.unlink(sn_lnk)
                    print("          -> Deleted deprecated snapshot data symbolic link : '{dest:s}' => "
                          "'{src:s}'.".format(src=old_link_target, dest=sn_lnk))
            else:  # Symbolic link does not exist, create it
                create_symlink = True

            if create_symlink:
                if not os.path.isdir(snapshot_dir_abspath):
                    raise ValueError("Directory path '{d:s}' cannot be found !".format(d=snapshot_dir_abspath))
                # Create symbolic link
                os.symlink(snapshot_dir_abspath, sn_lnk, target_is_directory=True)
                print("        - Created snapshot data symbolic link : '{dest:s}' => "
                      "'{src:s}'.".format(src=snapshot_dir_abspath, dest=sn_lnk))

    print("\nDone...\n"
          "# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #")
    return 0


if __name__ == "__main__":
    sys.exit(server_config())
