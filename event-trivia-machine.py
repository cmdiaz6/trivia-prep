#!/usr/bin/env python3

import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import pandas as pd
import random

# Load data
df = pd.read_csv("event-trivia-sheet.csv").fillna("")

# base path for media files
media_base = '/assets/media/'

# Initialize app
app = dash.Dash(__name__)

# Dynamically extract categories from the data
categories = sorted(df["Wheel Category"].dropna().unique())

app.layout = html.Div([
    html.H1("\ud83c\udfac The New Trivia Machine \U0001F916", style={"textAlign": "center", "marginBottom": "30px", "color": "#333"}),

    dcc.Store(id="used-trivia-store"),

    html.Div(style={"display": "flex", "justifyContent": "center", "alignItems": "start"}, children=[
        html.Div([
            html.Label("Choose a question type:", style={"fontWeight": "bold", "fontSize": "18px"}),
            dcc.RadioItems(
                id="question-toggle",
                options=[
                    {"label": "Event Trivia", "value": "std_trivia"},
                    {"label": "Bonus Trivia", "value": "bonus_trivia"},
                ],
                value="std_trivia",
                labelStyle={"display": "block", "margin": "5px 0"},
                inputStyle={"marginRight": "10px"}
            ),
            html.Label("Choose a category:", style={"fontWeight": "bold", "fontSize": "18px"}),
            dcc.RadioItems(
                id="category-selector",
                options=[{"label": category, "value": category} for category in categories],
                value=categories[0],
                labelStyle={"display": "block", "margin": "6px 0"},
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

#
def get_random_trivia(movie, question_toggle):
    movie_trivia = "std_trivia" in question_toggle
    trivia_cols = [col for col in movie.index if col.startswith("Question") and pd.notna(movie[col]) and movie[col].strip()]
    if movie_trivia:
        if not trivia_cols:
            return None, None
        col = random.choice(trivia_cols)
        question = movie[col]
        print(col)
        return question, movie.get("Answer", "ANSWER NOT FOUND"), movie.get("Multiple", "NO MULTIPLE CHOICE")
    else:
        return question, "NOTHING TO SEE HERE", "!"

@app.callback(
    [Output("trivia-output", "children"),
     Output("save-btn", "data-trivia"),
     Output("answer-output-wrapper", "children"),
     Output("save-status", "children", allow_duplicate=True)],
    [Input("generate-btn", "n_clicks")],
    [State("category-selector", "value"),
     #State("difficulty-selector", "value"),
     State("question-toggle", "value")],
    prevent_initial_call=True
)
def generate_trivia(generate_clicks, selected_category, question_toggle):
    filtered_df = df[df["Wheel Category"] == selected_category]
    attempts = 200
    while attempts > 0 and not filtered_df.empty:
        random_movie = filtered_df.sample(n=1).iloc[0]
        title = random_movie["Wheel Category"]
        test = random_movie.get("Question")
        link = random_movie.get("Media")

        question, answer, multiple_choices = get_random_trivia(random_movie, question_toggle)

        if not question:
            attempts -= 1
            continue
        else:
            print('--',title,' - ', answer)
        print('----------')

        display_items = [html.Div(f"{title}!", style={"fontWeight": "bold", "fontSize": "24px"})]

        if link:
            display_items.append( html.A(question, href=media_base + link, target="_blank") )
        else:
            display_items.append( html.Div(question, style={"marginTop": "10px"}) )

        trivia_data = f"{title}!: {question} | Choices: {answer}"

        if 'NO MULTIPLE CHOICE' in multiple_choices:
            answer_section = html.Details([
                html.Summary("\ud83d\udd75 Reveal Answer Choices"),
                html.Div( answer, style={"marginTop": "10px", "fontStyle": "italic"})
            ], style={"marginTop": "10px"})
        else:
            answer_section = html.Details([
                html.Summary("\ud83d\udd75 Reveal Answer Choices"),
                html.Div( [multiple_choices, html.Br(), answer], style={"marginTop": "10px", "fontStyle": "italic"})
            ], style={"marginTop": "10px"})

        return html.Div(display_items), trivia_data, answer_section, ""

    return "No trivia available for this category. Please try again later.", "", "", ""

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

