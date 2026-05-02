#!/usr/bin/env python3

import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import pandas as pd
import random
import json

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
                value=categories[0] if categories else None,
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

    # on-screen saved list
    html.Hr(),
    html.H3("Saved Trivia List", style={"textAlign": "center"}),
    html.Div(id="saved-list-display", style={
        "padding": "20px", 
        "fontSize": "16px", 
        "backgroundColor": "#eee", 
        "borderRadius": "10px",
        "margin": "20px auto",
        "maxWidth": "80%",
        "minHeight": "50px"
    }),

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

def get_random_trivia(movie, question_toggle):
    movie_trivia = "std_trivia" in question_toggle
    trivia_cols = [col for col in movie.index if col.startswith("Question") and pd.notna(movie[col]) and str(movie[col]).strip()]
    
    if movie_trivia:
        if not trivia_cols:
            return None, None, None
        col = random.choice(trivia_cols)
        question = movie[col]
        return question, movie.get("Answer", "ANSWER NOT FOUND"), movie.get("Multiple", "NO MULTIPLE CHOICE")
    else:
        return "Bonus Question Placeholder", "NOTHING TO SEE HERE", "!"

@app.callback(
    [Output("trivia-output", "children"),
     Output("save-btn", "data-trivia"),
     Output("answer-output-wrapper", "children"),
     Output("save-status", "children", allow_duplicate=True)],
    [Input("generate-btn", "n_clicks")],
    [State("category-selector", "value"),
     State("question-toggle", "value"),
     State("saved-list-display", "children")],
    prevent_initial_call=True
)
def generate_trivia(generate_clicks, selected_category, question_toggle, current_saved_list):
    # 1. Get all saved questions as a simple list of strings for comparison
    saved_questions = []
    if current_saved_list:
        for item in current_saved_list:
            # The structure of our Div is [bullet, display_text]
            content = item['props']['children'][1]
            # If it's a link, the text is inside its props
            if isinstance(content, dict) and 'props' in content:
                saved_questions.append(content['props']['children'])
            else:
                saved_questions.append(content)

    filtered_df = df[df["Wheel Category"] == selected_category]
    
    # 2. Filter out questions already in the saved list[cite: 1]
    available_rows = []
    for _, row in filtered_df.iterrows():
        question, answer, multiple_choices = get_random_trivia(row, question_toggle)
        full_string = f"{selected_category}: {question} (Ans: {answer})"
        if full_string not in saved_questions:
            available_rows.append((row, question, answer, multiple_choices))

    # 3. Handle 'All Questions Saved' scenario[cite: 1]
    if not available_rows:
        return html.Div("⚠️ All questions in this category have been saved!", 
                        style={"color": "red", "fontWeight": "bold"}), "", "", ""

    # 4. Pick from what's left
    random_movie, question, answer, multiple_choices = random.choice(available_rows)
    title = random_movie["Wheel Category"]
    link = random_movie.get("Media")

    display_items = [html.Div(f"{title}!", style={"fontWeight": "bold", "fontSize": "24px"})]

    if link:
        display_items.append( html.A(question, href=media_base + link, target="_blank") )
    else:
        display_items.append( html.Div(question, style={"marginTop": "10px"}) )

    trivia_payload = json.dumps({
        "text": f"{title}: {question} (Ans: {answer})",
        "link": link if link else None
    })

    if 'NO MULTIPLE CHOICE' in str(multiple_choices):
        answer_section = html.Details([
            html.Summary("\ud83d\udd75 Reveal Answer Choices"),
            html.Div( answer, style={"marginTop": "10px", "fontStyle": "italic"})
        ], style={"marginTop": "10px"})
    else:
        answer_section = html.Details([
            html.Summary("\ud83d\udd75 Reveal Answer Choices"),
            html.Div( [multiple_choices, html.Br(), answer], style={"marginTop": "10px", "fontStyle": "italic"})
        ], style={"marginTop": "10px"})

    return html.Div(display_items), trivia_payload, answer_section, ""

@app.callback(
    [Output("save-status", "children"),
     Output("saved-list-display", "children")],
    [Input("save-btn", "n_clicks")],
    [State("save-btn", "data-trivia"),
     State("saved-list-display", "children")]
)
def save_trivia(save_clicks, trivia_payload, current_list):
    if save_clicks > 0 and trivia_payload:
        if current_list is None:
            current_list = []
            
        data = json.loads(trivia_payload) # Unpack the text and link[cite: 1]
        text = data['text']
        link = data['link']
        
        # If there's a link, wrap the text in an html.A tag[cite: 1]
        if link:
            display_text = html.A(text, href=media_base + link, target="_blank", style={"color": "#0074D9"})
        else:
            display_text = text

        # Create a new entry
        new_entry = html.Div([
            "• ", 
            display_text
        ], style={"borderBottom": "1px solid #ccc", "padding": "5px"})
        
        current_list.append(new_entry)

        # save to file
        try:
            with open("used_trivia.txt", "a") as f:
                f.write(f"{text}\n")
            return html.Span("\u2705 Trivia saved!", id="save-animation"), current_list
        except Exception as e:
            return f"Error saving trivia: {e}", current_list
    return "", current_list

if __name__ == '__main__':
    app.run(debug=True)
