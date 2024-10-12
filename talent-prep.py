#!/usr/bin/env -S python -u

# based on movie-prep.py. read in list of talent, returns filmography
# only returns if in cast, not crew (director, producer, etc)

# https://github.com/celiao/tmdbsimple/
import tmdbsimple as tmdb
import re

with open('TMDB.API_KEY', 'r') as key_file:
    tmdb.API_KEY = key_file.read().strip()

delim='@ ' # using commas messes up some movies e.g. The Good, The Bad, and The Ugly

def print_talent_info(talent, year=None):
    search = tmdb.Search()
    response = search.person(query=talent, include_adult=False)

    # get first hit of search result (make sure title is accurate)
    # TODO: check release date or popularity to prevent remake errors
    #       e.g. Moana (2026) only has 1 cast member. I want Moana (2016)
    try:
        hit = search.results[0]     # or use response['results'] ?
    except IndexError:
        print( 'TALENT NOT FOUND',' ',talent, year, sep=delim, end=delim)
        return

    hit = tmdb.People( hit['id'] )
    print( talent, sep=delim, end=delim)

    films = hit.movie_credits() # list/dict of all
    films = films['cast'] # exclude crew (director, producer, etc)

    # Loop through films. get title (or original_title?) and release_date
    film_list = []
    for film in films:
        if film['release_date']: # exclude unreleased films
            film_date = film['title'] + ' (' + film['release_date'] + ')'
            film_list.append( film_date )
    print( *film_list, sep='/', end=delim)


# read list of talent
#year_match = re.compile("[12][0-9][0-9][0-9]")
with open('talent_list.txt') as talent_list:
    for line in talent_list:
        talent = line.strip()

        print_talent_info( talent ) #, year )
        print('')
