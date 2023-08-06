from edc_protocol_violation.action_items import (
    ProtocolDeviationViolationAction as BaseProtocolDeviationViolationAction,
)
from edc_protocol_violation.action_items import (
    ProtocolIncidentAction as BaseProtocolIncidentAction,
)


class ProtocolDeviationViolationAction(BaseProtocolDeviationViolationAction):

    reference_model = "edc_protocol_violation.protocoldeviationviolation"
    admin_site_name = "edc_protocol_violation"


class ProtocolIncidentAction(BaseProtocolIncidentAction):

    reference_model = "edc_protocol_violation.protocolincident"
    admin_site_name = "edc_protocol_violation"
