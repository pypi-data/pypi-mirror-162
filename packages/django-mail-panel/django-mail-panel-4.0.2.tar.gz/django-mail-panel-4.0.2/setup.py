# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mail_panel']

package_data = \
{'': ['*'],
 'mail_panel': ['static/debug_toolbar/mail/*', 'templates/mail_panel/*']}

install_requires = \
['django-debug-toolbar>=1.0']

setup_kwargs = {
    'name': 'django-mail-panel',
    'version': '4.0.2',
    'description': 'A panel for django-debug-toolbar that allows for viewing of recently sent email.',
    'long_description': '\n## Django Debug Toolbar - Mail Panel\n\n[![Build Status](https://secure.travis-ci.org/scuml/django-mail-panel.png?branch=master)](http://travis-ci.org/scuml/django-mail-panel)\n\n![](https://cloud.githubusercontent.com/assets/1790447/9289964/6aa7c4ba-434e-11e5-8594-3bb3efd0cd81.png)\n\n\nTesting and debugging e-mail while developing a Django app has never been pleasant.  Sending e-mail to a file-based backend requires a user to click through obtusely-named files and does not provide a way to preview rendered HTML.  Sending e-mail to a valid mailbox incurs a delay as the message is processed though a mail server, and clutters a developer\'s inbox.\n\nThe mail panel attempts to address these problems by providing a way to preview emails within the browser using [django-debug-toolbar](https://github.com/jazzband/django-debug-toolbar).\n\nThis mail panel is released under the Apache license. If you like it, please consider contributing!\n\nSpecial thanks to @ShawnMilo for the code review.\n\n\nInstallation\n============\n\nTo install the mail panel, first install this package with `pip install django-mail-panel`.  Then add the `mail_panel` app after `debug_toolbar`to the `INSTALLED_APPS` setting:\n\n```python\nINSTALLED_APPS = (\n    ...\n    \'debug_toolbar\',\n    \'mail_panel\',\n)\n```\n\nand add the panel `DEBUG_TOOLBAR_PANELS`:\n\n```python\nDEBUG_TOOLBAR_PANELS = (\n    ...\n    \'mail_panel.panels.MailToolbarPanel\',\n)\n```\n\n\nCollect static and you\'ll be good to go.\n\n```bash\n./manage.py collectstatic\n```\n\n\nConfiguration\n=============\n\nAfter installation, you now need to redirect mail to the mail toolbar.  Change your email backend to the following:\n\n```python\nEMAIL_BACKEND = \'mail_panel.backend.MailToolbarBackend\'\n```\n\n**Important:** This plugin uses Django\'s cache backend to store messages.  If you are using `DummyCache`, the mail panel will use a local memory cache, and will reset messages when the server is restarted.\n\n\n**[Optional]** \nBy default, mail toolbar stores messages for one day before removing them from cache.  You can change this with the following setting:\n\n```python\nMAIL_TOOLBAR_TTL = 86400  # 1 Day\n```\n\n**[Optional]**\nIf you use the `DEBUG_TOOLBAR_PANELS` to custom order your panels:\n\n```python\n    DEBUG_TOOLBAR_PANELS = [\n        "debug_toolbar.panels.history.HistoryPanel",\n        "debug_toolbar.panels.versions.VersionsPanel",\n        "debug_toolbar.panels.timer.TimerPanel",\n        "debug_toolbar.panels.settings.SettingsPanel",\n        "debug_toolbar.panels.headers.HeadersPanel",\n        "debug_toolbar.panels.request.RequestPanel",\n        "debug_toolbar.panels.sql.SQLPanel",\n        "debug_toolbar.panels.staticfiles.StaticFilesPanel",\n        "debug_toolbar.panels.templates.TemplatesPanel",\n        "debug_toolbar.panels.cache.CachePanel",\n        "debug_toolbar.panels.signals.SignalsPanel",\n        "debug_toolbar.panels.logging.LoggingPanel",\n        "debug_toolbar.panels.redirects.RedirectsPanel",\n        "debug_toolbar.panels.profiling.ProfilingPanel",\n        "mail_panel.panels.MailToolbarPanel",  # reposition to desired location\n    ]\n```\n\n\n\nTesting\n=======\n\nTo preview emails sent from your test suite, add the email backend override to your tests with the following:\n\n```python\nfrom django.test.utils import override_settings\n\n@override_settings(EMAIL_BACKEND=\'mail_panel.backend.MailToolbarBackend\')\ndef test_send_email(self):\n    # your code here\n```\n\n\nThe backend works similarly to the standard email backend and code should not need to be reworked when using the MailToolbarBackend.\n\n\n```python\nfrom django.core import mail\n\noriginal_outbox = len(mail.outbox)\n# Send mail ...\nassert(len(mail.outbox) == original_outbox + 1)\n```\n\nShameless Plugs\n=======\nLike Django Mail Panel?  Be sure to check out and support these other tools for Mac that will improve your workflow:\n\n**[Kubermagic](https://echodot.com/kubermagic/)** - Automate, and script away tedious kubectl commands with Kubermagic; a UI for developers, QA teams, and those starting to learn the ins-and-outs of Kubernetes.     \n\n\n**[Red](https://echodot.com/red/)** - A visual and interactive Redis client, featuring live updating keys, an interactive console, pub/sub, lua script support and much more.\n',
    'author': 'Stephen Mitchell',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/scuml/django-mail-panel',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
