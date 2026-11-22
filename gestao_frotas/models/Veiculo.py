from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import relationship
from models.Conexao import Base


class Veiculo(Base):
    __tablename__ = "veiculo"

    id = Column(Integer, primary_key=True, autoincrement=True)
    placa = Column(String(10), unique=True, nullable=False)
    marca = Column(String(60), nullable=False)
    modelo = Column(String(60), nullable=False)
    ano_fabricacao = Column(Integer, nullable=False)
    chassi = Column(String(30), unique=True, nullable=False)
    data_aquisicao = Column(Date, nullable=False)
    status = Column(String(30), nullable=False, default="Ativo")

    manutencoes = relationship(
        "RegistroManutencao",
        back_populates="veiculo",
        order_by="desc(RegistroManutencao.data_manutencao)",
    )

    def __init__(self, placa, marca, modelo, ano_fabricacao, chassi, data_aquisicao, status="Ativo", id=None):
        self.id = id
        self.placa = placa
        self.marca = marca
        self.modelo = modelo
        self.ano_fabricacao = ano_fabricacao
        self.chassi = chassi
        self.data_aquisicao = data_aquisicao
        self.status = status

    @property
    def custo_total_manutencao(self):
        return sum((m.custo for m in self.manutencoes), 0)

    def to_dict(self):
        return {
            "id": self.id,
            "placa": self.placa,
            "marca": self.marca,
            "modelo": self.modelo,
            "ano_fabricacao": self.ano_fabricacao,
            "chassi": self.chassi,
            "data_aquisicao": self.data_aquisicao.isoformat() if self.data_aquisicao else None,
            "status": self.status,
            "custo_total_manutencao": float(self.custo_total_manutencao),
            "quantidade_manutencoes": len(self.manutencoes),
        }