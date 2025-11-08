from google.adk.sessions import InMemorySessionService
from sqlite_artifact_service import SqliteArtifactService  # New import
from config import AppConfig

def setup_services():
    session_service = InMemorySessionService()
    artifact_service = SqliteArtifactService(db_path=AppConfig.DB_PATH)
    return session_service, artifact_service
