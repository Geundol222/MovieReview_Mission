import streamlit as st
import time

from api_client import ApiClient

st.set_page_config(page_title="Movies & Reviews", layout="wide")

# CSS for fixed image height and card styling
st.markdown("""
<style>
    img {
        height: 400px !important;
        object-fit: cover !important;
        width: 100% !important;
    }
    [data-testid="column"] > div {
        border: 1px solid rgba(250, 250, 250, 0.2);
        border-radius: 8px;
        padding: 1rem;
        background-color: rgba(255, 255, 255, 0.05);
    }
</style>
""", unsafe_allow_html=True)

# 사이드바: API 설정
st.sidebar.header("백엔드 설정")
default_base = st.session_state.get("api_base_url", "https://geundol222-movie-review.hf.space")
api_base_url = st.sidebar.text_input("API Base URL", value=default_base)
st.session_state["api_base_url"] = api_base_url
client = ApiClient(api_base_url)

# 페이지 상태 관리
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "main"
if "selected_movie" not in st.session_state:
    st.session_state["selected_movie"] = None


def go_to_reviews(movie):
    """리뷰 상세 페이지로 이동"""
    st.session_state["current_page"] = "reviews"
    st.session_state["selected_movie"] = movie
    st.rerun()


def go_to_main():
    """메인 페이지로 이동"""
    st.session_state["current_page"] = "main"
    st.session_state["selected_movie"] = None
    st.rerun()


# 리뷰 상세 페이지
if st.session_state["current_page"] == "reviews":
    movie = st.session_state["selected_movie"]
    st.title(f"📝 {movie.get('title')} - 전체 리뷰")

    # 뒤로가기 버튼
    if st.button("← 메인으로 돌아가기"):
        go_to_main()

    st.divider()

    # 영화 정보 표시
    col1, col2 = st.columns([1, 2])
    with col1:
        poster = movie.get("poster_url")
        if poster:
            try:
                st.image(poster, width=300)
            except Exception:
                st.info("이미지 로드 실패")
        else:
            st.info("포스터 없음")

    with col2:
        st.subheader(movie.get("title"))
        meta_items = []
        if movie.get("director"):
            meta_items.append(f"🎬 감독: {movie.get('director')}")
        if movie.get("genre"):
            meta_items.append(f"🎭 장르: {movie.get('genre')}")
        if movie.get("release_date"):
            meta_items.append(f"📅 개봉일: {movie.get('release_date')}")

        for item in meta_items:
            st.write(item)

        # 평균 평점
        rating, r_err = client.average_rating(movie["id"])
        if not r_err:
            st.success(f"⭐ 평균 감성 점수: {rating.get('average_sentiment'):.3f}")

    st.divider()

    # 전체 리뷰 표시
    reviews, err = client.list_reviews_by_movie(movie["id"])
    if err:
        st.error(f"리뷰 불러오기 실패: {err}")
    elif not reviews:
        st.info("리뷰가 없습니다.")
    else:
        st.subheader(f"전체 리뷰 ({len(reviews)}개)")
        for idx, review in enumerate(reviews, 1):
            with st.container(border=True):
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.markdown(f"**{review.get('author')}**")
                with col_b:
                    sentiment_color = "green" if review.get('sentiment_label') == 'positive' else "red"
                    st.markdown(f":{sentiment_color}[{review.get('sentiment_label')}] ({review.get('sentiment_score'):.3f})")

                st.write(review.get('content'))
                st.caption(f"등록일: {review.get('created_at')}")

# 메인 페이지
else:
    st.title("🎬 영화 & 리뷰")

    # 탭 생성
    tab_main, tab_add_movie, tab_add_review = st.tabs(["영화 목록", "영화 등록", "리뷰 작성"])

    # 탭 1: 영화 목록 (메인)
    with tab_main:
        st.header("영화 목록")

        # 검색 기능
        search_query = st.text_input("search", placeholder="🔍 영화 검색 (제목, 감독, 장르)", label_visibility="collapsed")

        movies, err = client.list_movies()
        if err:
            st.error(f"영화 목록 불러오기 실패: {err}")
        else:
            if not movies:
                st.info("등록된 영화가 없습니다.")
            else:
                # 검색 필터링
                if search_query:
                    search_lower = search_query.lower()
                    filtered_movies = [
                        m for m in movies
                        if search_lower in str(m.get('title', '')).lower()
                        or search_lower in str(m.get('director', '')).lower()
                        or search_lower in str(m.get('genre', '')).lower()
                    ]
                else:
                    filtered_movies = movies

                if not filtered_movies:
                    st.warning(f"'{search_query}'에 대한 검색 결과가 없습니다.")
                else:
                    # 3개 컬럼 고정
                    cols = st.columns(3)

                    for idx, movie in enumerate(filtered_movies):
                        col = cols[idx % 3]
                        with col:
                                # 포스터 - 고정 크기
                                poster = movie.get("poster_url")
                                if poster:
                                    try:
                                        col.image(poster, use_container_width=True)
                                    except Exception:
                                        col.info("이미지 로드 실패")
                                else:
                                    col.info("포스터 없음")

                                # 영화 정보
                                col.markdown(f"### {movie.get('title')}")
                                meta = " · ".join(
                                    str(x)
                                    for x in [movie.get("director"), movie.get("genre"), movie.get("release_date")]
                                    if x
                                )
                                if meta:
                                    col.caption(meta)

                                # 평균 평점
                                rating, r_err = client.average_rating(movie["id"])
                                if r_err:
                                    col.info("리뷰 없음")
                                else:
                                    col.success(f"⭐ 평균 점수: {rating.get('average_sentiment'):.3f}")

                                # 최근 리뷰 3개
                                reviews, rv_err = client.list_reviews_by_movie(movie["id"], limit=3)
                                if not rv_err and reviews:
                                    col.markdown("**최근 리뷰**")
                                    for review in reviews:
                                        with col.expander(f"{review.get('author')} - {review.get('sentiment_label')}"):
                                            st.write(f"**점수:** {review.get('sentiment_score'):.3f}")
                                            st.write(f"**내용:** {review.get('content')[:100]}{'...' if len(review.get('content', '')) > 100 else ''}")
                                            st.caption(f"등록일: {review.get('created_at')}")

                                    # 리뷰 더보기 버튼
                                    if col.button("📋 리뷰 더보기", key=f"more-{movie['id']}", use_container_width=True):
                                        go_to_reviews(movie)

                                # 삭제 버튼
                                if col.button("🗑️ 삭제", key=f"del-{movie['id']}", use_container_width=True):
                                    _, d_err = client.delete_movie(movie["id"])
                                    if d_err:
                                        st.error(f"삭제 실패: {d_err}")
                                    else:
                                        st.success("삭제 완료")
                                        st.rerun()

    # 탭 2: 영화 등록
    with tab_add_movie:
        st.header("영화 등록")
        with st.form("add_movie"):
            title = st.text_input("제목*")
            release_date = st.date_input("개봉일*")
            director = st.text_input("감독")
            genre = st.text_input("장르")
            poster_url = st.text_input("포스터 URL", placeholder="https://")
            submitted = st.form_submit_button("등록")
            if submitted:
                if not title:
                    st.error("제목은 필수입니다.")
                else:
                    payload = {
                        "title": title,
                        "release_date": release_date.isoformat(),
                        "director": director,
                        "genre": genre,
                        "poster_url": poster_url or None,
                    }
                    created, err = client.create_movie(payload)
                    if err:
                        st.error(f"등록 실패: {err}")
                    else:
                        st.success(f"영화 등록 완료! (ID: {created.get('id')})")
                        st.balloons()
                        st.rerun()

    # 탭 3: 리뷰 작성
    with tab_add_review:
        st.header("리뷰 작성")

        # 영화 목록 가져오기
        movies_for_review, err = client.list_movies()
        if err:
            st.error(f"영화 목록 불러오기 실패: {err}")
        elif not movies_for_review:
            st.info("영화를 먼저 등록하세요.")
        else:
            movie_options = {f"{m.get('title')} (개봉: {m.get('release_date')})": m.get("id") for m in movies_for_review}

            with st.form("add_review"):
                selected_movie = st.selectbox("영화 선택*", options=list(movie_options.keys()))
                author = st.text_input("작성자*")
                content = st.text_area("리뷰 내용*", height=150)
                submitted_review = st.form_submit_button("리뷰 등록")

                if submitted_review:
                    if not author or not content:
                        st.error("작성자와 리뷰 내용은 필수입니다.")
                    else:
                        payload = {
                            "movie_id": movie_options[selected_movie],
                            "author": author,
                            "content": content,
                        }
                        review, err = client.create_review(payload)
                        if err:
                            st.error(f"리뷰 등록 실패: {err}")
                        else:
                            st.success(
                                f"✅ 리뷰 등록 완료!\n\n"
                                f"- 감성 점수: {review.get('sentiment_score'):.3f}\n"
                                f"- 감성 레이블: {review.get('sentiment_label')}"
                            )
                            st.balloons()
                            st.rerun()
