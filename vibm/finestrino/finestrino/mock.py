"""
  This module provides a class :class:`MockTarget`, an implementation of 
  :py:class:`~finestrino.target.Target`.
  :class:`MockTarget` contains all data in-memory.
  The main purpose is unit testing workflows without writing to disk.
"""

import multiprocessing 
import warnings
from io import BytesIO
import sys

from finestrino import target

from finestrino.format import get_default_format, MixedUnicodeBytes

from finestrino import six

class MockFileSystem(target.FileSystem):
    """ 
    MockFileSystem inspects/ modifies _data to simulate file system operations.
    """
    _data = None

    def copy(self, path, dest, raise_if_exists=False):
        """ 
        Copies the contents of a single file path to dest.
        """
        if raise_if_exists and dest in self.get_all_data():
            raise RuntimeError('Destination exists: %s' % path)

        contents = self.get_all_data()[path]
        self.get_all_data()[dest] = contents

    def get_all_data(self):
        """ 
        This starts a server in the background, so we don't want to do it in the global scope.
        """

        if MockFileSystem._data is None:
            MockFileSystem._data = multiprocessing.Manager().dict()

        return MockFileSystem._data

    def get_data(self, fn):
        return self.get_all_data()[fn]

    def exists(self, path):
        return MockTarget(path).exists()

    def remove(self, path, recursive=True, skip_trash=True):
        """ 
        Removes the given mockfile.
        """
        if recursive:
            to_delete = []


            for s in self.get_all_data().keys():
                if s.startswith(path):
                    to_delete.append(s)

            for s in to_delete:
                self.get_all_data().pop(s)
        else:
            self.get_all_data().pop(path)

    def move(self, path, dest, raise_if_exists=False):
        """
        Moves a single file from path to dest.
        """
        if raise_if_exists and dest in self.get_all_data():
            raise RuntimeError("Destination Exists: %s" % path)

        contents = self.get_all_data().pop(path)
        self.get_all_data()[dest] = contents

    def listdir(self, path):
        """
        listdir does a prefix match of self.get_all_data(), but doesn't yet support globs.
        """
        return [s for s in self.get_all_data().keys() if s.startswith(path)]

    def isdir(self, path):
        return any(self.listdir(path))

    def mkdir(self, path, parents=True, raise_if_exists=False):
        """
        mkdir is a noop
        """
        pass 

    def clear(self):
        self.get_all_data().clear()

class MockTarget(target.FileSystemTarget):
    fs = MockFileSystem()

    def __init__(self, fn, is_tmp=None, mirror_on_stderr=False, format=None):
        self._mirror_on_stderr = mirror_on_stderr
        self.path = fn 
        if format is None:
            format = get_default_format()

        # Allow to write unicode in file for compatibility
        if six.PY2:
            format = format >> MixedUnicodeBytes

        self.format = format

    def exists(self):
        return self.path in self.fs.get_all_data()

    def move(self, path, raise_if_exists=False):
        """
        Call MockFileSystem's move command
        """
        self.fs.move(self.path, path, raise_if_exists)

    def rename(self, *args, **kwargs):
        """
        Call move to rename self
        """
        self.move(*args, **kwargs)

    def open(self, mode='r'):
        fn = self.path 
        mock_target = self 

        class Buffer(BytesIO):
            # Just to be able to do writing & rerading from same buffer 

            _write_line = True
            def set_wrapper(self, wrapper):
                self.wrapper = wrapper 

            def write(self, data):
                if mock_target._mirror_on_stderr:
                    if self._write_line:
                        sys.stderr.write(fn + ": ")

                    if six.binary_type:
                        sys.stderr.write(data.encode('utf8'))
                    else:
                        sys.stderr.write(data)


                    if data[-1] == '\n':
                        self._write_line = True 
                    else:
                        self._write_line = False 

                super(Buffer, self).write(data)

            def close(self):
                if mode[0] == 'w':
                    try:
                        mock_target.wrapper.flush()
                    except AttributeError:
                        pass
                    
                    mock_target.fs.get_all_data()[fn] = self.getValue()

                super(Buffer, self).close()

            def __exit__(self, exc_type, exc_val, exc_tb):
                if not exc_type:
                    self.close()

            def __enter__(self):
                return self

            def readable(self):
                return mode[0] == 'r'

            def writable(self):
                return mode[0] == 'w'

            def seekable(self):
                return False 

        if mode[0] == 'w':
            wrapper = self.format.pipe_writer(Buffer())
            wrapper.set_wrapper(wrapper)
            return wrapper
        else:
            return self.format.pipe_reader(Buffer(self.fs.get_all_data()[fn]))

class MockFile(MockTarget):
    def __init__(self, *args, **kwargs):
        warnings.warn("MockFile has been renamed MockTarget", DeprecationWarning, stacklevel=2)
        super(MockFile, self).__init__(*args, **kwargs)
    

    




    

