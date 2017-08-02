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

from congress_dashboard.api import congress


LOG = logging.getLogger(__name__)


def _get_policy_tables(request):
    # Return all policy tables.
    all_tables = []
    try:
        # Get all the policies.
        policies = congress.policies_list(request)
    except Exception as e:
        LOG.error('Unable to get list of policies: %s', str(e))
    else:
        try:
            for policy in policies:
                # Get all the tables in this policy.
                policy_name = policy['name']
                policy_tables = congress.policy_tables_list(request,
                                                            policy_name)
                # Get the names of the tables.
                datasource_tables = []
                for table in policy_tables:
                    table.set_id_as_name_if_empty()
                    table_name = table['name']
                    # Exclude service-derived tables.
                    if congress.TABLE_SEPARATOR not in table_name:
                        datasource_tables.append(table['name'])

                all_tables.append({'datasource': policy_name,
                                   'tables': datasource_tables})
        except Exception as e:
            LOG.error('Unable to get tables for policy "%s": %s',
                      policy_name, str(e))
    return all_tables


def _get_policy_violations_tables(request):
    """Return error and warning tables info for all policies. """
    try:
        # Get all the policies.
        policies = congress.policies_list(request)
    except Exception as e:
        LOG.error('Unable to get list of policies: %s', str(e))
    else:
        try:
            tables_data = []
            for policy in policies:
                policy_name = policy['name']
                policy_table_info = {}
                error_warning_tables = []
                # Get all the tables in this policy.
                policy_tables = congress.policy_tables_list(request,
                                                            policy_name)
                for table in policy_tables:
                    table_name = table['id']
                    if congress.TABLE_SEPARATOR in table_name:
                        continue
                    if table_name == 'error' or table_name == 'warning':
                        policy_table_info['policy'] = policy
                        error_warning_tables.append(table_name)
                if error_warning_tables:
                    policy_table_info['tables'] = error_warning_tables
                    tables_data.append(policy_table_info)
        except Exception as e:
            LOG.error('Unable to get tables for policy "%s": %s',
                      policy_name, str(e))
    return tables_data


def get_policy_violations_data(request):
    """Get the row count of each error and warning tables. """
    tables_data = _get_policy_violations_tables(request)
    violations_table = []

    for data in tables_data:
        policy = data['policy']
        tables = data['tables']
        row = congress.PolicyTable({"id": policy['name']})
        row.set_id_as_name_if_empty()
        row.set_policy_details(policy)
        for t in tables:
            rows = congress.policy_rows_list(request, policy['name'], t)
            if len(rows) > 0:
                row.set_value(t, len(rows))
        if row.get('error') or row.get('warning'):
            violations_table.append(row)
    return violations_table


def _get_service_tables(request):
    # Return all service tables.
    all_tables = []
    try:
        # Get all the services.
        services = congress.datasources_list(request)
    except Exception as e:
        LOG.error('Unable to get list of data sources: %s', str(e))
    else:
        try:
            for service in services:
                # Get all the tables in this service.
                service_id = service['id']
                service_tables = congress.datasource_tables_list(request,
                                                                 service_id)
                # Get the names of the tables.
                datasource_tables = []
                for table in service_tables:
                    table.set_id_as_name_if_empty()
                    datasource_tables.append(table['name'])

                all_tables.append({'datasource': service['name'],
                                   'tables': datasource_tables})
        except Exception as e:
            LOG.error('Unable to get tables for data source "%s": %s',
                      service_id, str(e))
    return all_tables


def get_datasource_tables(request):
    """Get names of all data source tables.

    Example:
    [
        {
            'datasource': 'classification',
            'tables': ['error']
        },
        {
            'datasource': 'neutronv2'
            'tables': ['networks', 'ports', ...]
        },
        ...
    ]
    """
    tables = _get_policy_tables(request)
    tables.extend(_get_service_tables(request))
    return tables


def get_datasource_columns(request):
    """Get of names of columns from all data sources.

    Example:
    [
        {
            'datasource': 'classification',
            'tables': [
                {
                    'table': 'error',
                    'columns': ['name']
                }
            ]
        },
        {
            'datasource': 'neutronv2',
            'tables': [
                {
                    'table': 'networks',
                    'columns':  ['id', 'tenant_id', ...],
                },
                ...
            ],
            ...
        },
        ...
    ]
    """
    all_columns = []

    # Get all the policy tables.
    policy_tables = _get_policy_tables(request)
    try:
        for policy in policy_tables:
            # Get all the columns in this policy. Unlike for the services,
            # there's currently no congress client API to get the schema for
            # all tables in a policy in a single call.
            policy_name = policy['datasource']
            tables = policy['tables']

            datasource_tables = []
            for table_name in tables:
                # Get all the columns in this policy table.
                schema = congress.policy_table_schema_get(request, policy_name,
                                                          table_name)
                columns = [c['name'] for c in schema['columns']]
                datasource_tables.append({'table': table_name,
                                          'columns': columns})

            all_columns.append({'datasource': policy_name,
                                'tables': datasource_tables})
    except Exception as e:
        LOG.error('Unable to get schema for policy "%s" table "%s": %s',
                  policy_name, table_name, str(e))

    try:
        # Get all the services.
        services = congress.datasources_list(request)
    except Exception as e:
        LOG.error('Unable to get list of data sources: %s', str(e))
    else:
        try:
            for service in services:
                # Get the schema for this service.
                service_id = service['id']
                service_name = service['name']
                schema = congress.datasource_schema_get(request, service_id)

                datasource_tables = []
                for table in schema['tables']:
                    # Get the columns for this table.
                    columns = [c['name'] for c in table['columns']]
                    datasource_table = {'table': table['table_id'],
                                        'columns': columns}
                    datasource_tables.append(datasource_table)

                all_columns.append({'datasource': service_name,
                                    'tables': datasource_tables})
        except Exception as e:
            LOG.error('Unable to get schema for data source "%s": %s',
                      service_id, str(e))

    return all_columns
