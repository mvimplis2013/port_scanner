"""
You can run this example like this:
    code::console
        $> finestrino --module examples.execution_summary_example examples.EntryPoint --local-scheduler
        '''
        ''' lots of spammy output
        '''
        INFO: There are 11 pending tasks unique to this worker
        INFO: worker worker(salt=84361665, workers=1, host=arash-beautiful-T440s, username=arash, pid=18534) was stopped. Shutting down Keep-Alive thread.
        INFO: 
        ==== Finestrino Execution Summary ====

        Scheduled 218 tasks of which:
        * 195 complete ones were encountered:
           - 195 examples.Bar(num=5...199)
        * 1 ran successfully: 
           - 1 examples.Boom(...)
        * 22 were left pending, among these:
            - 1 were missing external dependencies:
                - 1 MyExternal()
            - 21 had missing dependencies:
                - 1 examples.EntryPoint()
                - examples.Foo(num=100, num2=16) and 9 other examples.Foo
                - 10 examples.DateTask(date=1998-03-23...1998-04-01, num=5)

        This progress looks :| because there are missing external dependencies

        ==== Finestrino Execution Summary ====
"""
from __future__ import print_function

import datetime 

import finestrino 

class MyExternal(finestrino.ExternalTask):
    def complete(self):
        return False

class Boom(finestrino.Task):
    task_namespace = "examples"
    this_is_a_really_long_I_mean_way_too_long_and_annoying_parameter = finestrino.IntParameter()

    def run(self):
        print("Running Boom")

    def requires(self):
        for i in range(5, 200):
            yield Bar(i)

class Foo(finestrino.Task):
    task_namespace = "examples"

    num = finestrino.IntParameter()
    num2 = finestrino.IntParameter()

    def run(self):
        print("Running Foo")

    def requires(self):
        yield MyExternal()
        yield Boom(0)

class Bar(finestrino.Task):
    task_namespace = "examples"

    num = finestrino.IntParameter() 

    def run(self):
        self.output().open('w').close()

    def output(self):
        return finestrino.LocalTarget("/tmp/bar/%d" % self.num)

class DateTask(finestrino.Task):
    task_namespace = "examples"

    date = finestrino.DateParameter()
    num = finestrino.IntParameter()

    def run(self):
        print("Running DateTask")

    def requires(self):
        yield MyExternal()
        yield Boom(0)

class EntryPoint(finestrino.Task):
    task_namespace = "examples"

    def run(self):
        print("Runnning EntryPoint")

    def requires(self):
        for i in range(10):
            yield Foo(100, 2*i)
        
        for i in range(10):
            yield DateTask(datetime.date(1998, 3, 23) + datetime.timedelta(days=i), 5)


