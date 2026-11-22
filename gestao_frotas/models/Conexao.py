from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# Ligação ao banco de dados 'frota' no MySQL local (XAMPP)
DATABASE_URL: str = "mysql+pymysql://root:@localhost:3306/frota"

engine = create_engine(
    DATABASE_URL,
    echo=False,          # Altere para True se quiser visualizar os comandos SQL no terminal
    pool_pre_ping=True,  # Testa a conexão antes de executar cada consulta
    pool_recycle=3600
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db_session() -> Generator[Session, None, None]:
    """Gerador contextual para controle transacional da sessão."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()