import reflex as rx
import pandas as pd

_tfidf_cache = {"vectorizer": None, "matrix": None, "df": None}
df = pd.read_csv("Movies.csv")

# calculation to build recommendations
def build_recommendations(liked, disliked, seen, csv_path="Movies.csv"):
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    if _tfidf_cache["df"] is None:
        df_local = pd.read_csv(csv_path)
        df_local["features"] = (
            df_local.get("genres", "").fillna("") + " " +
            df_local.get("keywords", "").fillna("") + " "
        )
        tfidf = TfidfVectorizer(stop_words="english")
        tfidf_matrix = tfidf.fit_transform(df_local["features"])
        _tfidf_cache.update({"vectorizer": tfidf, "matrix": tfidf_matrix, "df": df_local})
    else:
        df_local = _tfidf_cache["df"]
        tfidf_matrix = _tfidf_cache["matrix"]

    if not liked:
        return []

    liked_idx = df_local[df_local["title"].isin(liked)].index.tolist()
    disliked_idx = df_local[df_local["title"].isin(disliked)].index.tolist()

    if len(liked_idx) == 0:
        return []

    liked_similarities = cosine_similarity(tfidf_matrix, tfidf_matrix[liked_idx])
    liked_score = liked_similarities.max(axis=1)

    df_copy = df_local.copy()
    df_copy["liked_score"] = liked_score

    if len(disliked_idx) > 0:
        disliked_similarities = cosine_similarity(tfidf_matrix, tfidf_matrix[disliked_idx])
        disliked_score = disliked_similarities.max(axis=1)
        df_copy["disliked_score"] = disliked_score
        df_copy["score"] = df_copy["liked_score"] - (0.5 * df_copy["disliked_score"])
    else:
        df_copy["score"] = df_copy["liked_score"]

    recs = df_copy[~df_copy["title"].isin(seen)].sort_values("score", ascending=False)
    return recs.head(10).to_dict("records")


# State
class State(rx.State):
    user_table: list[dict] = []
    count: int = 0
    liked_movies: list[str] = []
    disliked_movies: list[str] = []

# starts the process 
    def load_and_start(self):
        valid_movies = df[df["poster_url"].notna() & (df["poster_url"] != "")].copy()
        self.user_table = valid_movies.sample(min(200, len(valid_movies))).to_dict("records")
        self.count = 0
        self.liked_movies = []
        self.disliked_movies = []
        return rx.redirect("/discover")

# Stores meta data of liked movies
    def liked(self):
        title = self.current_movie.get("title")
        if title:
            self.liked_movies.append(title)
        return self.next_movie()

# Stores meta data of disliked movies
    def disliked(self):
        title = self.current_movie.get("title")
        if title:
            self.disliked_movies.append(title)
        return self.next_movie()

# Changes the movies in discover page
    def next_movie(self):
        self.count += 1
        if len(self.liked_movies) + len(self.disliked_movies) >= 10:
            return rx.redirect("/foryou")

# Handles when a movie is skipped in discover page
    def skipped(self):
        return self.next_movie()

# Handles when back is pressed in discover page
    def back(self):
        if self.count > 0:
            self.count -= 2
        else:
            self.count = -1
        return self.next_movie()

# Reset the app values to default
    def reset_to_main(self):
        self.count = 0
        return rx.redirect("/")

# Stores the meta data of the movie currently shown on discover page
    @rx.var
    def current_movie(self) -> dict:
        if self.user_table and self.count < len(self.user_table):
            return self.user_table[self.count]
        return {
            "title": "No Title",
            "poster_url": "https://via.placeholder.com/300x450?text=No+Poster",
            "genres": "Unknown",
        }

# Preloads movies in cache to reduce loading time
    @rx.var
    def preload_movies(self) -> list[dict]:
        if self.user_table and self.count < len(self.user_table):
            start_idx = self.count + 1
            end_idx = min(self.count + 20, len(self.user_table))
            return self.user_table[start_idx:end_idx]
        return []

# Stores the meta data of movies recommended by the build_recommendations function
    @rx.var
    def recommendations(self) -> list[dict]:
        if not self.liked_movies:
            return []
        seen_titles = [m.get("title") for m in self.user_table if m.get("title")]
        return build_recommendations(self.liked_movies, self.disliked_movies, seen_titles)


# UI elements

# NavBar
def navbar() -> rx.Component:
    return rx.flex(
        rx.button(
            "LUME",
            on_click=State.reset_to_main,
            color="white",
            font_size="2rem",
            font_weight="700",
            letter_spacing="20px",
            background_color="transparent",
            border="none",
            padding_x="0",
            padding_y="0",
            cursor="pointer",
            _hover={"transform": "scale(1.05)"},
            transition="all 0.8s ease",
        ),
        background_color="#8B0000",
        border="2px solid rgba(255,255,255,0.12)",
        height="75px",
        width="100%",
        position="fixed",
        z_index="1000",
        align="center",
        justify="center",
        padding_x="20px",
    )

# Home page
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

# Discover page
def discover_page() -> rx.Component:
    return rx.box(
        navbar(),
        rx.box(
            rx.box(
                [
                    rx.text(
                        letter,
                        color="#8b0000",
                        font_size="7rem",
                        font_weight="bold",
                        line_height="0.6",
                        style={
                            "transform": "rotate(90deg)",
                            "display": "inline-block",
                            "transformOrigin": "center center",
                            "margin": "0",
                        },
                    )
                    for letter in "#Discover"
                ],
                style={
                    "display": "flex",
                    "flexDirection": "column",
                    "alignItems": "center",
                    "gap": "6px",
                    "transform": "rotate(0deg)",
                    "display": "inline-flex",
                },
            ),
            padding_top="0px",
            padding_left="20px",
            width="auto",
            display="flex",
            justify_content="start",
            position="absolute",
            left="0",
            top="140px",
            z_index="5",
        ),
        rx.box(
            rx.foreach(
                State.preload_movies,
                lambda movie: rx.image(src=movie.get("poster_url"), display="none"),
            ),
            display="none",
        ),
        rx.flex(
            rx.hstack(
                rx.image(
                    src=State.current_movie["poster_url"],
                    width="500px",
                    height="auto",
                    border_radius="15px",
                    user_select="none",
                ),
                rx.vstack(
                    rx.box(
                        rx.text(
                            State.current_movie["title"],
                            color="white",
                            font_size="3rem",
                            font_weight="bold",
                            text_align="left",
                        ),
                    ),
                    rx.text(
                        "Genre: " + State.current_movie["genres"]
                        .to_string()
                        .replace("[", "")
                        .replace("]", "")
                        .replace("'", "")
                        .replace('"', ""),
                        color="#D3C0C0",
                        font_size="2rem",
                        font_weight="bold",
                        text_align="left",
                    ),
                    rx.hstack(
                        rx.button(
                            "Dislike",
                            on_click=State.disliked,
                            background_color="#7A1C1C",
                            font_size="2rem",
                            color="white",
                            width="250px",
                            height="100px",
                            border_radius="10px",
                            _hover={"transform": "scale(1.02)", "background_color": "#993333", "color": "#FFD7D7"},
                            transition="all 0.3s ease",
                        ),
                        rx.button(
                            "Like",
                            on_click=State.liked,
                            background_color="#145214",
                            font_size="2rem",
                            color="white",
                            width="250px",
                            height="100px",
                            border_radius="10px",
                            _hover={"transform": "scale(1.02)", "background_color": "#1E6A1E", "color": "#D7FFD7"},
                            transition="all 0.3s ease",
                        ),
                        spacing="2",
                        position="absolute",
                        bottom="100px",
                        left="0",
                        right="0",
                        top="590px",
                        justify_content="center",
                    ),
                    rx.hstack(
                        rx.button(
                            "Back",
                            on_click=State.back,
                            background_color="#444444",
                            font_size="1.5rem",
                            color="white",
                            width="150px",
                            height="50px",
                            border_radius="10px",
                            _hover={"transform": "scale(1.02)", "background_color": "#666666", "color": "#E0E0E0"},
                            transition="all 0.3s ease",
                        ),
                        rx.button(
                            "Restart",
                            on_click=State.load_and_start,
                            background_color="#444444",
                            font_size="1.5rem",
                            color="white",
                            width="180px",
                            height="50px",
                            border_radius="10px",
                            _hover={"transform": "scale(1.02)", "background_color": "#666666", "color": "#E0E0E0"},
                            transition="all 0.3s ease",
                        ),
                        rx.button(
                            "Skip",
                            on_click=State.skipped,
                            background_color="#444444",
                            font_size="1.5rem",
                            color="white",
                            width="150px",
                            height="50px",
                            border_radius="10px",
                            _hover={"transform": "scale(1.02)", "background_color": "#666666", "color": "#E0E0E0"},
                            transition="all 0.3s ease",
                        ),
                        spacing="2",
                        position="absolute",
                        bottom="100px",
                        left="0",
                        right="0",
                        top="700px",
                        justify_content="start",
                        gap="10px",
                    ),
                    border_radius="10px",
                    width="500px",
                    text_align="center",
                    position="relative",
                    min_height="700px",
                ),
                background_color="rgba(139, 0, 0, 0.3)",
                height="80vh",
                padding="30px",
                border_radius="20px",
                spacing="6",
                align_items="start",
            ),
            width="100%",
            justify_content="center",
            margin_top="140px",
        ),
        background_color="#1A0F0F",
        height="100vh",
        overflow="hidden",
        width="100%",
        flex_direction="column",
        gap="40px",
    )


#For You page
def foryou_page() -> rx.Component:
    def card(movie):
        return rx.box(
            rx.image(
                src=rx.cond(movie["poster_url"], movie["poster_url"], "https://via.placeholder.com/200x300"),
                width="280px",
                height="360px",
                border_radius="10px",
                loading="eager",
            ),
            rx.text(
                rx.cond(movie["title"], movie["title"], "Unknown"),
                max_width="220px",
                white_space="normal",
                overflow_wrap="break-word",
                word_break="break-word",
                color="white",
                font_size="1.1rem",
                margin_top="5px",
            ),
            background_color="rgba(139, 0, 0, 0.3)",
            padding="10px",
            border_radius="12px",
            margin="10px",
            transition="all 0.35s ease-out",
            _hover={"transform": "translateY(-6px)", "box_shadow": "0 8px 30px rgba(0,0,0,0.6)"},
        )

    return rx.box(
        navbar(),
        rx.hstack(
            rx.box(
                rx.box(
                    [
                        rx.text(
                            letter,
                            color="#8b0000",
                            font_size="5.5rem",
                            font_weight="bold",
                            line_height="0.5",
                            style={"transform": "rotate(90deg)", "display": "inline-block", "transformOrigin": "center center", "margin": "0"},
                        )
                        for letter in "#PickYourPoison"
                    ],
                    style={"display": "flex", "flexDirection": "column", "alignItems": "center", "gap": "6px", "transform": "rotate(0deg)", "display": "inline-flex"},
                ),
                padding_top="100px",
                padding_left="20px",
                width="30%",
                display="flex",
            ),
            rx.box(
                rx.flex(
                    rx.foreach(
                        State.recommendations,
                        lambda movie: card(movie),
                    ),
                    wrap="wrap",
                    justify="start",
                    padding_y="75px",
                ),
                width="300%",
            ),
            width="100%",
            align_items="start",
            justify_content="start",
            background_color="#1A0F0F",
            gap="0px",
        ),
        width="100%",
        height="100vh",
        background_color="#1A0F0F",
        overflow_x="hidden",
        overflow_y="hidden",
    )

#app
app = rx.App(style={"body": {"background_color": "#8f0000"}})
app.add_page(index, route="/")
app.add_page(discover_page, route="/discover")
app.add_page(foryou_page, route="/foryou")
