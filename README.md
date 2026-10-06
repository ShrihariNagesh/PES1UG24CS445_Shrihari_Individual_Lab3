# LAB-3_Activity_ShrihariNagesh_PES1UG24CS445

**SE Lab 3: Component Modelling & Architectural Pattern Selection**

| | |
|---|---|
| Name | Shrihari Nagesh |
| SRN | PES1UG24CS445 |
| Problem Statement | #17 Vaccination Cohort & Dose Scheduling System (Healthcare & Telemedicine) |
| Architecture chosen | Microservices |

Lab 1 (requirements and use-case diagram for the same system):
[LAB-1_Activity_ShrihariNagesh_PES1UG24CS445](https://github.com/ShrihariNagesh/LAB-1_Activity_ShrihariNagesh_PES1UG24CS445)

## Deliverables

| File | What it is |
|---|---|
| `uml_component_diagram.png` / `uml_component_diagram.pdf` | UML component diagram |
| `Architecture_Justification.docx` / `Architecture_Justification.pdf` | One-page written justification |

## Component diagram

![UML component diagram](uml_component_diagram.png)

### Components

| # | Component | Responsibility | Requirements covered |
|---|---|---|---|
| 1 | Citizen Portal | Web / mobile app: register, book a slot, download certificate | |
| 2 | Officer Console | Vaccination centre app: record a dose, scan a QR certificate | |
| 3 | API Gateway | Single entry point: login token check, role check, rate limiting, routing | |
| 4 | Citizen Registry Service | Citizen profiles and cohort assignment | FR-002 |
| 5 | Slot Booking Service | Centre slots and reservations; scaled out during rollouts | FR-003, NFR-002 |
| 6 | Vaccination Record Service | Dose records and dose-interval rules | FR-001, FR-004 |
| 7 | Certificate Service | Signs and verifies QR certificates | FR-005, NFR-001 |
| 8 | Notification Service | Appointment confirmations and reminders | |

Each of the four core services owns its own database (Citizen DB, Booking DB, Records DB, Certificate Store).

### Interfaces

| # | Interface | Provided by (ball) | Required by (socket) | Protocol |
|---|---|---|---|---|
| 1 | `ICitizenAPI` | API Gateway | Citizen Portal | REST / HTTPS |
| 2 | `IOfficerAPI` | API Gateway | Officer Console | REST / HTTPS |
| 3 | `IRegistration` | Citizen Registry Service | API Gateway | REST / JSON |
| 4 | `ISlotBooking` | Slot Booking Service | API Gateway | REST / JSON |
| 5 | `IDoseRecord` | Vaccination Record Service | API Gateway | REST / JSON |
| 6 | `ICertificateVerify` | Certificate Service | API Gateway | REST / JSON |
| 7 | `ICitizenLookup` | Citizen Registry Service | Slot Booking Service | REST |
| 8 | `IDoseEligibility` | Vaccination Record Service | Slot Booking Service | REST |
| 9 | `ICertificateIssue` | Certificate Service | Vaccination Record Service | Async event |
| 10 | `INotification` | Notification Service | Slot Booking Service | Async message |

## Why microservices (summary)

- **Uneven load:** only the Slot Booking Service needs extra instances during a cohort rollout (NFR-002).
- **Fault isolation:** if booking is overloaded, officers can still record doses and certificates can still be verified.
- **Security:** the certificate signing key lives only inside the Certificate Service.
- **Performance:** certificate verification is a small separate service, so it stays within 150 ms (NFR-001) during booking peaks.

The full reasoning, including the comparison with Layered and Client-Server, is in `Architecture_Justification.pdf`.
