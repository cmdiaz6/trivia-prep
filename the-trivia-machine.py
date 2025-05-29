#!/usr/bin/env python

import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import pandas as pd
import random

# Load data
df = pd.read_csv("trivia-sheet.csv")

# Initialize app
app = dash.Dash(__name__)

# Dynamically extract genres from the data
genres = sorted(df["Genre"].dropna().unique())

app.layout = html.Div([
    html.H1("\ud83c\udfac The Trivia Machine", style={"textAlign": "center", "marginBottom": "30px", "color": "#333"}),

    dcc.Store(id="used-trivia-store"),

    html.Div(style={"display": "flex", "justifyContent": "center", "alignItems": "start"}, children=[
        html.Div([
            dcc.Checklist(
                id="plot-toggle",
                options=[{"label": "Include Plot", "value": "show"}],
                value=["show"],
                style={"marginBottom": "20px"}
            ),
            html.Label("Choose a genre:", style={"fontWeight": "bold", "fontSize": "18px"}),
            dcc.RadioItems(
                id="genre-selector",
                options=[{"label": genre, "value": genre} for genre in genres],
                value=genres[0],
                labelStyle={"display": "block", "margin": "5px 0"},
                inputStyle={"marginRight": "10px"}
            ),
            html.Label("Choose a year range:", style={"fontWeight": "bold", "fontSize": "18px", "marginTop": "20px"}),
            dcc.RadioItems(
                id="year-selector",
                options=[
                    {"label": "All Years", "value": "all"},
                    {"label": "< 1970", "value": "pre1970"},
                    {"label": "1970 - 1999", "value": "1970to1999"},
                    {"label": "> 1999", "value": "post1999"},
                ],
                value="all",
                labelStyle={"display": "block", "margin": "5px 0"},
                inputStyle={"marginRight": "10px"}
            ),
            html.Button("\ud83c\udfb2 Get Random Trivia", id="generate-btn", n_clicks=0,
                        style={"marginTop": "10px", "backgroundColor": "#0074D9", "color": "white",
                               "border": "none", "padding": "10px 20px", "borderRadius": "5px",
                               "animation": "pulse 2s infinite"})
        ], style={"width": "30%", "display": "inline-block", "verticalAlign": "top", "padding": "20px",
                  "backgroundColor": "#f9f9f9", "borderRadius": "10px",
                  "boxShadow": "0 0 10px rgba(0,0,0,0.1)"}),

        html.Div([
            html.Div(id="trivia-output", style={"fontSize": "20px", "minHeight": "150px"}),
            html.Div(id="answer-output-wrapper"),
            html.Button("\ud83c\udfb2 Save Trivia", id="save-btn", n_clicks=0,
                        style={"marginTop": "10px", "backgroundColor": "#2ECC40", "color": "white",
                               "border": "none", "padding": "10px 20px", "borderRadius": "5px",
                               "transition": "transform 0.3s ease"}),
            html.Div(id="save-status", style={"marginTop": "10px", "fontStyle": "italic", "color": "green"})
        ], style={"width": "65%", "display": "inline-block", "padding": "20px", "verticalAlign": "top"})
    ]),

    dcc.Markdown("""
    <style>
    @keyframes saveEffect {
      0% { background-color: #2ECC40; transform: scale(1); }
      50% { background-color: #27AE60; transform: scale(1.1); }
      100% { background-color: #2ECC40; transform: scale(1); }
    }
    @keyframes pulse {
      0% { transform: scale(1); }
      50% { transform: scale(1.05); }
      100% { transform: scale(1); }
    }
    #save-btn.saved {
      animation: saveEffect 0.5s;
    }
    </style>
    """, dangerously_allow_html=True)
])

def get_filtered_df(selected_genre, selected_year_range):
    filtered = df[df["Genre"] == selected_genre]
    if selected_year_range == "pre1970":
        filtered = filtered[filtered["Year"] < 1970]
    elif selected_year_range == "1970to1999":
        filtered = filtered[(filtered["Year"] >= 1970) & (filtered["Year"] <= 1999)]
    elif selected_year_range == "post1999":
        filtered = filtered[filtered["Year"] > 1999]
    return filtered

def get_random_trivia(movie):
    trivia_cols = [col for col in movie.index if col.startswith("Trivia Q ") and pd.notna(movie[col]) and movie[col].strip()]
    if not trivia_cols:
        return None, None, None
    col = random.choice(trivia_cols)
    question = movie[col]
    answer_col = col.replace("Trivia Q ", "Q") + " Mult Choice & Answer"
    return question, movie.get(answer_col, ""), col

@app.callback(
    [Output("trivia-output", "children"),
     Output("save-btn", "data-trivia"),
     Output("answer-output-wrapper", "children"),
     Output("save-status", "children", allow_duplicate=True)],
    [Input("generate-btn", "n_clicks")],
    [State("genre-selector", "value"),
     State("year-selector", "value"),
     State("plot-toggle", "value")],
    prevent_initial_call=True
)
def generate_trivia(generate_clicks, selected_genre, selected_year_range, plot_toggle):
    filtered_df = get_filtered_df(selected_genre, selected_year_range)
    attempts = 10
    while attempts > 0 and not filtered_df.empty:
        random_movie = filtered_df.sample(n=1).iloc[0]
        title = random_movie["Title"]
        year = random_movie["Year"]
        plot = random_movie.get("Plot", "")

        question, answer_choices, col = get_random_trivia(random_movie)
        if not question:
            attempts -= 1
            continue

        include_plot = "show" in plot_toggle
        display_items = [html.Div(f"{title} ({year})", style={"fontWeight": "bold", "fontSize": "24px"})]
        if include_plot and plot:
            display_items.append(html.Div(f"Plot: {plot}", style={"marginTop": "10px", "fontStyle": "italic"}))
            trivia_data = f"{title} ({year}): {plot}"
            answer_section = html.Button("\ud83d\udd75 Reveal Answer Choices", disabled=True,
                                         style={"marginTop": "10px", "backgroundColor": "#ccc", "color": "white",
                                                "border": "none", "padding": "10px 20px", "borderRadius": "5px"})
        else:
            display_items.append(html.Div(question, style={"marginTop": "10px"}))
            trivia_data = f"{title} ({year}): {question} | Choices: {answer_choices}"
            answer_section = html.Details([
                html.Summary("\ud83d\udd75 Reveal Answer Choices"),
                html.Div(answer_choices, style={"marginTop": "10px", "fontStyle": "italic"})
            ], style={"marginTop": "10px"})

        return html.Div(display_items), trivia_data, answer_section, ""

    return "No trivia available for this genre. Please try again later.", "", "", ""

@app.callback(
    Output("save-status", "children"),
    [Input("save-btn", "n_clicks")],
    [State("save-btn", "data-trivia")]
)
def save_trivia(save_clicks, trivia_data):
    if save_clicks > 0 and trivia_data:
        try:
            with open("used_trivia.txt", "a") as f:
                f.write(f"{save_clicks}. {trivia_data}\n")
            return html.Span("\u2705 Trivia saved!", id="save-animation")
        except Exception as e:
            return f"Error saving trivia: {e}"
    return ""

if __name__ == '__main__':
    app.run(debug=True)
