"""Draws the UML component diagram for SE Lab 3.

Problem Statement #17 - Vaccination Cohort & Dose Scheduling System
Architecture: Microservices

Run:  python generate_component_diagram.py      (needs matplotlib)
Writes Architecture_Diagram.png and Architecture_Diagram.pdf next to this file.
"""
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Arc, Circle, Ellipse, FancyArrowPatch, Rectangle

OUT = os.path.dirname(os.path.abspath(__file__))

INK = "#1c1c1c"
MUTED = "#555555"
CLIENT = ("#E8F1FB", "#2F5D8A")
EDGE = ("#FFF1DC", "#A66A00")
SERVICE = ("#E6F4EA", "#2E6B3E")
STORE = ("#F0F0F0", "#555555")

R_BALL = 0.14
R_SOCK = 0.25
LW = 1.4

fig, ax = plt.subplots(figsize=(18.3, 12.3))
ax.set_xlim(0, 18.3)
ax.set_ylim(0, 12.3)
ax.set_aspect("equal")
ax.axis("off")


def component_icon(x, y, w, h, edge):
    """The small UML component symbol in the top-right corner of a box."""
    ix, iy = x + w - 0.42, y + h - 0.36
    ax.add_patch(Rectangle((ix, iy), 0.26, 0.22, fc="white", ec=edge, lw=1.0, zorder=4))
    for dy in (0.03, 0.13):
        ax.add_patch(Rectangle((ix - 0.07, iy + dy), 0.14, 0.06, fc="white", ec=edge, lw=1.0, zorder=5))


def component(x, y, w, h, name, sub=None, colors=SERVICE, name_size=10.5):
    """Rectangle with the <<component>> stereotype."""
    fill, edge = colors
    ax.add_patch(Rectangle((x, y), w, h, fc=fill, ec=edge, lw=1.6, zorder=3))
    component_icon(x, y, w, h, edge)
    cx = x + w / 2
    top = y + h / 2 + (0.30 if sub else 0.16)
    ax.text(cx, top, "«component»", ha="center", va="center", fontsize=8, color=MUTED, zorder=6)
    ax.text(cx, top - 0.30, name, ha="center", va="center", fontsize=name_size,
            fontweight="bold", color=INK, zorder=6)
    if sub:
        ax.text(cx, top - 0.60, sub, ha="center", va="top", fontsize=7.4, style="italic",
                color=MUTED, zorder=6, linespacing=1.25)


def database(x, y, w, h, name):
    """Cylinder with the <<database>> stereotype."""
    fill, edge = STORE
    eh = 0.22
    ax.add_patch(Rectangle((x, y + eh / 2), w, h - eh, fc=fill, ec="none", zorder=3))
    ax.plot([x, x], [y + eh / 2, y + h - eh / 2], color=edge, lw=1.4, zorder=4)
    ax.plot([x + w, x + w], [y + eh / 2, y + h - eh / 2], color=edge, lw=1.4, zorder=4)
    ax.add_patch(Ellipse((x + w / 2, y + eh / 2), w, eh, fc=fill, ec=edge, lw=1.4, zorder=3))
    ax.add_patch(Rectangle((x + 0.02, y + eh / 2), w - 0.04, eh / 2 + 0.02, fc=fill, ec="none", zorder=3.5))
    ax.add_patch(Ellipse((x + w / 2, y + h - eh / 2), w, eh, fc="#FAFAFA", ec=edge, lw=1.4, zorder=5))
    ax.text(x + w / 2, y + h / 2 + 0.03, "«database»", ha="center", va="center", fontsize=7.5,
            color=MUTED, zorder=6)
    ax.text(x + w / 2, y + h / 2 - 0.22, name, ha="center", va="center", fontsize=9.5,
            fontweight="bold", color=INK, zorder=6)


def assembly_h(x_req, x_prov, y, name, proto):
    """Horizontal ball-and-socket. Requirer on the left, provider on the right."""
    bx = (x_req + x_prov) / 2
    ax.plot([x_prov, bx + R_BALL], [y, y], color=INK, lw=LW, zorder=2)
    ax.plot([x_req, bx - R_SOCK], [y, y], color=INK, lw=LW, zorder=2)
    ax.add_patch(Circle((bx, y), R_BALL, fc="white", ec=INK, lw=LW, zorder=4))
    ax.add_patch(Arc((bx, y), 2 * R_SOCK, 2 * R_SOCK, theta1=90, theta2=270, color=INK, lw=LW, zorder=4))
    ax.text(bx, y + 0.40, name, ha="center", va="center", fontsize=9, fontweight="bold", color=INK)
    ax.text(bx, y - 0.42, proto, ha="center", va="center", fontsize=7.6, color=MUTED)


def assembly_v(x, y_req, y_prov, name, proto):
    """Vertical ball-and-socket between stacked components."""
    by = (y_req + y_prov) / 2
    if y_prov > y_req:  # provider above, requirer below
        ax.plot([x, x], [y_prov, by + R_BALL], color=INK, lw=LW, zorder=2)
        ax.plot([x, x], [y_req, by - R_SOCK], color=INK, lw=LW, zorder=2)
        t1, t2 = 180, 360
    else:  # provider below, requirer above
        ax.plot([x, x], [y_prov, by - R_BALL], color=INK, lw=LW, zorder=2)
        ax.plot([x, x], [y_req, by + R_SOCK], color=INK, lw=LW, zorder=2)
        t1, t2 = 0, 180
    ax.add_patch(Circle((x, by), R_BALL, fc="white", ec=INK, lw=LW, zorder=4))
    ax.add_patch(Arc((x, by), 2 * R_SOCK, 2 * R_SOCK, theta1=t1, theta2=t2, color=INK, lw=LW, zorder=4))
    ax.text(x + 0.45, by + 0.13, name, ha="left", va="center", fontsize=9, fontweight="bold", color=INK)
    ax.text(x + 0.45, by - 0.15, proto, ha="left", va="center", fontsize=7.6, color=MUTED)


def use_dep(x1, x2, y, label="«use»  SQL"):
    """Dashed usage dependency with an open arrowhead."""
    ax.add_patch(FancyArrowPatch((x1, y), (x2, y), arrowstyle="->", mutation_scale=14,
                                 linestyle=(0, (5, 4)), color=INK, lw=1.2, zorder=2,
                                 shrinkA=0, shrinkB=0))
    ax.text((x1 + x2) / 2, y + 0.17, label, ha="center", va="center", fontsize=7.6, color=MUTED)


# ---------------------------------------------------------------- layout
CL_X, CL_W = 0.5, 3.0            # clients
GW_X, GW_W = 5.5, 2.4            # gateway
SV_X, SV_W = 10.3, 3.4           # services
DB_X, DB_W = 15.5, 2.3           # stores + notification

ROW1, ROW2, ROW3, ROW4 = 9.5, 6.75, 4.0, 1.5
H = 1.5
H2 = 2.0

for cx, text in ((CL_X + CL_W / 2, "CLIENT APPS"), (GW_X + GW_W / 2, "EDGE"),
                 (SV_X + SV_W / 2, "MICROSERVICES"),
                 (DB_X + DB_W / 2, "NOTIFICATION  +  ONE DATABASE PER SERVICE")):
    ax.text(cx, 10.62, text, ha="center", va="center", fontsize=8.2, color=MUTED, fontweight="bold")
ax.plot([0.5, 17.8], [10.42, 10.42], color="#CFCFCF", lw=0.8)

ax.text(9.15, 11.85, "UML Component Diagram — Vaccination Cohort & Dose Scheduling System",
        ha="center", va="center", fontsize=15, fontweight="bold", color=INK)
ax.text(9.15, 11.4, "Microservices Architecture   ·   SE Lab 3   ·   Problem Statement #17   ·   "
        "Shrihari Nagesh (PES1UG24CS445)", ha="center", va="center", fontsize=9.5, color=MUTED)

# clients
component(CL_X, 7.45, CL_W, H, "Citizen Portal", "web / mobile app\nregister · book · download certificate", CLIENT)
component(CL_X, 4.25, CL_W, H, "Officer Console", "vaccination centre app\nrecord dose · scan QR", CLIENT)

# gateway
ax.add_patch(Rectangle((GW_X, 0.75), GW_W, 9.5, fc=EDGE[0], ec=EDGE[1], lw=1.6, zorder=3))
component_icon(GW_X, 0.75, GW_W, 9.5, EDGE[1])
gcx = GW_X + GW_W / 2
ax.text(gcx, 5.95, "«component»", ha="center", va="center", fontsize=8, color=MUTED, zorder=6)
ax.text(gcx, 5.62, "API Gateway", ha="center", va="center", fontsize=11.5, fontweight="bold", color=INK, zorder=6)
ax.text(gcx, 5.28, "single entry point\nlogin token check (JWT)\nrole check: citizen / officer\nrate limiting\n"
        "routing to services\n[NFR-002]",
        ha="center", va="top", fontsize=7.6, style="italic", color=MUTED, zorder=6, linespacing=1.35)

# services
component(SV_X, ROW1 - H / 2, SV_W, H, "Citizen Registry Service", "profiles · cohort assignment\n[FR-002]")
component(SV_X, ROW2 - H2 / 2, SV_W, H2, "Slot Booking Service",
          "centre slots · reservations\nscaled out during rollouts\n[FR-003, NFR-003]")
component(SV_X, ROW3 - H / 2, SV_W, H, "Vaccination Record Service", "dose records · interval rules\n[FR-001, FR-004]")
component(SV_X, ROW4 - H / 2, SV_W, H, "Certificate Service",
          "signs and verifies QR certificates\n[FR-005, FR-006, NFR-001]")

# notification + stores
N_Y, N_H = 6.80, 1.07
component(DB_X, N_Y, DB_W, N_H, "Notification Service", "[FR-007]", SERVICE, name_size=9.2)
database(DB_X, ROW1 - 0.5, DB_W, 1.0, "Citizen DB")
database(DB_X, 5.62, DB_W, 0.95, "Booking DB")
database(DB_X, ROW3 - 0.5, DB_W, 1.0, "Records DB")
database(DB_X, ROW4 - 0.5, DB_W, 1.0, "Certificate Store")

# ---------------------------------------------------------------- interfaces
# clients require, gateway provides
assembly_h(CL_X + CL_W, GW_X, 8.2, "ICitizenAPI", "«REST / HTTPS»")
assembly_h(CL_X + CL_W, GW_X, 5.0, "IOfficerAPI", "«REST / HTTPS»")

# gateway requires, services provide
gw_r = GW_X + GW_W
assembly_h(gw_r, SV_X, ROW1, "IRegistration", "«REST / JSON»")
assembly_h(gw_r, SV_X, ROW2, "ISlotBooking", "«REST / JSON»")
assembly_h(gw_r, SV_X, ROW3, "IDoseRecord", "«REST / JSON»")
assembly_h(gw_r, SV_X, ROW4, "ICertificateVerify", "«REST / JSON»")

# service to service
XV = 11.15
assembly_v(XV, ROW2 + H2 / 2, ROW1 - H / 2, "ICitizenLookup", "«REST» get cohort + eligibility window")
assembly_v(XV, ROW2 - H2 / 2, ROW3 + H / 2, "IDoseEligibility", "«REST» dose-interval check")
assembly_v(XV, ROW3 - H / 2, ROW4 + H / 2, "ICertificateIssue", "«async event» final dose recorded")

sv_r = SV_X + SV_W
assembly_h(sv_r, DB_X, N_Y + N_H / 2, "INotification", "«async message»")

# data stores
use_dep(sv_r, DB_X, ROW1)
use_dep(sv_r, DB_X, 6.1)
use_dep(sv_r, DB_X, ROW3)
use_dep(sv_r, DB_X, ROW4)

# ---------------------------------------------------------------- legend
LX, LY, LEG_W, LEG_H = 0.5, 0.75, 4.3, 2.75
ax.add_patch(Rectangle((LX, LY), LEG_W, LEG_H, fc="white", ec="#BDBDBD", lw=0.9, zorder=1))
ax.text(LX + 0.15, LY + LEG_H - 0.22, "LEGEND", fontsize=8, fontweight="bold", color=MUTED, va="center")

ly = LY + LEG_H - 0.62
ax.plot([LX + 0.2, LX + 0.62], [ly, ly], color=INK, lw=LW)
ax.add_patch(Circle((LX + 0.76, ly), R_BALL, fc="white", ec=INK, lw=LW))
ax.text(LX + 1.25, ly, "Provided interface (ball)", fontsize=8.2, va="center", color=INK)

ly -= 0.5
ax.plot([LX + 0.2, LX + 0.55], [ly, ly], color=INK, lw=LW)
ax.add_patch(Arc((LX + 0.8, ly), 2 * R_SOCK, 2 * R_SOCK, theta1=90, theta2=270, color=INK, lw=LW))
ax.text(LX + 1.25, ly, "Required interface (socket)", fontsize=8.2, va="center", color=INK)

ly -= 0.5
ax.plot([LX + 0.15, LX + 0.39], [ly, ly], color=INK, lw=LW)
ax.add_patch(Arc((LX + 0.64, ly), 2 * R_SOCK, 2 * R_SOCK, theta1=90, theta2=270, color=INK, lw=LW))
ax.add_patch(Circle((LX + 0.64, ly), R_BALL, fc="white", ec=INK, lw=LW))
ax.plot([LX + 0.78, LX + 1.05], [ly, ly], color=INK, lw=LW)
ax.text(LX + 1.25, ly, "Assembly connector\n(socket side calls the ball side)", fontsize=8.2, va="center",
        color=INK, linespacing=1.2)

ly -= 0.55
ax.add_patch(FancyArrowPatch((LX + 0.15, ly), (LX + 1.05, ly), arrowstyle="->", mutation_scale=12,
                             linestyle=(0, (5, 4)), color=INK, lw=1.2, shrinkA=0, shrinkB=0))
ax.text(LX + 1.25, ly, "«use» dependency (database queries)", fontsize=8.2, va="center", color=INK)

ly -= 0.45
for i, (col, lab) in enumerate(((CLIENT, "client"), (EDGE, "edge"), (SERVICE, "service"), (STORE, "data store"))):
    sx = LX + 0.15 + i * 1.02
    ax.add_patch(Rectangle((sx, ly - 0.1), 0.26, 0.2, fc=col[0], ec=col[1], lw=1.0))
    ax.text(sx + 0.33, ly, lab, fontsize=7.6, va="center", color=INK)

ax.text(9.15, 0.3,
        "Booking flow:  Citizen Portal → API Gateway → Slot Booking Service → "
        "(Citizen Registry: cohort)  +  (Vaccination Record: dose-interval check) → Booking DB → Notification Service",
        ha="center", va="center", fontsize=8.4, color=MUTED)

for ext, kw in (("png", {"dpi": 200}), ("pdf", {})):
    fig.savefig(os.path.join(OUT, f"Architecture_Diagram.{ext}"), bbox_inches="tight", pad_inches=0.25,
                facecolor="white", **kw)
print("written")
