# Copyright 2015 VMware.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import logging

from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from horizon import exceptions
from horizon import forms
from horizon import messages

from congress_dashboard.api import congress


LOG = logging.getLogger(__name__)


class CreateDatasource(forms.SelfHandlingForm):
    name = forms.CharField(max_length=255,
                           label=_("Data Source Name"),
                           help_text='Name of the data source')

    driver = forms.ThemableChoiceField(label=_("Driver"),
                                       help_text='Data Source driver')

    description = forms.CharField(label=_("Description"),
                                  required=False,
                                  help_text='Data Source Description')
    username = forms.CharField(
        max_length=255,
        label=_("UserName"),
        help_text='username to connect to the driver service')

    password = forms.CharField(widget=forms.PasswordInput(render_value=False),
                               label=_('Password'))

    tenant_name = forms.CharField(max_length=255, label=_("Project Name"))

    # TODO(ramineni): support adding lazy tables
    # lazy_tables = forms.CharField(max_length=255, label=_("Lazy Tables"))
    auth_url = forms.URLField(max_length=255, label=_("Keystone Auth URL"))
    poll_time = forms.IntegerField(
        label=_("Poll Interval (in seconds)"),
        help_text='periodic interval congress needs to poll data')

    failure_url = 'horizon:admin:datasources:index'

    @classmethod
    def _instantiate(cls, request, *args, **kwargs):
        return cls(request, *args, **kwargs)

    def __init__(self, request, *args, **kwargs):
        super(CreateDatasource, self).__init__(request, *args, **kwargs)
        driver_choices = [('', _("Select a Driver"))]
        drivers = congress.supported_driver_list(request)
        driver_choices.extend(drivers)
        self.fields['driver'].choices = driver_choices

    def handle(self, request, data):
        datasource_name = data['name']
        datasource_description = data.get('description')
        datasource_driver = data.pop('driver')
        config = {
            'username': data['username'],
            'password': data['password'],
            'tenant_name': data['tenant_name'],
            'auth_url': data['auth_url'],
            'poll_time': data['poll_time']
        }
        try:
            params = {
                'name': datasource_name,
                'driver': datasource_driver,
                'description': datasource_description,
                'config': config
            }
            datasource = congress.create_datasource(request, params)
            msg = _('Created Data Source "%s"') % datasource_name
            LOG.info(msg)
            messages.success(request, msg)
        except Exception as e:
            msg_args = {'datasource_name': datasource_name, 'error': str(e)}
            msg = _('Failed to create data source "%(datasource_name)s": '
                    '%(error)s') % msg_args
            LOG.error(msg)
            messages.error(self.request, msg)
            redirect = reverse(self.failure_url)
            raise exceptions.Http302(redirect)
        return datasource
