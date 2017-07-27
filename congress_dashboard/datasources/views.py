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

import copy
import logging

from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from horizon import exceptions
from horizon import forms
from horizon import messages
from horizon import tables

from congress_dashboard.api import congress
from congress_dashboard.datasources import forms as datasource_forms
from congress_dashboard.datasources import tables as datasources_tables


logger = logging.getLogger(__name__)


class IndexView(tables.MultiTableView):
    """List service and policy defined data."""
    table_classes = (datasources_tables.DataSourcesTable,
                     datasources_tables.DataSourceStatusesTable, )
    template_name = 'admin/datasources/index.html'

    def get_datasources_list_data(self):
        try:
            datasources = congress.datasources_list(self.request)
            return datasources
        except Exception as e:
            msg = _('Unable to get data sources list: %s') % str(e)
            messages.error(self.request, msg)
            return []

    def get_service_status_data(self):
        ds = []
        try:
            ds = congress.datasource_statuses_list(self.request)
            logger.debug("ds status : %s " % ds)
        except Exception as e:
            msg = _('Unable to get data source status list: %s') % str(e)
            messages.error(self.request, msg)
        return ds


class DatasourceView(tables.DataTableView):
    template_name = 'admin/datasources/datasource_detail.html'
    table_class = datasources_tables.DataSourcesTablesTable

    def get_data(self):
        ds_id = self.kwargs['datasource_id']
        ds_temp = []
        try:
            ds_tables = congress.datasource_tables_list(self.request, ds_id)
            for table in ds_tables:
                table.set_value('datasource_id', ds_id)
                table.set_id_as_name_if_empty()
                # Object ids within a Horizon table must be unique. Otherwise,
                # Horizon will cache the column values for the object by id and
                # use the same column values for all rows with the same id.
                table.set_value('table_id', table['id'])
                table.set_value('id', '%s-%s' % (ds_id, table['table_id']))
                ds_temp.append(table)

            logger.debug("ds_temp %s" % ds_temp)
            return ds_temp
        except Exception as e:
            msg_args = {'ds_id': ds_id, 'error': str(e)}
            msg = _('Unable to get tables list for service "%(ds_id)s": '
                    '%(error)s') % msg_args
            messages.error(self.request, msg)
            return []

    def get_context_data(self, **kwargs):
        context = super(DatasourceView, self).get_context_data(**kwargs)
        datasource_id = self.kwargs['datasource_id']
        try:
            datasource = congress.datasource_get(self.request, datasource_id)
            status = congress.datasource_status_list(self.request,
                                                     datasource['name'])
            context['last_updated'] = status['last_updated']
            context['subscribers'] = status['subscribers']
            context['subscriptions'] = status['subscriptions']
            context['last_error'] = status['last_error']
            context['number_of_updates'] = status['number_of_updates']
            context['datasource_name'] = datasource['name']
            context['status'] = ('Active' if status['initialized']
                                 else 'Not Active')
            return context
        except Exception as e:
            msg_args = {'ds_id': datasource_id, 'error': str(e)}
            msg = _('Unable to get status for data source "%(ds_id)s": '
                    '%(error)s') % msg_args
            messages.error(self.request, msg)
            return []


class CreateView(forms.ModalFormView):
    form_class = datasource_forms.CreateDatasource
    template_name = 'admin/datasources/create.html'
    success_url = reverse_lazy('horizon:admin:datasources:index')


class DetailView(tables.DataTableView):
    """List details about and rows from a data source (service or policy)."""
    table_class = datasources_tables.DataSourceRowsTable
    template_name = 'admin/datasources/detail.html'

    def get_data(self):
        datasource_id = self.kwargs['datasource_id']
        table_name = self.kwargs.get('policy_table_name')
        is_service = False
        try:
            if table_name:
                # Policy data table.
                rows = congress.policy_rows_list(self.request, datasource_id,
                                                 table_name)
                if congress.TABLE_SEPARATOR in table_name:
                    table_name_parts = table_name.split(
                        congress.TABLE_SEPARATOR)
                    maybe_datasource_name = table_name_parts[0]
                    datasources = congress.datasources_list(self.request)
                    for datasource in datasources:
                        if datasource['name'] == maybe_datasource_name:
                            # Serivce-derived policy data table.
                            is_service = True
                            datasource_id = datasource['id']
                            table_name = table_name_parts[1]
                            break
            else:
                # Service data table.
                is_service = True
                datasource = congress.datasource_get_by_name(
                    self.request, datasource_id)
                table_name = self.kwargs['service_table_name']
                rows = congress.datasource_rows_list(
                    self.request, datasource_id, table_name)
        except Exception as e:
            msg_args = {
                'table_name': table_name,
                'ds_id': datasource_id,
                'error': str(e)
            }
            msg = _('Unable to get rows in table "%(table_name)s", data '
                    'source "%(ds_id)s": %(error)s') % msg_args
            messages.error(self.request, msg)
            redirect = reverse('horizon:admin:datasources:index')
            raise exceptions.Http302(redirect)

        # Normally, in Horizon, the columns for a table are defined as
        # attributes of the Table class. When the class is instantiated,
        # the columns are processed during the metaclass initialization. To
        # add columns dynamically, re-create the class from the metaclass
        # with the added columns, re-create the Table from the new class,
        # then reassign the Table stored in this View.
        column_names = []
        table_class_attrs = copy.deepcopy(dict(self.table_class.__dict__))
        # Get schema from the server.
        schema = {}
        try:
            if is_service:
                schema = congress.datasource_table_schema_get(
                    self.request, datasource_id, table_name)
            else:
                schema = congress.policy_table_schema_get(
                    self.request, datasource_id, table_name)
        except Exception as e:
            # Unable to get the schema, might be atomic rule, just display
            # without column names ...
            schema['columns'] = []

        row_len = 0
        if len(rows):
            row_len = len(rows[0].get('data', []))

        columns = schema['columns']
        if not row_len or row_len == len(columns):
            for col in columns:
                col_name = col['name']
                # Attribute name for column in the class must be a valid
                # identifier. Slugify it.
                col_slug = slugify(col_name)
                column_names.append(col_slug)
                table_class_attrs[col_slug] = tables.Column(
                    col_slug, verbose_name=col_name)
        else:
            # There could be another table with the same name and different
            # arity. Divide the rows into unnamed columns. Number them for
            # internal reference.
            for i in xrange(0, row_len):
                col_name = str(i)
                column_names.append(col_name)
                table_class_attrs[col_name] = tables.Column(
                    col_name, verbose_name='')

        # Class and object re-creation, using a new class name, the same base
        # classes, and the new class attributes, which now includes columns.
        columnized_table_class_name = '%s%sRows' % (
            slugify(datasource_id).title(), slugify(table_name).title())
        columnized_table_class = tables.base.DataTableMetaclass(
            str(columnized_table_class_name), self.table_class.__bases__,
            table_class_attrs)

        self.table_class = columnized_table_class
        columnized_table = columnized_table_class(self.request, **self.kwargs)
        self._tables[columnized_table_class._meta.name] = columnized_table

        # Map columns names to row values.
        num_cols = len(column_names)
        for row in rows:
            try:
                row_data = row['data']
                row.delete_by_key('data')
                for i in xrange(0, num_cols):
                    row.set_value(column_names[i], row_data[i])
            except Exception as e:
                msg_args = {
                    'table_name': table_name,
                    'ds_id': datasource_id,
                    'error': str(e)
                }
                msg = _('Unable to get data for table "%(table_name)s", data '
                        'source "%(ds_id)s": %(error)s') % msg_args
                messages.error(self.request, msg)
                redirect = reverse('horizon:admin:datasources:index')
                raise exceptions.Http302(redirect)
        return rows

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        if 'policy_table_name' in kwargs:
            table_name = kwargs.get('policy_table_name')
            context['datasource_type'] = _('Policy')
            datasource_name = kwargs['datasource_id']
        else:
            table_name = kwargs['service_table_name']
            context['datasource_type'] = _('Service')
            try:
                datasource_id = kwargs['datasource_id']
                datasource = congress.datasource_get(self.request,
                                                     datasource_id)
                datasource_name = datasource['name']
            except Exception as e:
                datasource_name = datasource_id
                logger.info('Failed to get data source "%s": %s' %
                            (datasource_id, str(e)))
        context['datasource_name'] = datasource_name
        context['table_name'] = table_name
        return context
