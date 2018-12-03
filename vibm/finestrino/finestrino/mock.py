"""
  This module provides a class :class:`MockTarget`, an implementation of 
  :py:class:`~finestrino.target.Target`.
  :class:`MockTarget` contains all data in-memory.
  The main purpose is unit testing workflows without writing to disk.
"""

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


    

