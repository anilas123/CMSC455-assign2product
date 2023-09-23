from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

# Define the URL of the product-service
product_service_url = "http://127.0.0.1:5049/products"

carts = [
    {
        "user_id": 1,
        "items": []
    },
    {
        "user_id": 2,
        "items": []
    },
]

# Modify the get_products function to return a dictionary
def get_products():
    try:
        response = requests.get(product_service_url)
        if response.status_code == 200:
            product_data = response.json()
            return product_data if isinstance(product_data, dict) else {}
        else:
            print(f"Failed to fetch product data. Status code: {response.status_code}")
            return {}
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to product-service: {e}")
        return {}

# Update the add_to_cart function
@app.route('/cart/<int:user_id>/add/<int:product_id>', methods=['POST'])
def add_to_cart(user_id, product_id):
    data = request.json
    quantity = data.get('quantity')

    if not quantity:
        return jsonify({'error': 'Quantity must be specified'}), 400

    user_cart = next((cart for cart in carts if cart["user_id"] == user_id), None)
    if user_cart:
        # Fetch product data from the product-service using the get_products() function
        product_data = get_products()
        product = product_data.get(str(product_id))

        print(product)
        
        if product:
            product_name = product["name"]
            product_price = product["price"]

            # Check if the item is already in the cart
            item = next((item for item in user_cart["items"] if item["product_id"] == product_id), None)
            if item:
                item["quantity"] += quantity
            else:
                # Add the item to the cart with product details
                user_cart["items"].append({
                    "product_id": product_id,
                    "name": product_name,
                    "price": product_price,
                    "quantity": quantity
                })

                # After adding to the cart, remove the specified quantity from the product service
                product_quantity = product.get('quantity', 0)
                if product_quantity >= quantity:
                    product['quantity'] -= quantity
                    # Update the product data on the product-service side
                    product_service_update_url = f'http://127.0.0.1:5049/products/{product_id}'
                    response = requests.put(product_service_update_url, json=product)
                    if response.status_code != 200:
                        # Handle the update failure here
                        return jsonify({'error': 'Failed to update product quantity'}), 500
                else:
                    return jsonify({'error': 'Insufficient product quantity'}), 400

            return jsonify({'message': f'{quantity} product(s) added to the cart for user {user_id}', 'cart_contents': user_cart['items']}), 201
        else:
            return jsonify({'error': 'Product not found'}), 404
    else:
        return jsonify({'error': 'User cart not found'}), 404

# Update the remove_from_cart function
@app.route('/cart/<int:user_id>/remove/<int:product_id>', methods=['POST'])
def remove_from_cart(user_id, product_id):
    data = request.json
    quantity = data.get('quantity')

    if not quantity:
        return jsonify({'error': 'Quantity must be specified'}), 400

    user_cart = next((cart for cart in carts if cart["user_id"] == user_id), None)
    if user_cart:
        item = next((item for item in user_cart["items"] if item["product_id"] == product_id), None)
        if item:
            if item["quantity"] > quantity:
                item["quantity"] -= quantity
            else:
                user_cart["items"].remove(item)

            # Increase the product quantity in the product-service
            product_data = get_products()
            product = product_data.get(str(product_id))
            
            if product:
                product['quantity'] += quantity
                product_service_update_url = f'http://127.0.0.1:5049/products/{product_id}'
                response = requests.put(product_service_update_url, json=product)
                if response.status_code != 200:
                    # Handle the update failure here
                    pass

            return jsonify({'message': f'{quantity} product(s) removed from the cart for user {user_id}'}), 200

    return jsonify({'error': 'Product not found in the cart'}), 404

@app.route('/cart/test', methods=['GET'])
def testing():
        get_products()
        return {}



if __name__ == '__main__':
    with app.app_context():
        app.run(debug=True, port=5050)