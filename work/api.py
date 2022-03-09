from email import header, message
from functools import wraps
from lib2to3.pgen2 import token
import traceback
from flask import Blueprint, render_template, abort, request
import json
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="cred_sml.json"
from firebase_admin import firestore, auth
db= firestore.client()

def checkToken(f):
    @wraps(f)
    def decorated_function(*args, **kws):
        if not 'Authorization' in request.headers:
            abort(401, {'message': 'Unauthorized caller'})
        user = None
        try:
            data = request.headers['Authorization']
            header_token = str(data)
            token = header_token.split(" ")[-1]
            user = auth.verify_id_token(token)
            kws['uid'] = user['uid']
            kws['email'] = user['email']

        except Exception:
            traceback.print_exc()
            abort(401)

        return f(*args,**kws)
    return decorated_function

user_info = Blueprint('user_info', __name__)

@user_info.route('/user', methods=['POST'])
def store_user_info():
    user_info=request.json
    
    db.collection('user_info').document().set(user_info)
    return json.dumps({
        'status':"ok"
    })
@user_info.route('/list-entries',methods=['POST'])
def list_entries():
    email=request.json.get('email')
    documents=db.collection("user_info").where('email',u'==',email).get()
    listOfEntries = [ document.reference.id for document in documents]
    return json.dumps({
        "status":"ok",
        "entries":listOfEntries
    })

@user_info.route('/details/<id>',methods=['GET'])
def details(id):
    data = db.collection("user_info").document(id).get().to_dict()
    return json.dumps({
        "status":"ok",
        "data":data
    })
@user_info.route('/alldata',methods=['GET'])
def all_users(*args, **kws):    
    alldata = db.collection('user_info').get()    
    allId = [ user.reference.id for user in alldata]
    listUsers = []
    for eachId in allId:
        tempData = db.collection('user_info').document(eachId).get().to_dict()
        tempData['docId'] = eachId
        listUsers.append(tempData)
    print(listUsers)

    return json.dumps({
        "status": "ok",
        "users": listUsers
    })


@user_info.route('/update-email',methods=['POST'])
def update_email():
    id=request.json.get('id')
    email=request.json.get('email')
    data=db.collection("user_info").document(id)
    data.update({'email':email})
    return json.dumps({
        "status":"ok",
    })

@user_info.route('/delete-entry',methods=['POST'])
def delete_entry():
    id=request.json.get('id')
    data=db.collection("user_info").document(id)
    data.delete()
    return json.dumps({
        "status":"ok",
    })