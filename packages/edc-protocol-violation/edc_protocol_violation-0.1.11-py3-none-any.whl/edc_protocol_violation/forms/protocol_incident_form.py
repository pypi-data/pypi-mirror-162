from django import forms
from edc_action_item.forms import ActionItemFormMixin
from edc_form_validators import FormValidatorMixin
from edc_sites.forms import SiteModelFormMixin

from ..form_validators import ProtocolIncidentFormValidator
from ..models import ProtocolIncident


class ProtocolIncidentForm(
    SiteModelFormMixin, FormValidatorMixin, ActionItemFormMixin, forms.ModelForm
):

    form_validator_cls = ProtocolIncidentFormValidator

    class Meta(ActionItemFormMixin.Meta):
        model = ProtocolIncident
        fields = "__all__"
