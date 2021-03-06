""" 
The abstract :py:class:Target` class.
It is a central concept of finestrino and represents the state of the workflow
"""
import abc
import logging 
import warnings
import random
import os
import io
import tempfile

from finestrino import six 


logger = logging.getLogger("finestrino-interface")

@six.add_metaclass(abc.ABCMeta)
class Target(object):
    """ 
    A Target is a resource generated by a :py:class:`~finestrino.task.Task`.
    For example, a Target might correspond to a file in HDFS or data in a database.
    The Target interface defines one method that must be overriden :py:meth:`exists`,
    which signifies if the Target has been created or Not.

    Typically, a :py:class:`~finestrino.task.Task` will define one or more Targets 
    as output, and the Task is considered complete if and only if each of its output Targets exist.
    """
    @abc.abstractmethod
    def exists(self):
        """
        Returns True if the :py:class:`Target` exists and False otherwise.
        """
        pass

class FileSystemException(Exception):
    """ 
    Base class for generic file system exceptions.
    """
    pass

class FileAlreadyExists(FileSystemException):
    """ 
    Raised when a parent directory doesn't exist.
    (Imagine mkdir without a -p)
    """
    pass

class MissingParentDirectory(FileSystemException):
    """
    Raised when ever a parent directory doesn't exist.
    (Imagine a mkdir without -p)
    """
    pass
     
class NotADirectory(FileSystemException):
    """ 
    Raised when a file system operation can't be performed because an 
    expected directory is actually a fiel.
    """
    pass

@six.add_metaclass(abc.ABCMeta)
class FileSystem(object):
    """ 
    FileSystem abstraction used in conjunction with :python:class:`FileSystemTarget`.

    Typically a FileSystem is associated with instances of a :py:class:FileSystemTarget`. 
    The instances of the :py:class:`FileSystemTarget` will delegate methods such as 
    :py:meth:`FileSystemTarget.exists` and :py:meth:`FileSystemTarget.remove` to the FileSystem.

    Methods of FileSystem raise :py:class:`FileSystemException` if there is a problem completing the operation.
    """

    @abc.abstractmethod
    def exists(self, path):
        """ 
        Return TRUE if file or directory at PATH exist, False otherwise.

        :param str path: a path within the FileSystem to check for existence.
        """
        pass

    @abc.abstractmethod
    def remove(self, path, recursive=True, skip_trash=True):
        """ 
        Remove file or directory at location PATH.

        :param str path: a path within the FileSystem to remove.
        :param bool recursive: if the path is a directory, recursively, remove the directory and
            all of its descendants.
        """
        pass

    def mkdir(self, path, parents=True, raise_if_exists=False):
        """ 
        Create directory at location ``path`` and implicitly create parent directories 
        if they do not already exist.

        :param str path: a path within the FileSystem to create as a directory.
        :param bool parents: Create parent directories when necessary. When is parents=False and the
            parent folder does not exist then raise an finestrino.target.MissingParentDirectory
        :param bool raise_if_exists: raise an finestrino.target.FileAlreadyExists if 
            the folder already exists.
        """ 
        raise NotImplementedError("mkdir() not implemented on {0}".format(self.__class__.__name__))

    def isdir(self, path):
        """ 
        Return ``True`` if the location at ``path`` is a directory. If not then return ``False``.

        :param str path: a path within the FileSystem to check as a directory.

        "Note: This method is optional, not all FileSystem subclass implements it.
        """
        raise NotImplementedError("isdir() not implemented on {0}".format(self.__class__.__name__))

    def listdir(self, path):
        """ 
        Return a list of files ropted in path.

        This returns an iterable of the files rooted at ``path``. This is intended to be a recursive listing.

        :param str path: a path within the FileSystem to list.

        "Note": This method is optional, not all FileSystem subclasses implement it.
        """
        raise NotImplementedError("listdir() not implemented on {0}".format(self.__class__.__name__))

    def move(self, path, dest):
        """ 
        Move a file from path to dest.
        """
        raise NotImplementedError("move() not implemeneted on {0}".format(self.__class__.__name__))

    def rename_dont_save(self, path, dest):
        """ 
        Potentially rename ``path`` to ``dest``, but do not move it into the ``dest`` folder (if it is a folder). 
        This relates to :ref:`AtomicWrites`.

        This method will just do ``move()`` if the file doesn't ``exists()`` already.
        """
        warnings.warn("File System {} client doesn't support atomic mv.".format(self.__class__.__name__))

        if self.exists(dest):
            raise FileAlreadyExists()

        self.move(path, dest)

    def rename(self, *args, **kwargs):
        """
        Alias for ``move()``
        """
        self.move(*args, **kwargs)

    def copy(self, path, dest):
        """
        Copy a file or a directory with contents.

        Currently, LocalFileSystem and MockFileSystem support only single file copying but 
        S3Client copies either a file or a directory as required.
        """
        raise NotImplementedError("copy() not implemented on {0}".format(self.__class__.__name__))

class FileSystemTarget(Target):
    """" 
    Base class for FileSystem Targets like :class:`~finestrino.file.LocalTarget` and 
    :class:`~finestrino.contrib.hdfs.HdfsTarget`.

    A FileSystemTarget has an associated :py:class:`FileSystem` to which certain 
    operations can be delegated. By default :py:meth:`exists`and :py:meth:`remove`
    are delegated to the :py:class:`FileSystem`, which is determined by the 
    :py:attr:`fs` attribute.

    Methods of FileSystemTarget raise a :py:class:`FileSystemException` if there 
    is a problem completing the operation.     
    """ 
    def __init__(self, path):
        """ Initializes a FileSystemTarget instance.
        
        Arguments:
            path {str} -- the path associated with this FileSystemTarget
        """
        self.path = path

    @abc.abstractproperty
    def fs(self):
        """
        The :py:class:`FileSystem` associated with this FileSystemTarget.
        """
        raise NotImplementedError()


    @abc.abstractmethod
    def open(self, mode):
        """ 
        Open the FileSystem target.

        This method returns a file-like object which can either be read or 
        written to depending on the specified mode.

        :param str mode: the mode 'r' opens the FileSystemTarget in read-only and 'w' will open in write mode.

        Subclasses can implement additional options.  
        """
        pass

    def exists(self):
        """
        Returns `True` if the path for this FileSystemTarget exists, `False` otherwise.

        This method is implemented by using the :py:attr:`fs`.
        """
        path = self.path

        if "*" in path or "?" in path or "[" in path or "{" in path:
            logger.warning("Using wildchards in path %s might lead to processing of an incomplete dataset; " 
                "override exists() to suppress the warning.", path)

        return self.fs.exists(path)

    def remove(self):
        """
        Remove the resource at the path specified by this FileSystemTarget.

        This method is implemented by using the :py:attr:`fs`.
        """
        self.fs.remove(self.path)

    def remporary_path(self):
        """
        A context manager that enables a reasonably sort, general and magic-less way to solve the :ref:`Atomicwrites`.

        * On 'enering', it will create the parenet directories so temp_path is writtable right away (:py:meth:FileSystem.mkdir)
        * On 'exiting', it will move the temporary file if there was no exception thrown (:py:meth:FileSystem.rename_dont_move)
        """
        class _Manager(object):
            target = self

            def __init__(self):
                num = random.randrange(0, 1e10)
            
                slashless_path = self.target.path.rstrip("/").rstrip("\\")

                self._temp_path = "{}-finestrino-temp-{%010}{}".format(
                    slashless_path, num, self.target._trailing_slash()
                )

                tmp_dir = os.path.dirname(slashless_path)
                if tmp_dir:
                    self.target.fs.mkdir(tmp_dir, parent=True, raise_if_exists=False)

            def __enter__(self):
                return self._temp_path

            def __exit__(self, exc_type, exc_value, traceback):
                if exc_type == None:
                    # There were no exceptions
                    self.target.fs.rename_dont_move(self._temp_path, self.target.path)

                return False # False means we do not suppress the exception

        _Manager()

    def _touchz(self):
        with self.open('w'):
            pass

    def _trailing_slash(self):
        return self.path[-1] if self.path[-1] in r"\/" else ""

class AtomicLocalFile(io.BufferedWriter):
    """
    Abstract class to create a Target that creates a temporary file 
    in the local filesystem before moving it to its final destination. 
    """
    def __init__(self, path):
        self.__tmp_path = self.generate_tmp_path(path)
        self.path = path 
        super(AtomicLocalFile, self).__init__(io.FileIO(self.__tmp_path, 'w'))

    def close(self):
        super(AtomicLocalFile, self).close()
        self.move_to_final_destination()

    def  generate_tmp_path(self, path):
        return os.path.join(tempfile.gettempdir(), "finestrino-s3-tmp-%09d" % random.randrange(0, 1e10))

    def move_to_final_destination(self):
        raise NotImplementedError()

    def __del__(self):
        if os.path.exists(self.tmp_path):
            os.remove(self.tmp_path)

    @property
    def tmp_path(self):
        return self.__tmp_path

    def __exit__(self, exc_type, exc_value, traceback):
        " Close/ commit the file if there are no exception"
        if exc_type:
            return

        return super(AtomicLocalFile, self).__exit__(exc_type, exc_value, traceback)
    
