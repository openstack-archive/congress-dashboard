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

from django.template.defaultfilters import linebreaksbr
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy
from horizon import exceptions
from horizon import messages
from horizon import tables
from openstack_dashboard import policy

from congress_dashboard.api import congress


LOG = logging.getLogger(__name__)


class CreateRule(tables.LinkAction):
    name = 'create_rule'
    verbose_name = _('Construct Rule')
    url = 'horizon:admin:policies:create_rule'
    classes = ('ajax-modal',)
    icon = 'plus'
    policy_rules = (('policy', 'create_rule'),)

    def get_link_url(self, datum=None):
        policy_name = self.table.kwargs['policy_name']
        return reverse(self.url, args=(policy_name,))


class CreateRawRule(tables.LinkAction):
    name = 'create_raw_rule'
    verbose_name = _('Enter Rule')
    url = 'horizon:admin:policies:create_raw_rule'
    classes = ('ajax-modal',)
    icon = 'plus'
    policy_rules = (('policy', 'create_raw_rule'),)

    def get_link_url(self, datum=None):
        policy_name = self.table.kwargs['policy_name']
        return reverse(self.url, args=(policy_name,))


class DeleteRule(policy.PolicyTargetMixin, tables.DeleteAction):
    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u'Delete Rule',
            u'Delete Rules',
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u'Deleted rule',
            u'Deleted rules',
            count
        )

    redirect_url = 'horizon:admin:policies:detail'

    def delete(self, request, obj_id):
        policy_name = self.table.kwargs['policy_name']
        LOG.info('User %s deleting policy "%s" rule "%s" in tenant %s',
                 request.user.username, policy_name, obj_id,
                 request.user.tenant_name)
        try:
            congress.policy_rule_delete(request, policy_name, obj_id)
            LOG.info('Deleted policy rule "%s"', obj_id)
        except Exception as e:
            msg_args = {'rule_id': obj_id, 'error': str(e)}
            msg = _('Failed to delete policy rule "%(rule_id)s": '
                    '%(error)s') % msg_args
            LOG.error(msg)
            messages.error(request, msg)
            redirect = reverse(self.redirect_url, args=(policy_name,))
            raise exceptions.Http302(redirect)


class PolicyRulesTable(tables.DataTable):
    id = tables.Column("id", verbose_name=_("Rule ID"))
    name = tables.Column("name", verbose_name=_("Name"))
    comment = tables.Column("comment", verbose_name=_("Comment"))
    rule = tables.Column("rule", verbose_name=_("Rule"),
                         filters=(congress.format_rule, linebreaksbr,))

    class Meta(object):
        name = "policy_rules"
        verbose_name = _("Rules")
        table_actions = (CreateRule, CreateRawRule, DeleteRule,)
        row_actions = (DeleteRule,)
        hidden_title = False


def get_policy_table_link(datum):
    return reverse('horizon:admin:policies:policy_table_detail',
                   args=(datum['policy_name'], datum['name']))


class PoliciesTablesTable(tables.DataTable):
    name = tables.Column("name", verbose_name=_("Table Name"),
                         link=get_policy_table_link)

    class Meta(object):
        name = "policies_tables"
        verbose_name = _("Policy Table Data")
        hidden_title = False
