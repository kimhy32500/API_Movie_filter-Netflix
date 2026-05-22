class MovieApiObject:
    """
    영화(Movie) API Object Layer
    HTTP 엔드포인트 호출 규격을 캡슐화한다.
    엔드포인트 경로가 변경되면 이 파일만 수정하면 된다.
    """

    def __init__(self, client):
        self.client = client

    def get_movies(self, genre=None):
        """영화 목록 조회 (장르 필터 선택 가능)"""
        params = {}

        if genre is not None:
            params["genre"] = genre

        return self.client.get("/api/movies", params=params)

    def search_movies(self, query: str):
        """영화 검색"""
        return self.client.get(
            "/api/movies/search",
            params={"query": query}
        )

    def get_movie_detail(self, movie_id: int):
        """영화 상세 조회"""
        return self.client.get(f"/api/movies/{movie_id}")
