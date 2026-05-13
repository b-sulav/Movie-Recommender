import reflex as rx
import pandas as pd
import numpy as np

# Cache for TF-IDF artifacts to avoid re-fitting on every request
_tfidf_cache = {"vectorizer": None, "matrix": None, "df": None}


def build_recommendations(liked, disliked, seen, csv_path="Movies.csv"):

    # Lazy import sklearn to avoid import-time overhead
    from sklearn.feature_extraction.text import TfidfVectorizer

    if _tfidf_cache["df"] is None:
        df = pd.read_csv(csv_path)
        df["features"] = df.get("genres", "").fillna("") + " " + df.get("keywords", "").fillna("")
        tfidf = TfidfVectorizer(stop_words="english")
        tfidf_matrix = tfidf.fit_transform(df["features"])  # sparse csr_matrix
        _tfidf_cache.update({"vectorizer": tfidf, "matrix": tfidf_matrix, "df": df})
    else:
        df = _tfidf_cache["df"]
        tfidf_matrix = _tfidf_cache["matrix"]

    # If no liked movies, nothing to recommend
    if not liked:
        return []

    # Map titles to indices
    liked_idx = df[df["title"].isin(liked)].index.tolist()
    disliked_idx = df[df["title"].isin(disliked)].index.tolist()

    # If liked titles not found in dataset, return empty
    if len(liked_idx) == 0:
        return []

    liked_vecs = tfidf_matrix[liked_idx].toarray()
    user_profile = liked_vecs.mean(axis=0)  # ndarray shape (D,)

    if len(disliked_idx) > 0:
        disliked_vecs = tfidf_matrix[disliked_idx].toarray()
        user_profile = user_profile - disliked_vecs.mean(axis=0)

    user_profile = np.asarray(user_profile).ravel()
    norm = np.linalg.norm(user_profile)
    if norm == 0:
        return []
    user_profile = user_profile / norm

    # Compute similarity using sparse_matrix.dot(dense_vector) 
    similarities = tfidf_matrix.dot(user_profile).flatten() 

    df = df.copy()
    df["score"] = similarities

    # Exclude seen movies and return top results
    recs = df[~df["title"].isin(seen)].sort_values("score", ascending=False)
    return recs.head(10).to_dict("records")


# State
class State(rx.State):
    user_table: list[dict] = []
    count: int = 0
    liked_movies: list[str] = []
    disliked_movies: list[str] = []

    def load_and_start(self):
        try:
            df = pd.read_csv("Movies.csv")
            self.user_table = df.sample(15).to_dict("records")
            self.count = 0
            self.liked_movies = []
            self.disliked_movies = []
            return rx.redirect("/discover")
        except Exception as e:
            print(f"Error loading CSV: {e}")

    def liked(self):
        title = self.current_movie.get("title")
        if title:
            self.liked_movies.append(title)
        return self.next_movie()

    def disliked(self):
        title = self.current_movie.get("title")
        if title:
            self.disliked_movies.append(title)
        return self.next_movie()

    def next_movie(self):
        self.count += 1
        if self.count >= 15:
            return rx.redirect("/foryou")

    def reset_to_main(self):
        self.count = 0
        return rx.redirect("/")

    @rx.var
    def current_movie(self) -> dict:
        if self.user_table and self.count < len(self.user_table):
            return self.user_table[self.count]
        return {
            "title": "No Title",
            "poster_url": "https://via.placeholder.com/300x450?text=No+Poster",
            "genres": "Unknown",
        }
        
    @rx.var
    def recommendations(self) -> list[dict]:
        if not self.liked_movies:
            return []
        seen_titles = [m.get("title") for m in self.user_table if m.get("title")]
        return build_recommendations(self.liked_movies, self.disliked_movies, seen_titles)

def navbar() -> rx.Component:
    return rx.flex(
        rx.text(
            "LUME",
            color="white",
            font_size="2rem",
            font_weight="700",
            letter_spacing="20px",
            text_align="center",
        ),
        background_color="#8B0000",
        border="2px solid rgba(255,255,255,0.12)",
        height="80px",
        width="100%",
        position="fixed",
        top="0",
        left="0",
        z_index="1000",
        align="center",
        justify="center",
        padding_x="20px",
    )

def index() -> rx.Component:
    return rx.box(
        navbar(),
        rx.center(
            rx.vstack(
                rx.heading(
                    "Cinema,",
                    left="20px",
                    top="300px",
                    color="white",
                    position="fixed",
                    font_size="12rem",
                    font_weight="bold",
                ),
                rx.heading(
                    "Tailored.",
                    left="50px",
                    top="500px",
                    color="#D3C0C0",
                    position="fixed",
                    font_size="10rem",
                    font_style="italic",
                ),
                rx.image(
                    src="/popcorn.png",
                    width="650px",
                    height="auto",
                    position="fixed",
                    right="0px",
                    bottom="100px",
                    z_index="10",
                    style={"transition": "transform 0.4s ease-out"},
                    _hover={"transform": "rotate(-10deg)"},
                ),
                rx.button(
                    "Start",
                    on_click=State.load_and_start,
                    background_color="#A52A2A",
                    color="white",
                    font_size="3rem",
                    font_weight="bold",
                    padding_x="50px",
                    padding_y="50px",
                    position="fixed",
                    left="80px",
                    top="700px",
                    border_radius="10px",
                    z_index="11",
                    _hover={
                        "background_color": "#8B1A1A",
                        "color": "#FFD7D7",
                        "transform": "scale(1.02)",
                        "box_shadow": "0 6px 30px rgba(10, 10, 10, 0.6)",
                    },
                    transition="all 0.3s ease",
                ),
                spacing="6",
                text_align="center",
            ),
            width="100%",
            height="100vh",
        ),
        width="100%",
        background_color="#1A0F0F",
    )


def discover_page() -> rx.Component:
    return rx.box(
        navbar(),
        rx.box(
            rx.image(
                src=State.current_movie["poster_url"],
                width="450px",
                border_radius="15px",
                user_select="none",
                style={"transition": "transform 0.3s ease-out"},
                _hover={"transform": "scale(1.01)"},
            ),
            position="relative",
        ),
        rx.hstack(
            rx.button(
                "Dislike",
                on_click=State.disliked,
                background_color="#A52A2A",
                font_size="2rem",
                color="white",
                width="150px",
                height="50px",
                _hover={
                    "transform": "scale(1.02)",
                    "background_color": "#8B1A1A",
                    "color": "#FFD7D7",
                },
                transition="all 0.3s ease",
            ),
            rx.button(
                "Like",
                on_click=State.liked,
                background_color="#A52A2A",
                font_size="2rem",
                color="white",
                width="150px",
                height="50px",
                _hover={
                    "transform": "scale(1.02)",
                    "background_color": "#8B1A1A",
                    "color": "#FFD7D7",
                },
                transition="all 0.3s ease",
            ),
        ),
        background="#1A0F0F",
        width="100%",
        display="flex",
        min_height="100vh",
        justify_content="center",
        align_items="center",
        flex_direction="column",
        gap="40px",
    )


def foryou_page() -> rx.Component:
    def card(movie):
        return rx.box(
            rx.image(
                src=rx.cond(movie["poster_url"], movie["poster_url"], "https://via.placeholder.com/200x300"),
                width="250px",
                border_radius="10px",
                style={"transition": "transform 0.3s ease-out"},
                _hover={"box_shadow":"10px,10px,0px,0px ,rgba(100,100,100,1)"}
            ),
            rx.text(
                rx.cond(movie["title"], movie["title"], "Unknown"),
                color="white",
                font_size="1rem",
                margin_top="10px",
                text_align="center",
                max_width="250px",
                overflow="auto",
                white_space="nowrap",
            ),
            background_color="rgba(255,255,255,0.03)",
            padding="20px",
            border_radius="12px",
            margin="10px",
            transition="all 0.35s ease-out",
            _hover={
                "transform": "translateY(-6px)",
                "box_shadow": "0 8px 30px rgba(0,0,0,0.6)",
            },
        )

    return rx.box(
        navbar(),
        rx.center(
            rx.vstack(
                rx.heading(
                    "For You",
                    color="white",
                    font_size="3rem",
                    margin_bottom="20px",
                ),
                rx.flex(
                    rx.foreach(
                        State.recommendations,
                        lambda movie: card(movie),
                    ),
                    wrap="wrap",
                    justify="center",
                    gap="20px",
                ),
                rx.button(
                    "Back",
                    on_click=State.reset_to_main,
                    background_color="#E50914",
                    color="white",
                    size="4",
                    padding_x="40px",
                    _hover={
                        "background_color": "#b20710",
                        "transform": "scale(1.05)",
                    },
                ),
                spacing="6",
                margin_top="50px",
            ),
        ),
        width="100%",
        height="100vh",
        background_color="#1A0F0F",
    )


app = rx.App(style={"body": {"background_color": "#8f0000"}})
app.add_page(index, route="/")
app.add_page(discover_page, route="/discover")
app.add_page(foryou_page, route="/foryou")
