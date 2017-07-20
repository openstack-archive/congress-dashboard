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

from django.core.urlresolvers import reverse
from horizon import forms
from horizon import workflows

from congress_dashboard.policies.rules import forms as rule_forms
from congress_dashboard.policies.rules import workflows as rule_workflows


class CreateView(workflows.WorkflowView):
    workflow_class = rule_workflows.CreateRule
    ajax_template_name = 'admin/policies/rules/create.html'
    success_url = 'horizon:admin:policies:detail'

    def get_success_url(self):
        return reverse(self.success_url,
                       args=(self.kwargs['policy_name'],))

    def get_initial(self):
        return {'policy_name': self.kwargs['policy_name']}


class CreateRawView(forms.ModalFormView):
    form_class = rule_forms.CreateRawRule
    template_name = 'admin/policies/rules/create_raw.html'
    success_url = 'horizon:admin:policies:detail'

    def get_context_data(self, **kwargs):
        context = super(CreateRawView, self).get_context_data(**kwargs)
        context["policy_name"] = self.kwargs['policy_name']
        return context

    def get_initial(self):
        initial = super(CreateRawView, self).get_initial()
        initial.update({'policy_name': self.kwargs['policy_name']})
        return initial

    def get_success_url(self):
        return reverse(self.success_url,
                       args=(self.kwargs['policy_name'],))
