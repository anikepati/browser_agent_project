from google.adk.sessions import InMemorySessionService
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from config import AppConfig

def setup_services():
    session_service = InMemorySessionService()
    artifact_service = InMemoryArtifactService(base_dir=AppConfig.ARTIFACT_DIR)
    return session_service, artifact_service
