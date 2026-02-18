from rest_framework.test import APIClient

from productory_checkout.models import OrderStatus


def test_catalog_and_checkout_flow(cart, product):
    client = APIClient()

    item_response = client.post(
        "/api/checkout/cart-items/",
        {"cart_id": cart.id, "product_id": product.id, "quantity": 3},
        format="json",
    )
    assert item_response.status_code == 201

    checkout_response = client.post(
        "/api/checkout/checkout/",
        {"cart_id": cart.id, "email": "buyer@example.com", "full_name": "Buyer"},
        format="json",
    )
    assert checkout_response.status_code == 201
    assert checkout_response.data["total_amount"] == "37.50"
    assert len(checkout_response.data["items"]) == 1


def test_order_transition_endpoint(cart, product):
    client = APIClient()
    client.post(
        "/api/checkout/cart-items/",
        {"cart_id": cart.id, "product_id": product.id, "quantity": 1},
        format="json",
    )
    checkout = client.post(
        "/api/checkout/checkout/",
        {"cart_id": cart.id, "email": "buyer@example.com"},
        format="json",
    )
    order_id = checkout.data["id"]

    transition = client.post(
        f"/api/checkout/orders/{order_id}/transition/",
        {"status": OrderStatus.PAID},
        format="json",
    )
    assert transition.status_code == 200
    assert transition.data["status"] == OrderStatus.PAID


def test_product_list_serializer_shape(product):
    client = APIClient()
    response = client.get("/api/catalog/products/")

    assert response.status_code == 200
    payload = response.json()
    assert payload[0]["sku"] == product.sku
    assert "category_name" in payload[0]
    assert "description" not in payload[0]
