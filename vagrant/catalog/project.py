from flask import (Flask, render_template, request, redirect, jsonify, url_for,
                   flash)
# import orm
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User
# import in step 3
from flask import session as login_session
import random, string
# import in step 5
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from oauth2client.client import AccessTokenCredentials
import httplib2, json
from flask import make_response
import requests
import myform
import os
from werkzeug import secure_filename


app = Flask(__name__)
# uploads folder should exists in the server
# app config
UPLOAD_FOLDER = os.path.dirname(__file__)
app.config['UPLOAD_FOLDER'] = os.path.join(UPLOAD_FOLDER, './static/uploads')

CLIENT_ID = json.loads(open('g_client_secrets.json', 'r').
                       read())['web']['client_id']

# Connect to Database and create database session
engine = create_engine('sqlite:///catalogwithusers.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/login')
def showLogin():
    # the state is a verification code that used between client and server
    # so server can be sure that the client is making request not others
    state = ''.join(random.choice(string.ascii_uppercase +
                                  string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    print login_session
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('g_client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # check that the access token is valid
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # if there was an error in the access token info, abort:
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID:"), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    # check if the user has loged in
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials.access_token
    credentials = AccessTokenCredentials(login_session['credentials'], 'user-agent-value')
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['provider'] = 'google'
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # check if user exists, if not, make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    # render a output
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; \
                  height: 300px;\
                  border-radius: 150px;\
                  -webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % (login_session['username']))
    print "done!"
    return output


@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    credentials = AccessTokenCredentials(login_session['credentials'], 'user-agent-value')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# login with facebook
@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data

    # Exchange client token for long-lived server-side token with GET request
    app_id = json.loads(open('fb_client_secrets.json',
                             'r').read())['web']['app_id']
    app_secret = json.loads(open('fb_client_secrets.json',
                                 'r').read())['web']['app_secret']
    url = ('https://graph.facebook.com/'
           'oauth/access_token?grant_type=fb_exchange_token'
           '&client_id=%s&client_secret=%s&fb_exchange_token=%s' %
           (app_id, app_secret, access_token))
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = 'https://graph.facebook.com/v2.4/me'
    # strip expire tag from access token
    token = result.split("&")[0]

    url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    data = json.loads(result)
    # populate login session
    login_session['provider'] = 'facebook'
    login_session['username'] = data['name']
    login_session['email'] = data['email']
    login_session['facebook_id'] = data['id']

    # The token must be stored in the login_session in order to properly logout
    # let's strip out the information before the equals sign in our token
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # retrive profile pic
    url = ('https://graph.facebook.com/v2.4/me/'
           'picture?%s&redirect=0&height=200&width=200' % token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data['data']['url']

    # check if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    # give output
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; \
                  height: 300px;\
                  border-radius: 150px;\
                  -webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    return output


# facebook logout function
@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/\
           permissions?access_token=%s' % (facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return 'You have been loged out'


# a general logout function
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['credentials']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']

        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfull been loged out.")
        return redirect(url_for('showCategories'))
    else:
        flash("You are not logged in yet")
        redirect(url_for('showRestaurants'))


# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    print "use id is: %s" % user.id
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# JSON APIs to view catalog Information
@app.route('/catalog.json')
def catalogJSON():
    categories = session.query(Category).all()
    return jsonify(categories=[r.serialize for r in categories])


# Show all categories and latest added items
@app.route('/')
@app.route('/catalog')
def showCategories():
    categories = session.query(Category).all()
    latestitems = session.query(Item).order_by(desc(Item.id)).limit(10)
    if 'username' not in login_session:
        return render_template('index_public.html',
                               categories=categories,
                               latestitems=latestitems)
    else:
        return render_template('index.html',
                               categories=categories,
                               latestitems=latestitems)


# show all items belonging to one category
@app.route('/catalog/<string:category_name>')
def showCategoryItems(category_name):
    categories = session.query(Category).all()
    items = session.query(Item).filter_by(category_name=category_name).all()
    if len(items) == 0:
        return redirect(url_for('showCategories'))
    return render_template('categoryitems.html', category_name=category_name, categories=categories, items=items)


# show the detail of one item
@app.route('/catalog/<string:category_name>/<string:item_name>')
def showItemDetail(category_name, item_name):
    item = session.query(Item).filter_by(name=item_name).first()
    creator = item.user_id
    if item.pic_name is None:
        item.pic_name = "noItemImage.gif"
    if (('username' not in login_session) or
       (creator != login_session['user_id'])):
        return render_template('itemdetail_public.html', item=item)
    else:
        return render_template('itemdetail.html', item=item)


# add a new item
@app.route('/catalog/newItem/', methods=['GET', 'POST'])
def newItem():
    if 'username' not in login_session:
        return redirect('/login')

    if request.method == 'POST':
        file = request.files['upload']
        if file:
            filename = secure_filename(file.filename)
            filename = str(login_session['user_id']) + "_" + filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            newItem = Item(name=request.form['name'],
                           description=request.form['description'],
                           category_name=request.form['category'],
                           user_id=login_session['user_id'],
                           pic_name=filename)
        else:
            newItem = Item(name=request.form['name'],
                           description=request.form['description'],
                           category_name=request.form['category'],
                           user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()
        flash('New Item %s Successfully Added' % newItem.name)
        return redirect(url_for('showCategories'))
    else:
        categories = session.query(Category).all()
        form = myform.MyForm()
        form.category.choices = [(g.name, g.name) for g in categories]
        # return render_template('newitem.html', categories=categories)
        return render_template('newitem.html', form=form)


# edit an item
@app.route('/catalog/<string:item_name>/edit', methods=['GET', 'POST'])
def editItem(item_name):
    if 'username' not in login_session:
        return redirect('/login')

    editItem = session.query(Item).filter_by(name=item_name).first()

    if login_session['user_id'] != editItem.user_id:
        return "<script>function myFunction() \
                {alert('You are not authorized to edit this item.');\
                window.location.href='/catalog';}\
                </script><body onload='myFunction()'>"

    if request.method == 'POST':
        file = request.files['upload']
        if file:
            editItem.name = request.form['name']
            editItem.description = request.form['description']
            editItem.category_name = request.form['category']
            if editItem.pic_name:
                pic_path = './static/uploads/' + editItem.pic_name
                os.remove(pic_path)
            filename = secure_filename(file.filename)
            filename = login_session['user_id'] + "_" + filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            editItem.pic_name = filename
        else:
            editItem.name = request.form['name']
            editItem.description = request.form['description']
            editItem.category_name = request.form['category']
        session.add(editItem)
        session.commit()
        flash('Item %s Successfully Edited' % editItem.name)
        return redirect(url_for('showCategories'))
    else:
        categories = session.query(Category).all()
        form = myform.MyForm()
        form.category.choices = [(g.name, g.name) for g in categories]
        return render_template('edititem.html', editItem=editItem, form=form)


# delete an item
@app.route('/catalog/<string:item_name>/delete', methods=['GET', 'POST'])
def deleteItem(item_name):
    if 'username' not in login_session:
        return redirect('/login')

    deleteItem = session.query(Item).filter_by(name=item_name).first()

    if login_session['user_id'] != deleteItem.user_id:
        return "<script>function myFunction() \
                {alert('You are not authorized to delete this item.');\
                window.location.href='/catalog';}\
                </script><body onload='myFunction()'>"

    if request.method == 'POST':
        item_pic = deleteItem.pic_name
        if item_pic:
            pic_path = './static/uploads/' + item_pic
            os.remove(pic_path)
        session.delete(deleteItem)
        session.commit()
        flash('Item %s Successfully Deleted' % deleteItem.name)
        return redirect(url_for('showCategories'))
    else:
        return render_template('deleteitem.html', deleteItem=deleteItem)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
