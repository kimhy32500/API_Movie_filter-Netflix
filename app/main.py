from enum import IntEnum
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from app.tmdb_client import client

app = FastAPI(title="Netflix")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class MediaGenre(IntEnum):
    ACTION = 28
    COMEDY = 35
    DRAMA = 18
    HORROR = 27
    MYSTERY = 9648
    ROMANCE = 10749
    ANIMATION = 16
    DOCUMENTARY = 99
    SCI_FI_FANTASY = 10765
    CHRONICLE = 878
    THRILLER = 53
    ACTION_ADVENTURE = 10759
    REALITY = 10764


# ---------------------------------------------------------------
# 🎬 영화 엔드포인트
# 주의: /api/movies/search 가 /api/movies/{movie_id} 보다 반드시 위에 있어야 함
# FastAPI는 라우팅을 등록 순서대로 매칭하므로, 순서가 바뀌면
# "search" 문자열이 {movie_id} 파라미터로 잡혀 422 에러 발생
# ---------------------------------------------------------------

@app.get("/api/movies/search")
async def search_movies(query: str):
    if not query.strip():
        raise HTTPException(status_code=400, detail="검색어가 비어 있습니다.")

    movies = await client.get_movies()

    results = [
        movie for movie in movies
        if query.lower() in movie.get("title", "").lower()
    ]

    return results


@app.get("/api/movies")
async def get_movies(
    genre: Optional[MediaGenre] = Query(default=None)
):
    movies = await client.get_movies()

    if genre:
        movies = [
            movie for movie in movies
            if genre.value in movie.get("genre_ids", [])
        ]

        movies = sorted(
            movies,
            key=lambda x: x.get("vote_average", 0),
            reverse=True
        )[:20]

    return movies


@app.get("/api/movies/{movie_id}")
async def movie_detail(movie_id: int):
    movies = await client.get_movies()

    for movie in movies:
        if movie.get("id") is not None and movie.get("id") == movie_id:
            return movie

    raise HTTPException(status_code=404, detail="영화를 찾을 수 없습니다.")


# ---------------------------------------------------------------
# 📺 TV 엔드포인트
# 주의: /api/tv/search 가 /api/tv/{tv_id} 보다 반드시 위에 있어야 함
# ---------------------------------------------------------------

@app.get("/api/tv/search")
async def search_tv(query: str):
    if not query.strip():
        raise HTTPException(status_code=400, detail="검색어가 비어 있습니다.")

    tv_shows = await client.get_tv_shows()

    results = [
        tv for tv in tv_shows
        if query.lower() in tv.get("title", "").lower()
    ]

    return results


@app.get("/api/tv")
async def get_tv(
    genre: Optional[MediaGenre] = Query(default=None)
):
    tv_shows = await client.get_tv_shows()

    if genre:
        tv_shows = [
            tv for tv in tv_shows
            if genre.value in tv.get("genre_ids", [])
        ]

        tv_shows = sorted(
            tv_shows,
            key=lambda x: x.get("vote_average", 0),
            reverse=True
        )[:20]

    return tv_shows


@app.get("/api/tv/{tv_id}")
async def tv_detail(tv_id: int):
    tv_shows = await client.get_tv_shows()

    for tv in tv_shows:
        if tv.get("id") is not None and tv.get("id") == tv_id:
            return tv

    raise HTTPException(status_code=404, detail="TV 프로그램을 찾을 수 없습니다.")