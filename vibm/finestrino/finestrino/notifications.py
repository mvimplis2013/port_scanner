""" 
Supports sending emails when tasks failed. 

In particular using the configuration `receiver` should set up Finestrino for 
sending emails in case of tasks failure.

.. code-block:: ini
    [email]
    receiver = foo@bar.nz
"""

import logging
import socket
import sys
import textwrap

import finestrino.task
import finestrino.parameter


logger = logging.getLogger("finestrino-interface")

DEFAULT_CLIENT_EMAIL = "finestrino-client@%s" % socket.gethostname()

class TestNotificationsTask(finestrino.task.Task):
    """ 
    You may invoke this Task to quickly check if you correctly have setup
    your notifications Configuration. You can run:

    .. code-block:: console

            $ finestrino TestNotificationsTask --local-scheduler --email-force-send

    And then check your email inbox to see if you an error email or any other
    kind of notifications that you expected.
    """ 
    raise_in_complete = finestrino.parameter.BoolParameter(
        description = "If True, fail in complete() instead of run()",
    )

    def run(self):
        raise ValueError("Testing notifications triggering")

    def complete():
        if self.raise_in_complete:
            raise ValueError("Testing notifications triggering")

        return False

class email(finestrino.Config):
    force_send = finestrino.parameter.BoolParameter(
        default = False,
        description = 'Send e-mail even from tty',
    ) 

    format = finestrino.parameter.ChoiceParameter(
        default = 'plain',
        config_path = dict(section='core', name='email-type'),
        choices = ('plain', 'html', 'none'),
        description = 'Format type to send the e-mails',
    )

    method = finestrino.parameter.ChoiceParameter(
        default = 'smtp',
        config_path = dict(section='email', name='type'),
        choices = ('smtp', 'sendgrid', 'ses', 'sns'), 
        description = 'Method for sending e-mail',
    ) 

    prefix = finestrino.parameter.Parameter(
        default = '',
        config_path = dict(section='core', name='email-prefix'),
        description = 'Prefix for subject lines in all e-mails',
    )

    receiver = finestrino.parameter.Parameter(
        default = '',
        config_path = dict(section='core', name='error-email'),
        description = 'Address to send error-emails to',
    )

    sender = finestrino.parameter.Parameter(
        default = DEFAULT_CLIENT_EMAIL,
        config_path = dict(section='core', name='email-sender'),
        description = "Address to send email from",
    )

def send_email(subject, message, sender, recipients, image_png=None):
    """ 
    Decides whether to send notification. Notification is cancelled if there 
    are no recipients or if stdout is on tty or if in debug mode.

    Dispatches on config value email.method. Default is 'smtp'.     
    """ 
    notifiers = {
        "ses": send_email_ses,
        "sendgrid": send_email_sendgrid,
        "smtp": send_email_smtp,
        "sns": send_email_sns,
    }

    subject = _prefix(subject)
    
    if not recipients or recipients == (None,):
        return

    if _email_disabled_reason():
        logger.info("Not sending email to %r because %s",
            recipients, _email_disabled_reason())

        return

    # Clean the reipients lists to allow multiple email addresses, 
    # comma separated in finestrino.cfg
    recipients_tmp = []
    
    for r in recipients:
        recipients_tmp.extend([a.strip() for a in r.split(',') if a.strip()])

    # Replace original recipients with the clean list
    recipients = recipients_tmp

    logger.info("Sending email to %r", recipients)

    # Get appropriate sender and call it to send the notification
    email_sender = notifiers[email().method]
    email_sender(sender, subject, message, recipients, image_png)

    logger.info()

     