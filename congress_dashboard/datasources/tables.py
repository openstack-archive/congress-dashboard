# Copyright 2014 VMware.
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

from django.template.defaultfilters import unordered_list
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy
from horizon import tables

from congress_dashboard.api import congress


def get_resource_url(obj):
    return reverse('horizon:admin:datasources:datasource_table_detail',
                   args=(obj['datasource_id'], obj['table_id']))


class DataSourcesTablesTable(tables.DataTable):
    name = tables.Column("name", verbose_name=_("Table Name"),
                         link=get_resource_url)

    class Meta(object):
        name = "datasources_tables"
        verbose_name = _("Service Data")
        hidden_title = False


class DataSourceRowsTable(tables.DataTable):
    class Meta(object):
        name = "datasource_rows"
        verbose_name = _("Rows")
        hidden_title = False


class CreateDatasource(tables.LinkAction):
    name = 'create_datasource'
    verbose_name = _('Create Data Source')
    url = 'horizon:admin:datasources:create'
    classes = ('ajax-modal',)
    icon = 'plus'


class DeleteDatasource(tables.DeleteAction):
    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Delete Data Source",
            u'Deleted Data Sources',
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u'Deleted Data Source',
            u'Deleted Data Sources',
            count
        )

    redirect_url = 'horizon:admin:datasources:index'

    def delete(self, request, name):
        congress.delete_datasource(request, name)


class DataSourcesTable(tables.DataTable):
    name = tables.Column("name", verbose_name=_("Data Source Name"),
                         link='horizon:admin:datasources:datasource_detail')
    enabled = tables.Column("enabled", verbose_name=_("Enabled"))
    driver = tables.Column("driver", verbose_name=_("Driver"))
#   config = tables.Column("config", verbose_name=_("Config"))

    class Meta(object):
        name = "datasources_list"
        verbose_name = _("Data Sources")
        hidden_title = False
        table_actions = (CreateDatasource, DeleteDatasource)
        row_actions = (DeleteDatasource, )


class DataSourceStatusesTable(tables.DataTable):
    datasource_name = tables.Column("service",
                                    verbose_name=_("Service"))
    last_updated = tables.Column("last_updated",
                                 verbose_name=_("Last Updated"))
    subscriptions = tables.Column("subscriptions",
                                  verbose_name=_("Subscriptions"),
                                  wrap_list=True, filters=(unordered_list,))
    last_error = tables.Column("last_error", verbose_name=_("Last Error"))
    subscribers = tables.Column("subscribers", verbose_name=_("Subscribers"),
                                wrap_list=True, filters=(unordered_list,))
    initialized = tables.Column("initialized", verbose_name=_("Initialized"))
    number_of_updates = tables.Column("number_of_updates",
                                      verbose_name=_("Number of Updates"))

    class Meta(object):
        name = "service_status"
        verbose_name = _("Service Status")
        hidden_title = False
