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

from django.template.defaultfilters import linebreaksbr
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy
from horizon import tables

from congress_dashboard.api import congress


def get_policy_link(datum):
    return reverse('horizon:admin:library:detail', args=(datum['id'],))


class ActivatePolicy(tables.BatchAction):
    name = 'activate_policy'
    verbose_name = _('Activate')
    icon = 'plus'

    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Activate Policy",
            u"Activate Policy",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Activated Policy",
            u"Activated Policy",
            count
        )

    def action(self, request, obj_id):
        congress.policy_create(request, {}, obj_id)


class LibraryTable(tables.DataTable):
    id = tables.Column("id", verbose_name=_("Policy ID"), hidden=True,
                       sortable=False)
    name = tables.Column("name", verbose_name=_("Policy Name"),
                         link=get_policy_link)
    desc = tables.WrappingColumn("description", verbose_name=_("Description"),
                                 sortable=False)

    class Meta(object):
        name = "policy_library"
        verbose_name = _("Policy Library")
        row_actions = (ActivatePolicy, )
        hidden_title = True


class LibraryPolicyRulesTable(tables.DataTable):
    name = tables.Column("name", verbose_name=_("Rule Name"),
                         classes=('nowrap-col',))
    rule = tables.Column("rule", verbose_name=_("Rule"),
                         filters=(congress.format_rule, linebreaksbr,))
    comment = tables.WrappingColumn("comment", verbose_name=_("Comment"))

    class Meta(object):
        name = "policy_library_rules"
        verbose_name = _("Policy Rules")
        hidden_title = False
