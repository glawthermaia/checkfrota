from flask import render_template, request, redirect, url_for
from flask_login import login_required
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash
from models.Conexao import engine
from models.Usuario import Usuario


def init_usuario_routes(app):
    Session = sessionmaker(bind=engine)

    @app.route("/usuarios")
    @login_required
    def lista_usuarios():
        session = Session()
        usuarios = session.query(Usuario).all()
        session.close()
        return render_template("usuarios/list.html", usuarios=usuarios)

    @app.route("/usuarios/novo")
    def cadastro_usuario():
        return render_template("usuarios/cad.html", usuario=None)

    @app.route("/usuarios/editar/<int:id>")
    @login_required
    def pre_editar_usuario(id):
        session = Session()
        usuario = session.query(Usuario).filter_by(id=id).first()
        session.close()
        return render_template("usuarios/cad.html", usuario=usuario)

    @app.route("/usuarios/salvar", methods=["POST"])
    def salvar_usuario():
        session = Session()
        id_usuario = request.form.get("id")
        nome = request.form.get("nome")
        usuario_email = request.form.get("usuario")
        senha = request.form.get("senha")

        if id_usuario:
            u = session.query(Usuario).filter_by(id=int(id_usuario)).first()
            if u:
                u.nome = nome
                u.usuario = usuario_email
                if senha:
                    u.senha = generate_password_hash(senha)
        else:
            novo = Usuario(
                id=None,
                usuario=usuario_email,
                nome=nome,
                senha=generate_password_hash(senha),
            )
            session.add(novo)

        session.commit()
        session.close()
        return redirect(url_for("login"))

    @app.route("/usuarios/deletar/<int:id>")
    @login_required
    def deletar_usuario(id):
        session = Session()
        u = session.query(Usuario).filter_by(id=id).first()
        if u:
            session.delete(u)
            session.commit()
        session.close()
        return redirect(url_for("lista_usuarios"))