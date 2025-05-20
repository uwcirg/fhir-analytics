import csv
import json
from fhirpathpy import evaluate
from typing import ClassVar 


def eval_first(resource, path):
    """fhirpath always returns a list - return first element from list if found"""
    result = evaluate(resource, path)
    return result[0] if result else None


class MedicationRequest:
    """Namespace class for parsing and generating CSV results for MediationRequest"""
    resource_type: ClassVar[str] = 'MedicationRequest'

    @staticmethod
    def csv_headers():
        return ("id", "subject", "medication.system", "medication.code", "medication.display")

    @staticmethod
    def csv_data(d):
        data = {
            "id": d.get("id"),
            "subject": eval_first(d, "subject.reference"),
            "medication.system": eval_first(d, "medicationCodeableConcept.coding[0].system"),
            "medication.code": eval_first(d, "medicationCodeableConcept.coding[0].code"),
            "medication.display": eval_first(d, "medicationCodeableConcept.coding[0].display"),
        }
        assert tuple(data.keys()) == MedicationRequest.csv_headers()
        return data


class Patient:
    """Namespace class for parsing and generating CSV results for Patient"""
    resource_type: ClassVar[str] = 'Patient'

    @staticmethod
    def csv_headers():
        return ("id", "given", "family", "birthDate")

    def csv_data(d):
        data = {
            "id": d.get("id"),
            "given": eval_first(d, "name.given.first()"),
            "family": eval_first(d, "name.family.first()"),
            "birthDate": d.get("birthDate"),
        }
        assert tuple(data.keys()) == Patient.csv_headers()
        return data


class QuestionnaireResponse():
    """Namespace class for parsing and generating CSV results for Patient"""
    resource_type: ClassVar[str] = 'QuestionnaireResponse'

    @staticmethod
    def csv_headers():
        return ("id", "subject", "authored", "questionnaire", "status")

    @staticmethod
    def csv_data(d):
        data = {
            "id": d.get("id"),
            "subject": eval_first(d, "subject.reference"),
            "authored": d.get("authored"),
            "questionnaire": d.get("questionnaire").split('/')[-1],
            "status": d.get("status"),
        }
        assert tuple(data.keys()) == QuestionnaireResponse.csv_headers()
        return data


for resource_type in (MedicationRequest, Patient, QuestionnaireResponse):
    rows = []
    with open(f"data/fhir/cosri-demo/{resource_type.resource_type}.ndjson", "r", encoding="utf-8") as f:
        for line in f:
            data = json.loads(line)

            if hasattr(resource_type, 'normalize'):
                data = resource_type.normalize(data)
            rows.append(resource_type.csv_data(data))

    with open(f"output/{resource_type.resource_type}.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=resource_type.csv_headers())
        writer.writeheader()
        writer.writerows(rows)

