import jwt
from random import randint

class Secury():
    """
    secury_key_lock -> Chave De Criptografia

    todos os attr q tiver _secury_ no inicio ficara com Criptografia
    """
    secury_key_lock = 'senha123'

    def __getattribute__(self,attr):
        if not attr[0] == '_' and  hasattr(self, f'_secury_{attr}'):
            data = getattr(self,f'_secury_{attr}')
            try:
                return jwt.decode(data,self.secury_key_lock,algorithms='HS256')[attr]
            except Exception:
                return 'Você Não Tem Permissão Para Ler Esse Informação'
        return super().__getattribute__(attr)

    def __setattr__(self,attr:str,value):
        if attr.startswith('_secury_'):
            value = jwt.encode({attr[len('_secury_'):]:value},self.secury_key_lock)
            super().__setattr__(attr,value)
            return
        else:
            if hasattr(self, f'_secury_{attr}'):
                value = jwt.encode({attr:value},self.secury_key_lock)
                super().__setattr__(f'_secury_{attr}',value)
                return
        super().__setattr__(attr,value)

if __name__ == '__main__':
    from flask import Flask
    from flask_sqlalchemy import SQLAlchemy
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.db'
    db = SQLAlchemy(app)
    class XX(db.Model,Secury):
        id = db.Column(db.Integer,primary_key=True)
        _secury_teste = db.Column(db.String)
    db.create_all()
    xx = XX()
    xx.teste = 'Ola Mundo'
    db.session.add(xx)
    db.session.commit()
    print(xx.teste)

