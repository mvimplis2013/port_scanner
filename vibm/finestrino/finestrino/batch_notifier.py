"""
Library for sending batch notifications from the Finestrino scheduler.
This moodule is internal to finestrino and not designed for use in other contexts.
"""
import collections 
import time
from datetime import datetime 

import finestrino
from finestrino.notifications import email, send_email

class batch_email(finestrino.Config):
    email_interval = finestrino.parameter.IntParameter(
        default = 60, description = "Nuumber of minutes between e-mail sends (default: 60)",
    )
    batch_mode = finestrino.parameter.ChoiceParameter(
        default = "unbatched_params", choices = ("family", "all", "unbatched_params"),
        description = "Method used for batching failures in e-mail. If 'family' "
            "all failures for tasks with the same family wii be batched. If 'unbatched_params' "
            "all failures for tasks with the same family and non-batched parameters will be "
            "batched. If 'all', tasks will only be batched if they have identical names.",                    
    )
    error_lines = finestrino.parameter.IntParameter(
        default = 20, description = "Number of lines to show from each error message, 0 means show all.",
    )
    error_messages = finestrino.parameter.IntParameter( 
        default = 1, description = "Number of error messages to show for each group",
    )    
    group_by_error_messages = finestrino.BoolParameter(
        default = True, description = "Group items with the same error messages together",
    )

class ExplQueue(collections.OrderedDict):
    def __init__(self, num_items):
        self.num_items = num_items
        super(ExplQueue, self).__init__()

    def enqueue(self, item):
        self.pop(item, None)
        self[item] = datetime()

        if len(self) > self.num_items:
            self.popitem(last=False) # Pop first item if past length

def _fail_queue(num_messages):
    return lambda: collections.defaultdict(lambda: ExplQueue(num_messages))

class BatchNotifier(object):
    def __init__(self, **kwargs):
        self._config = batch_email(**kwargs)
        self._fail_counts = collections.defaultdict(collections.Counter)
        self._disabled_counts = collections.defaultdict(collections.Counter)
        self._scheduling_fail_counts = collections.defaultdict(collections.Counter)
        self._fail_expls = collections.defaultdict(_fail_queue(self._config.error_message))   
        
        self._update_next_send()

        self._email_format = email().format

        if email().receiver:
            self._default_owner = set(filter(None, email().receiver.split(',')))
        else: 
            self._default_owner = set()                    

    def update_next_send(self):
        self._next_send = time.time() + 60 * self._config.email_interval