import os
from flask import Flask
from flask import request, render_template, make_response, jsonify

from flask.ext import restful
from flask.ext.pymongo import PyMongo
from flask.ext.pymongo import MongoClient
from bson.json_util import dumps
from bson.objectid import ObjectId

from flask.ext.restful import reqparse

## Patch for Flask-Restful
## http://blog.alienretro.com/using-mongodb-with-flask-restful/
## http://flask-restful.readthedocs.org/en/latest/extending.html
def output_json(obj, code, headers=None):
  """Output a JSON response from a MONGO BSON.

  This is needed because we need to use a custom JSON converter
  that knows how to translate MongoDB types to JSON.
  """
  resp = make_response(dumps(obj), code)
  resp.headers.extend(headers or {})

  return resp

DEFAULT_REPRESENTATIONS = {'application/json': output_json}

app = Flask(__name__)

MONGO_URL = os.environ.get('MONGOHQ_URL')
#connection = Connection(MONGO_URL)
client = MongoClient(MONGO_URL)
 
db = client.articles

@app.route('/robots.txt')
def robots():
  res = app.make_response('User-agent: *\nAllow: /')
  res.mimetype = 'text/plain'
  return res


@app.route('/')
def hello():
	return 'Hello World!'


## Start of UVG Tot API

api = restful.Api(app)
api.representations = DEFAULT_REPRESENTATIONS


class ArticleAPIList(restful.Resource):
  '''Handle Individual article Resources'''

  def get(self):
    return db.articles.find()


  def put(self):
    return {},404


api.add_resource(ArticleAPIList, '/articles')
