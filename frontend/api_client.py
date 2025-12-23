import os
import requests
from typing import Any, Dict, Optional, Tuple



class ApiClient:
    def __init__(self, base_url: Optional[str] = None) -> None:
        self.base_url = (base_url or os.getenv("API_BASE_URL") or "http://127.0.0.1:8000").rstrip(
            "/"
        )

    def _request(self, method: str, path: str, **kwargs: Any) -> Tuple[Optional[Any], Optional[str]]:
        url = f"{self.base_url}{path}"
        try:
            resp = requests.request(method, url, timeout=10, **kwargs)
            if resp.ok:
                # 빈 본문이거나 JSON이 아닌 경우도 대비
                if resp.text:
                    return resp.json(), None
                return {}, None
            return None, f"{resp.status_code}: {resp.text}"
        except Exception as e:  # noqa: BLE001
            return None, str(e)

    # Movies
    def list_movies(self) -> Tuple[Optional[Any], Optional[str]]:
        return self._request("get", "/movies")

    def create_movie(self, payload: Dict[str, Any]) -> Tuple[Optional[Any], Optional[str]]:
        return self._request("post", "/movies", json=payload)

    def delete_movie(self, movie_id: int) -> Tuple[Optional[Any], Optional[str]]:
        return self._request("delete", f"/movies/{movie_id}")

    # Reviews
    def list_reviews(self) -> Tuple[Optional[Any], Optional[str]]:
        return self._request("get", "/reviews")

    def list_reviews_by_movie(self, movie_id: int, limit: Optional[int] = None) -> Tuple[Optional[Any], Optional[str]]:
        params = {"limit": limit} if limit is not None else {}
        return self._request("get", f"/reviews/movie/{movie_id}", params=params)

    def create_review(self, payload: Dict[str, Any]) -> Tuple[Optional[Any], Optional[str]]:
        return self._request("post", "/reviews", json=payload)

    def average_rating(self, movie_id: int) -> Tuple[Optional[Any], Optional[str]]:
        return self._request("get", f"/reviews/movie/{movie_id}/rating")
