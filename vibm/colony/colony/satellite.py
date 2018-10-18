#!/usr/bin/env python

"""This class is an interface for Reactionner and Poller daemons.
"""

# Try to see if we are in an Android device or not 
is_android = True
try:
    import android
except ImportError:
    is_android = False

from Queue import Empty

if not is_android:
    from multiprocessing import Queue, active_children, cpu_count
else:
    from Queue import Queue

# Interface for Arbiter (our big MASTER)
class IForArbiter(Interface):
    doc = 'Remove a scheduler connection (internal)'

    # Arbiter ask us to stop using a specific scheduler_id
    def remove_from_conf(self, sched_id):
        try:
            del self.app.schedulers[sched_id]
        except KeyError:
            pass

    remove_from_conf.doc = doc

    doc = 'Return the managed configuration scheduler -IDs (internal)'
    # Arbiter asked me which which is the managed scheduler-ID.
    # After checking might ask to remove the specific id
    def what_i_managed(self):
        logger.debug("The arbiter asked me what I manage. It is %s", self.app.what_i_managed())
        return self.app.what_i_managed()

    what_i_managed.need_lock = False
    what_i_managed.doc = doc

    doc = 'Ask the daemon to drop its configuration and wait for a new one'
    # Call by arbiter if the configuration we are running is outdated 
    # (stop-and-wait for new configuration)
    def wait_new_conf(self):
        logger.debug("Arbiter wants me to wait for a new configuration")
        self.app.schedulers.clear()
        self.app.cur_conf = None

    wait_new_conf.doc = doc

    doc = 'Push broker objects to the daemon (internal)'
    # Following methods are only used by broker
    # Used by Arbiter to push BROKS to broker
    def push_broks(self, broks):
        with self.app.arbiter_brocks_lock:
            self.app.arbiter_broks.extend(broks)
    
    push_broks.method = 'post'
    # We are using a Lock just for not locking from Arbiter
    push_broks.need_lock = False
    push_broks.doc = doc

    doc = 'Get the external commands from the daemon (internal)'
    # The Arbiter ask us our external commands in queue
    def get_external_commands(self):
        with self.app.external_commands_lock:
            cmds = self.app.get_external_commands()
            raw = cPickle.dumps(cmds)
        return raw
    get_external_commands.need)lock = False
    get_external_commands.doc = doc

    doc = 'Does the daemon got configuration (receiver)'
    # Only useful for receiver
    def got_conf(self):
        return self.app.cur_conf is not None
    got_conf.need_lock = False
    got_conf.doc = doc

    doc = 'Push hostname/ scheduler links (receiver in direct routing)'
    # Used by the receivers to get the hostnames managed by schedulers
    def push_host_names(self, sched_id, hnames):
        self.app.push_host_names(sched_id, hnames)
    push_host_names.method = 'post'
    push_host_names.doc = doc


class IScheduler(Interface):
    """Interface for Schedulers
    If we are passive, they connect to this and send/get actions
    
    Arguments:
        Interface {[type]} -- [description]
    """

    doc = 'Push new actions to the scheduler (internal)'
    # A Scheduler send me actions to do 
    def push_actions(self, actions, sched_id):
        self.app.add_actions(actions, sched_id)
    push_actions.method = 'post'
    push_actions.doc = doc

    doc = 'Get the returns of the actions (internal)'
    # A Scheduler asks us the action return value
    def get_returns(self, sched_id):
        # print "A scheduler ask us the action return value"
        ret = self.app.get_return_for_passive(int(sched_id))
        # print "Send back", len(ret), "returns"
        return cPickle.dumps(ret)
    get_returns.doc = doc

class IBroks(Interface):
    """Interface for Brokers
    They connect here and get all broks (data for brokers)
    data must be ORDERED ! (initial status before update)
    """

    doc = 'Get broks from the daemon'
    # Poller or Reactionner ask us actions
    def get_broks(self, bname, broks_batch=0):
        res = self.app.get_broks(brocks_batch)
        return base64.b64encode(zlib.compress(cPickle.dumps(res), 2))
    get_broks.doc = doc

class IStats(Interface):
    """Interface for various stats about poller/ reactionneractivity
    
    Arguments:
        Interface {[type]} -- [description]
    """

    doc = 'Get raw stats from daemon'
    def get_raw_stats(self):
        app = self.app
        res = {}

        for sched_id in app.schedulers:
            sched = app.schedulers[sched_id]
            lst = []

            res[sched_id] = lst

            for mod in app.q_by_mod:
                # In workers we 've got actions send to queue
                for (i, q) in app.q_by_mod[mod].items():
                    lst.append({
                        'scheduler_name': sched['name'],
                        'moduke': mod,
                        'queue_number': i,
                        'queue_size': q.size(),
                        'return queue_len': app.get_returns_queue_len()})
            
        return res
    get_raw_stats.doc = doc


class BaseSatellite(Daemon):
    
    def __init__(self, name, config_file, is_daemon, do_replace, debug, debug_file):
        super(BaseSatellite, self).__init__(name, config_file, is_daemon, do_replace, 
            debug, debug_file)

        # Our Schedulers
        self.schedulers = {}

        # Now we create the interfaces
        self.interface = IForArbiter(self)
        self.istats = IStats(self)

        # Can have a queue of external commands given by modules
        # They will be taken by Arbiter to process
        self.external_commands = []
        self.external_commands_lock = threading.RLock()

    # The Arbiter can can resend us a new config in the pyro_daemon port.
    # It is NOT  a blocking wait.
    # When new config is available, we re-init the connections with schedulers
    def watch_for_new_conf(self, timeout):
        self.handleRequests(timeout)

    def do_stop(self):
        if self.http_daemon and self.interface:
            logger.info("[%s] Stopping all network connections", self.name)
            self.http_daemon.unregister(self.interface)

        super(BaseSatellite, self).do_stop()

    # Give the arbiter the data about ready to manage
    # the IDs of schedulers
    def what_i_managed(self):
        r = {}
        for (k,v) in self.schedulers.iteritems():
            r[k] = v['push_flavor']

        return r

    # Call by Arbiter to get our external commands
    def get_external_commands(self):
        res = self.external_commands
        self.external_commands = []

        return res

class Satellite(BaseSatellite):
    """ Our Main App Class """

    def __init__(self, name, config_file, is_daemon, do_replace, debug, debug_file):
        # keep broks so they can be consumed by a broker 
        self.broks = []

        # dictionary of active workers
        self.workers = []

        # Init stats like Load 4 Workers
        self.wait_ratio = Load(initial_value = 1)

        self.brok_interface = IBroks(self)
        self.scheduler_interface = ISchedulers(self)

        # Just for having these attributes defined here
        self.uri2 = None
        self.uri3 = None
        self.s = None

        self.returns_queue = None
        self.q_by_mod = {}


    def pynag_con_init(self, id):
        _t = time.time()
        r = self.do_pynag_con_init(id)
        statmgr = timing('con-init.scheduler', time.time() - _t, "perf")

        return r

    def do_pynag_con_init(self, id):
        sched = self.schedulers[id]

        if not sched['active']:
            return 

        sname = sched['name']
        uri = sched['uri']
        running_id = sched['running_id']
        timeout = sched['timeout']
        data_timeout = sched['data_timeout']
        logger.info("[%s] Init connection with %s at %s (%ss,%ss)",
            self.name, sname, uri, timeout, data_timeout)

        try:
            sch_con = sched['con'] = HTTPClient(
                uri=uri, strong_ssl = sched['hard_ssl_name_check'],
                timeout=timeout, data_timeout=data_timeout
            )
        except HTTPExceptions, exp:
            logger.warning("[%s] Scheduler %s is not initialized or has network problem: %s",
                self.name, sname, str(exp))

            sched['con'] = None
            return

        try:
            new_run_id = sch_con.get('get_running_id')
            new_run_id = float(new_run_id)
        except (HTTPExceptions, cPicklingError, KeyError), exp:
            logger.warning("[%s] The running %s is not initialized or has network problem: %s", 
                self.name, sname, str(exp))
            sched['con'] = None
            return

        if sched['running_id'] != 0 and new_run_id != running_id:
            logger.info("[%s] The running id of the scheduler %s changed, "
                "we must clear all its actions",
                self.name, sname)
            del sched['wait_homerun'][:]
        sched['running_id'] = new_run_id
        logger.info("[%s] Connection OK with scheduler %s", self.name, sname)

    # Manage actions returned from Workers
    # We just put them to appropriate scheduler
    def manage_action_return(self, action):
        cls_type = action.__class__.my_type

        if cls_type not in ['check', 'notification', 'eventhandler']:
            self.add(action)
            return

        sched_id = action.sched_id

        del action.sched_id

        try:
            del action.worker_id
        except AttributeError:
            pass

        try:
            del self.schedulers[sched_id]['actions'][action.get_id()]
        except KeyError:
            pass

        try:
            del self.schedulers[sched_id]['actions'][action.get_id()]
        except KeyError:
            pass

        try:
            self.schedulers[sched_id]['wait_homerun'].append(action)
        except KeyError:
            pass

    def manage_returns(self):
        _t = time.time()
        r = self.do_manage_returns()
        _type = self.__class__.my_type
        statsmgs.timing('core.%s.manage-returns' % _type, time.time()-_t, 'perf')

        return 

        



