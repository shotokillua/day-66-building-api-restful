from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)
app.app_context().push() # app_context().push() methods push the application context into the context stack (access to the application context is required for code to be executed)
##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=True)
    img_url = db.Column(db.String(500), nullable=True)
    location = db.Column(db.String(250), nullable=True)
    seats = db.Column(db.String(250), nullable=True)
    has_toilet = db.Column(db.Boolean, nullable=True)
    has_wifi = db.Column(db.Boolean, nullable=True)
    has_sockets = db.Column(db.Boolean, nullable=True)
    can_take_calls = db.Column(db.Boolean, nullable=True)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

## HTTP GET - Read Record
@app.route("/")
def home():
    return render_template("index.html")

# def to_dict(self):
#     # Method 1.
#     dictionary = {}
#     # Loop through each column in the data record
#     for column in self.__table__.columns:
#         # Create a new dictionary entry;
#         # where the key is the name of the column
#         # and the value is the value of the column
#         dictionary[column.name] = getattr(self, column.name)
#     return dictionary

    # # Method 2. Altenatively use Dictionary Comprehension to do the same thing.
    # return {column.name: getattr(self, column.name) for column in self.__table__.columns}
    #             # {key}        # {value}

@app.route('/random', methods=["GET"])
def get_random_cafe():
    if request.method == "GET":
        cafe_random = random.choice(db.session.query(Cafe).all()) # choose a random record object in the database
        dic = cafe_random.__dict__ # turn that object into a dictionary
        del dic['_sa_instance_state'] # delete the 'sa_instance_state' element bc it cannot be passed into a json
        return jsonify(cafe=dic)


@app.route("/all")
def get_all_cafes():
    cafes = db.session.query(Cafe).all() # this is a list
    #This uses a List Comprehension but you could also split it into 3 lines.
    return jsonify(cafes=[cafe.to_dict() for cafe in cafes])

@app.route('/search')
def search():
    query_location = request.args.get("loc")
    cafe = db.session.query(Cafe).filter_by(location=query_location).first()
    if cafe:
        return jsonify(cafe=cafe.to_dict())
    else:
        return jsonify(error={'Not Found': "Sorry, we don't have a cafe at that location."})

## HTTP POST - Create Record
@app.route("/add", methods=["POST"])
def post_new_cafe():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("loc"),
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        can_take_calls=bool(request.form.get("calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price"),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})

## HTTP PUT/PATCH - Update Record

@app.route('/update-price/<int:cafe_id>', methods=["PATCH"])
def patch_new_price(cafe_id):
    new_price = request.args.get('new_price')
    cafe = db.session.query(Cafe).get(cafe_id)
    if cafe:
        cafe.coffee_price = new_price
        db.session.commit()
        ## Just add the code after the jsonify method. 200 = Ok
        return jsonify(response={"success": "Successfully updated the price."}), 200
    else:
        # 404 = Resource not found
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404

## HTTP DELETE - Delete Record

@app.route('/report-closed/<int:cafe_id>', methods=["DELETE"])
def delete_cafe(cafe_id):
    api_key = request.args.get('api-key')
    if api_key == "TopSecretAPIKey":
        cafe = db.session.query(Cafe).get(cafe_id)
        if cafe:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(response={"success": "Successfully deleted the cafe from the database."}), 200
        else:
            return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404
    else:
        return jsonify(error={"Forbidden": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


if __name__ == '__main__':
    app.run(debug=True)

# Published API Documention --> https://documenter.getpostman.com/view/27004415/2s93Y2T2YD
# from flask import Flask, jsonify, render_template, request
# from flask_sqlalchemy import SQLAlchemy
# import random
#
# app = Flask(__name__)
#
# ##CREATE DB
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy(app)
#
#
# ##CREATE TABLE
# class Cafe(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(250), unique=True, nullable=False)
#     map_url = db.Column(db.String(500), nullable=False)
#     img_url = db.Column(db.String(500), nullable=False)
#     location = db.Column(db.String(250), nullable=False)
#     seats = db.Column(db.String(250), nullable=False)
#     has_toilet = db.Column(db.Boolean, nullable=False)
#     has_wifi = db.Column(db.Boolean, nullable=False)
#     has_sockets = db.Column(db.Boolean, nullable=False)
#     can_take_calls = db.Column(db.Boolean, nullable=False)
#     coffee_price = db.Column(db.String(250), nullable=True)
#
#     def to_dict(self):
#         return {column.name: getattr(self, column.name) for column in self.__table__.columns}
#
#
# @app.route("/")
# def home():
#     return render_template("index.html")
#
#
# @app.route("/random")
# def get_random_cafe():
#     cafes = db.session.query(Cafe).all()
#     random_cafe = random.choice(cafes)
#     return jsonify(cafe=random_cafe.to_dict())
#
#
# @app.route("/all")
# def get_all_cafes():
#     cafes = db.session.query(Cafe).all()
#     return jsonify(cafes=[cafe.to_dict() for cafe in cafes])
#
#
# @app.route("/search")
# def get_cafe_at_location():
#     query_location = request.args.get("loc")
#     cafe = db.session.query(Cafe).filter_by(location=query_location).first()
#     if cafe:
#         return jsonify(cafe=cafe.to_dict())
#     else:
#         return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."}), 404
#
#
# @app.route("/add", methods=["POST"])
# def post_new_cafe():
#     new_cafe = Cafe(
#         name=request.form.get("name"),
#         map_url=request.form.get("map_url"),
#         img_url=request.form.get("img_url"),
#         location=request.form.get("loc"),
#         has_sockets=bool(request.form.get("sockets")),
#         has_toilet=bool(request.form.get("toilet")),
#         has_wifi=bool(request.form.get("wifi")),
#         can_take_calls=bool(request.form.get("calls")),
#         seats=request.form.get("seats"),
#         coffee_price=request.form.get("coffee_price"),
#     )
#     db.session.add(new_cafe)
#     db.session.commit()
#     return jsonify(response={"success": "Successfully added the new cafe."})
#
#
# @app.route("/update-price/<int:cafe_id>", methods=["PATCH"])
# def patch_new_price(cafe_id):
#     new_price = request.args.get("new_price")
#     cafe = db.session.query(Cafe).get(cafe_id)
#     if cafe:
#         cafe.coffee_price = new_price
#         db.session.commit()
#         return jsonify(response={"success": "Successfully updated the price."}), 200
#     else:
#         return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404
#
#
# @app.route("/report-closed/<int:cafe_id>", methods=["DELETE"])
# def delete_cafe(cafe_id):
#     api_key = request.args.get("api-key")
#     if api_key == "TopSecretAPIKey":
#         cafe = db.session.query(Cafe).get(cafe_id)
#         if cafe:
#             db.session.delete(cafe)
#             db.session.commit()
#             return jsonify(response={"success": "Successfully deleted the cafe from the database."}), 200
#         else:
#             return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404
#     else:
#         return jsonify(error={"Forbidden": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403
#
#
# if __name__ == '__main__':
#     app.run(debug=True)