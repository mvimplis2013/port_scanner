from libnmap.process import NmapProcess
from libnmap.parser import NmapParser

def do_scan(targets, options):
    parsed = None
    nmproc = NmapProcess(targets, options)
    rc = nmproc.run()

    
if __name__ == "__main__":
    report = do_scan("127.0.0.1", "-sV")

    if report:
        print_scan(report)
    else:
        print("No results returned")
