import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth


app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where
    drinks is the list of drinks or appropriate status code indicating reason
    for failure
'''


@app.route('/drinks', methods=['GET'])
def retrieve_drinks():

    drinks = Drink.query.all()

    return jsonify({
        'success': True,
        'drinks': [d.short() for d in drinks]
    }), 200

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where
    drinks is the list of drinks or appropriate status code indicating reason
    for failure
'''


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def retrieve_drinks_details(payload):

    drinks = Drink.query.all()

    return jsonify({
       'success': True,
       'drinks': [d.long() for d in drinks]
    }), 200


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where
    drink an array containing only the newly created drink or appropriate
    status code indicating reason for failure
'''


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_a_drink(payload):
    data = request.get_json()
    title = data.get('title', None)
    recipe = data.get('recipe', None)
    drink = Drink(title=title, recipe=json.dumps(recipe))
    try:
        drink.insert()
    except:
        abort(422)
    return jsonify({
        'success': True,
        'drinks': drink.long()
    }), 200

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where
    drink an array containing only the updated drink or appropriate status code
    indicating reason for failure
'''


@app.route('/drinks/<int:drinks_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drinks(payload, drinks_id):
    data = request.get_json()
    drink = Drink.query.filter(Drink.id == drinks_id).one_or_none()

    if drink is None:
        abort(404)

    try:
        title = data['title']
        recipe = json.dumps(data.get('recipe'))
        drink.title = title
        drink.recipe = recipe
        drink.update()

        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        }), 200

    except:
        abort(422)

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id
    is the id of the deleted record or appropriate status code indicating
    reason for failure
'''


@app.route('/drinks/<int:drinks_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, drinks_id):
    try:
        drink = Drink.query.filter(Drink.id == drinks_id).one_or_none()

        if not drink:
            abort(404)

        drink.delete()

        return jsonify({
            'success': True,
            'drink': drinks_id
        }), 200

    except:
        abort(422)

# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400


@app.errorhandler(401)
def not_authorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "not authorized"
    }), 401


@app.errorhandler(403)
def not_authorized(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "not permitted"
    }), 403
'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''


@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error
    }), error.status_code
