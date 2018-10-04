import json

from ..core import Provider, Response
from ..utils import requests
from ..utils.schema.helpers import one_or_more

class MailGun(Provider):
    """ Send emails via MailGun """

    base_url = "https://api.mailgun.net/v3/{domain}/messages"
    site_url = "https://documentation.mailgun.com/"
    name = "mailgun"
    path_to_errors = ("message",)

    __properties_to_change = [
        "tag",
        "dkim",
        "deliverytime",
        "testmode",
        "tracking",
        "tracking_clicks",
        "tracking_opens",
        "require_tls",
        "skip_verification",
    ]

    __email_list = one_or_more(
        {
            "type": "string",
            "title": "Email address of the recipient(s). Example: `Bob <bob@host.com>`.",
        }
    )

    _required = {
        "allOf": [
            {"required": ["to", "domain", "api_key"]},
            {"anyOf": [{"required": ["from"]}, {"required": ["from_"]}]},
            {
                "anyOf": [{"required": ["message"]}, {"required": ["html"]}]
            },
        ]
    }

    _schema = {
        "type": "object",
        "propertiers": {
            "api_key": {
                "type": "string",
                "title": "User's API key",
            },
            "message": {
                "type": "string",
                "title": "Body of the message. (text version)",
            },
            "html": {"type": "string", "title": "Body of the message. (HTML version)"},
            "to": __email_list,
            "from": {
                "type": "string",
                "title": "Email address for FROM header",
                "duplicate": True,
            },
            "from_": {
                "type": "string",
                "format": "email",
                "title": "Email address for FROM header",
                "duplicate": True,
            },
            "domain": {"type": "string", "title": "MailGun's domain to use"},
            "cc": __email_list,
            "bcc": __email_list,
            "subject": {
                "type": "string",
                "title": "Message subject",
            },
            "attachment": one_or_more( 
                {
                    "type": "string",
                    "format": "valid_file",
                    "title": "File Attachment",
                },
            ),
            "inline": one_or_more( 
                {
                    "type": "string",
                    "format": "valid_file",
                    "title": "Attachment with inline disposition. Can be used to send inline images",
                }
            ),
            "tag": one_or_more(
                schema = {
                    "type": "string",
                    "format": "ascii",
                    "title": "Tag string",
                    "maxLength": 128,
                },
                max=3,
            ),
            "dkim": {
                "type": "boolean",
                "title": "Enables/ Disables DKIM signatures on per-message basis",
            },
            "deliverytime": {
                "type": "string",
                "format": "rfc2822",
                "title": "Desired time of delivery. Note: Messages can be scheduled for a maximum of 3 days in the future.",
            },
            "testmode": {
                "type": "boolean",
                "title": "Enables sending in test mode."
            },
            "tracking": {
                "type": "boolean",
                "title": "Toggles tracking on a per-message basis",
            },
            "tracking_clicks": {
                "type": ["string", "boolean"],
                "title": "Toggles clicks tracking on a per-message basis. Has higher priority than domain-level setting. Pass yes, no or htmlonly.",
            },
            "tracking_opens": {
                "type": "boolean",
                "title": "Toggles opens tracking on a per-message basis.",
            },
            "require_tls": {
                "type": "boolean",
                "title": "If set to True this requires the message only be sent over a TLS connection."
                "If a TLS connection cannot be esatblished, MailGun will not deliver the message. If set to False "
                "Mailgun will still try and upgrade the connection but if Mailgun can not the message will be delivered "
                "over a plaintext SMTP connection.",
            },
            "skip_verification": {
                "type": "boolean",
                "title": "If set to True, the certificate and hostname will not be verified when "
                "trying to establish a TLS connection and MailGun will accept any certificate",
            },
            "headers": {
                "type": "object",
                "additionalProperties": {"type": "string"},
                "title": "Any other header to add",
            },
            "data": {
                "type": "object",
                "additionalProperties": {"type": "object"},
                "title": "attach a custom JSON data to the message",
            },
        },
        "additionalProperties": False,
    }