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

from django.utils.translation import ugettext_lazy as _
from horizon import messages
from horizon import tables

import congress_dashboard.datasources.utils as ds_utils
from congress_dashboard.monitoring import tables as monitor_tables

LOG = logging.getLogger(__name__)


class IndexView(tables.DataTableView):
    """List policy violations."""
    table_class = monitor_tables.MonitoringTable
    template_name = 'admin/monitoring/index.html'

    def get_data(self):
        try:
            violations_data = ds_utils.get_policy_violations_data(self.request)
            return violations_data
        except Exception as e:
            msg = _('Unable to policy violations data: %s') % str(e)
            LOG.exception(msg)
            messages.error(self.request, msg)
            return []
