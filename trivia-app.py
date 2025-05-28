#!/usr/bin/env python

import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import pandas as pd
import random

# Load data
df = pd.read_csv("trivia-sheet.csv")  # Ensure columns include "Title", "Year", "Genre", "Plot", "Trivia Q 1", "Trivia Q 2", etc.

# Initialize app
app = dash.Dash(__name__)

# Define genres
genres = ["Action / Adventure", "Animation", "Comedy", "Drama", "Fantasy", "Horror", "Sci-Fi"]

app.layout = html.Div([
    html.Div([
        html.Label("Choose a genre:"),
        dcc.RadioItems(
            id="genre-selector",
            options=[{"label": genre, "value": genre} for genre in genres],
            value=genres[0]  # Default selection
        ),
        html.Button("Get Random Trivia", id="generate-btn", n_clicks=0)
    ], style={"width": "30%", "display": "inline-block", "verticalAlign": "top"}),

    html.Div([
        html.Div(id="trivia-output", style={"fontSize": "20px"}),
        html.Button("Save Trivia", id="save-btn", n_clicks=0, style={"marginTop": "10px"}),
        html.Div(id="save-status", style={"marginTop": "5px", "color": "green"})
    ], style={"width": "65%", "display": "inline-block", "paddingLeft": "20px"})
])

@app.callback(
    [Output("trivia-output", "children"),
     Output("save-btn", "data-trivia")],  # Store trivia data for saving
    [Input("generate-btn", "n_clicks"),
     Input("genre-selector", "value")]
)
def generate_trivia(n_clicks, selected_genre):
    if n_clicks > 0 and selected_genre:
        filtered_df = df[df["Genre"] == selected_genre]  # Filter movies by genre
        attempts = 10  # Limit retries to avoid infinite loops

        while attempts > 0:
            random_movie = filtered_df.sample(n=1).iloc[0]  # Select a random movie
            title = random_movie["Title"]
            year = random_movie["Year"]
            plot = random_movie["Plot"]

            # Find all non-empty trivia columns
            trivia_columns = [col for col in random_movie.index if col.startswith("Trivia Q ") and pd.notna(random_movie[col]) and random_movie[col].strip()]

            if trivia_columns:
                trivia_question = random_movie[random.choice(trivia_columns)]  # Pick a random trivia question
                trivia_data = f"{title} ({year}): {trivia_question}"  # Format for saving
                return (html.Div([
                    html.Div(f"**{title}**", style={"fontWeight": "bold", "fontSize": "24px"}),
                    html.Div(trivia_question, style={"marginTop": "10px"}),
                    html.Div(f"Plot: {plot}", style={"marginTop": "10px", "fontStyle": "italic"})
                ]), trivia_data)
            
            attempts -= 1  # Try another movie if no trivia found

        return ("No trivia available for this genre. Please try again later.", "")
    
    return ("Choose a genre and click the button to generate a trivia question!", "")

@app.callback(
    Output("save-status", "children"),
    [Input("save-btn", "n_clicks")],
    [State("save-btn", "data-trivia")]
)
def save_trivia(n_clicks, trivia_data):
    if n_clicks > 0 and trivia_data:
        try:
            with open("used_trivia.txt", "a") as f:
                f.write(f"{n_clicks}. {trivia_data}\n")  # Numbered entry
            return "Trivia saved successfully!"
        except Exception as e:
            return f"Error saving trivia: {e}"
    return ""

if __name__ == '__main__':
    app.run(debug=True)
