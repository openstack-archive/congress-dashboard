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

from django.utils.translation import ugettext_lazy as _
from horizon import tables


class LibraryTable(tables.DataTable):
    id = tables.Column("id", verbose_name=_("Policy ID"), hidden=True,
                       sortable=False)
    name = tables.Column("name", verbose_name=_("Policy Name"))
    desc = tables.WrappingColumn("description", verbose_name=_("Description"),
                                 sortable=False)

    class Meta(object):
        name = "policy_library"
        verbose_name = _("Policy Library")
        hidden_title = True
