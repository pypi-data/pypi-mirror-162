# -*- coding: utf-8 -*-
# Modules
# ------------------------------------------------

from __future__ import unicode_literals, absolute_import

import logging
import os
import threading
import time
import fcntl
import json
import datetime

_logger = None

# ------- - https://github.com/benediktschmitt/py-filelock    --------

def logger():
    """Returns the logger instance used in this module."""
    global _logger
    _logger = _logger or logging.getLogger(__name__)
    return _logger


# Exceptions
# ------------------------------------------------
class Timeout(OSError):
    """
    Raised when the lock could not be acquired in *timeout*
    seconds.
    """

    def __init__(self, lock_file):
        """
        """
        #: The path of the file lock.
        self.lock_file = lock_file

    def __str__(self):
        temp = "The file lock '{}' could not be acquired."\
               .format(self.lock_file)
        return temp


# Classes
# ------------------------------------------------

# This is a helper class which is returned by :meth:`BaseFileLock.acquire`
# and wraps the lock to make sure __enter__ is not called twice when entering
# the with statement.
# If we would simply return *self*, the lock would be acquired again
# in the *__enter__* method of the BaseFileLock, but not released again
# automatically.
#
# :seealso: issue #37 (memory leak)
class _Acquire_ReturnProxy(object):

    def __init__(self, lock):
        self.lock = lock

    def __enter__(self):
        return self.lock

    def __exit__(self, exc_type, exc_value, traceback):
        self.lock.release()
        return None


class BaseFileLock(object):
    """
    Implements the base class of a file lock.
    """

    def __init__(self, lock_file, timeout=-1):
        """
        """
        # The path to the lock file.
        self._lock_file = lock_file

        # The file descriptor for the *_lock_file* as it is returned by the
        # os.open() function.
        # This file lock is only NOT None, if the object currently holds the
        # lock.
        self._lock_file_fd = None

        # The default timeout value.
        self.timeout = timeout

        # We use this lock primarily for the lock counter.
        self._thread_lock = threading.Lock()

        # The lock counter is used for implementing the nested locking
        # mechanism. Whenever the lock is acquired, the counter is increased and
        # the lock is only released, when this value is 0 again.
        self._lock_counter = 0

    @property
    def lock_file(self):
        """
        The path to the lock file.
        """
        return self._lock_file

    @property
    def timeout(self):
        """
        You can set a default timeout for the filelock. It will be used as fallback value in the acquire method, if
        no timeout value (*None*) is given.

        If you want to disable the timeout, set it to a negative value.

        A timeout of 0 means, that there is exactly one attempt to acquire the file lock.
        """
        return self._timeout

    @timeout.setter
    def timeout(self, value):
        """
        """
        self._timeout = float(value)

    def _acquire(self):
        """
        If the file lock could be acquired, self._lock_file_fd holds the file descriptor of the lock file.
        """
        raise NotImplementedError()

    def _release(self):
        """
        Releases the lock and sets self._lock_file_fd to None.
        """
        raise NotImplementedError()

    @property
    def is_locked(self):
        """
        True, if the object holds the file lock.
        """
        return self._lock_file_fd is not None

    def acquire(self, timeout=None, poll_intervall=0.05):
        """
        Acquires the file lock or fails with a :exc:`Timeout` error. This method returns a *proxy* object instead
        of *self*, so that it can be used in a with statement without side effects.

        .. code-block:: python

            # You can use this method in the context manager (recommended)
            with lock.acquire():
                pass

            # Or use an equivalent try-finally construct:
            lock.acquire()
            try:
                pass
            finally:
                lock.release()

        :arg float timeout:
            The maximum time waited for the file lock.
            If ``timeout < 0``, there is no timeout and this method will
            block until the lock could be acquired.
            If ``timeout`` is None, the default :attr:`~timeout` is used.

        :arg float poll_intervall:
            We check once in *poll_intervall* seconds if we can acquire the
            file lock.

        :raises Timeout:
            if the lock could not be acquired in *timeout* seconds.
        """
        # Use the default timeout, if no timeout is provided.
        if timeout is None:
            timeout = self.timeout

        # Increment the number right at the beginning.
        # We can still undo it, if something fails.
        with self._thread_lock:
            self._lock_counter += 1

        lock_id = id(self)
        lock_filename = self._lock_file
        start_time = time.time()
        try:
            while True:
                with self._thread_lock:
                    if not self.is_locked:
                        logger().debug('Attempting to acquire lock %s on %s', lock_id, lock_filename)
                        self._acquire()

                if self.is_locked:
                    logger().debug('Lock %s acquired on %s', lock_id, lock_filename)
                    break
                elif timeout >= 0 and time.time() - start_time > timeout:
                    logger().debug('Timeout on acquiring lock %s on %s', lock_id, lock_filename)
                    raise Timeout(self._lock_file)
                else:
                    logger().debug('Lock %s not acquired on %s, waiting %s seconds ...', lock_id, lock_filename,
                                   poll_intervall)
                    time.sleep(poll_intervall)
        except:
            # Something did go wrong, so decrement the counter.
            with self._thread_lock:
                self._lock_counter = max(0, self._lock_counter - 1)

            raise
        return _Acquire_ReturnProxy(lock=self)

    def release(self, force=False):
        """
        Releases the file lock.

        Please note, that the lock is only completely released, if the lock counter is 0.

        Also note, that the lock file itself is not automatically deleted.

        :arg bool force:
            If true, the lock counter is ignored and the lock is released in every case.
        """
        with self._thread_lock:

            if self.is_locked:
                self._lock_counter -= 1

                if self._lock_counter == 0 or force:
                    lock_id = id(self)
                    lock_filename = self._lock_file

                    logger().debug('Attempting to release lock %s on %s', lock_id, lock_filename)
                    self._release()
                    self._lock_counter = 0
                    logger().debug('Lock %s released on %s', lock_id, lock_filename)

        return None

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.release()
        return None

    def __del__(self):
        self.release(force=True)
        return None


class FileLock(BaseFileLock):
    """
    Uses the :func:`fcntl.flock` to hard lock the lock file on unix systems.
    """

    def _acquire(self):
        open_mode = os.O_RDWR | os.O_CREAT | os.O_TRUNC
        fd = os.open(self._lock_file, open_mode)

        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except (IOError, OSError):
            os.close(fd)
        else:
            self._lock_file_fd = fd
        return None

    def _release(self):
        # Attempt to remove the lockfile:
        #
        #   https://github.com/benediktschmitt/py-filelock/issues/31
        #   https://stackoverflow.com/questions/17708885/flock-removing-locked-file-without-race-condition
        fd = self._lock_file_fd
        self._lock_file_fd = None
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)
        try:
            os.remove(self._lock_file)
        except OSError:
            pass
        return None


class JobStatus(object):
    job_status_fname = "job_status.json"
    lock_file_name = "job_status.json.lock"

    @classmethod
    def _lock_file_path(cls, job_dir="./"):
        lfn = os.path.join(job_dir, cls.lock_file_name)
        return lfn

    @classmethod
    def _job_status_fpath(cls, job_dir="./"):
        jsfpath = os.path.join(job_dir, cls.job_status_fname)
        return jsfpath

    @classmethod
    def exists(cls, job_dir="./"):
        return os.path.isfile(cls._job_status_fpath(job_dir))

    @classmethod
    def last_updated(cls, last_update_time, job_dir="./"):
        lk = FileLock(cls._lock_file_path(job_dir), timeout=5)
        try:
            with lk:
                jsfpath = cls._job_status_fpath(job_dir)
                up_time = datetime.datetime.utcfromtimestamp(os.path.getmtime(jsfpath))
                if last_update_time is None or up_time > last_update_time:
                    with open(jsfpath, 'r') as f:
                        st_dict = json.load(f)
                        new_status = st_dict.get('status', None)
                        new_message = st_dict.get('message', None)
                    return up_time, new_status, new_message
                return None
        except Timeout:
            return None

    @classmethod
    def update(cls, status, message, job_dir="./"):
        lk = FileLock(cls._lock_file_path(job_dir), timeout=5)
        try:
            with lk:
                msg_dict = {'status': status, 'message': message}
                with open(cls._job_status_fpath(job_dir), 'w') as f:
                    json.dump(msg_dict, f)
        except Timeout:
            err_msg = "Could not update job status : '{path:s}' job status file is " \
                      "locked !".format(path=cls._job_status_fpath(job_dir))
            logger().error(err_msg)
            raise IOError(err_msg)


__all__ = ["Timeout", "BaseFileLock", "FileLock", "JobStatus"]
