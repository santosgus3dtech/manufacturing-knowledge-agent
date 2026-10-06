from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

from .models import QuoteBreakdown, QuoteRequest

MONEY = Decimal("0.01")

MATERIALS: dict[str, dict[str, Decimal]] = {
    "PLA": {
        "cost_per_gram": Decimal("0.026"),
        "machine_hour": Decimal("2.40"),
        "power_kw": Decimal("0.11"),
        "packaging": Decimal("1.20"),
    },
    "PETG": {
        "cost_per_gram": Decimal("0.034"),
        "machine_hour": Decimal("3.00"),
        "power_kw": Decimal("0.13"),
        "packaging": Decimal("1.40"),
    },
    "ABS": {
        "cost_per_gram": Decimal("0.039"),
        "machine_hour": Decimal("3.40"),
        "power_kw": Decimal("0.16"),
        "packaging": Decimal("1.50"),
    },
    "TOUGH RESIN": {
        "cost_per_gram": Decimal("0.082"),
        "machine_hour": Decimal("4.80"),
        "power_kw": Decimal("0.09"),
        "packaging": Decimal("1.80"),
    },
}


def _money(value: Decimal) -> Decimal:
    return value.quantize(MONEY, rounding=ROUND_HALF_UP)


def estimate_quote(request: QuoteRequest) -> QuoteBreakdown:
    material_name = request.material.strip().upper()
    if material_name not in MATERIALS:
        supported = ", ".join(MATERIALS)
        raise ValueError(f"Unsupported material. Choose one of: {supported}")

    profile = MATERIALS[material_name]
    weight = Decimal(str(request.part_weight_g))
    hours = Decimal(str(request.print_hours))
    labor_minutes = Decimal(str(request.labor_minutes))
    quantity = Decimal(request.quantity)

    material_cost = profile["cost_per_gram"] * weight
    energy_cost = profile["power_kw"] * hours * Decimal("0.24")
    machine_cost = profile["machine_hour"] * hours
    labor_cost = labor_minutes / Decimal(60) * Decimal("24.00")
    packaging_cost = profile["packaging"]
    direct_cost = material_cost + energy_cost + machine_cost + labor_cost + packaging_cost
    risk_buffer = direct_cost * Decimal(str(request.failure_rate_percent)) / Decimal(100)
    unit_cost = direct_cost + risk_buffer
    unit_price = unit_cost * (Decimal(1) + Decimal(str(request.margin_percent)) / Decimal(100))
    rounded_unit_price = _money(unit_price)

    return QuoteBreakdown(
        material=material_name.title(),
        quantity=request.quantity,
        material_cost=float(_money(material_cost)),
        energy_cost=float(_money(energy_cost)),
        machine_cost=float(_money(machine_cost)),
        labor_cost=float(_money(labor_cost)),
        packaging_cost=float(_money(packaging_cost)),
        risk_buffer=float(_money(risk_buffer)),
        unit_cost=float(_money(unit_cost)),
        unit_price=float(rounded_unit_price),
        total_price=float(_money(rounded_unit_price * quantity)),
    )
