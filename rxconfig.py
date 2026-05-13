import reflex as rx

config = rx.Config(
    app_name="Movie_Recommender",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ]
)