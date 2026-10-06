from manufacturing_agent.models import QuoteRequest
from manufacturing_agent.pricing import estimate_quote


def test_quote_is_deterministic_and_balanced() -> None:
    quote = estimate_quote(
        QuoteRequest(
            material="PETG",
            part_weight_g=72,
            print_hours=3.5,
            labor_minutes=18,
            quantity=2,
            failure_rate_percent=8,
            margin_percent=35,
        )
    )

    assert quote.material == "Petg"
    assert quote.material_cost == 2.45
    assert quote.total_price == round(quote.unit_price * 2, 2)
    assert quote.unit_price > quote.unit_cost > 0


def test_quote_rejects_unknown_material() -> None:
    try:
        estimate_quote(QuoteRequest(material="Unobtainium"))
    except ValueError as exc:
        assert "Unsupported material" in str(exc)
    else:
        raise AssertionError("Unsupported material should fail")
