#!/usr/bin/env bash
# load_synthetic_fhir.sh — Load synthetic FHIR R4 resources into HAPI FHIR server
set -euo pipefail

FHIR_URL="${FHIR_URL:-http://localhost:8080/fhir}"

echo "=== Loading synthetic FHIR data into $FHIR_URL ==="

# Use PUT to control resource IDs so references work

echo "[1/9] Creating Patient pat-001..."
curl -s -X PUT "$FHIR_URL/Patient/pat-001" \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "Patient",
    "id": "pat-001",
    "name": [{"family": "TestSmith", "given": ["Jane"]}],
    "gender": "female",
    "birthDate": "1985-07-23",
    "address": [{"city": "Springfield", "state": "IL", "postalCode": "62701"}],
    "identifier": [{"system": "urn:oid:2.16.840.1.113883.4.1", "value": "SYNTH-001"}]
  }' | python3 -c "import sys,json; r=json.load(sys.stdin); print(f'  -> {r[\"resourceType\"]}/{r.get(\"id\",\"?\")}')"

echo "[2/9] Creating Patient pat-002..."
curl -s -X PUT "$FHIR_URL/Patient/pat-002" \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "Patient",
    "id": "pat-002",
    "name": [{"family": "TestDoe", "given": ["John"]}],
    "gender": "male",
    "birthDate": "1972-03-15",
    "deceasedDateTime": "2025-01-10",
    "address": [{"city": "Chicago", "state": "IL", "postalCode": "60601"}]
  }' | python3 -c "import sys,json; r=json.load(sys.stdin); print(f'  -> {r[\"resourceType\"]}/{r.get(\"id\",\"?\")}')"

echo "[3/9] Creating Practitioner..."
curl -s -X PUT "$FHIR_URL/Practitioner/prac-001" \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "Practitioner",
    "id": "prac-001",
    "name": [{"family": "DrHouse", "given": ["Gregory"]}],
    "identifier": [{"system": "http://hl7.org/fhir/sid/us-npi", "value": "1234567890"}]
  }' | python3 -c "import sys,json; r=json.load(sys.stdin); print(f'  -> {r[\"resourceType\"]}/{r.get(\"id\",\"?\")}')"

echo "[4/9] Creating Encounter..."
curl -s -X PUT "$FHIR_URL/Encounter/enc-001" \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "Encounter",
    "id": "enc-001",
    "status": "finished",
    "class": {"system": "http://terminology.hl7.org/CodeSystem/v3-ActCode", "code": "AMB", "display": "ambulatory"},
    "subject": {"reference": "Patient/pat-001"},
    "period": {"start": "2025-06-15T09:00:00Z", "end": "2025-06-15T10:30:00Z"},
    "participant": [{"individual": {"reference": "Practitioner/prac-001"}}]
  }' | python3 -c "import sys,json; r=json.load(sys.stdin); print(f'  -> {r[\"resourceType\"]}/{r.get(\"id\",\"?\")}')"

echo "[5/9] Creating Condition..."
curl -s -X PUT "$FHIR_URL/Condition/cond-001" \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "Condition",
    "id": "cond-001",
    "subject": {"reference": "Patient/pat-001"},
    "encounter": {"reference": "Encounter/enc-001"},
    "code": {"coding": [{"system": "http://hl7.org/fhir/sid/icd-10-cm", "code": "E11.9", "display": "Type 2 diabetes mellitus without complications"}]},
    "onsetDateTime": "2020-03-01",
    "clinicalStatus": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/condition-clinical", "code": "active"}]}
  }' | python3 -c "import sys,json; r=json.load(sys.stdin); print(f'  -> {r[\"resourceType\"]}/{r.get(\"id\",\"?\")}')"

echo "[6/9] Creating Observation (Vital Signs)..."
curl -s -X PUT "$FHIR_URL/Observation/obs-vital-001" \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "Observation",
    "id": "obs-vital-001",
    "status": "final",
    "category": [{"coding": [{"system": "http://terminology.hl7.org/CodeSystem/observation-category", "code": "vital-signs", "display": "Vital Signs"}]}],
    "code": {"coding": [{"system": "http://loinc.org", "code": "85354-9", "display": "Blood pressure panel"}]},
    "subject": {"reference": "Patient/pat-001"},
    "encounter": {"reference": "Encounter/enc-001"},
    "effectiveDateTime": "2025-06-15T09:15:00Z",
    "component": [
      {"code": {"coding": [{"system": "http://loinc.org", "code": "8480-6", "display": "Systolic BP"}]}, "valueQuantity": {"value": 128, "unit": "mmHg"}},
      {"code": {"coding": [{"system": "http://loinc.org", "code": "8462-4", "display": "Diastolic BP"}]}, "valueQuantity": {"value": 82, "unit": "mmHg"}}
    ]
  }' | python3 -c "import sys,json; r=json.load(sys.stdin); print(f'  -> {r[\"resourceType\"]}/{r.get(\"id\",\"?\")}')"

echo "[7/9] Creating Observation (Lab Result - HbA1c)..."
curl -s -X PUT "$FHIR_URL/Observation/obs-lab-001" \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "Observation",
    "id": "obs-lab-001",
    "status": "final",
    "category": [{"coding": [{"system": "http://terminology.hl7.org/CodeSystem/observation-category", "code": "laboratory", "display": "Laboratory"}]}],
    "code": {"coding": [{"system": "http://loinc.org", "code": "4548-4", "display": "Hemoglobin A1c"}]},
    "subject": {"reference": "Patient/pat-001"},
    "encounter": {"reference": "Encounter/enc-001"},
    "effectiveDateTime": "2025-06-15T09:30:00Z",
    "valueQuantity": {"value": 7.2, "unit": "%", "system": "http://unitsofmeasure.org", "code": "%"}
  }' | python3 -c "import sys,json; r=json.load(sys.stdin); print(f'  -> {r[\"resourceType\"]}/{r.get(\"id\",\"?\")}')"

echo "[8/9] Creating MedicationRequest..."
curl -s -X PUT "$FHIR_URL/MedicationRequest/medrx-001" \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "MedicationRequest",
    "id": "medrx-001",
    "status": "active",
    "intent": "order",
    "subject": {"reference": "Patient/pat-001"},
    "encounter": {"reference": "Encounter/enc-001"},
    "medicationCodeableConcept": {"coding": [{"system": "http://www.nlm.nih.gov/research/umls/rxnorm", "code": "860975", "display": "Metformin 500 MG Oral Tablet"}]},
    "authoredOn": "2025-06-15",
    "requester": {"reference": "Practitioner/prac-001"}
  }' | python3 -c "import sys,json; r=json.load(sys.stdin); print(f'  -> {r[\"resourceType\"]}/{r.get(\"id\",\"?\")}')"

echo "[9/9] Creating Immunization..."
curl -s -X PUT "$FHIR_URL/Immunization/imm-001" \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "Immunization",
    "id": "imm-001",
    "status": "completed",
    "vaccineCode": {"coding": [{"system": "http://hl7.org/fhir/sid/cvx", "code": "208", "display": "COVID-19 mRNA Vaccine"}]},
    "patient": {"reference": "Patient/pat-001"},
    "occurrenceDateTime": "2025-01-15",
    "performer": [{"actor": {"reference": "Practitioner/prac-001"}}]
  }' | python3 -c "import sys,json; r=json.load(sys.stdin); print(f'  -> {r[\"resourceType\"]}/{r.get(\"id\",\"?\")}')"

echo ""
echo "=== Verifying loaded data ==="
for rt in Patient Practitioner Encounter Condition Observation MedicationRequest Immunization; do
  count=$(curl -s "$FHIR_URL/$rt?_summary=count" | python3 -c "import sys,json; print(json.load(sys.stdin).get('total',0))")
  echo "  $rt: $count"
done

echo ""
echo "=== Done! Synthetic FHIR data loaded successfully ==="
