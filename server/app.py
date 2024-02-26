#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def home():
    return ''

@app.route('/campers', methods = ['GET', 'POST'])
def campers():
    campers = [camper.to_dict(rules = ('-signups',)) for camper in Camper.query.all()]
    if request.method == 'GET':
        response_body = campers
        status = 200
    elif request.method == 'POST':
        try:
            camper_json = request.get_json()
            camper = Camper()
            for k, v in camper_json.items():
                setattr(camper, k, v)
            
            db.session.add(camper)
            db.session.commit()

            response_body = camper.to_dict()
            status = 201
        except ValueError as e:
            response_body = {"errors": [str(e)]}
            status = 400
    return make_response(response_body, status)        
    
    
@app.route('/campers/<int:id>', methods = ['GET', 'PATCH'])
def camper_by_id(id):
    camper = Camper.query.filter(Camper.id == id).first()

    if not camper:
        response_body = {'error': 'Camper not found'}
        status = 404
    else:
        if request.method == 'GET':
            response_body = camper.to_dict()
            status = 200
        elif request.method == 'PATCH':
            try:
                camper_json = request.get_json()
                for k, v in camper_json.items():
                    setattr(camper, k, v)
                
                db.session.commit()

                response_body = camper.to_dict()
                status = 202
            except ValueError as e:
                response_body = {"errors": [str(e)]}
                status = 400
    return make_response(response_body, status)

@app.route('/activities')
def activities():
    activities = [activity.to_dict(rules = ('-signups',)) for activity in Activity.query.all()]
    return make_response(activities, 200)

@app.route('/activities/<int:id>', methods = ['DELETE'])
def activity_by_id(id):
    activity = Activity.query.filter(Activity.id == id).first()
    
    if not activity:
        response_body = {'error': 'Activity not found'}
        status = 404
    else:
        if request.method == 'DELETE':
            db.session.delete(activity)
            db.session.commit()

            response_body = {}
            status = 204
    
    return make_response(response_body, status)

@app.route('/signups', methods=['POST'])
def signups():

    if request.method == 'POST':
        try:
            signup_json = request.get_json()
            signup = Signup()

            for k,v in signup_json.items():
                setattr(signup, k, v)
            
            db.session.add(signup)
            db.session.commit()

            response_body = signup.to_dict()
            status = 201

        except ValueError as e:
            response_body = {'errors': [str(e)]}
            status = 400

    return make_response(response_body, status)

if __name__ == '__main__':
    app.run(port=5555, debug=True)
