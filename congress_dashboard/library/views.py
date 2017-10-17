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

from congress_dashboard.api import congress
from congress_dashboard.library import tables as library_tables

LOG = logging.getLogger(__name__)


class IndexView(tables.DataTableView):
    """List policies from library."""
    table_class = library_tables.LibraryTable
    template_name = 'admin/library/index.html'

    def get_data(self):
        try:
            policies = congress.list_policies_from_library(self.request)
            return policies
        except Exception as e:
            msg = _('Unable to list library policies: %s') % str(e)
            LOG.exception(msg)
            messages.error(self.request, msg)
            return []
