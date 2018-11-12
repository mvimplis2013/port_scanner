from rq import Connection, Queue, Worker

def main():
    with Connection():
        q = Queue()
        Worker(q).work()

if __name__ == "__main__":
    main()

