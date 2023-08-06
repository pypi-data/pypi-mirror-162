# coding: utf-8

import json

import requests
from sentry.plugins.bases.notify import NotificationPlugin

import sentry_feishu
from .forms import FeiShuOptionsForm

FeiShuTalk_API = "https://open.feishu.cn/open-apis/bot/v2/hook/{token}"


class FeiShuPlugin(NotificationPlugin):
    """
    Sentry plugin to send error counts to FeiShu.
    """
    author = 'chengpeng'
    author_url = 'https://github.com/chengandpeng/sentry_feishu'
    version = sentry_feishu.VERSION
    description = 'Send error counts to FeiShu.'
    resource_links = [
        ('Source', 'https://github.com/chengandpeng/sentry_feishu'),
    ]

    slug = 'FeiShu'
    title = 'FeiShu'
    conf_key = slug
    conf_title = title
    project_conf_form = FeiShuOptionsForm

    def is_configured(self, project):
        """
        Check if plugin is configured.
        """
        return bool(self.get_option('access_token', project))

    def notify_users(self, group, event, *args, **kwargs):
        self.post_process(group, event, *args, **kwargs)

    def post_process(self, group, event, *args, **kwargs):
        """
        Process error.
        """
        if not self.is_configured(group.project):
            return

        if group.is_ignored():
            return

        access_token = self.get_option('access_token', group.project)
        send_url = FeiShuTalk_API.format(token=access_token)
        project = event.group.project
        title = event.title.encode("utf-8").decode("utf-8")
        project_name = project.get_full_name().encode("utf-8").decode("utf-8")
        device = event.get_tag('device')
        level = group.get_level_display().upper()

        data = {
            "msg_type": "interactive",
            "card": {
                "header": {
                    "title": {
                        "content": "【Sentry Alert】 {project_name}".format(project_name=project_name),
                        "tag": "plain_text"
                    }
                },
                "elements": [
                    {
                        "tag": "div",
                        "text": {
                            "content": "**Title:** {title}\n**Level:** {level}\n**Device:** {device}\n**Message:** {message}\n".format(title=title, level=level, device=device, message=event.message),
                            "tag": "lark_md"
                        }
                    },
                    {
                        "actions": [
                            {
                                "tag": "button",
                                "text": {
                                    "content": "查看详情",
                                    "tag": "lark_md"
                                },
                                "url": u"{}events/{}/".format(group.get_absolute_url(), event.event_id),
                                "type": "normal"
                            }
                        ],
                        "tag": "action"
                    }
                ],
            }
        }
        requests.post(
            send_url,
            json=data
        )
