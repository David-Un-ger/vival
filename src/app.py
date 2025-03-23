import dash_mantine_components as dmc
from dash import Dash, Input, Output, State, _dash_renderer, ctx, dcc
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify
from flask import Flask, send_from_directory

from src.components import paper_with_label
from src.data.database import create_table, get_dictionary, get_image, get_random_word
from src.definitions import IMAGE_FOLDER

_dash_renderer._set_react_version("18.2.0")

server = Flask(__name__)


@server.route("/images/<path:image_name>")
def serve_image(image_name):
    """Use the flask server to serve the images as they are not accessible from the Dash app"""
    return send_from_directory(IMAGE_FOLDER, image_name)


app = Dash(external_stylesheets=dmc.styles.ALL, server=server)

"""
Callback structure:
- If a word is entered, the search button is clicked or the URL is loaded the word store is updated
   - This shows the output card
   - And triggers the loading animation
   - And it triggers the loading of the dict information
   - Further it updates the URL with the word
- Once the dict information is loaded
    - The output is updated with the dict information
    - The image generation is triggered
- Once the image is generated
    - The image is shown
"""

app.layout = dmc.MantineProvider(
    children=[
        dcc.Store(id="store-word"),
        dcc.Store(id="store-dict"),
        dcc.Location(id="url", refresh="callback-nav"),
        dmc.Stack(
            [
                dmc.Title("vival", style={"fontSize": "80px", "fontWeight": "bold", "marginBottom": "-20px"}, order=1),
                dmc.Title("The Visual Dictionary", style={"fontSize": "16px"}, order=2),
                dmc.TextInput(
                    id="search-input",
                    w=300,
                    radius="sm",
                    # autoComplete="on",
                    spellCheck=False,
                    rightSectionWidth="68",
                    rightSection=dmc.Group(
                        gap="0px",
                        wrap="nowrap",
                        children=[
                            dmc.ActionIcon(
                                id="clear-button",
                                children="✕",
                                variant="transparent",
                                size="md",
                            ),
                            dmc.ActionIcon(
                                DashIconify(icon="material-symbols:search"),
                                id="search-button",
                                size="md",
                            ),
                        ],
                    ),
                ),
                dmc.Card(
                    [
                        dmc.LoadingOverlay(
                            visible=False,
                            id="loading-overlay-card",
                            overlayProps={"radius": "sm", "blur": 5},
                            zIndex=10,
                        ),
                        dmc.Grid(
                            children=[
                                dmc.GridCol(
                                    span=6,
                                    children=[
                                        dmc.Title("landscape", id="show-word"),
                                        paper_with_label(
                                            "Meaning",
                                            [
                                                dmc.Text(
                                                    id="show-meaning",
                                                    size="sm",
                                                )
                                            ],
                                        ),
                                        paper_with_label(
                                            "Usage examples",
                                            [
                                                dmc.List(id="show-usage", size="sm"),
                                            ],
                                        ),
                                        paper_with_label(
                                            "Phonetics",
                                            [
                                                dmc.Text(size="sm", id="show-phonetics"),
                                            ],
                                        ),
                                        paper_with_label(
                                            "Synonyms",
                                            [
                                                dmc.Group(id="show-synonyms"),
                                            ],
                                        ),
                                    ],
                                ),
                                dmc.GridCol(
                                    span=6,
                                    children=[
                                        paper_with_label(
                                            "",
                                            [
                                                dmc.LoadingOverlay(
                                                    visible=False,
                                                    id="loading-overlay-image",
                                                    overlayProps={"radius": "sm", "blur": 5},
                                                    zIndex=10,
                                                ),
                                                dmc.Image(id="show-image"),
                                            ],
                                            center=True,
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ],
                    withBorder=True,
                    shadow="sm",
                    radius="sm",
                    w=800,
                    # visibleFrom="display: none",
                    id="show-card",
                ),
            ],
            align="center",
            gap="sm",
        ),
    ],
    forceColorScheme="dark",
)


@app.callback(
    Output("store-word", "data", allow_duplicate=True),
    Output("loading-overlay-card", "visible", allow_duplicate=True),
    Output("show-card", "style", allow_duplicate=True),  # required to show the loading animation
    Input("search-input", "n_submit"),
    Input("search-button", "n_clicks"),
    Input("url", "search"),
    State("search-input", "value"),
    prevent_initial_call=True,
)
def enter_search(n_submit, n_clicks, url, word):
    if n_submit is None and n_clicks is None and url is None:
        raise PreventUpdate
    if ctx.triggered_id == "url":
        # if the url is loaded, use the url. Otherwise use the text input
        if url is None:
            raise PreventUpdate

        if url == "":
            word = get_random_word()
        else:
            url_word = url.lstrip("?s=")
            if url_word == word:
                raise PreventUpdate
            word = url_word
    return word, True, {"display": "block"}


@app.callback(Output("url", "search"), Input("store-word", "data"), prevent_initial_call=True)
def update_url_from_store(word):
    if not word:
        raise PreventUpdate

    return f"?s={word}"


@app.callback(
    Output("store-dict", "data"),
    Output("show-card", "style", allow_duplicate=True),
    Output("show-word", "children"),
    Output("loading-overlay-card", "visible", allow_duplicate=True),
    Output("loading-overlay-image", "visible", allow_duplicate=True),
    Input("store-word", "data"),
    prevent_initial_call=True,
)
def show_word_and_get_dict(word):
    dict_ = get_dictionary(word)
    return dict_, {"display": "block"}, word, False, True


@app.callback(
    Output("show-meaning", "children"),
    Output("show-usage", "children"),
    Output("show-synonyms", "children"),
    Output("show-phonetics", "children"),
    Input("store-dict", "data"),
)
def show_card_infos(dict_):
    if dict_ is None:
        raise PreventUpdate
    meaning = dict_.get("meaning")
    usage = dict_.get("usage")
    synonyms = dict_.get("synonyms")
    phonetics = dict_.get("phonetics")

    usage = [dmc.ListItem(sentence) for sentence in usage]
    synonyms = [dmc.Badge(synonym) for synonym in synonyms]

    return meaning, usage, synonyms, phonetics


@app.callback(
    Output("show-image", "src"),
    Output("loading-overlay-image", "visible"),
    Input("store-dict", "data"),
)
def show_image(dict_):
    if dict_ is None:
        raise PreventUpdate

    image_text = dict_.get("image_description")
    word = dict_.get("word")
    return get_image(word, image_text), False


@app.callback(
    Output("search-input", "value"),
    Output("show-card", "style", allow_duplicate=True),
    Input("clear-button", "n_clicks"),
    prevent_initial_call=True,
)
def clear_search_and_hide_output_card(n_clicks):
    if n_clicks is None:
        raise PreventUpdate

    return "", {"display": "none"}


if __name__ == "__main__":
    # app.run(debug=False)
    create_table()
    app.run(host="0.0.0.0", port=8050, debug=True)  # http://localhost:8050
