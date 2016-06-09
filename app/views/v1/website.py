import os
import requests
import json
from flask import request, jsonify, render_template, redirect, url_for, session, abort
from react.render import render_component
from apiclient import discovery
import httplib2
from oauth2client import client
from app import webapp
from app.models import *
from app.decorators import user_session

components_path = os.path.join(os.path.dirname(__file__), '../../', 'static', 'js', 'src', 'components')

def path(js_file):
    return os.path.join(components_path, js_file)

@webapp.route('/')
@user_session
def homepage(props):
    store = {'component': 'home.jsx'}
    collections = Collection.getHomepageCollections() 
    props.update({
        'collections': collections,
        'page': 'home'
        })
    store['props'] = props
    rendered = render_component(path(store['component']), props=props)
    return render_template('index.html', 
            rendered=rendered, 
            title='Home', 
            store=store)

@webapp.route('/books/')
@webapp.route('/book/')
@webapp.route('/books/category/')
@webapp.route('/books/category/<int:category_id>')
@webapp.route('/books/category/<category_slug>')
@webapp.route('/books/collection/')
@webapp.route('/books/collection/<int:collection_id>')
@webapp.route('/books/collection/<int:collection_id>-<slug>')
@user_session
def catalog(**kwargs):
    store = {'component': 'catalog.jsx'}
    query = Utils.getParam(request.args, 'q', default='')
    search_type = Utils.getParam(request.args, 'type', default='free')
    page = Utils.getParam(request.args, 'page', var_type='int', default=1)
   
    results, catalog = [], []
    if query:
        results = WebUtils.fetchSearchResults(query, search_type, page)  
    elif 'category_slug' in kwargs or 'category_id' in kwargs:
        entity = 'category_id' if 'category_id' in kwargs else 'category_slug'
        query = Item.fetchCategory(slug=kwargs[entity])['category_name']
        results = WebUtils.fetchSearchResults(query, 'category', page)  
    elif 'collection_id' in kwargs:
        results = Collection(kwargs['collection_id']).getObj()
        query = results['name']
        #results = WebUtils.fetchSearchResults(query, 'collection', page)   
        # NOTE alternate source: from DB
        results['items'] = WebUtils.extendItemWebProperties(results['items'])
    else:
        catalog = Collection.getHomepageCollections(items=True)
    props = kwargs['props']
    props.update({
            'search_results': results,
            'catalog': catalog,
            'categories': Search.getAllSearchCategories(),
            'query': query,
            'page': 'catalog',
            'page_num': page
            })
    store['props'] = props
    rendered = render_component(path(store['component']), props=props)
    return render_template('catalog.html',
            rendered=rendered,
            title='Catalog',
            store=store)
   
@webapp.route('/book/rent/<int:item_id>')
@webapp.route('/book/rent/<int:item_id>-<slug>')
@user_session
def itemPage(**kwargs):
    store = {'component': 'item.jsx'}
    item_data = Search().getById([kwargs['item_id']]) 
    if item_data:
        item_data = item_data[0]
        categories = []
        for category in item_data['categories']:
            categories.append(Item.fetchCategory(name=category)) 
        item_data['categories'] = categories
        # get reviews
        # get metadata info
    else:
        abort(404)

    # NOTE switchable: elasticsearch/DB
    #item_data = Item(kwargs['item_id']).getObj()
    #item_data.update(Item.getCustomProperties([item_data]))

    item_data['img_small'] = webapp.config['S3_HOST'] + item_data['img_small'] 
    props = kwargs['props']
    props.update({
        'item_data': item_data,
        'page': 'item'
        })
    store['props'] = props
    rendered = render_component(path(store['component']), props=props)
    return render_template('item.html',
            rendered=rendered,
            title=item_data['item_name'],
            store=store)

@webapp.route('/terms/')
@user_session
def terms(props):
    store = {'component': 'terms.jsx'}
    store['props'] = props
    rendered = render_component(path(store['component']), props=props)
    return render_template('terms.html',
            rendered=rendered,
            title='Terms and Conditions',
            store=store) 


@webapp.route('/googlesignin', methods=['POST'])
def googlesignin():
    auth_code = Utils.getParam(request.form, 'data', '')
    if not auth_code:
        return ''
    client_secret_file = '/etc/ostrich_conf/google_client_secret.json' 
    credentials = client.credentials_from_clientsecrets_and_code(
           client_secret_file,
           ['profile', 'email'],
           auth_code)
    http_auth = credentials.authorize(httplib2.Http())
    users_service = discovery.build('oauth2', 'v2', http=http_auth)
    user_document = users_service.userinfo().get().execute()

    from app import cache
    cache_key = credentials.id_token['sub']
    user = cache.get(cache_key)
    if not user:
        user_data = {
            'username': user_document['email'],
            'name': user_document['name'],
            'email': user_document['email'],
            'google_id': credentials.id_token['sub'],
            'picture': user_document['picture'],
            'source': 'web'
            }

        user = User.createUser(user_data)
        WebUtils.storeUserSession(user)
    visible_user_data = {
        'user': session['_user']
    }
    return jsonify(data=visible_user_data)


@webapp.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
