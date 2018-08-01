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
import uuid

from django.utils.translation import ugettext_lazy as _
from horizon import messages
from horizon import tables

from congress_dashboard.api import congress
from congress_dashboard.library import tables as library_tables

LOG = logging.getLogger(__name__)


class IndexView(tables.DataTableView):
    """List policies from library."""
    table_class = library_tables.LibraryTable
    template_name = 'admin/library/index.html'

    def get_data(self):
        try:
            policies = congress.list_policies_from_library(self.request,
                                                           include_rules=False)
            return policies
        except Exception as e:
            msg = _('Unable to list library policies: %s') % str(e)
            LOG.exception(msg)
            messages.error(self.request, msg)
            return []


class DetailView(tables.DataTableView):
    """List details about and rules in a policy."""
    table_class = library_tables.LibraryPolicyRulesTable
    template_name = 'admin/library/detail.html'

    def get_data(self):
        try:
            policy_id = self.kwargs['policy_name']
            rules = congress.show_library_policy(self.request,
                                                 policy_id)['rules']
            for r in rules:
                head = r['rule'].split(congress.RULE_SEPARATOR)[0]
                name = (head.split('(')[0]).replace('_', ' ').title()
                name = name.split('[')[0]
                r.set_value('name', name)
                r.set_id_if_empty(uuid.uuid4())
            return rules
        except Exception as e:
            msg = _('Unable to list rules of library policy: %s') % str(e)
            LOG.exception(msg)
            messages.error(self.request, msg)
            return []

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        try:
            policy_id = self.kwargs['policy_name']
            policy = congress.show_library_policy(self.request, policy_id,
                                                  include_rules=False)
            context['policy'] = policy
            return context
        except Exception as e:
            margs = {'id': policy_id, 'error': str(e)}
            msg = _('Unable to get library policy %(id)s: %(error)s') % margs
            LOG.exception(msg)
            messages.error(self.request, msg)
            return []
