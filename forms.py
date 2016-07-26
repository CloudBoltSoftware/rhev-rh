import os
import requests

from django import forms

from utilities.exceptions import CloudBoltException
from resourcehandlers.forms import (
    BaseResourceHandlerCredentialsForm, BaseResourceHandlerSettingsForm,
)
from .models import RhevResourceHandler
from infrastructure.models import Environment

import ovirtsdk.api
import ovirtsdk.infrastructure
from ovirtsdk.infrastructure.errors import (
    RequestError,
    ConnectionError,
    UnsecuredConnectionAttemptError,
)
import ovirtsdk.xml


class RhevCredentialsForm(BaseResourceHandlerCredentialsForm):

    class Meta(BaseResourceHandlerCredentialsForm.Meta):
        model = RhevResourceHandler
        fields = ('protocol',) + BaseResourceHandlerCredentialsForm.Meta.fields

    protocol = forms.ChoiceField(
        label='Protocol',
        choices=(('https', 'HTTPS'), ('http', 'HTTP'),),
        required=True,
    )

    def clean(self):
        super(RhevCredentialsForm, self).clean()

        ip = self.cleaned_data.get('ip')
        protocol = self.cleaned_data.get('protocol')
        port = self.cleaned_data.get('port')
        serviceaccount = self.cleaned_data.get('serviceaccount')
        servicepasswd = self.cleaned_data.get('servicepasswd')
        # NOTE: If either of these is not set, the form will display
        # errors, because they have "required" set to True.

        if serviceaccount and servicepasswd:
            api_url = RhevResourceHandler.get_api_url(protocol, ip, port)
            cert_filename = RhevResourceHandler.get_cert_filename(ip, port)

            # download the cert file
            try:
                if not os.path.exists(RhevResourceHandler.cert_directory):
                    os.makedirs(RhevResourceHandler.cert_directory)
                response = requests.get(api_url + "/ca.crt", verify=False)
                with open(cert_filename, "w") as f:
                    f.write(response.text)
            except requests.RequestException:
                raise CloudBoltException(
                    "Could not obtain SSL certificate from {0}".format(ip))

            try:
                ovirtsdk.api.API(
                    url=api_url,
                    username=serviceaccount,
                    password=servicepasswd,
                    ca_file=cert_filename)
            except (RequestError, ConnectionError,
                    UnsecuredConnectionAttemptError):
                raise forms.ValidationError("Unable to connect to RHEV-M with"
                                            " the information provided.")

        return self.cleaned_data


class RhevSettingsForm(BaseResourceHandlerSettingsForm):

    class Meta(BaseResourceHandlerSettingsForm.Meta):
        model = RhevResourceHandler
        fields = (BaseResourceHandlerSettingsForm.Meta.fields
                  + ("clusterName",))

    clusterName = forms.CharField(label="Cluster name")
    environments = forms.ModelMultipleChoiceField(
        queryset=Environment.objects.exclude(name="Unassigned"),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        rh = kwargs.get("instance")
        super(RhevSettingsForm, self).__init__(*args, **kwargs)

        if rh:
            self.fields["environments"].initial = rh.environment_set.all()

    def save(self, *args, **kwargs):
        new_envs = self.cleaned_data["environments"]
        rh = super(RhevSettingsForm, self).save()

        rh.environment_set = new_envs

        return rh


class RhevQuickSetupSettingsForm(RhevSettingsForm):

    class Meta(RhevSettingsForm.Meta):
        model = RhevResourceHandler
        exclude = ('custom_fields', )
