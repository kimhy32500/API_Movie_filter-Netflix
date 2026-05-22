class TvApiObject:
    """
    TV 프로그램 API Object Layer
    HTTP 엔드포인트 호출 규격을 캡슐화한다.
    엔드포인트 경로가 변경되면 이 파일만 수정하면 된다.
    """

    def __init__(self, client):
        self.client = client

    def get_tv(self, genre=None):
        """TV 프로그램 목록 조회 (장르 필터 선택 가능)"""
        params = {}

        if genre is not None:
            params["genre"] = genre

        return self.client.get("/api/tv", params=params)

    def search_tv(self, query: str):
        """TV 프로그램 검색"""
        return self.client.get(
            "/api/tv/search",
            params={"query": query}
        )

    def get_tv_detail(self, tv_id: int):
        """TV 프로그램 상세 조회"""
        return self.client.get(f"/api/tv/{tv_id}")
