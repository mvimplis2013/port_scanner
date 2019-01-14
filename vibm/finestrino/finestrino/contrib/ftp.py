"""
This library is a wrapper of ftplib.
It is convenient for moving data from/ to FTP server.

There is an example on how to use it in ``examples/ftp_experiment_outputs.py``.

You can also find unitests for each class.

Be aware that nornal ftp does not provide secure communication.
"""
import ftplib
from ftplib import FTP
from ftplib import FTP_TLS

import os
import datetime
import random
import tempfile
import io

import logging 

import finestrino
import finestrino.format
from finestrino.format import FileWrapper

logger = logging.getLogger("finestrino-interface")

class RemoteFileSystem(finestrino.target.FileSystem):
    def __init__(self, host, username=None, password=None, port=None, tls=False, timeout=60, sft=False, pysftp_conn_kwargs=None):
        self.host = host
        self.username = username
        self.password = password 
        self.tls = tls 
        self.timeout = timeout 
        self.sftp = sft 
        self.pysftp_conn_kwargs = pysftp_conn_kwargs or {}

        if port is None:
            if self.sftp:
                self.port = 22
            else:
                self.port = 21
        else:
            self.port = port

    def _connect(self):
        """
        Log in to ftp.
        """
        if self.sftp:
            self._sftp_connect()
        else:
            self._ftp_connect()

    def _sftp_connect(self):
        try:
            import pysftp
        except ImportError:
            logger.warning("Please install pysftp to use SFTP!")
            
        self.conn = pysftp.Connection(self.host, username=self.username, password=self.password, port=self.port, **self.pysftp_conn_kwargs)

    def _ftp_connect(self):
        if self.tls:
            self.conn = ftplib.FTP_TLS()
        else:
            self.conn = ftplib.FTP()

        self.conn.connect(self.host, self.port, timeout=self.timeout)
        self.conn.login(self.username, self.password)

        if self.tls:
            self.conn.prot_p()

    def _close(self):
        """ 
        Close ftp connection.
        """
        if self.sftp:
            self._sftp_close()
        else:
            self._ftp_close()

    def _sftp_close(self):
        self.conn.close()

    def _ftp_close(self):
        self.conn.quit()

    def exists(self, path, mtime=False):
        """
        Return `True` if file or directory at `path` exist, `False` otherwise.

        Additional check on modified time when `mtime` is passed in.

        Return `False` if the file's modified time is older than mtime.
        """
        self._connect()

        if self.sftp:
            exists = self._sftp_exists(path, mtime)
        else:
            exists = self._ftp_exists(path, mtime)

        self._close()

        return exists

    def _sftp_exists(self, path, mtime):
        exists = False

        if mtime:
            exists = self.conn.stat(path).st_mtime > mtime
        elif self.conn.exists(path):
            exists = True

        return exists 

    def _ftp_exists(self, path, mtime):
        dirname, fn = os.path.split(path)

        files = self.conn.nlst(dirname)

        exists = False
        if path in files or fn in files:
            if mtime:
                mdtm = self.conn.sendcmd("MDTM " + path)
                modified = datetime.datetime.strptime(mdtm[4:], "%Y%m%d%H%M%S")
                exists = modified > mtime
            else:
                exists = True
        
        return exists

    def remove(self, path, recursive=True):
        """
        Remove file or directory at location `path`.

        """
        self._connect()

        if self.sftp:
            self._sftp_remove(path, recursive)
        else:
            self._ftp_remove(path, recursive)

        self._close()

    def _sftp_remove(self, path, recursive):
        if self.conn.isfile(path):
            self.conn.unlink(path)
        else:
            if not recursive:
                raise RuntimeError("Path is not a regular file, and recursive is not set")

            directories = []
            # walk the tree and execute callbacks when files, directories and unknown types are encountered.
            # files must be removed first, then directories after files are gone.

            self.conn.walktree(path, self.conn.unlink, directories.append, self.conn.unlink)
            for directory in reversed(directories):
                self.conn.rmdir(directory)

            self.conn.rmdir(path)

    def _ftp_remove(self, path, recursive):
        if recursive:
            self._rm_recursive(self.conn, path)
        else:
            try:
                # try to delete file
                self.conn.delete(path)
            except ftplib.all_errors:
                # it is a folder 
                self.conn.rmd(path)

    def _rm_recursive(self, ftp, path):
        """ 
        Recursively delete a directory tree on a remote server.
        """
        wd = ftp.pwd()

        # check if it is a file first, because some FTP sewrversdon't return correctly on ftp.nlst()
        try:
            ftp.cwd(path)
        except ftplib.all_errors:
            # this is a file
            ftp.delete(path)
            return 

        try:
            names = ftp.nlst()
        except ftplib.all_errors:
            # some FTP server complain when you try and list non-existent paths
            return

        for name in names:
            if os.path.split(name)[1] in ('.', ', ', '..'):
                continue

            try:
                ftp.cwd(name)
                ftp.cwd(wd)
                ftp.cwd(path)

                self._rm_recursive(ftp, name)
            except ftplib.all_errors as e:
                ftp.delete(name)

        try:
            ftp.cwd(wd)
            ftp.rmd(path)
        except ftplib.all_errors as e:
            print('_rm_recursive: Could not remove {0}: {1}'.format(path, e))

    def put(self, local_path, path, atomic=True):
        """
        Put file from local filesystem to (s)FTP.
        """
        self._connect()

        if self.sftp:
            self._sftp_put(local_path, path, atomic)
        else:
            self._ftp_put(local_path, path, atomic)
        
        self._close()

    def _sftp_put(self, local_path, path, atomic):
        normpath = os.path.normpath(path)
        directory = os.path.dirname(normpath)
        self.conn.makedirs(directory)

        if atomic:
            tmp_path = os.path.join(directory, 'finestrino-tmp-{:09d}'.format(randon.randrange(0, 1e10)))
        else:
            tmp_path = normpath

        self.conn.put(local_path, tmp_path)

        if atomic:
            self.conn.rename(tmp_path, normpath)

    def _ftp_put(self, local_path, path, atomic):
        normpath = os.path.normpath(path)
        folder = os.path.dirname(normpath)

        for subfolder in folder.split(os.sep):
            if subfolder and subfolder not in self.conn.nlst():
                self.conn.mkd(subfolder)

            self.conn.cwd(subfolder)

        # go back to ftp root folder
        self.conn.cwd("/")

        # random file name
        if atomic:
            tmp_path = folder + os.sep + "finestrino-tmp-%09d" % random.randrange(0, 1e10)
        else:
            tmp_path = normpath

        self.conn.storbinary("STOR %s" % tmp_path, open(local_path, 'rb'))

        if atomic:
            self.conn.rename(tmp_path, normpath)

    def get(self, path, local_path):
        """
        Download file from (s)FTP to local filesystem.
        """
        normpath = os.path.normpath(local_path)
        folder = os.path.dirname(normpath)

        if folder and not os.path.exists(folder):
            os.makedirs(folder)

        tmp_local_path = local_path + "-finestrino-tmp-%09d" + random.randrange(0, 1e10)

        # download file
        self._connect()

        if self.sftp:
            self._sftp_get(path, tmp_local_path)
        else:
            self._ftp_get(path, tmp_local_path)

        self._close()

        os.rename(tmp_local_path, local_path)

    def _sftp_get(self, path, tmp_local_path):
        self.conn.get(path, tmp_local_path)

    def _ftp_get(self, path, tmp_local_path):
        self.conn.retrbinary("RETR %s" % path, open(tmp_local_path))

    def listdir(self, path="./"):
        """
        Gets a list of the contents of path in (s)FTP.
        """
        self._connect()

        if self.sftp:
            contents = self._sftp_listdir(path)
        else:
            contents = self._ftp_listdir(path)

        self._close()

        return contents

    def _sftp_listdir(self, path):
        return self.conn.listdir(remotepath=path)

    def _ftp_listdir(self, path):
        return self.conn.nlst(path)

class AtomicFtpFile(finestrino.target.AtomicLocalFile):
    """ 
    Simple class that writes to a temp file and upload to ftp on close().

    Also cleans up the temp file if close is not invoked.
    """
    def __init__(self, fs, path):
        """ 
        Initializes an AtomicFtpFile instance.
        """
        self._fs = fs
        super(AtomicFtpFile, self).__init__(path)

    def move_to_final_destination(self):
        self._fs.put(self.tmp_path, self.path)

    @property
    def fs(self):
        return self._fs

class RemoteTarget(finestrino.target.FileSystemTarget):
    """
    Target used for reading from remote files.

    The target is implemented using ssh commands streaming data over the network.
    """

    def __init__(self, path, host, format=None, username=None, password=None, port=None, mtime=None, tls=False, timeout=60, sftp=False, pysftp_conn_kwargs=None):
        if format is None:
            format = finestrino.format.get_default_format()

        self.path = path 
        self.mtime = mtime
        self.format = format
        self.tls = tls 
        self.timeout = timeout
        self.sftp = sftp
        self._fs = RemoteFileSystem(host, username, password, port, tls, timeout, sftp, pysftp_conn_kwargs)

    @property
    def fs(self):
        return self._fs

    def open(self, mode):
        """
        Open the FileSystem Target.

        This method returns a file-like object which can be read from or written to depending on specified mode.

        :param mode: the mode `r` opens the FileSystemTarget in read-only mode, whereas `w` will open the 
                    FileSystemTarget in write mode. Subclasses can implement additional options. 

        :type mode: str
        """
        if mode == 'w':
            return self.format.pipe_writer(AtomicFtpFile(self._fs, self.path))
        elif mode == 'r':
            temp_dir = os.path.join(tempfile.gettempdir(), 'finestrino-contrib-ftp')
            self.__tmp_path = temp_dir + "/" + self.path.lstrip('/') + '-finestrino-tmp-%09d' % random.randrange(0, 1e10)
            # download file to local 
            self._fs.get(self.path, self.__tmp_path)

            return self.format.pipe_reader(
                    FileWrapper(io.BufferedReader(io.FileIO(self.__tmp_path, 'r')))
            )
        else:
            raise Exception("mode must be 'r' or 'w' (got: %s)" % mode)


    def exists(self):
        return self.fs.exists(self.path, self.mtime)

    def put(self, local_path, atomic=True):
        return self.fs.put(local_path, self.path, atomic)

    def get(self, local_path):
        self.fs.get(self.path, local_path)
 

