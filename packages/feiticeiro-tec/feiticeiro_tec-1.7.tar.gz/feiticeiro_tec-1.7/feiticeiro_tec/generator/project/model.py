from datetime import datetime
from feiticeiro_tec.secury import Secury
from .. import db
class Model(Secury):
    secury_key_lock = 'secret'
    id = db.Column(db.Integer,primary_key=True)
    data_criacao = db.Column(db.DateTime,default=datetime.utcnow())