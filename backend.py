import os
from flask import Flask
from flask import request, render_template, make_response, jsonify

from flask.ext import restful
from flask.ext.pymongo import PyMongo
from bson.json_util import dumps
from bson.objectid import ObjectId

from flask.ext.restful import reqparse

DEFAULT_REPRESENTATIONS = {'application/json': output_json}

app = Flask(__name__)

mongo = PyMongo(app, config_prefix="MONGOHQ_URL")


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
    return mongo.db.articles.find()


  def put(self):
    return {},404


api.add_resource(ArticleAPIList, '/articles')
