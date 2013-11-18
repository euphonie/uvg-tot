import os
import ast
import datetime
from flask import Flask
from flask import request,flash, render_template, make_response, jsonify

import logging
from logging.handlers import RotatingFileHandler

from flask.ext import restful
from flask.ext.pymongo import PyMongo
from flask.ext.pymongo import MongoClient
from bson.json_util import dumps
from bson.objectid import ObjectId
from werkzeug.routing import BaseConverter, ValidationError
from itsdangerous import base64_encode, base64_decode
from bson.errors import InvalidId

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

def valid_unicode(value, name):
	'''Converts query to unicode '''
	v = unicode(value)
	return v

def valid_tag_list(value,name):
	return ast.literal_eval(value)

DEFAULT_REPRESENTATIONS = {'application/json': output_json}

app = Flask(__name__)
app.secret_key = 'Ya1jNH2RvZg3kf9G7u4i6T2U82lD4Nz1'

if not app.debug:
	MONGO_URL = os.environ.get('MONGOHQ_URL')
	client = MongoClient(MONGO_URL)
else :
	client = MongoClient()
db = client['app19537990']

@app.errorhandler(500)
def internal_error(exception):
	app.logger.exception(exception)
	return render_template('500.html'), 500

@app.route('/robots.txt')
def robots():
	res = app.make_response('User-agent: *\nAllow: /')
	res.mimetype = 'text/plain'
	return res

@app.route('/')
def feed():
	query = request.args.get('q')
	if query is not None:
		clean_dict = {}
		clean_dict['title'] = {'$regex':query,'$options':'i'}
		clean_dict['content'] = {'$regex':query,'$options':'i'}
		clean_dict['tag_list'] = {'$elemMatch':{'tag':query}}
		return render_template('feed.html',articles=db.articles.find({'$or':[{'title':clean_dict['title']}, {'content':clean_dict['content']}, {'tag_list':clean_dict['tag_list']}]}),results=True)
	else:
		return render_template('feed.html',articles=db.articles.find())
	
@app.route('/about')
def about():
	return render_template('about.html')

@app.route('/view/<article_id>')
def view(article_id=-1):
	article_view = db.articles.find({'_id':ObjectId(article_id)})
	return render_template('view.html',article=article_view)

@app.route('/new')
def new():
	return render_template('new.html')

@app.route('/publish', methods=['POST'])
def publish():
	values = {}
	values['title'] = request.form['title']
	values['content'] = request.form['content']
	tags = []
	for tag in (request.form['tag-list'].split(',')):
		tags.append({'tag':tag})
	values['tag_list'] = tags
	values['contact_name'] = request.form['contact_name']
	values['contact_phone'] = request.form['contact_phone']
	values['contact_email'] = request.form['contact_email']
	flash('Publicado exitosamente!','success')
	db.articles.insert(values)
	return render_template('feed.html',articles=db.articles.find())
	
## Start of UVG Tot API

api = restful.Api(app)
api.representations = DEFAULT_REPRESENTATIONS

search_parser = reqparse.RequestParser()
search_parser.add_argument('q', type=valid_unicode)
search_parser.add_argument('type',type=str)

insertion_parser = reqparse.RequestParser()
insertion_parser.add_argument('title', type=str)
insertion_parser.add_argument('content',type=str)
insertion_parser.add_argument('tag_list',type=valid_tag_list)
insertion_parser.add_argument('contact_name',type=str)
insertion_parser.add_argument('contact_phone',type=str)
insertion_parser.add_argument('contact_mail',type=str)

class ArticleAPI(restful.Resource):
	''' Handle Individual article resource'''
	def get(self, article_id=-1):
		app.logger.info(article_id)
		return db.articles.find({'_id':ObjectId(article_id)})
		
	def post(self):
		article = insertion_parser.parse_args()
		article["creation_date"] = datetime.datetime.utcnow()
		response = db.articles.insert(article)
		return response

class ArticleAPIList(restful.Resource):
	'''Handle List of article Resources'''

	def get(self):
		input_dict = search_parser.parse_args()
		clean_dict = {}
		if input_dict == {}:
			return db.articles.find()
		else:
			clean_dict['title'] = {'$regex':input_dict['q'],'$options':'i'}
			clean_dict['content'] = {'$regex':input_dict['q'],'$options':'i'}
			clean_dict['tag_list'] = {'$elemMatch':{'tag':query}}
			return db.articles.find({'$or':[{'title':clean_dict['title']}, {'content':clean_dict['content']},{'tag_list':clean_dict['tag_list']}]})


api.add_resource(ArticleAPIList, '/articles')
api.add_resource(ArticleAPI,'/article','/article/<article_id>')


if __name__ == '__main__':
	handler = RotatingFileHandler('foo.log', maxBytes=10000, backupCount=1)
	handler.setLevel(logging.INFO)
	app.logger.addHandler(handler)
	app.run(debug=False)
	