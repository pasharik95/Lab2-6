from flask import Flask
import json
import requests
from flask import render_template, request
from flask import redirect
from flask_wtf import Form
from wtforms import StringField
from wtforms import DateField
from wtforms import IntegerField
from wtforms import SubmitField
from neo4j import import_api_data

from flask import Flask, redirect, url_for, session, request, jsonify
from flask_oauthlib.client import OAuth

#region initialisation
app = Flask(__name__)

app.debug = True
app.secret_key = 'development'
oauth = OAuth(app)

github = oauth.remote_app(
    'github',
    consumer_key='3367efadc12fd02f2d5e',
    consumer_secret='9d116dc625f17260d2ecebdbd69ebcfbbdc103fd',
    request_token_params={'scope': 'user:email'},
    base_url='https://api.github.com/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize'
)

WTF_CSRF_ENABLED = False
#endregion

# region Form
class SFForm(Form):
    # id = IntegerField('id')
    name = StringField('name')
    datereg = DateField('datereg')
    regnumb = IntegerField('regnumb')
    person = IntegerField('Person')
    address = IntegerField('Address')
    submit = SubmitField('submit')
# endregion

# region API routing
@app.route('/')
def index():
    form = SFForm(csrf_enabled=False)
    r = requests.get('http://127.0.0.1:5010/api/SF')
    data = json.loads(r.text)
    #print(r.text)
    if 'github_token' in session:
        return render_template('authorized.html', objects=data["objects"], form=form)
    return render_template('unauthorized.html', objects=data["objects"], form=form)

@app.route('/delete/<int:SF_id>')
def delete(SF_id):
    r = requests.delete('http://127.0.0.1:5010/api/SF/' + str(SF_id))
    #import_api_data()
    return index()


@app.route('/update/<int:SF_id>')
def update(SF_id):
    form = SFForm(csrf_enabled=False)
    r = requests.get('http://127.0.0.1:5010/api/SF/'+str(SF_id))
    data = json.loads(r.text)
    #print(r.text)
    return render_template('update.html', SF=data, form=form)


@app.route('/send_update/<int:SF_id>', methods=['POST'])
def send_update(SF_id):
    name = str(request.form['name'])
    datereg = str(request.form['datereg'])
    regnumb = int(request.form['regnumb'])
    address_id = int(request.form['address'])
    person_id = int(request.form['person'])
    # creation_date = request.form['creation_date']
    # approval_date = request.form['approval_date']
    header = {'Content-Type':'application/json'}
    data = json.dumps({
                       "name": name,
                       "datereg": datereg,
                       "regnumb": regnumb,
                       "address_id":address_id,
                       "person_id":person_id})

    print(data)
    r = requests.patch('http://127.0.0.1:5010/api/SF/' + str(SF_id), data=data, headers=header)
    # r = requests.patch('http://127.0.0.1:5010/api/method/' + str(method_id))
    # r._content =
    #import_api_data()
    return index()


@app.route('/add', methods=['POST'])
def add():
    name = str(request.form['name'])
    datereg = str(request.form['datereg'])
    regnumb = int(request.form['regnumb'])
    address_id = int(request.form['address'])
    person_id = int(request.form['person'])
    # creation_date = request.form['creation_date']
    # approval_date = request.form['approval_date']
    header = {'Content-Type':'application/json'}
    data = json.dumps({
                       "name": name,
                       "datereg": datereg,
                       "regnumb": regnumb,
                       "address_id":address_id,
                       "person_id":person_id})
    r = requests.post('http://127.0.0.1:5010/api/SF', headers=header, data=data)
    #import_api_data()
    return index()
# endregion

# region OAuth routing
@app.route('/login')
def login():
    return github.authorize(callback=url_for('authorized', _external=True))


@app.route('/logout')
def logout():
    session.pop('github_token', None)
    return redirect(url_for('index'))


@app.route('/login/authorized')
def authorized():
    resp = github.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error'],
            request.args['error_description']
        )
    session['github_token'] = (resp['access_token'], '')
    me = github.get('user')
    return index()


@github.tokengetter
def get_github_oauth_token():
    return session.get('github_token')
#endregion

#region PDF

@app.route('/print')
def print_form():
    r = requests.get('http://127.0.0.1:5010/api/demand')
    demand_data = json.loads(r.text)
    r = requests.get('http://127.0.0.1:5010/api/debtor')
    debtor_data = json.loads(r.text)
    r = requests.get('http://127.0.0.1:5010/api/creditor')
    creditor_data = json.loads(r.text)
    return render_template('print.html',
                           demands=demand_data["objects"],
                           debtors=debtor_data["objects"],
                           creditors=creditor_data["objects"])

# @app.route('/pdf/<string:name>')
# def generate_pdf(name):
#     pdfkit.from_url('http://127.0.0.1:5000/print', name + ".pdf")
#     return name + ".pdf generated"

#endregion

if __name__ == '__main__':
    app.run()
