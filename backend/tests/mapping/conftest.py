import json
from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"
EXPECTED_DIR = Path(__file__).parent / "expected"


def load_fixture(filename: str) -> dict:
    with open(FIXTURES_DIR / filename) as f:
        return json.load(f)


def load_expected(filename: str) -> dict:
    with open(EXPECTED_DIR / filename) as f:
        return json.load(f)


@pytest.fixture
def patient_r4():
    return load_fixture("patient_r4.json")


@pytest.fixture
def encounter_r4():
    return load_fixture("encounter_r4.json")


@pytest.fixture
def condition_r4():
    return load_fixture("condition_r4.json")


@pytest.fixture
def procedure_r4():
    return load_fixture("procedure_r4.json")


@pytest.fixture
def observation_vitals_r4():
    return load_fixture("observation_vitals_r4.json")


@pytest.fixture
def observation_labs_r4():
    return load_fixture("observation_labs_r4.json")


@pytest.fixture
def medication_request_r4():
    return load_fixture("medication_request_r4.json")


@pytest.fixture
def medication_dispense_r4():
    return load_fixture("medication_dispense_r4.json")


@pytest.fixture
def immunization_r4():
    return load_fixture("immunization_r4.json")


@pytest.fixture
def patient_r5():
    return load_fixture("patient_r5.json")


@pytest.fixture
def encounter_r5():
    return load_fixture("encounter_r5.json")


@pytest.fixture
def edge_cases_r4():
    return load_fixture("edge_cases_r4.json")
