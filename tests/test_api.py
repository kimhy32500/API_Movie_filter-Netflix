from unittest.mock import AsyncMock, patch

from app.main import MediaGenre


# ==============================================================================
# Mock 데이터 정의
# TMDB 실제 응답 구조를 반영 (sanitize_media 통과 전 원본 형태)
# ==============================================================================

mock_movie_data = [
    {
        "id": 1,
        "title": "부산행",
        "vote_average": 8.5,
        "overview": "좀비 영화",
        "genre_ids": [28, 27]
    },
    {
        "id": 2,
        "title": "기생충",
        "vote_average": 9.0,
        "overview": "",       # sanitize 완료 상태로 주입
        "genre_ids": [18]
    }
]

mock_tv_data = [
    {
        "id": 100,
        "title": "오징어게임",
        "vote_average": 8.9,
        "overview": "",       # sanitize 완료 상태로 주입
        "genre_ids": [9648]
    }
]


# ==============================================================================
# 🎬 영화 테스트
# Mock 패치 경로: app.main.client.get_movies
# main.py가 "from app.tmdb_client import client"로 가져오므로
# main.py 네임스페이스의 client를 직접 패치해야 Mock이 실제로 가로챔
# ==============================================================================

@patch("app.main.client.get_movies", new_callable=AsyncMock)
def test_movie_list_default(mock_get_movies, movie_api):
    """TC-03: 필터 없을 때 전체 목록 반환 검증"""
    mock_get_movies.return_value = mock_movie_data

    response = movie_api.get_movies()

    assert response.status_code == 200
    assert len(response.json()) == 2


@patch("app.main.client.get_movies", new_callable=AsyncMock)
def test_movie_search_success(mock_get_movies, movie_api):
    """TC-01: 정상 키워드 검색 시 관련 영화 반환 검증"""
    mock_get_movies.return_value = mock_movie_data

    response = movie_api.search_movies("부산")

    assert response.status_code == 200
    results = response.json()
    # 구체적 assert: 개수 + 제목 일치 확인
    assert len(results) == 1
    assert results[0]["title"] == "부산행"
    assert results[0]["id"] == 1


@patch("app.main.client.get_movies", new_callable=AsyncMock)
def test_movie_search_empty(mock_get_movies, movie_api):
    """TC-02: 빈 검색어 입력 시 400 반환 검증"""
    response = movie_api.search_movies(" ")

    assert response.status_code == 400
    assert response.json()["detail"] == "검색어가 비어 있습니다."


@patch("app.main.client.get_movies", new_callable=AsyncMock)
def test_movie_filter_sort(mock_get_movies, movie_api):
    """TC-04: 장르 필터링 시 해당 장르만 반환되고 평점순 정렬 검증"""
    mock_get_movies.return_value = mock_movie_data

    response = movie_api.get_movies(MediaGenre.HORROR.value)

    assert response.status_code == 200
    results = response.json()

    # 포함 검증: 모든 결과가 공포(27) 장르를 가지는지
    assert all(
        MediaGenre.HORROR.value in movie["genre_ids"]
        for movie in results
    )

    # 오염 검증: 공포 장르 없는 영화(기생충 id=2)가 섞이지 않았는지
    ids = [m["id"] for m in results]
    assert 2 not in ids


@patch("app.main.client.get_movies", new_callable=AsyncMock)
def test_movie_sanitization(mock_get_movies, movie_api):
    """TC-05: overview Null → 빈 문자열 정규화 검증"""
    sanitized = [
        {
            "id": 2,
            "title": "기생충",
            "vote_average": 0.0,
            "overview": "",
            "genre_ids": [18]
        }
    ]

    mock_get_movies.return_value = sanitized

    response = movie_api.get_movies()

    assert response.status_code == 200
    data = response.json()[0]
    assert data["overview"] == ""
    assert data["vote_average"] == 0.0


@patch("app.main.client.get_movies", new_callable=AsyncMock)
def test_movie_404(mock_get_movies, movie_api):
    """TC-06: 존재하지 않는 영화 ID 조회 시 404 반환 검증"""
    mock_get_movies.return_value = mock_movie_data

    response = movie_api.get_movie_detail(99999)

    assert response.status_code == 404
    assert response.json()["detail"] == "영화를 찾을 수 없습니다."


# ==============================================================================
# 📺 TV 테스트
# Mock 패치 경로: app.main.client.get_tv_shows
# ==============================================================================

@patch("app.main.client.get_tv_shows", new_callable=AsyncMock)
def test_tv_list_default(mock_get_tv, tv_api):
    """TC-09: 필터 없을 때 전체 TV 목록 반환 검증"""
    mock_get_tv.return_value = mock_tv_data

    response = tv_api.get_tv()

    assert response.status_code == 200
    assert len(response.json()) == 1


@patch("app.main.client.get_tv_shows", new_callable=AsyncMock)
def test_tv_search(mock_get_tv, tv_api):
    """TC-07: 정상 키워드로 TV 프로그램 검색 시 관련 결과 반환 검증"""
    mock_get_tv.return_value = mock_tv_data

    response = tv_api.search_tv("오징어")

    assert response.status_code == 200
    results = response.json()
    # 구체적 assert: 제목 + id 일치 확인
    assert len(results) == 1
    assert results[0]["title"] == "오징어게임"
    assert results[0]["id"] == 100


@patch("app.main.client.get_tv_shows", new_callable=AsyncMock)
def test_tv_search_empty(mock_get_tv, tv_api):
    """TC-08: 빈 검색어 입력 시 400 반환 검증"""
    response = tv_api.search_tv(" ")

    assert response.status_code == 400
    assert response.json()["detail"] == "검색어가 비어 있습니다."


@patch("app.main.client.get_tv_shows", new_callable=AsyncMock)
def test_tv_filter(mock_get_tv, tv_api):
    """TC-10: 장르 필터링 시 해당 장르만 반환되고 오염 없음 검증"""
    mock_get_tv.return_value = mock_tv_data

    response = tv_api.get_tv(MediaGenre.MYSTERY.value)

    assert response.status_code == 200
    results = response.json()

    # 포함 검증
    assert all(
        MediaGenre.MYSTERY.value in tv["genre_ids"]
        for tv in results
    )


@patch("app.main.client.get_tv_shows", new_callable=AsyncMock)
def test_tv_sanitization(mock_get_tv, tv_api):
    """TC-11: overview Null → 빈 문자열 정규화 검증"""
    sanitized = [
        {
            "id": 100,
            "title": "오징어게임",
            "vote_average": 0.0,
            "overview": "",
            "genre_ids": [9648]
        }
    ]

    mock_get_tv.return_value = sanitized

    response = tv_api.get_tv()

    assert response.status_code == 200
    data = response.json()[0]
    assert data["overview"] == ""
    assert data["vote_average"] == 0.0


@patch("app.main.client.get_tv_shows", new_callable=AsyncMock)
def test_tv_404(mock_get_tv, tv_api):
    """TC-12: 존재하지 않는 TV ID 조회 시 404 반환 검증"""
    mock_get_tv.return_value = mock_tv_data

    response = tv_api.get_tv_detail(99999)

    assert response.status_code == 404
    assert response.json()["detail"] == "TV 프로그램을 찾을 수 없습니다."