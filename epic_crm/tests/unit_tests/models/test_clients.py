from models.clients import Client


def test_client_to_list():
    client = Client(
        id=1,
        full_name="Jean Dupont",
        email="jean@dupont.com",
        phone="0601020304",
        enterprise="Dupont SARL",
        sales_contact_id=5,
    )

    result = client.to_list()
    assert isinstance(result, tuple)
    assert result[0] == 1
    assert result[1] == "Jean Dupont"
    assert result[2] == "jean@dupont.com"
