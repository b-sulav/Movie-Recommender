import reflex as rx
import pandas as pd

# State
class State(rx.State):
    user_table: list[dict] = []
    count: int = 0

    def load_and_start(self):
        try:
            df = pd.read_csv("Movies.csv")
            self.user_table = df.sample(15).to_dict("records")
            self.count = 0
            return rx.redirect("/discover")
        except Exception as e:
            print(f"Error loading CSV: {e}")

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
            "poster_url": "https://via.placeholder.com/300x450?text=No+Poster"
        }

    def handle_swipe(self, event_data: dict):
        dx = event_data.get("delta_x", 0)
        if dx > 150:
            return self.next_movie()
        elif dx < -150:
            return self.next_movie()


# Navbar
def navbar() -> rx.Component:
    return rx.flex(
        rx.button(
            rx.image(
                width="100px",
                height="auto",
            ),
            on_click=State.reset_to_main,
            background="transparent",
            border="none",
            _hover={"cursor": "pointer", "opacity": "0.8"},
            position="absolute",
            left="40px",
        ),
        background_color="#8B0000",
        height="10px",
        width="100%",
        position="fixed",
        top="0",
        left="0",
        z_index="1000",
        align="center",
        justify="center",
        padding_x="20px",
    )


# Footer
def footer() -> rx.Component:
    return rx.flex(
        background_color="#8B0000",
        height="10px",
        width="100%",
        position="fixed",
        bottom="0",
        left="0",
        z_index="1000",
        align="center",
        justify="center",
        padding_x="20px",
    )


# Home
def index() -> rx.Component:
    return rx.box(
        navbar(),
        footer(),
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
                    _hover={"transform": "rotate(-15deg)"},
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


# Discover
def discover_page() -> rx.Component:
    return rx.box(
        navbar(),
        footer(),
        rx.image(
            src=State.current_movie["poster_url"],
            width="450px",
            border_radius="15px",
            user_select="none",
            style={"transition": "transform 0.3s ease-out"},
            _hover={"transform": "scale(1.05)"},
        ),
        rx.hstack(
            rx.button(
                "Dislike",
                on_click=State.next_movie,
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
                on_click=State.next_movie,
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


# ForYou
def foryou_page() -> rx.Component:
    return rx.box(
        navbar(),
        footer(),
        rx.center(
            rx.vstack(
                rx.heading(
                    "For You",
                    color="white",
                    font_size="3rem",
                    margin_bottom="20px",
                ),
                rx.box(
                    rx.text(
                        "Based on your swipes, we think you'll love these...",
                        color="gray",
                    ),
                    padding="20px",
                    text_align="center",
                ),
                rx.button(
                    "Main Menu",
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
                margin_top="100px",
            ),
        ),
        width="100%",
        height="100vh",
        background_color="#1A0F0F",
    )


# App
app = rx.App(style={"body": {"background_color": "#8f0000"}})
app.add_page(index, route="/")
app.add_page(discover_page, route="/discover")
app.add_page(foryou_page, route="/foryou")
