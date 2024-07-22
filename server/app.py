#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route("/restaurants")
def get_restaurants():

    restaurants = [restaurant.to_dict() for restaurant in Restaurant.query.all()]

    response = make_response(
        restaurants,
        200
    )

    return response

@app.route('/restaurants/<int:id>')
def get_restaurant_id(id):
    restaurant = Restaurant.query.filter(Restaurant.id == id).first()

    if restaurant:
        restaurant_dict = restaurant.to_dict()
        restaurant_dict['restaurant_pizzas'] = [rp.to_dict() for rp in restaurant.restaurant_pizzas]
        response = make_response(
            restaurant_dict,
            200
        )
    else:
        response = make_response(
            {"error": "Restaurant not found"},
            404
        )

    return response

@app.route('/restaurants/<int:id>', methods=['GET','DELETE'])
def delete_restaurant_id(id):
    restaurant = Restaurant.query.filter(Restaurant.id == id).first()

    if restaurant:
        if request.method == 'GET':
            restaurant_dict= restaurant.to_dict()
            response = make_response(
               restaurant_dict,
               200
            )
            return response
        elif request.method == 'DELETE':
            db.session.delete(restaurant)
            db.session.commit()

            response_body = {
                "message": "Restaurant deleted"
            }
            response = make_response(
               response_body,
               204
            )
            return response
    else:
        response_body = {
            "error": "Restaurant not found"
        }
        response = make_response(
               response_body,
               404
        )
        return response
    
@app.route("/pizzas")
def get_pizzas():

    pizzas = [pizza.to_dict() for pizza in Pizza.query.all()]

    response = make_response(
        pizzas,
        200
    )

    return response

@app.route("/restaurant_pizzas", methods=['POST'])
def create_restaurant_pizza():
    try:
        data = request.get_json()
        price = int(data.get("price"))
        if price < 1 or price > 30:
            raise ValueError("Price must be between 1 and 30")

        new_restaurant_pizza = RestaurantPizza(
            price=price,
            pizza_id=data.get("pizza_id"),
            restaurant_id=data.get("restaurant_id"),
        )

        db.session.add(new_restaurant_pizza)
        db.session.commit()

        rp_dict = new_restaurant_pizza.to_dict()
        rp_dict['pizza_id'] = new_restaurant_pizza.pizza_id
        rp_dict['restaurant_id'] = new_restaurant_pizza.restaurant_id

        response = make_response(
            jsonify(rp_dict),
            201,
        )

        return response
    except Exception as e:
        error_response = jsonify({"errors": ["validation errors"]})
        return error_response, 400

if __name__ == "__main__":
    app.run(port=5555, debug=True)
