import os
from sqlalchemy import create_engine, Column, String, Text, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from logging_setup import setup_logging

logger = setup_logging()

Base = declarative_base()

class Artifact(Base):
    __tablename__ = 'artifacts'
    name = Column(String, primary_key=True)
    content = Column(Text)

class SqliteArtifactService:
    def __init__(self, db_path):
        # Ensure DB directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        logger.info(f"SQLite ArtifactService initialized at {db_path}")

    def save_artifact(self, name, content):
        with self.Session() as session:
            artifact = session.query(Artifact).filter_by(name=name).first()
            if artifact:
                artifact.content = content
            else:
                artifact = Artifact(name=name, content=content)
                session.add(artifact)
            session.commit()
        logger.info(f"Saved artifact: {name}")

    def load_artifact(self, name):
        with self.Session() as session:
            artifact = session.query(Artifact).filter_by(name=name).first()
            return artifact.content if artifact else None
        logger.info(f"Loaded artifact: {name}")
