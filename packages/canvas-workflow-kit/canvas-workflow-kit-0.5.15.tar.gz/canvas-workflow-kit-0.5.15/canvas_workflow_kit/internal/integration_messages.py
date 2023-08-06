from typing import Any, Dict

def ensure_patient_in_group(patient_key: str, group_externally_exposable_id: str) -> Dict[str, Any]:
    
    return {
        'integration_type': 'PatientGroup',
        'integration_source': 'SDK',
        'handling_options': {
            'respond_async': True
        },
        'integration_payload': {
            'externally_exposable_id': group_externally_exposable_id,
            'group_type': 'person',
            'members': {
                'mode': 'appendOrRemove',
                'entries': [{
                    'uuid': patient_key,
                }]
            }
        }
    }

def ensure_patient_not_in_group(patient_key: str, group_externally_exposable_id: str) -> str:
    return {
        'integration_type': 'PatientGroup',
        'integration_source': 'SDK',
        'handling_options': {
            'respond_async': True
        },
        'integration_payload': {
            'externally_exposable_id': group_externally_exposable_id,
            'group_type': 'person',
            'members': {
                'mode': 'appendOrRemove',
                'entries': [{
                    'uuid': patient_key,
                    'inactive': True
                }]
            }
        }
    }
    