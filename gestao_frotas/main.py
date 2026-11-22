from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required
from flasgger import Swagger
from sqlalchemy.orm import sessionmaker
from werkzeug.security import check_password_hash

from models.Conexao import engine, Base
from models.Usuario import Usuario
from models import Veiculo, RegistroManutencao
from controllers.UsuarioController import init_usuario_routes
from controllers.VeiculoController import init_veiculo_routes
from controllers.ManutencaoController import init_manutencao_routes
from controllers.VeiculoControllerRest import init_veiculo_rest_routes
from controllers.ManutencaoControllerRest import init_manutencao_rest_routes

app = Flask(__name__)
app.secret_key = "chave-secreta-gestao-frotas-ifce"

Swagger(app)
Base.metadata.create_all(engine)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

Session = sessionmaker(bind=engine)


@login_manager.user_loader
def load_user(user_id):
    session = Session()
    user = session.query(Usuario).filter_by(id=int(user_id)).first()
    session.close()
    return user


@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario_form = request.form.get("usuario")
        senha_form = request.form.get("senha")

        session = Session()
        user = session.query(Usuario).filter_by(usuario=usuario_form).first()
        session.close()

        if user and check_password_hash(user.senha, senha_form):
            login_user(user)
            return redirect(url_for("lista_veiculos"))
        return render_template("login.html", msg="Usuário ou senha inválidos.")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


init_usuario_routes(app)
init_veiculo_routes(app)
init_manutencao_routes(app)
init_veiculo_rest_routes(app)
init_manutencao_rest_routes(app)

if __name__ == "__main__":
    app.run(debug=True, port=5001)