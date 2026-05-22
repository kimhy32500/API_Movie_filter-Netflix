import pytest

from fastapi.testclient import TestClient

from app.main import app
from app.tmdb_client import movie_cache, tv_cache

from tests.api_objects.movie_api import MovieApiObject
from tests.api_objects.tv_api import TvApiObject


@pytest.fixture
def client():
    """
    FastAPI Test Client
    scope 기본값(function)으로 설정 - 각 테스트가 독립적인 클라이언트 인스턴스 사용
    session scope는 autouse clear_cache와 타이밍 충돌 위험이 있어 제거
    """
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def movie_api(client):
    """Movie API Object 주입"""
    return MovieApiObject(client)


@pytest.fixture
def tv_api(client):
    """TV API Object 주입"""
    return TvApiObject(client)


@pytest.fixture(autouse=True)
def clear_cache():
    """
    테스트 간 캐시 오염 방지
    각 테스트 실행 전후로 캐시 초기화
    """
    movie_cache["timestamp"] = 0
    movie_cache["data"] = []

    tv_cache["timestamp"] = 0
    tv_cache["data"] = []

    yield

    movie_cache["timestamp"] = 0
    movie_cache["data"] = []

    tv_cache["timestamp"] = 0
    tv_cache["data"] = []