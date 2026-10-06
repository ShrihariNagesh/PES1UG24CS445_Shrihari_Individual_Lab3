"""Unit tests for vaccination_core_engine.py.

Each test names the requirement it checks and, where one exists, the Jira bug
it guards against (BBPS-1 to BBPS-6).

Run:  python -m unittest test_vaccination_core_engine -v
"""

import threading
import time
import unittest
from datetime import date, timedelta

from vaccination_core_engine import (
    COHORT_PHASE_1, COHORT_PHASE_2, COHORT_PHASE_3,
    STATUS_DOSE_ADMINISTERED, STATUS_FULLY_VACCINATED, STATUS_SLOT_BOOKED,
    CapacityError, CertificateSigner, EligibilityError, ValidationError,
    VaccinationSystem,
)

DAY_0 = date(2026, 9, 1)


def new_system() -> VaccinationSystem:
    system = VaccinationSystem(CertificateSigner(b"unit-test-signing-key"))
    system.open_cohort(COHORT_PHASE_2)
    system.open_cohort(COHORT_PHASE_3)
    return system


def give_first_dose(system: VaccinationSystem, citizen_id: str) -> None:
    slot = system.add_slot("C1", "Centre One", "560041", DAY_0, 10)
    booking = system.book_slot(citizen_id, slot.slot_id)
    system.record_dose("OFF-1", booking.booking_id, "Covaxin", "B-100", DAY_0)


class DoseIntervalTests(unittest.TestCase):
    """FR-001"""

    def setUp(self):
        self.system = new_system()
        self.citizen = self.system.register_citizen("Ravi", 40, "ID-1")
        give_first_dose(self.system, self.citizen.citizen_id)

    def test_tc01_dose2_blocked_on_day_27(self):
        """FR-001 / BBPS-1: a slot 27 days after Dose 1 must be refused."""
        slot = self.system.add_slot("C1", "Centre One", "560041",
                                    DAY_0 + timedelta(days=27), 10)
        with self.assertRaises(EligibilityError):
            self.system.book_slot(self.citizen.citizen_id, slot.slot_id)
        self.assertEqual(slot.booked, 0)

    def test_tc02_dose2_allowed_on_day_28(self):
        """FR-001: a slot exactly 28 days after Dose 1 is accepted."""
        slot = self.system.add_slot("C1", "Centre One", "560041",
                                    DAY_0 + timedelta(days=28), 10)
        booking = self.system.book_slot(self.citizen.citizen_id, slot.slot_id)
        self.assertEqual(booking.dose_number, 2)


class CohortTests(unittest.TestCase):
    """FR-002"""

    def setUp(self):
        self.system = new_system()

    def test_tc03_cohort_by_age_and_occupation(self):
        """FR-002: occupation and age decide the cohort."""
        nurse = self.system.register_citizen("Asha", 30, "ID-1", occupation="healthcare")
        senior = self.system.register_citizen("Mohan", 67, "ID-2")
        adult = self.system.register_citizen("Kiran", 25, "ID-3")
        self.assertEqual(nurse.cohort, COHORT_PHASE_1)
        self.assertEqual(senior.cohort, COHORT_PHASE_2)
        self.assertEqual(adult.cohort, COHORT_PHASE_3)

    def test_tc04_comorbidity_gives_priority_cohort(self):
        """FR-002 / BBPS-2: the comorbidity flag must not be ignored."""
        citizen = self.system.register_citizen("Lata", 35, "ID-4", has_comorbidity=True)
        self.assertEqual(citizen.cohort, COHORT_PHASE_2)

    def test_tc05_invalid_registrations_rejected(self):
        """FR-002: under-age, duplicate ID and blank name are refused."""
        self.system.register_citizen("Ravi", 40, "ID-5")
        with self.assertRaises(EligibilityError):
            self.system.register_citizen("Child", 12, "ID-6")
        with self.assertRaises(ValidationError):
            self.system.register_citizen("Copy", 40, "ID-5")
        with self.assertRaises(ValidationError):
            self.system.register_citizen("  ", 40, "ID-7")


class BookingTests(unittest.TestCase):
    """FR-003, FR-007"""

    def setUp(self):
        self.system = new_system()

    def test_tc06_booking_uses_capacity_and_full_slot_rejected(self):
        """FR-003: the count goes up by one per booking and stops at capacity."""
        slot = self.system.add_slot("C1", "Centre One", "560041", DAY_0, 1)
        first = self.system.register_citizen("A", 30, "ID-1")
        second = self.system.register_citizen("B", 31, "ID-2")
        self.system.book_slot(first.citizen_id, slot.slot_id)
        self.assertEqual(slot.remaining, 0)
        self.assertEqual(first.status, STATUS_SLOT_BOOKED)
        with self.assertRaises(CapacityError):
            self.system.book_slot(second.citizen_id, slot.slot_id)
        self.assertEqual(self.system.search_slots("560041", DAY_0), [])

    def test_tc07_last_seat_taken_only_once_under_concurrency(self):
        """FR-003 / BBPS-3: 20 simultaneous requests for 1 seat, 1 winner."""
        slot = self.system.add_slot("C1", "Centre One", "560041", DAY_0, 1)
        citizens = [self.system.register_citizen(f"P{i}", 30, f"ID-{i}")
                    for i in range(20)]
        results = []
        start = threading.Barrier(len(citizens))

        def attempt(citizen_id):
            start.wait()
            try:
                self.system.book_slot(citizen_id, slot.slot_id)
                results.append("booked")
            except CapacityError:
                results.append("full")

        threads = [threading.Thread(target=attempt, args=(c.citizen_id,))
                   for c in citizens]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        self.assertEqual(results.count("booked"), 1)
        self.assertEqual(results.count("full"), 19)
        self.assertEqual(slot.booked, 1)

    def test_tc08_closed_cohort_cannot_book(self):
        """FR-003: only cohorts opened for the rollout may book."""
        system = VaccinationSystem(CertificateSigner(b"unit-test-signing-key"))
        citizen = system.register_citizen("Kiran", 25, "ID-1")
        slot = system.add_slot("C1", "Centre One", "560041", DAY_0, 5)
        with self.assertRaises(EligibilityError):
            system.book_slot(citizen.citizen_id, slot.slot_id)

    def test_tc09_booking_confirmation_is_queued(self):
        """FR-007: every successful booking queues one confirmation."""
        slot = self.system.add_slot("C1", "Centre One", "560041", DAY_0, 5)
        citizen = self.system.register_citizen("Ravi", 40, "ID-1")
        self.system.book_slot(citizen.citizen_id, slot.slot_id)
        self.assertEqual(len(self.system.outbox), 1)
        self.assertIn("Centre One", self.system.outbox[0].message)


class DoseRecordTests(unittest.TestCase):
    """FR-004"""

    def setUp(self):
        self.system = new_system()
        self.citizen = self.system.register_citizen("Ravi", 40, "ID-1")
        slot = self.system.add_slot("C1", "Centre One", "560041", DAY_0, 5)
        self.booking = self.system.book_slot(self.citizen.citizen_id, slot.slot_id)

    def test_tc10_empty_batch_number_rejected(self):
        """FR-004 / BBPS-4: a blank batch number must not be saved."""
        for bad in ("", "   "):
            with self.assertRaises(ValidationError):
                self.system.record_dose("OFF-1", self.booking.booking_id,
                                        "Covaxin", bad, DAY_0)
        self.assertEqual(self.citizen.status, STATUS_SLOT_BOOKED)
        self.assertEqual(self.system.dose_records[self.citizen.citizen_id], [])

    def test_tc11_status_moves_to_dose_administered(self):
        """FR-004: Slot Booked -> Dose Administered, batch number stored."""
        record = self.system.record_dose("OFF-1", self.booking.booking_id,
                                         "Covaxin", "B-100", DAY_0)
        self.assertEqual(self.citizen.status, STATUS_DOSE_ADMINISTERED)
        self.assertEqual(record.batch_number, "B-100")


class CertificateTests(unittest.TestCase):
    """FR-005, FR-006, NFR-001"""

    def setUp(self):
        self.system = new_system()
        self.citizen = self.system.register_citizen("Ravi", 40, "ID-1")
        give_first_dose(self.system, self.citizen.citizen_id)

    def _give_second_dose(self):
        day = DAY_0 + timedelta(days=28)
        slot = self.system.add_slot("C1", "Centre One", "560041", day, 5)
        booking = self.system.book_slot(self.citizen.citizen_id, slot.slot_id)
        self.system.record_dose("OFF-1", booking.booking_id, "Covaxin", "B-200", day)

    def test_tc12_no_certificate_before_final_dose(self):
        """FR-005 / BBPS-5: one dose out of two gives no certificate."""
        self.assertNotIn(self.citizen.citizen_id, self.system.certificates)
        with self.assertRaises(EligibilityError):
            self.system.generate_certificate(self.citizen.citizen_id)

    def test_tc13_certificate_issued_after_final_dose(self):
        """FR-005: QR payload carries citizen ID, dose dates and a signature."""
        self._give_second_dose()
        self.assertEqual(self.citizen.status, STATUS_FULLY_VACCINATED)
        qr = self.system.certificates[self.citizen.citizen_id]
        valid, data = self.system.verify_certificate(qr)
        self.assertTrue(valid)
        self.assertEqual(data["citizen_id"], self.citizen.citizen_id)
        self.assertEqual([d["date"] for d in data["doses"]],
                         ["2026-09-01", "2026-09-29"])
        self.assertEqual(len(qr.rsplit(".", 1)[1]), 64)   # SHA-256 hex digest

    def test_tc14_tampered_or_garbage_certificate_rejected(self):
        """FR-006: a changed or malformed QR payload fails verification."""
        self._give_second_dose()
        qr = self.system.certificates[self.citizen.citizen_id]
        flipped = qr[:-1] + ("0" if qr[-1] != "0" else "1")
        self.assertEqual(self.system.verify_certificate(flipped), (False, None))
        self.assertEqual(self.system.verify_certificate("not-a-certificate"),
                         (False, None))
        other = VaccinationSystem(CertificateSigner(b"a-different-signing-key"))
        self.assertEqual(other.verify_certificate(qr), (False, None))

    def test_tc15_verification_is_fast_and_reuses_the_key(self):
        """NFR-001 / BBPS-6: local timing check, key prepared only once.

        This is a single-machine sanity check, not the peak-load benchmark
        that NFR-001 asks for.
        """
        self._give_second_dose()
        qr = self.system.certificates[self.citizen.citizen_id]
        runs = 2000
        started = time.perf_counter()
        for _ in range(runs):
            self.system.verify_certificate(qr)
        average_ms = (time.perf_counter() - started) * 1000 / runs
        self.assertLess(average_ms, 150)
        self.assertEqual(self.system.signer.key_loads, 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
