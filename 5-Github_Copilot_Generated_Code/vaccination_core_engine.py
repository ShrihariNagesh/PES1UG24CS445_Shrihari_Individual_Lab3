"""Core engine for the Vaccination Cohort & Dose Scheduling System.

Problem Statement #17 (Healthcare & Telemedicine)
Shrihari Nagesh, PES1UG24CS445

This module holds the business rules only (no web server, no database):

    FR-001  dose-interval enforcement
    FR-002  citizen registration and cohort assignment
    FR-003  centre search and slot booking within capacity
    FR-004  officer check-in and dose recording
    FR-005  signed QR certificate after the final dose
    FR-006  certificate verification
    FR-007  booking confirmation notifications

Each rule that had a defect logged in the Jira bug tracker (BBPS-1 to BBPS-6)
is marked with the bug key next to the line that fixes it.

Standard library only. Run the tests with:
    python -m unittest test_vaccination_core_engine -v
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import threading
from dataclasses import dataclass, field
from datetime import date
from typing import Dict, List, Optional, Tuple

# --------------------------------------------------------------------------
# Rules that a Health Authority Admin would configure
# --------------------------------------------------------------------------

MIN_AGE = 18
SENIOR_AGE = 60
MIN_INTERVAL_DAYS = 28          # minimum gap between Dose 1 and Dose 2
REQUIRED_DOSES = 2

COHORT_PHASE_1 = "PHASE_1_HEALTHCARE_FRONTLINE"
COHORT_PHASE_2 = "PHASE_2_SENIOR_OR_COMORBID"
COHORT_PHASE_3 = "PHASE_3_GENERAL_ADULT"

PRIORITY_OCCUPATIONS = {"HEALTHCARE", "FRONTLINE"}

STATUS_REGISTERED = "Registered"
STATUS_SLOT_BOOKED = "Slot Booked"
STATUS_DOSE_ADMINISTERED = "Dose Administered"
STATUS_FULLY_VACCINATED = "Fully Vaccinated"


class VaccinationError(Exception):
    """Base class for every rule violation raised by the engine."""


class ValidationError(VaccinationError):
    """Input is missing or malformed."""


class EligibilityError(VaccinationError):
    """The citizen is not allowed to do this yet."""


class CapacityError(VaccinationError):
    """The slot has no seats left."""


# --------------------------------------------------------------------------
# Data records
# --------------------------------------------------------------------------

@dataclass
class Citizen:
    citizen_id: str
    name: str
    age: int
    has_comorbidity: bool
    occupation: str
    cohort: str
    status: str = STATUS_REGISTERED


@dataclass
class Slot:
    slot_id: str
    centre_id: str
    centre_name: str
    pincode: str
    slot_date: date
    capacity: int
    booked: int = 0

    @property
    def remaining(self) -> int:
        return self.capacity - self.booked


@dataclass
class Booking:
    booking_id: str
    citizen_id: str
    slot_id: str
    dose_number: int
    slot_date: date
    administered: bool = False


@dataclass
class DoseRecord:
    citizen_id: str
    dose_number: int
    vaccine_brand: str
    batch_number: str
    administered_on: date
    officer_id: str


@dataclass
class Notification:
    citizen_id: str
    message: str


# --------------------------------------------------------------------------
# Certificate signing (kept in its own class, like the Certificate Service)
# --------------------------------------------------------------------------

class CertificateSigner:
    """Signs and verifies certificate payloads.

    The secret key never leaves this class, which mirrors the architecture:
    only the Certificate Service can sign.

    Prototype note: this uses HMAC-SHA256 from the standard library. A real
    deployment would use an asymmetric signature (for example Ed25519) so
    that offline verifiers hold only the public key.
    """

    def __init__(self, secret_key: bytes):
        if len(secret_key) < 16:
            raise ValidationError("signing key must be at least 16 bytes")
        self._secret_key = secret_key
        # BBPS-6: the key object is prepared once and reused for every
        # verification instead of being looked up on each request.
        self._cached_mac = hmac.new(self._secret_key, digestmod=hashlib.sha256)
        self.key_loads = 1

    def _sign(self, body: bytes) -> str:
        mac = self._cached_mac.copy()
        mac.update(body)
        return mac.hexdigest()

    def encode(self, data: dict) -> str:
        """Return the text that goes inside the QR code."""
        body = json.dumps(data, sort_keys=True, separators=(",", ":")).encode()
        token = base64.urlsafe_b64encode(body).decode() + "." + self._sign(body)
        return token

    def decode(self, qr_payload: str) -> Tuple[bool, Optional[dict]]:
        """Return (is_valid, data). Data is None when the check fails."""
        try:
            body_b64, signature = qr_payload.rsplit(".", 1)
            body = base64.urlsafe_b64decode(body_b64.encode())
        except (ValueError, TypeError):
            return False, None
        if not hmac.compare_digest(self._sign(body), signature):
            return False, None
        return True, json.loads(body)


# --------------------------------------------------------------------------
# The engine
# --------------------------------------------------------------------------

@dataclass
class VaccinationSystem:
    signer: CertificateSigner
    open_cohorts: set = field(default_factory=lambda: {COHORT_PHASE_1})
    citizens: Dict[str, Citizen] = field(default_factory=dict)
    slots: Dict[str, Slot] = field(default_factory=dict)
    bookings: Dict[str, Booking] = field(default_factory=dict)
    dose_records: Dict[str, List[DoseRecord]] = field(default_factory=dict)
    certificates: Dict[str, str] = field(default_factory=dict)
    outbox: List[Notification] = field(default_factory=list)

    def __post_init__(self):
        self._gov_ids: set = set()
        self._booking_lock = threading.Lock()
        self._counter = 0

    def _next_id(self, prefix: str) -> str:
        self._counter += 1
        return f"{prefix}-{self._counter:04d}"

    # ---------------------------------------------------------------- FR-002
    @staticmethod
    def assign_cohort(age: int, has_comorbidity: bool, occupation: str) -> str:
        """Pick the earliest cohort the citizen qualifies for."""
        if occupation.upper() in PRIORITY_OCCUPATIONS:
            return COHORT_PHASE_1
        # BBPS-2: the comorbidity flag is part of the rule, not only the age.
        if age >= SENIOR_AGE or has_comorbidity:
            return COHORT_PHASE_2
        return COHORT_PHASE_3

    def register_citizen(self, name: str, age: int, gov_id: str,
                         has_comorbidity: bool = False,
                         occupation: str = "OTHER") -> Citizen:
        if not name or not name.strip():
            raise ValidationError("name is required")
        if not isinstance(age, int) or isinstance(age, bool) or not 0 < age < 130:
            raise ValidationError("age must be a whole number between 1 and 129")
        if age < MIN_AGE:
            raise EligibilityError(f"citizens under {MIN_AGE} are not eligible")
        if not gov_id or not gov_id.strip():
            raise ValidationError("government ID is required")
        if gov_id in self._gov_ids:
            raise ValidationError("a profile already exists for this ID")

        citizen = Citizen(
            citizen_id=self._next_id("CIT"),
            name=name.strip(),
            age=age,
            has_comorbidity=bool(has_comorbidity),
            occupation=occupation.upper(),
            cohort=self.assign_cohort(age, has_comorbidity, occupation),
        )
        self._gov_ids.add(gov_id)
        self.citizens[citizen.citizen_id] = citizen
        self.dose_records[citizen.citizen_id] = []
        return citizen

    def open_cohort(self, cohort: str) -> None:
        """Rollout control: start vaccinating another cohort."""
        self.open_cohorts.add(cohort)

    # ---------------------------------------------------------------- FR-003
    def add_slot(self, centre_id: str, centre_name: str, pincode: str,
                 slot_date: date, capacity: int) -> Slot:
        if capacity <= 0:
            raise ValidationError("capacity must be positive")
        slot = Slot(self._next_id("SLOT"), centre_id, centre_name, pincode,
                    slot_date, capacity)
        self.slots[slot.slot_id] = slot
        return slot

    def search_slots(self, pincode: str, slot_date: date) -> List[Slot]:
        """Slots at centres in this pincode on this date that still have seats."""
        return [s for s in self.slots.values()
                if s.pincode == pincode and s.slot_date == slot_date
                and s.remaining > 0]

    # ---------------------------------------------------------------- FR-001
    def next_dose_number(self, citizen_id: str) -> int:
        return len(self.dose_records[citizen_id]) + 1

    def days_until_eligible(self, citizen_id: str, on_date: date) -> int:
        """0 when the citizen may take the next dose on on_date."""
        records = self.dose_records[citizen_id]
        if not records:
            return 0
        gap = (on_date - records[-1].administered_on).days
        # BBPS-1: the booking is blocked while the gap is LESS THAN the
        # minimum. Day 27 is blocked, day 28 is allowed.
        if gap < MIN_INTERVAL_DAYS:
            return MIN_INTERVAL_DAYS - gap
        return 0

    def book_slot(self, citizen_id: str, slot_id: str) -> Booking:
        citizen = self._get_citizen(citizen_id)
        slot = self.slots.get(slot_id)
        if slot is None:
            raise ValidationError("unknown slot")

        if citizen.cohort not in self.open_cohorts:
            raise EligibilityError("this cohort is not open for booking yet")

        dose_number = self.next_dose_number(citizen_id)
        if dose_number > REQUIRED_DOSES:
            raise EligibilityError("all required doses are already recorded")
        if any(b.citizen_id == citizen_id and not b.administered
               for b in self.bookings.values()):
            raise EligibilityError("citizen already has an open booking")

        wait = self.days_until_eligible(citizen_id, slot.slot_date)
        if wait > 0:
            raise EligibilityError(
                f"Dose {dose_number} is locked for {wait} more day(s): the "
                f"minimum interval is {MIN_INTERVAL_DAYS} days")

        # BBPS-3: check and decrement happen together under one lock, so two
        # citizens can never both take the last seat.
        with self._booking_lock:
            if slot.booked >= slot.capacity:
                raise CapacityError("this slot is full")
            slot.booked += 1
            booking = Booking(self._next_id("BKG"), citizen_id, slot_id,
                              dose_number, slot.slot_date)
            self.bookings[booking.booking_id] = booking

        citizen.status = STATUS_SLOT_BOOKED
        # FR-007: confirmation goes to the notification outbox.
        self.outbox.append(Notification(
            citizen_id,
            f"Dose {dose_number} booked at {slot.centre_name} on "
            f"{slot.slot_date.isoformat()}"))
        return booking

    # ---------------------------------------------------------------- FR-004
    def record_dose(self, officer_id: str, booking_id: str, vaccine_brand: str,
                    batch_number: str, administered_on: date) -> DoseRecord:
        if not officer_id or not officer_id.strip():
            raise ValidationError("officer ID is required")
        booking = self.bookings.get(booking_id)
        if booking is None:
            raise ValidationError("unknown booking")
        if booking.administered:
            raise ValidationError("this booking has already been used")
        if not vaccine_brand or not vaccine_brand.strip():
            raise ValidationError("vaccine brand is required")
        # BBPS-4: a dose can never be saved without a batch number.
        if not batch_number or not batch_number.strip():
            raise ValidationError("batch number is required")

        citizen = self._get_citizen(booking.citizen_id)
        record = DoseRecord(citizen.citizen_id, booking.dose_number,
                            vaccine_brand.strip(), batch_number.strip(),
                            administered_on, officer_id.strip())
        self.dose_records[citizen.citizen_id].append(record)
        booking.administered = True
        citizen.status = STATUS_DOSE_ADMINISTERED

        if len(self.dose_records[citizen.citizen_id]) == REQUIRED_DOSES:
            citizen.status = STATUS_FULLY_VACCINATED
            self.generate_certificate(citizen.citizen_id)
        return record

    # ---------------------------------------------------------------- FR-005
    def generate_certificate(self, citizen_id: str) -> str:
        citizen = self._get_citizen(citizen_id)
        records = self.dose_records[citizen_id]
        # BBPS-5: the certificate needs ALL required doses, not just one.
        if len(records) != REQUIRED_DOSES:
            raise EligibilityError(
                f"certificate needs {REQUIRED_DOSES} doses, "
                f"{len(records)} recorded")
        qr_payload = self.signer.encode({
            "citizen_id": citizen.citizen_id,
            "name": citizen.name,
            "doses": [{"dose": r.dose_number, "date": r.administered_on.isoformat(),
                       "brand": r.vaccine_brand, "batch": r.batch_number}
                      for r in records],
        })
        self.certificates[citizen_id] = qr_payload
        return qr_payload

    # ---------------------------------------------------------------- FR-006
    def verify_certificate(self, qr_payload: str) -> Tuple[bool, Optional[dict]]:
        """Check a scanned QR payload. Works without any database lookup."""
        return self.signer.decode(qr_payload)

    # ------------------------------------------------------------------ misc
    def _get_citizen(self, citizen_id: str) -> Citizen:
        citizen = self.citizens.get(citizen_id)
        if citizen is None:
            raise ValidationError("unknown citizen")
        return citizen


def demo() -> None:
    """Walk one citizen through the whole flow and print each step."""
    system = VaccinationSystem(CertificateSigner(b"demo-key-not-for-production"))
    nurse = system.register_citizen("Asha Rao", 34, "ID-1001", occupation="healthcare")
    print(f"Registered {nurse.name}: cohort {nurse.cohort}")

    first = system.add_slot("C1", "Jayanagar PHC", "560041", date(2026, 9, 1), 2)
    booking = system.book_slot(nurse.citizen_id, first.slot_id)
    system.record_dose("OFF-7", booking.booking_id, "Covaxin", "B-221", date(2026, 9, 1))
    print(f"Dose 1 recorded, status: {nurse.status}")

    early = system.add_slot("C1", "Jayanagar PHC", "560041", date(2026, 9, 28), 2)
    try:
        system.book_slot(nurse.citizen_id, early.slot_id)
    except EligibilityError as err:
        print(f"Day 27 booking blocked: {err}")

    on_time = system.add_slot("C1", "Jayanagar PHC", "560041", date(2026, 9, 29), 2)
    booking = system.book_slot(nurse.citizen_id, on_time.slot_id)
    system.record_dose("OFF-7", booking.booking_id, "Covaxin", "B-305", date(2026, 9, 29))
    print(f"Dose 2 recorded, status: {nurse.status}")

    qr = system.certificates[nurse.citizen_id]
    valid, data = system.verify_certificate(qr)
    print(f"Certificate valid: {valid}, doses on record: {len(data['doses'])}")
    valid, _ = system.verify_certificate(qr[:-1] + ("0" if qr[-1] != "0" else "1"))
    print(f"Tampered certificate valid: {valid}")


if __name__ == "__main__":
    demo()
