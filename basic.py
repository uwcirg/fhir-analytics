import csv
from fhir.resources.codeableconcept import CodeableConcept as BaseCC
from fhir.resources.extension import Extension
from fhir.resources.medicationrequest import MedicationRequest as BaseMR
from fhir.resources.patient import Patient as BasePatient
import json
from pydantic import ConfigDict, Field
from typing import ClassVar, List, Optional, Union


class CodeableConcept(BaseCC):
    extension: Optional[List[Extension]] = Field(default=None)

    # necessary to avoid validation errors with `extensions`
    model_config = ConfigDict(extra="allow")


class MedicationRequest(BaseMR):
    """Specialize MedicationRequest for csv generation"""
    resource_type: ClassVar[str] = 'MedicationRequest'

    # override medication to allow extensions w/i codeableConcepts
    medication: Optional[Union[CodeableConcept, dict]] = Field(default=None)

    @staticmethod
    def csv_headers():
        return ("id", "subject", "medication.system", "medication.code", "medication.display")

    def csv_data(self):
        data = {
            "id": self.id or "",
            "subject": self.subject.reference,
            "medication.system": self.medication.codeableConcept["coding"][0]["system"],
            "medication.code": self.medication.codeableConcept["coding"][0]["code"],
            "medication.display": self.medication.codeableConcept["coding"][0]["display"],
        }
        assert tuple(data.keys()) == MedicationRequest.csv_headers()
        return data


    @staticmethod
    def normalize(data):
        '''Return data (dict) normalized to FHIR spec'''
        # HAPI flatens medication request - convert to FHIR compliant if necessary
        if "medicationCodeableConcept" in data:
            data["medication"] = {
                "codeableConcept": data.pop("medicationCodeableConcept")
            }

        # Add in any missing required fields, using default values
        if "status" not in data:
            data["status"] = "active"
        if "intent" not in data:
            data["intent"] = "order"
        return data


class Patient(BasePatient):
    """Specialize Patient for csv generation"""
    resource_type: ClassVar[str] = 'Patient'

    @staticmethod
    def csv_headers():
        return ("id", "given", "family", "birthDate")

    def csv_data(self):
        data = {
            "id": self.id if self.id else "",
            "given": (self.name[0].given[0] if self.name else ""),
            "family": (self.name[0].family if self.name else ""),
            "birthDate": self.birthDate or "",
        }
        assert tuple(data.keys()) == Patient.csv_headers()
        return data


# TODO: expand to remaining list of requested resources
for resource_type in (Patient, MedicationRequest):
    rows = []
    with open(f"data/fhir/cosri-demo/{resource_type.resource_type}.ndjson", "r", encoding="utf-8") as f:
        for line in f:
            data = json.loads(line)
            if hasattr(resource_type, 'normalize'):
                data = resource_type.normalize(data)
            resource = resource_type.model_validate(data)
            rows.append(resource.csv_data())

    with open(f"output/{resource_type.resource_type}.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=resource_type.csv_headers())
        writer.writeheader()
        writer.writerows(rows)

