import os
import time
import asyncio
from typing import Dict

import httpx
from dotenv import load_dotenv

load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3"
WATCH_PROVIDER = 8
WATCH_REGION = "KR"
CACHE_TTL = 180

movie_cache = {
    "timestamp": 0,
    "data": []
}

tv_cache = {
    "timestamp": 0,
    "data": []
}


class TMDBClient:
    def __init__(self):
        self._semaphore = None

    def _get_semaphore(self):
        if self._semaphore is None:
            self._semaphore = asyncio.Semaphore(10)
        return self._semaphore

    async def _fetch_page(self, endpoint: str, page: int):
        params = {
            "api_key": TMDB_API_KEY,
            "language": "ko-KR",
            "page": page,
            "watch_region": WATCH_REGION,
            "with_watch_providers": WATCH_PROVIDER,
        }

        async with self._get_semaphore():
            async with httpx.AsyncClient(timeout=10.0) as client:  # ← 매 요청마다 생성/해제
                response = await client.get(
                    f"{BASE_URL}/{endpoint}",
                    params=params
                )
                response.raise_for_status()
                return response.json().get("results", [])

    async def fetch_bulk_data(self, media_type: str):
        # 매 호출마다 세마포어를 새로 생성하여 이벤트 루프 충돌 방지
        self._semaphore = asyncio.Semaphore(10)

        endpoint = "discover/movie" if media_type == "movie" else "discover/tv"

        tasks = [
            self._fetch_page(endpoint, page)
            for page in range(1, 26)
        ]

        pages = await asyncio.gather(*tasks)

        merged = []
        for page_data in pages:
            merged.extend(page_data)

        return [self.sanitize_media(item) for item in merged]

    def sanitize_media(self, item: Dict):
        item["title"] = item.get("title") or item.get("name") or "제목 없음"
        item["vote_average"] = float(item.get("vote_average") or 0.0)
        item["overview"] = item.get("overview") or ""
        item["genre_ids"] = item.get("genre_ids", [])
        return item

    async def get_movies(self):
        now = time.time()

        if now - movie_cache["timestamp"] < CACHE_TTL:
            return movie_cache["data"]

        data = await self.fetch_bulk_data("movie")

        movie_cache["timestamp"] = now
        movie_cache["data"] = data

        return data

    async def get_tv_shows(self):
        now = time.time()

        if now - tv_cache["timestamp"] < CACHE_TTL:
            return tv_cache["data"]

        data = await self.fetch_bulk_data("tv")

        tv_cache["timestamp"] = now
        tv_cache["data"] = data

        return data


client = TMDBClient()
