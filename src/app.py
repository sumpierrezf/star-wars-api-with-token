"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character, Planet, Vehicle, Favourite
import json
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

#EMPEZAMOS A TRABAJAR DESDE ACA
#Este endpoint trae la info de todos los usuarios.
@app.route('/user', methods=['GET'])
def handle_hello():
    allusers = User.query.all()
    results = list(map(lambda item: item.serialize(), allusers))
    return jsonify(results), 200

#Aca obtengo info de un user.
@app.route('/user/<int:user_id>', methods=['GET'])
def get_info_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return jsonify({"msg": "Usuario no existente."}), 404
    else:
        return jsonify(user.serialize()), 200

@app.route('/user', methods=['POST'])
def add_user():
    request_body = request.data
    decoded_object = json.loads(request_body)
    get_email = User.query.filter_by(email=decoded_object["email"]).first()
    if get_email is None:
        new_user = User(user_name=decoded_object["user_name"], email=decoded_object["email"], password=decoded_object["password"])
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"msg":"Usuario creado correctamente."}), 200
    else:
        return jsonify({"msg":"El usuario ya existe"}), 400

#Aca traemos todos los characters
@app.route('/characters', methods=['GET'])
def handle_characters():
    all_characters = Character.query.all()
    results = list(map(lambda item: item.serialize(), all_characters))
    return jsonify(results), 200

#Aca traemos los planetas
@app.route('/planets', methods=['GET'])
def handle_planets():
    all_planets = Planet.query.all()
    results = list(map(lambda item: item.serialize(), all_planets))
    return jsonify(results), 200

#Aca traemos los vehiculos
@app.route('/vehicles', methods=['GET'])
def handle_vehicles():
    all_vehicles = Vehicle.query.all()
    results = list(map(lambda item: item.serialize(), all_vehicles))
    return jsonify(results), 200

#Aca traemos los favoritos
@app.route('/favourite', methods=['GET'])
def handle_favourites():
    all_favourites = Favourite.query.all()
    results = list(map(lambda item: item.serialize(), all_favourites))
    return jsonify(results), 200

#POST actualiza la info de personajes.
@app.route('/favourite/characters/<int:user_ID>/<int:character_ID>', methods=['POST'])
def add_favourite_character(user_ID, character_ID):
    character = Favourite.query.filter_by(character_id=character_ID,user_id=user_ID).first()
    if character is None:
        existe = Character.query.filter_by(id=character_ID).first()
        if existe is None:
            return jsonify({"msg":"El personaje no existe"}),404
        else:
            user = User.query.filter_by(id=user_ID).first()
            if user is None:
                return jsonify({"msg":"El usuario no existe"}),404
            else:
                new_favourite = Favourite(character_id=character_ID,user_id=user_ID)
                db.session.add(new_favourite)
                db.session.commit()
                return jsonify({"msg":"Personaje agregado a favoritos"}),200
    else:
        return jsonify({"msg":"El personaje ya ha sido agregado"}),404

#POST actualiza la info de planetas.
@app.route('/favourite/planets/<int:user_ID>/<int:planet_ID>', methods=['POST'])
def add_favourite_planet(user_ID, planet_ID):
    planet = Favourite.query.filter_by(planet_id=planet_ID,user_id=user_ID).first()
    if planet is None:
        existe = Planet.query.filter_by(id=planet_ID).first()
        if existe is None:
            return jsonify({"msg":"El planeta no existe"}),404
        else:
            user = User.query.filter_by(id=user_ID).first()
            if user is None:
                return jsonify({"msg":"El usuario no existe"}),404
            else:
                new_favourite = Favourite(planet_id=planet_ID,user_id=user_ID)
                db.session.add(new_favourite)
                db.session.commit()
                return jsonify({"msg":"Planeta agregado a favoritos"}),200
    else:
        return jsonify({"msg":"El planeta ya ha sido agregado"}),404

#POST actualiza la info de vehiculos.
@app.route('/favourite/vehicles/<int:user_ID>/<int:vehicle_ID>', methods=['POST'])
def add_favourite_vehicle(user_ID, vehicle_ID):
    vehicle = Favourite.query.filter_by(vehicle_id=vehicle_ID,user_id=user_ID).first()
    if vehicle is None:
        existe = Vehicle.query.filter_by(id=vehicle_ID).first()
        if existe is None:
            return jsonify({"msg":"El vehiculo no existe."}),404
        else:
            user = User.query.filter_by(id=user_ID).first()
            if user is None:
                return jsonify({"msg":"El usuario no existe"}),404
            else:
                new_favourite = Favourite(vehicle_id=vehicle_ID,user_id=user_ID)
                db.session.add(new_favourite)
                db.session.commit()
                return jsonify({"msg":"Vehiculo agregado a favoritos"}),200
    else:
        return jsonify({"msg":"El vehiculo ya ha sido agregado"}),404

#METODO DELETE CHARACTER
@app.route('/favourite/characters/<int:user_ID>/<int:character_ID>', methods=['DELETE'])
def borrar_character_fav(user_ID, character_ID):
    # Aquí verificamos si el usuario ingresado existe
    user_fav = User.query.filter_by(id=user_ID).first()
    if user_fav is None:
        return jsonify({"msg": "El usuario ingresado no existe"}), 404
    #Aquí verificamos si el personaje ya esté ingresado en favoritos
    fav_character = Character.query.filter_by(id=character_ID).first()
    if fav_character is None:
        return jsonify({"msg": "El personaje ingresado no existe dentro de favoritos"}), 404
    #Aquí le indicamos que debe borrar al personaje seleccionado
    borrar_character = Favourite.query.filter_by(user_id=user_ID).filter_by(character_id=character_ID).first()
    if borrar_character is None:
        return jsonify({"msg":"El personaje no existe dentro de favoritos"}),404
    else:
        db.session.delete(borrar_character)
        db.session.commit()
        return jsonify({"msg": "El personaje seleccionado fue borrado con exito"}), 200

#DELETE PLANET
@app.route('/favourite/planets/<int:user_ID>/<int:planet_ID>', methods=['DELETE'])
def borrar_planet_fav(user_ID, planet_ID):
    # Aquí verificamos si el usuario ingresado existe
    user_fav = User.query.filter_by(id=user_ID).first()
    if user_fav is None:
        return jsonify({"msg": "El usuario ingresado no existe"}), 404
    #Aquí verificamos si el planeta ya esta ingresado en favoritos
    fav_planet = Planet.query.filter_by(id=planet_ID).first()
    if fav_planet is None:
        return jsonify({"msg": "El planeta ingresado no existe dentro de favoritos"}), 404
    #Aquí le indicamos que debe borrar al planeta seleccionado
    borrar_planet = Favourite.query.filter_by(user_id=user_ID).filter_by(planet_id=planet_ID).first()
    if borrar_planet is None:
        return jsonify({"msg":"El planeta no existe dentro de favoritos"}),404
    else:
        db.session.delete(borrar_planet)
        db.session.commit()
        return jsonify({"msg": "El planeta seleccionado fue borrado con exito"}), 200

#DELETE VEHICLE
@app.route('/favourite/vehicles/<int:user_ID>/<int:vehicle_ID>', methods=['DELETE'])
def borrar_vehicle_fav(user_ID, vehicle_ID):
    # Aquí verificamos si el usuario ingresado existe
    user_fav = User.query.filter_by(id=user_ID).first()
    if user_fav is None:
        return jsonify({"msg": "El usuario ingresado no existe"}), 404
    #Aquí verificamos si el vehiculo ya esta ingresado en favoritos
    fav_vehicle = Vehicle.query.filter_by(id=vehicle_ID).first()
    if fav_vehicle is None:
        return jsonify({"msg": "El vehiculo ingresado no existe dentro de favoritos"}), 404
    #Aquí le indicamos que debe borrar al vehiculo seleccionado
    borrar_vehicle = Favourite.query.filter_by(user_id=user_ID).filter_by(vehicle_id=vehicle_ID).first()
    if borrar_vehicle is None:
        return jsonify({"msg":"El vehiculo no existe dentro de favoritos"}),404
    else:
        db.session.delete(borrar_vehicle)
        db.session.commit()
        return jsonify({"msg": "El vehiculo seleccionado fue borrado con exito"}), 200


    
#ACA TERMINAMOS DE TRABAJAR
# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
