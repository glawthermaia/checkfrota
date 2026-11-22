from datetime import datetime
from flask import request, jsonify
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker, joinedload

from models.Conexao import engine
from models.Veiculo import Veiculo


def init_veiculo_rest_routes(app):
    Session = sessionmaker(bind=engine)

    @app.route("/v1/veiculos", methods=["GET"])
    def api_listar_veiculos():
        """
        Listar e filtrar veículos da frota
        ---
        tags:
          - Veículos
        parameters:
          - name: status
            in: query
            type: string
            required: false
            description: Filtrar por status (Ativo, Em Manutenção, Inativo, Vendido)
          - name: marca
            in: query
            type: string
            required: false
          - name: modelo
            in: query
            type: string
            required: false
        responses:
          200:
            description: Lista de veículos retornada com sucesso
        """
        session = Session()
        status = request.args.get("status")
        marca = request.args.get("marca")
        modelo = request.args.get("modelo")

        query = session.query(Veiculo).options(joinedload(Veiculo.manutencoes))
        if status:
            query = query.filter(Veiculo.status == status)
        if marca:
            query = query.filter(Veiculo.marca.ilike(f"%{marca}%"))
        if modelo:
            query = query.filter(Veiculo.modelo.ilike(f"%{modelo}%"))

        veiculos = [v.to_dict() for v in query.all()]
        session.close()
        return jsonify(veiculos), 200

    @app.route("/v1/veiculos/<int:id>", methods=["GET"])
    def api_obter_veiculo(id):
        """
        Consultar prontuário completo de um veículo por ID
        ---
        tags:
          - Veículos
        parameters:
          - name: id
            in: path
            type: integer
            required: true
        responses:
          200:
            description: Dados do veículo e histórico de manutenções
          404:
            description: Veículo não encontrado
        """
        session = Session()
        v = (
            session.query(Veiculo)
            .options(joinedload(Veiculo.manutencoes))
            .filter_by(id=id)
            .first()
        )
        if not v:
            session.close()
            return jsonify({"erro": "Veículo não encontrado"}), 404

        dados = v.to_dict()
        dados["manutencoes"] = [m.to_dict() for m in v.manutencoes]
        session.close()
        return jsonify(dados), 200

    @app.route("/v1/veiculos", methods=["POST"])
    def api_criar_veiculo():
        """
        Cadastrar novo veículo na frota
        ---
        tags:
          - Veículos
        parameters:
          - in: body
            name: body
            required: true
            schema:
              type: object
              required: [placa, marca, modelo, ano_fabricacao, chassi, data_aquisicao]
              properties:
                placa: {type: string, example: "ABC1D23"}
                marca: {type: string, example: "Fiat"}
                modelo: {type: string, example: "Strada"}
                ano_fabricacao: {type: integer, example: 2024}
                chassi: {type: string, example: "9BD5781FFPY999999"}
                data_aquisicao: {type: string, example: "2024-05-10"}
                status: {type: string, example: "Ativo"}
        responses:
          201:
            description: Veículo cadastrado com sucesso
          400:
            description: Placa ou chassi duplicado
        """
        data = request.get_json()
        session = Session()
        try:
            novo = Veiculo(
                placa=data["placa"].strip().upper(),
                marca=data["marca"].strip(),
                modelo=data["modelo"].strip(),
                ano_fabricacao=int(data["ano_fabricacao"]),
                chassi=data["chassi"].strip().upper(),
                data_aquisicao=datetime.strptime(data["data_aquisicao"], "%Y-%m-%d").date(),
                status=data.get("status", "Ativo"),
            )
            session.add(novo)
            session.commit()
            res = novo.to_dict()
            session.close()
            return jsonify(res), 201
        except IntegrityError:
            session.rollback()
            session.close()
            return jsonify({"erro": "Placa ou Chassi já cadastrado"}), 400

    @app.route("/v1/veiculos/<int:id>/desativar", methods=["PATCH"])
    def api_desativar_veiculo(id):
        """
        Desativar veículo (Inativo/Vendido) preservando histórico
        ---
        tags:
          - Veículos
        parameters:
          - name: id
            in: path
            type: integer
            required: true
          - in: body
            name: body
            required: false
            schema:
              type: object
              properties:
                status: {type: string, example: "Inativo"}
        responses:
          200:
            description: Status atualizado com preservação de histórico
          404:
            description: Veículo não encontrado
        """
        data = request.get_json(silent=True) or {}
        novo_status = data.get("status", "Inativo")
        if novo_status not in ("Inativo", "Vendido"):
            novo_status = "Inativo"

        session = Session()
        v = session.query(Veiculo).filter_by(id=id).first()
        if not v:
            session.close()
            return jsonify({"erro": "Veículo não encontrado"}), 404

        v.status = novo_status
        session.commit()
        res = v.to_dict()
        session.close()
        return jsonify(res), 200