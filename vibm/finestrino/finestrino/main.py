class FinestrinoMain(object):
    def __init__(self):
        self.args = self.parse_args()

    def init_args(self):
        version = "Finestrino v" + __version__
