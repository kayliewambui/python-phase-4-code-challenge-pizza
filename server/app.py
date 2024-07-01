#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
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

class Restaurants(Resource):
    def get(self):
        restaurants = [r.to_dict(rules=['-restaurant_pizzas']) for r in Restaurant.query.all()]
        return make_response(restaurants, 200)

api.add_resource(Restaurants, '/restaurants')

class RestaurantByID(Resource):
    def get(self, id):
        try:
            restaurant = Restaurant.query.filter_by(id = id).first().to_dict()

            return make_response(restaurant, 200)
        except Exception as error:
            print(error)
            return make_response({"error" : "Restaurant not found"}, 404)

    # def patch(self, id):
    #     restaurant = Restaurant.query.filter_by(id = id).first()

    #     if restaurant:
    #         for attr in request.form:
    #             setattr(restaurant, attr, request.form[attr])
    #         db.session.add(restaurant)
    #         db.session.commit()
    #         return (restaurant.to_dict(), 204)  

    def delete(self, id):
        try:
            restaurant = Restaurant.query.filter_by(id = id).first()

            if restaurant:
                db.session.delete(restaurant)
                db.session.commit()

            restaurant_after_deletion = Restaurant.query.filter_by(id = id).first()

            if restaurant_after_deletion == None:
                return make_response({"message": "deletion is successful"}, 204)
        except Exception as error:
            print(error)
            return make_response({"error": "deletion is unsuccessful"}, 500)

api.add_resource(RestaurantByID, '/restaurants/<int:id>')

class Pizzas(Resource):
    def get(self):
        pizzas = [p.to_dict(rules = ["-restaurant_pizzas"]) for p in Pizza.query.all()]
        return make_response(pizzas, 200)

api.add_resource(Pizzas, "/pizzas")

class RestaurantPizzas(Resource):
    def post(self):
        try:
            data = request.get_json()

            new_rp = RestaurantPizza(
                price = data['price'],
                pizza_id = data['pizza_id'],
                restaurant_id = data['restaurant_id'],
            )

            db.session.add(new_rp)
            db.session.commit()
            
            return make_response(new_rp.to_dict(), 201)
        except Exception as error:
            print(error)
            # who tf put square bracket outside the error's value for the app_test.py
            return make_response({"errors": ["validation errors"]}, 400) 

api.add_resource(RestaurantPizzas, "/restaurant_pizzas")

if __name__ == "__main__":
    app.run(port=5555, debug=True)
