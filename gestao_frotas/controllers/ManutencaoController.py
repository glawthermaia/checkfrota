from datetime import datetime
from decimal import Decimal
from flask import render_template, request, redirect, url_for
from flask_login import login_required
from sqlalchemy.orm import sessionmaker

from models.Conexao import engine
from models.Veiculo import Veiculo
from models.RegistroManutencao import RegistroManutencao


def init_manutencao_routes(app):
    Session = sessionmaker(bind=engine)

    @app.route("/manutencoes/novo/<int:id_veiculo>")
    @login_required
    def cadastro_manutencao(id_veiculo):
        session = Session()
        veiculo = session.query(Veiculo).filter_by(id=id_veiculo).first()
        session.close()

        if not veiculo:
            return redirect(url_for("lista_veiculos", msg="Veículo não encontrado."))

        return render_template("manutencoes/cad.html", veiculo=veiculo, manutencao=None)

    @app.route("/manutencoes/editar/<int:id>")
    @login_required
    def pre_editar_manutencao(id):
        session = Session()
        manutencao = session.query(RegistroManutencao).filter_by(id=id).first()
        if not manutencao:
            session.close()
            return redirect(url_for("lista_veiculos", msg="Registro de manutenção não encontrado."))

        veiculo = session.query(Veiculo).filter_by(id=manutencao.id_veiculo).first()
        session.close()
        return render_template("manutencoes/cad.html", veiculo=veiculo, manutencao=manutencao)

    @app.route("/manutencoes/salvar", methods=["POST"])
    @login_required
    def salvar_manutencao():
        session = Session()
        id_manutencao = request.form.get("id")
        id_veiculo = int(request.form.get("id_veiculo"))
        data_manutencao = datetime.strptime(request.form.get("data_manutencao"), "%Y-%m-%d").date()
        odometro_km = int(request.form.get("odometro_km"))
        tipo_manutencao = request.form.get("tipo_manutencao", "").strip()
        descricao_servico = request.form.get("descricao_servico", "").strip()
        custo = Decimal(request.form.get("custo").replace(",", "."))

        if id_manutencao:
            m = session.query(RegistroManutencao).filter_by(id=int(id_manutencao)).first()
            if m:
                m.data_manutencao = data_manutencao
                m.odometro_km = odometro_km
                m.tipo_manutencao = tipo_manutencao
                m.descricao_servico = descricao_servico
                m.custo = custo
            msg = "Registro de manutenção atualizado com sucesso!"
        else:
            nova = RegistroManutencao(
                id_veiculo=id_veiculo,
                data_manutencao=data_manutencao,
                odometro_km=odometro_km,
                tipo_manutencao=tipo_manutencao,
                descricao_servico=descricao_servico,
                custo=custo,
            )
            session.add(nova)
            msg = "Manutenção registrada com sucesso!"

        session.commit()
        session.close()
        return redirect(url_for("detalhar_veiculo", id=id_veiculo, msg=msg))

    @app.route("/manutencoes/deletar/<int:id>")
    @login_required
    def deletar_manutencao(id):
        session = Session()
        m = session.query(RegistroManutencao).filter_by(id=id).first()
        if m:
            id_veiculo = m.id_veiculo
            session.delete(m)
            session.commit()
            session.close()
            return redirect(
                url_for("detalhar_veiculo", id=id_veiculo, msg="Registro de manutenção excluído.")
            )
        session.close()
        return redirect(url_for("lista_veiculos"))