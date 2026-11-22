from datetime import datetime
from decimal import Decimal
from flask import request, jsonify
from sqlalchemy.orm import sessionmaker

from models.Conexao import engine
from models.Veiculo import Veiculo
from models.RegistroManutencao import RegistroManutencao


def init_manutencao_rest_routes(app):
    Session = sessionmaker(bind=engine)

    @app.route("/v1/veiculos/<int:id_veiculo>/manutencoes", methods=["GET"])
    def api_listar_manutencoes_veiculo(id_veiculo):
        """
        Listar histórico de manutenções de um veículo
        ---
        tags:
          - Manutenções
        parameters:
          - name: id_veiculo
            in: path
            type: integer
            required: true
        responses:
          200:
            description: Lista de manutenções do veículo
        """
        session = Session()
        registros = (
            session.query(RegistroManutencao)
            .filter_by(id_veiculo=id_veiculo)
            .order_by(RegistroManutencao.data_manutencao.desc())
            .all()
        )
        res = [r.to_dict() for r in registros]
        session.close()
        return jsonify(res), 200

    @app.route("/v1/manutencoes", methods=["POST"])
    def api_criar_manutencao():
        """
        Registrar nova manutenção vinculada a um veículo
        ---
        tags:
          - Manutenções
        parameters:
          - in: body
            name: body
            required: true
            schema:
              type: object
              required: [id_veiculo, data_manutencao, odometro_km, tipo_manutencao, descricao_servico, custo]
              properties:
                id_veiculo: {type: integer, example: 1}
                data_manutencao: {type: string, example: "2026-11-22"}
                odometro_km: {type: integer, example: 35000}
                tipo_manutencao: {type: string, example: "Preventiva"}
                descricao_servico: {type: string, example: "Troca de óleo e filtros"}
                custo: {type: number, example: 420.50}
        responses:
          201:
            description: Manutenção registrada com sucesso
          404:
            description: Veículo vinculado não encontrado
        """
        data = request.get_json()
        session = Session()
        veiculo = session.query(Veiculo).filter_by(id=int(data["id_veiculo"])).first()
        if not veiculo:
            session.close()
            return jsonify({"erro": "Veículo não encontrado"}), 404

        nova = RegistroManutencao(
            id_veiculo=veiculo.id,
            data_manutencao=datetime.strptime(data["data_manutencao"], "%Y-%m-%d").date(),
            odometro_km=int(data["odometro_km"]),
            tipo_manutencao=data["tipo_manutencao"],
            descricao_servico=data["descricao_servico"],
            custo=Decimal(str(data["custo"])),
        )
        session.add(nova)
        session.commit()
        res = nova.to_dict()
        session.close()
        return jsonify(res), 201

    @app.route("/v1/manutencoes/<int:id>", methods=["DELETE"])
    def api_deletar_manutencao(id):
        """
        Excluir registro de manutenção
        ---
        tags:
          - Manutenções
        parameters:
          - name: id
            in: path
            type: integer
            required: true
        responses:
          200:
            description: Manutenção excluída com sucesso
          404:
            description: Registro não encontrado
        """
        session = Session()
        m = session.query(RegistroManutencao).filter_by(id=id).first()
        if not m:
            session.close()
            return jsonify({"erro": "Registro de manutenção não encontrado"}), 404

        session.delete(m)
        session.commit()
        session.close()
        return jsonify({"mensagem": "Manutenção excluída com sucesso"}), 200