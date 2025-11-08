import os
from sqlalchemy import create_engine, Column, String, Text, select
from sqlalchemy.orm import sessionmaker, scoped_session
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
        self.engine = create_engine(f'sqlite:///{db_path}', connect_args={'check_same_thread': False})  # Thread-safe
        Base.metadata.create_all(self.engine)
        self.Session = scoped_session(sessionmaker(bind=self.engine))  # Scoped for thread-safety
        logger.info(f"SQLite ArtifactService initialized at {db_path}")

    def save_artifact(self, name, content):
        session = self.Session()
        try:
            artifact = session.query(Artifact).filter_by(name=name).first()
            if artifact:
                artifact.content = content
            else:
                artifact = Artifact(name=name, content=content)
                session.add(artifact)
            session.commit()
            logger.info(f"Saved artifact: {name}")
        finally:
            self.Session.remove()  # Clean up scoped session

    def load_artifact(self, name):
        session = self.Session()
        try:
            artifact = session.query(Artifact).filter_by(name=name).first()
            return artifact.content if artifact else None
        finally:
            self.Session.remove()
        logger.info(f"Loaded artifact: {name}")
