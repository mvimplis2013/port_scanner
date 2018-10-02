from ..core import Provider, Response
from ..utils import requests

class Slack(Provider):
    """ Send Slack webhook notifications """

    base_url = "https://hooks.slack.com/services"
    site_url = "https://api.slack.com/incoming-webhooks"

    name = "slack"

    __fields = {
        "type": "array",
        "title": "Fields are displayed in a table on the message",
        "minItems": 1,
        "items": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "title": "Required Field Title"},
                "value": {
                    "type": "string",
                    "title": "Text value of the field. May contain standard message markup and must"
                    " be escaped as normal. May be multi-line",                    
                },
                "short": {
                    "type": "boolean",
                    "title": "Optional flag indicating whether the `value` is short enough to be displayed"
                    " side-by-side with other values",
            },
            "required": ["title"],
            "additionalProperties": False,
        },
    }

    __attachments = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "title": "Attachment title",
                },
                "author_name": {
                    "type": "string",
                    "title": "Small text used to display the author's name",
                },
                "author_icon": {
                    "type": "string",
                    "title": "A valid URL that displays a small 16x16px image to the left of the author's name."
                    " Will only work if author_name is present",
                },
                "title_link": {
                    "type": "string",
                    "title": "Attachment title URL",
                },
                "image_url" {
                    "type": "string",
                    "format": "uri",
                    "title": "Thumbnail URL",
                },
                "footer": {
                    "type": "string",
                    "format": "timestamp"
                }
            }
        }
    }