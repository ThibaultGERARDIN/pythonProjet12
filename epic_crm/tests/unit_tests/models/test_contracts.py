from models.contracts import Contract


def test_contract_to_list():
    contract = Contract(
        id=10,
        total_amount=5000.0,
        to_be_paid=1000.0,
        is_signed=True,
        client_id=2,
        sales_contact_id=1
    )

    result = contract.to_list()
    assert isinstance(result, tuple)
    assert result[0] == 10
    assert result[2] == 5000.0
    assert result[3] == 1000.0
    assert result[4] is True
