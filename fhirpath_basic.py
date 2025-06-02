import csv
import json
from fhirpathpy import evaluate
from typing import ClassVar 

input_path = "data/fhir/cosri-demo"
output = "output"


def eval_first(resource, path):
    """fhirpath always returns a list - return first element from list if found"""
    result = evaluate(resource, path)
    return result[0] if result else None


def parse_subject(data):
    """remove common Patient/ portion of reference as requested"""
    reference = eval_first(data, "subject.reference")
    pat = "Patient/"
    if reference.startswith(pat):
        return reference[len(pat):]
    return reference


class MedicationRequest:
    """Namespace class for parsing and generating CSV results for MediationRequest"""
    resource_type: ClassVar[str] = 'MedicationRequest'

    @staticmethod
    def csv_headers():
        return ("MedicationRequest.id", "Patient.id", "authoredOn", "medication.system", "medication.code", "medication.display")

    @staticmethod
    def csv_data(d):
        data = {
            "MedicationRequest.id": d.get("id"),
            "Patient.id": parse_subject(d),
            "authoredOn": d.get("authoredOn"),
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
        return ("Patient.id", "given", "family", "birthDate")

    def csv_data(d):
        data = {
            "Patient.id": d.get("id"),
            "given": eval_first(d, "name.given.first()"),
            "family": eval_first(d, "name.family.first()"),
            "birthDate": d.get("birthDate"),
        }
        assert tuple(data.keys()) == Patient.csv_headers()
        return data


class Procedure:
    """Namespace class for parsing and generating CSV results for Procedure"""
    resource_type: ClassVar[str] = 'Procedure'

    @staticmethod
    def csv_headers():
        return ("Procedure.id", "Patient.id", "performedDateTime", "status", "code.system", "code.code", "code.display", "code.text")

    def csv_data(d):
        data = {
            "Procedure.id": d.get("id"),
            "Patient.id": parse_subject(d),
            "performedDateTime": d.get("performedDateTime"),
            "status": d.get("status"),
            "code.system": eval_first(d, "code.coding.first().system"),
            "code.code": eval_first(d, "code.coding.first().code"),
            "code.display": eval_first(d, "code.coding.first().display"),
            "code.text": eval_first(d, "code.text"),
        }
        assert tuple(data.keys()) == Procedure.csv_headers()
        return data


class Questionnaire:
    """Namespace class for parsing and generating CSV results for Questionnaire"""
    resource_type: ClassVar[str] = 'Questionnaire'

    @staticmethod
    def csv_headers():
        return ("Questionnaire.id", "title", "linkId", "text")

    @staticmethod
    def questionnaire_items(q):
        items = evaluate(q, "item")
        for item in items:
            linkId = item.get("linkId")
            text = item.get("text")
            yield linkId, text


    @staticmethod
    def csv_data(d):
        rows = []
        for linkId, text in Questionnaire.questionnaire_items(d):
            data = {
                "Questionnaire.id": d.get("id"),
                "title": d.get("title"),
                "linkId": linkId,
                "text": text,
            }
            rows.append(data)
        assert tuple(data.keys()) == Questionnaire.csv_headers()
        return rows


class QuestionnaireResponse():
    """Namespace class for parsing and generating CSV results for Patient"""
    resource_type: ClassVar[str] = 'QuestionnaireResponse'

    @staticmethod
    def csv_headers():
        return ("QuestionnaireResponse.id", "Patient.id", "session", "authored", "questionnaire", "status", "linkId", "answer.code", "answer.text")

    @staticmethod
    def questionnaire_items(qr):
        items = evaluate(qr, "item")
        for item in items:
            linkId = eval_first(item, "linkId")
            answer_code = eval_first(item, "answer.first().valueCoding.code")
            answer_text = eval_first(item, "answer.first().valueCoding.display")
            yield linkId, answer_code, answer_text

    @staticmethod
    def csv_data(d):
        rows = []
        for linkId, answer_code, answer_text in QuestionnaireResponse.questionnaire_items(d):
            data = {
                "QuestionnaireResponse.id": d.get("id"),
                "Patient.id": parse_subject(d),
                "session": eval_first(d, "identifier.value"),
                "authored": d.get("authored"),
                "questionnaire": d.get("questionnaire").split('/')[-1],
                "status": d.get("status"),
                "linkId": linkId,
                "answer.code": answer_code,
                "answer.text": answer_text,
            }
            assert tuple(data.keys()) == QuestionnaireResponse.csv_headers()
            rows.append(data)
        return rows


for resource_type in (MedicationRequest, Patient, Procedure, Questionnaire, QuestionnaireResponse):
    print(f"Processing {resource_type.resource_type}...")
    rows = []
    with open(f"{input_path}/{resource_type.resource_type}.ndjson", "r", encoding="utf-8") as f:
        for line in f:
            data = json.loads(line)

            if hasattr(resource_type, 'normalize'):
                data = resource_type.normalize(data)

            results = resource_type.csv_data(data)
            # Some types return multiple rows, i.e. QuestionnaireResponse
            if isinstance(results, list):
                for row in results:
                    rows.append(row)
            else:
                rows.append(results)

    with open(f"{output}/{resource_type.resource_type}.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=resource_type.csv_headers())
        writer.writeheader()
        writer.writerows(rows)

print(f"Process complete, see {output} directory")
