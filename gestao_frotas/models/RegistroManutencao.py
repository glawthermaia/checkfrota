from sqlalchemy import Column, Integer, String, Date, Text, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from models.Conexao import Base


class RegistroManutencao(Base):
    __tablename__ = "registroManutencao"

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_veiculo = Column(Integer, ForeignKey("veiculo.id"), nullable=False)
    data_manutencao = Column(Date, nullable=False)
    odometro_km = Column(Integer, nullable=False)
    tipo_manutencao = Column(String(50), nullable=False)
    descricao_servico = Column(Text, nullable=False)
    custo = Column(Numeric(10, 2), nullable=False)

    veiculo = relationship("Veiculo", back_populates="manutencoes")

    def __init__(self, id_veiculo, data_manutencao, odometro_km, tipo_manutencao, descricao_servico, custo, id=None):
        self.id = id
        self.id_veiculo = id_veiculo
        self.data_manutencao = data_manutencao
        self.odometro_km = odometro_km
        self.tipo_manutencao = tipo_manutencao
        self.descricao_servico = descricao_servico
        self.custo = custo

    def to_dict(self):
        return {
            "id": self.id,
            "id_veiculo": self.id_veiculo,
            "data_manutencao": self.data_manutencao.isoformat() if self.data_manutencao else None,
            "odometro_km": self.odometro_km,
            "tipo_manutencao": self.tipo_manutencao,
            "descricao_servico": self.descricao_servico,
            "custo": float(self.custo) if self.custo is not None else 0.0,
        }