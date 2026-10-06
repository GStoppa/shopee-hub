from app import create_app
from app.extensions import db
from app.models.user_model import User

app = create_app()

with app.app_context():
    db.create_all()
    if not User.find_by_email("admin@shopee.com"):
        admin = User(name="Administrador Shopee", email="admin@shopee.com")
        admin.set_password("123456")
        db.session.add(admin)
        db.session.commit()
        print("Utilizador de teste criado com sucesso!")
    else:
        print("Utilizador de teste já existe na base de dados.")