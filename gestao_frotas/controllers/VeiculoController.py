from datetime import datetime
from flask import render_template, request, redirect, url_for
from flask_login import login_required
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker, joinedload

from models.Conexao import engine
from models.Veiculo import Veiculo


def init_veiculo_routes(app):
    Session = sessionmaker(bind=engine)

    @app.route("/veiculos")
    @login_required
    def lista_veiculos():
        session = Session()
        status = request.args.get("status", "").strip()
        marca = request.args.get("marca", "").strip()
        modelo = request.args.get("modelo", "").strip()
        msg = request.args.get("msg", "")

        query = session.query(Veiculo).options(joinedload(Veiculo.manutencoes))

        if status:
            query = query.filter(Veiculo.status == status)
        if marca:
            query = query.filter(Veiculo.marca.ilike(f"%{marca}%"))
        if modelo:
            query = query.filter(Veiculo.modelo.ilike(f"%{modelo}%"))

        veiculos = query.order_by(Veiculo.id.desc()).all()
        session.close()

        return render_template(
            "veiculos/list.html",
            veiculos=veiculos,
            filtro_status=status,
            filtro_marca=marca,
            filtro_modelo=modelo,
            msg=msg,
        )

    @app.route("/veiculos/buscar")
    @login_required
    def buscar_veiculo():
        termo = request.args.get("termo", "").strip()
        if not termo:
            return redirect(url_for("lista_veiculos"))

        session = Session()
        veiculo = None

        if termo.isdigit():
            veiculo = session.query(Veiculo).filter_by(id=int(termo)).first()

        if not veiculo:
            veiculo = session.query(Veiculo).filter(Veiculo.placa.ilike(termo)).first()

        session.close()

        if veiculo:
            return redirect(url_for("detalhar_veiculo", id=veiculo.id))

        return redirect(url_for("lista_veiculos", msg=f"Nenhum veículo encontrado para '{termo}'."))

    @app.route("/veiculos/<int:id>")
    @login_required
    def detalhar_veiculo(id):
        session = Session()
        msg = request.args.get("msg", "")
        veiculo = (
            session.query(Veiculo)
            .options(joinedload(Veiculo.manutencoes))
            .filter_by(id=id)
            .first()
        )
        session.close()

        if not veiculo:
            return redirect(url_for("lista_veiculos", msg="Veículo não encontrado."))

        return render_template("veiculos/detalhe.html", veiculo=veiculo, msg=msg)

    @app.route("/veiculos/novo")
    @login_required
    def cadastro_veiculo():
        return render_template("veiculos/cad.html", veiculo=None)

    @app.route("/veiculos/editar/<int:id>")
    @login_required
    def pre_editar_veiculo(id):
        session = Session()
        veiculo = session.query(Veiculo).filter_by(id=id).first()
        session.close()

        if not veiculo:
            return redirect(url_for("lista_veiculos", msg="Veículo não encontrado."))

        return render_template("veiculos/cad.html", veiculo=veiculo)

    @app.route("/veiculos/salvar", methods=["POST"])
    @login_required
    def salvar_veiculo():
        session = Session()
        id_veiculo = request.form.get("id")
        placa = request.form.get("placa", "").strip().upper()
        marca = request.form.get("marca", "").strip()
        modelo = request.form.get("modelo", "").strip()
        ano_fabricacao = int(request.form.get("ano_fabricacao"))
        chassi = request.form.get("chassi", "").strip().upper()
        data_aquisicao = datetime.strptime(request.form.get("data_aquisicao"), "%Y-%m-%d").date()
        status = request.form.get("status", "Ativo")

        try:
            if id_veiculo:
                v = session.query(Veiculo).filter_by(id=int(id_veiculo)).first()
                if v:
                    v.placa = placa
                    v.marca = marca
                    v.modelo = modelo
                    v.ano_fabricacao = ano_fabricacao
                    v.chassi = chassi
                    v.data_aquisicao = data_aquisicao
                    v.status = status
                msg = f"Veículo {placa} atualizado com sucesso!"
            else:
                novo = Veiculo(
                    placa=placa,
                    marca=marca,
                    modelo=modelo,
                    ano_fabricacao=ano_fabricacao,
                    chassi=chassi,
                    data_aquisicao=data_aquisicao,
                    status=status,
                )
                session.add(novo)
                msg = f"Veículo {placa} cadastrado com sucesso!"

            session.commit()
            session.close()
            return redirect(url_for("lista_veiculos", msg=msg))

        except IntegrityError:
            session.rollback()
            session.close()
            return redirect(
                url_for("lista_veiculos", msg="Erro: Placa ou Chassi já cadastrado em outro veículo.")
            )

    @app.route("/veiculos/desativar/<int:id>")
    @login_required
    def desativar_veiculo(id):
        novo_status = request.args.get("status", "Inativo")
        if novo_status not in ("Inativo", "Vendido"):
            novo_status = "Inativo"

        session = Session()
        v = session.query(Veiculo).filter_by(id=id).first()
        if v:
            v.status = novo_status
            placa = v.placa
            session.commit()
            session.close()
            return redirect(
                url_for(
                    "lista_veiculos",
                    msg=f"Veículo {placa} marcado como '{novo_status}'. Histórico de manutenções preservado.",
                )
            )
        session.close()
        return redirect(url_for("lista_veiculos"))