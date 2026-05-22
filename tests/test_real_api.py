# ==============================================================================
# test_real_api.py - 실제 TMDB API 연동 통합 테스트 (Integration Test)
#
# 목적: Mock 없이 실제 TMDB 서버와 통신하여 연동 무결성을 검증한다.
# 주의: 인터넷 연결 및 .env의 TMDB_API_KEY가 반드시 필요하다.
# 실행: pytest tests/test_real_api.py -v
# ==============================================================================

import pytest  # noqa: F401  fixture 자동 주입을 위해 필요
from tests.api_objects.movie_api import MovieApiObject  # noqa: F401
from tests.api_objects.tv_api import TvApiObject  # noqa: F401


# ==============================================================================
# 🎬 영화 실제 API 테스트
# ==============================================================================

def test_real_movie_list_returns_data(movie_api):
    """
    [TC-R01] 실제 TMDB에서 넷플릭스 영화 목록이 정상 반환되는지 검증
    - 상태코드 200 확인
    - 데이터가 1개 이상 존재하는지 확인
    """
    response = movie_api.get_movies()

    assert response.status_code == 200
    results = response.json()
    assert len(results) > 0


def test_real_movie_list_schema(movie_api):
    """
    [TC-R02] 실제 영화 목록 응답의 필드 구조(Schema)가 규격과 일치하는지 검증
    - 필수 필드 존재 여부 확인
    - 각 필드의 데이터 타입 확인
    - 평점 범위(0.0 ~ 10.0) 확인
    """
    response = movie_api.get_movies()
    results = response.json()

    # 첫 번째 아이템으로 스키마 검증
    item = results[0]

    # 필수 필드 존재 확인
    assert "id" in item
    assert "title" in item
    assert "vote_average" in item
    assert "overview" in item
    assert "genre_ids" in item

    # 데이터 타입 확인
    assert isinstance(item["id"], int)
    assert isinstance(item["title"], str)
    assert isinstance(item["vote_average"], float)
    assert isinstance(item["overview"], str)
    assert isinstance(item["genre_ids"], list)

    # 평점 범위 확인
    assert 0.0 <= item["vote_average"] <= 10.0


def test_real_movie_list_no_null_fields(movie_api):
    """
    [TC-R03] 실제 응답 전체에서 Null 필드가 없는지 검증 (Data Sanitization 확인)
    - sanitize_media가 실제로 작동하여 None이 없는지 전수 확인
    """
    response = movie_api.get_movies()
    results = response.json()

    for item in results:
        assert item["title"] is not None
        assert item["vote_average"] is not None
        assert item["overview"] is not None
        assert item["genre_ids"] is not None


def test_real_movie_genre_filter(movie_api):
    """
    [TC-R04] 실제 장르 필터링 시 해당 장르 영화만 반환되는지 검증
    - 액션(28) 필터 적용
    - 포함 검증: 모든 결과가 액션 장르 ID를 가지는지 확인
    - 최대 20개 제한 확인
    """
    ACTION_GENRE_ID = 28

    response = movie_api.get_movies(genre=ACTION_GENRE_ID)

    assert response.status_code == 200
    results = response.json()

    # 결과가 존재해야 함
    assert len(results) > 0

    # 최대 20개 제한 확인
    assert len(results) <= 20

    # 포함 검증: 모든 영화가 액션 장르를 가지는지 전수 확인
    assert all(
        ACTION_GENRE_ID in movie["genre_ids"]
        for movie in results
    )


def test_real_movie_genre_filter_sorted(movie_api):
    """
    [TC-R05] 실제 장르 필터링 결과가 평점 내림차순으로 정렬되는지 검증
    - 앞 순위 평점 >= 뒷 순위 평점 전수 확인
    """
    ACTION_GENRE_ID = 28

    response = movie_api.get_movies(genre=ACTION_GENRE_ID)
    results = response.json()

    # 평점 내림차순 정렬 전수 검증
    for i in range(len(results) - 1):
        assert results[i]["vote_average"] >= results[i + 1]["vote_average"]


def test_real_movie_search_success(movie_api):
    """
    [TC-R06] 실제 키워드 검색 시 관련 영화가 반환되는지 검증
    - 상태코드 200 확인
    - 결과 구조(Schema) 확인
    """
    response = movie_api.search_movies("기생충")

    assert response.status_code == 200
    results = response.json()
    assert len(results) > 0

    # 구조 확인 (실제 데이터라 정확한 값 단언 대신 타입 검증)
    assert isinstance(results[0]["title"], str)
    assert isinstance(results[0]["vote_average"], float)


def test_real_movie_search_empty(movie_api):
    """
    [TC-R07] 빈 검색어 입력 시 400 반환 검증
    - 서버 내부 로직이므로 실제 API 호출과 동일한 결과
    """
    response = movie_api.search_movies(" ")

    assert response.status_code == 400
    assert response.json()["detail"] == "검색어가 비어 있습니다."


def test_real_movie_detail_not_found(movie_api):
    """
    [TC-R08] 존재하지 않는 영화 ID 조회 시 404 반환 검증
    """
    response = movie_api.get_movie_detail(99999999)

    assert response.status_code == 404
    assert response.json()["detail"] == "영화를 찾을 수 없습니다."


# ==============================================================================
# 📺 TV 실제 API 테스트
# ==============================================================================

def test_real_tv_list_returns_data(tv_api):
    """
    [TC-R09] 실제 TMDB에서 넷플릭스 TV 목록이 정상 반환되는지 검증
    """
    response = tv_api.get_tv()

    assert response.status_code == 200
    results = response.json()
    assert len(results) > 0


def test_real_tv_list_schema(tv_api):
    """
    [TC-R10] 실제 TV 목록 응답의 필드 구조(Schema)가 규격과 일치하는지 검증
    """
    response = tv_api.get_tv()
    results = response.json()

    item = results[0]

    # 필수 필드 존재 확인
    assert "id" in item
    assert "title" in item
    assert "vote_average" in item
    assert "overview" in item
    assert "genre_ids" in item

    # 데이터 타입 확인
    assert isinstance(item["id"], int)
    assert isinstance(item["title"], str)
    assert isinstance(item["vote_average"], float)
    assert isinstance(item["overview"], str)
    assert isinstance(item["genre_ids"], list)

    # 평점 범위 확인
    assert 0.0 <= item["vote_average"] <= 10.0


def test_real_tv_list_no_null_fields(tv_api):
    """
    [TC-R11] 실제 TV 응답 전체에서 Null 필드가 없는지 검증
    """
    response = tv_api.get_tv()
    results = response.json()

    for item in results:
        assert item["title"] is not None
        assert item["vote_average"] is not None
        assert item["overview"] is not None
        assert item["genre_ids"] is not None


def test_real_tv_genre_filter(tv_api):
    """
    [TC-R12] 실제 장르 필터링 시 해당 장르 TV만 반환되는지 검증
    - 미스터리(9648) 필터 적용
    - 포함 검증 + 최대 20개 제한 확인
    """
    MYSTERY_GENRE_ID = 9648

    response = tv_api.get_tv(genre=MYSTERY_GENRE_ID)

    assert response.status_code == 200
    results = response.json()

    assert len(results) > 0
    assert len(results) <= 20

    # 포함 검증
    assert all(
        MYSTERY_GENRE_ID in tv["genre_ids"]
        for tv in results
    )


def test_real_tv_genre_filter_sorted(tv_api):
    """
    [TC-R13] 실제 TV 장르 필터링 결과가 평점 내림차순으로 정렬되는지 검증
    """
    MYSTERY_GENRE_ID = 9648

    response = tv_api.get_tv(genre=MYSTERY_GENRE_ID)
    results = response.json()

    for i in range(len(results) - 1):
        assert results[i]["vote_average"] >= results[i + 1]["vote_average"]


def test_real_tv_search_success(tv_api):
    """
    [TC-R14] 실제 키워드로 TV 검색 시 관련 결과 반환 검증
    """
    response = tv_api.search_tv("오징어")

    assert response.status_code == 200
    results = response.json()
    assert len(results) > 0

    assert isinstance(results[0]["title"], str)
    assert isinstance(results[0]["vote_average"], float)


def test_real_tv_search_empty(tv_api):
    """
    [TC-R15] 빈 검색어 입력 시 400 반환 검증
    """
    response = tv_api.search_tv(" ")

    assert response.status_code == 400
    assert response.json()["detail"] == "검색어가 비어 있습니다."


def test_real_tv_detail_not_found(tv_api):
    """
    [TC-R16] 존재하지 않는 TV ID 조회 시 404 반환 검증
    """
    response = tv_api.get_tv_detail(99999999)

    assert response.status_code == 404
    assert response.json()["detail"] == "TV 프로그램을 찾을 수 없습니다."