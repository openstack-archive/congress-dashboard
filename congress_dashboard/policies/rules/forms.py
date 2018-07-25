# Copyright 2017 NEC, Corp
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


class CreateRawRule(forms.SelfHandlingForm):
    rule = forms.CharField(label=_("Rule"),
                           widget=forms.Textarea(attrs={'rows': 5}))
    rule_name = forms.CharField(max_length=255, label=_("Rule Name"),
                                required=False)
    comment = forms.CharField(max_length=255, label=_("Description"),
                              required=False)
    failure_url = 'horizon:admin:policies:detail'

    def __init__(self, request, *args, **kwargs):
        super(CreateRawRule, self).__init__(request, *args, **kwargs)
        initial = kwargs.get('initial', {})
        policy_name = initial.get('policy_name')
        self.fields['policy_name'] = forms.CharField(widget=forms.HiddenInput,
                                                     initial=policy_name)

    def handle(self, request, data):
        rule_name = data['rule_name']
        comment = data['comment']
        rule = data['rule']
        policy_name = data['policy_name']
        try:
            params = {
                'name': rule_name,
                'comment': comment,
                'rule': rule,
            }

            rule = congress.policy_rule_create(request, policy_name,
                                               body=params)
            msg = _("Rule created with id %s") % rule['id']
            LOG.info(msg)
            messages.success(request, msg)
            return rule
        except Exception as e:
            msg = _('Error creating rule : %s') % str(e)
            LOG.error(msg)
            messages.error(self.request, msg)
            redirect = reverse(self.failure_url, args=(policy_name,))
            raise exceptions.Http302(redirect)
