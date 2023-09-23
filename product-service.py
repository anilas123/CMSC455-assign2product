from flask import Flask, jsonify, request

app = Flask(__name__)

products = {
    1: {
        "name": "Bread",
        "price": 3.9,
        "quantity": 50
    },
    2: {
        "name": "Milk",
        "price": 2,
        "quantity": 100
    },
    3: {
        "name": "Eggs",
        "price": 1.5,
        "quantity": 60
    }
}

@app.route('/products', methods=['GET'])
def get_products():
    return jsonify(products)

@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = products.get(product_id)
    print(product)
    if product:
        return jsonify(product)
    else:
        return jsonify({"error": "Product not found"}), 404

@app.route('/products', methods=['POST'])
def add_product():
    data = request.json

    new_product_id = max(products.keys()) + 1
    new_product = {
        "name": data.get('name'),
        "price": data.get('price'),
        "quantity": data.get('quantity')
    }

    if not new_product["name"] or not new_product["price"] or not new_product["quantity"]:
        return jsonify({"error": "Invalid request data"}), 400

    products[new_product_id] = new_product

    return jsonify({"message": "Product added successfully", "product": new_product}), 201

@app.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    data = request.json

    product = products.get(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    # Update the product properties with the new data
    product["name"] = data.get('name', product["name"])
    product["price"] = data.get('price', product["price"])
    product["quantity"] = data.get('quantity', product["quantity"])

    return jsonify({"message": "Product updated successfully", "product": product}), 200


if __name__ == '__main__':
    app.run(debug=True, port=5049)