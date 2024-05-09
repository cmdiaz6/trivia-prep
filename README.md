# trivia-prep
Getting movie info from TMDB to help with movie trivia prep for a friend

## Installation
- uses tmdbsimple python API: https://github.com/celiao/tmdbsimple
```
pip install tmdbsimple
```
- Get a TMDB account and an API key: https://developer.themoviedb.org/docs/getting-started
- Put your API key in a file called TMDB.API_KEY

## Usage
In movie_list.txt put movie titles (optional: follow by 4-digit year to make sure it's the right one) and then run this sucker
```
./movie_prep.py > output.txt
```
prints a bunch of lines to copy into an excel doc. Split cells by delim='@'. One day I'll make this a CSV directly
