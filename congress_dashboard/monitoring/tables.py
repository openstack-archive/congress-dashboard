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


class MonitoringTable(tables.DataTable):
    errors = tables.Column("error", verbose_name=_("Errors"))
    warnings = tables.Column("warning", verbose_name=_("Warnings"))
    policy_name = tables.Column("policy_name",
                                verbose_name=_("violated policy name"))
    policy_description = tables.Column("policy_description",
                                       verbose_name=_("Policy Description"))
    policy_owner_id = tables.Column("policy_owner_id",
                                    verbose_name=_("Policy Owner"))

    class Meta(object):
        name = "monitoring"
        verbose_name = _("Monitoring")
