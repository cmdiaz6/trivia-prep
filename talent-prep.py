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
        try:
            if 99 in film['genre_ids']: # skip documentaries
                continue 
            release_year = int( film['release_date'][0:4] )
            if film['release_date'] and release_year < 2026:
                film_list.append( (film['title'], film['release_date'], film['character']) )
        except:
            continue #release date or genre_ids not found
    film_list.sort(key=lambda x: x[1]) # sort by date
    for film in film_list:
        print( film[0] + ' (' + film[1] + ') - ' + film[2], end=' % ')

    # Check bio for academy award
    print(' ', end=delim)
    oscar_check = re.compile('[^.]+academy award[^.]+', re.IGNORECASE)
    bio = hit.info()['biography']
    if oscar_check.search( bio ):
        print( oscar_check.search( bio ).group(0), end=delim )
    else:
        print( 'NO OSCAR MENTIONS IN BIO', end=delim )



# read list of talent
#year_match = re.compile("[12][0-9][0-9][0-9]")
with open('talent_list.txt') as talent_list:
    for line in talent_list:
        talent = line.strip()

        print_talent_info( talent ) #, year )
        print('')
