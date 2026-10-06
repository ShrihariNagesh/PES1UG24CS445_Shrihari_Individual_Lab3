# 5. AI-Generated Code: Vaccination Core Engine

**Problem Statement #17** | Shrihari Nagesh | PES1UG24CS445

## How this code was produced

The code in this folder was generated with an AI coding assistant (**Claude**), then run and tested.
It has **not** been run through GitHub Copilot, so this folder holds no Copilot screenshots.

To add GitHub Copilot evidence: open this folder in VS Code, paste the prompts from section 4 into
Copilot Chat one at a time, and save screenshots of the prompt, the generated code and the passing
tests in a `screenshots/` folder here.

## 1. Files

| File | What it is |
|---|---|
| `vaccination_core_engine.py` | Business rules for FR-001 to FR-007. Standard library only |
| `test_vaccination_core_engine.py` | 15 unit tests (TC-01 to TC-15) |

The engine is the rule layer only. It has no web server, no database and no user interface.

## 2. What the engine covers

| Requirement | Function | Tests |
|---|---|---|
| FR-001 Dose interval lock | `days_until_eligible()`, `book_slot()` | TC-01, TC-02 |
| FR-002 Registration and cohort | `register_citizen()`, `assign_cohort()` | TC-03, TC-04, TC-05 |
| FR-003 Search and booking | `search_slots()`, `book_slot()` | TC-06, TC-07, TC-08 |
| FR-004 Dose recording | `record_dose()` | TC-10, TC-11 |
| FR-005 Certificate generation | `generate_certificate()` | TC-12, TC-13 |
| FR-006 Certificate verification | `verify_certificate()` | TC-14 |
| FR-007 Booking confirmation | `book_slot()` adds to `outbox` | TC-09 |
| NFR-001 Verification speed | `CertificateSigner` | TC-15 (local timing only) |

Not covered: PDF export of the certificate (FR-005), the 24-hour reminder (FR-007), encryption and
access control (NFR-002), and load behaviour (NFR-003). Those need a deployed system.

**Signature note.** The prototype signs with HMAC-SHA256 from the standard library. A real
deployment would use an asymmetric signature (for example Ed25519), so that offline verifiers hold
only the public key and the private key stays inside the Certificate Service.

## 3. Jira defects covered in code

Each defect logged in the bug tracker (`Bug_BPS#17`) has a comment at the line that prevents it and
a test that would fail if it returned. Jira status is as of the Lab 2 bug report.

| Jira key | Defect | Root cause in the report | Guard in the engine | Test |
|---|---|---|---|---|
| BBPS-1 | Dose 2 bookable on day 27 | Off-by-one in the interval comparison | Block while `gap < 28` | TC-01 |
| BBPS-2 | Comorbidity flag ignored | Flag not passed to the rule | `age >= 60 or has_comorbidity` | TC-04 |
| BBPS-3 | Last seat booked twice | Check and decrement not atomic | Both steps under one lock | TC-07 |
| BBPS-4 | Empty batch number saved | Missing required-field check | Blank batch raises `ValidationError` | TC-10 |
| BBPS-5 | Certificate before final dose | Trigger checked "at least one dose" | Requires dose count equal to required doses | TC-12 |
| BBPS-6 | Verification slow under load | Key looked up on every request | Key prepared once and reused | TC-15 (partial) |
| BBPS-7 | Health data in plaintext | Endpoint served over plain HTTP | Not an engine change (deployment setting) | none |

## 4. Prompts to reproduce this in GitHub Copilot

**Prompt 1: data model**
> Create a Python module using only the standard library for a vaccination scheduling system. Add
> dataclasses for Citizen, Slot, Booking and DoseRecord, and a VaccinationSystem class that stores
> them in dictionaries. Add exception classes ValidationError, EligibilityError and CapacityError.

**Prompt 2: registration and cohort (FR-002, BBPS-2)**
> Add register_citizen(name, age, gov_id, has_comorbidity, occupation). Reject blank names, ages
> under 18 and duplicate IDs. Assign a cohort: healthcare or frontline occupation is phase 1, age 60
> or above or any comorbidity is phase 2, everyone else is phase 3. The comorbidity flag must be
> used.

**Prompt 3: dose interval and booking (FR-001, FR-003, BBPS-1, BBPS-3)**
> Add book_slot(citizen_id, slot_id). Refuse if the citizen's cohort is not open. Refuse Dose 2 when
> the slot date is fewer than 28 days after Dose 1, so day 27 is blocked and day 28 is allowed. Check
> capacity and increase the booked count inside one threading.Lock so the last seat cannot be given
> twice.

**Prompt 4: dose recording (FR-004, BBPS-4)**
> Add record_dose(officer_id, booking_id, vaccine_brand, batch_number, administered_on). Reject a
> blank batch number. Move the citizen status from "Slot Booked" to "Dose Administered".

**Prompt 5: certificate (FR-005, FR-006, BBPS-5, BBPS-6)**
> Add a CertificateSigner class that signs a JSON payload with HMAC-SHA256 and verifies it with
> hmac.compare_digest. Prepare the key once and reuse it. Generate a certificate only when the number
> of recorded doses equals the required doses. The payload holds the citizen ID and the dose dates.

**Prompt 6: tests**
> Write unittest tests for every rule above, including day 27 and day 28, comorbidity, a full slot,
> 20 threads competing for one seat, a blank batch number, a certificate requested after one dose,
> and a tampered certificate.

## 5. How to run

```bash
cd 5-Github_Copilot_Generated_Code
python vaccination_core_engine.py                       # short demo
python -m unittest test_vaccination_core_engine -v      # 15 tests
```

Test result:

```text
test_tc01_dose2_blocked_on_day_27 ... ok
test_tc02_dose2_allowed_on_day_28 ... ok
test_tc03_cohort_by_age_and_occupation ... ok
test_tc04_comorbidity_gives_priority_cohort ... ok
test_tc05_invalid_registrations_rejected ... ok
test_tc06_booking_uses_capacity_and_full_slot_rejected ... ok
test_tc07_last_seat_taken_only_once_under_concurrency ... ok
test_tc08_closed_cohort_cannot_book ... ok
test_tc09_booking_confirmation_is_queued ... ok
test_tc10_empty_batch_number_rejected ... ok
test_tc11_status_moves_to_dose_administered ... ok
test_tc12_no_certificate_before_final_dose ... ok
test_tc13_certificate_issued_after_final_dose ... ok
test_tc14_tampered_or_garbage_certificate_rejected ... ok
test_tc15_verification_is_fast_and_reuses_the_key ... ok
----------------------------------------------------------------------
Ran 15 tests in 0.042s
OK
```
