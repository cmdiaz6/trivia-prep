#!/usr/bin/env -S python -u

# https://github.com/celiao/tmdbsimple/
import tmdbsimple as tmdb
import re
#import csv
#from collections import OrderedDict
#genres = list(OrderedDict.fromkeys(genres)) # remove duplicates

#TODO: write to CSV file - separate cell with line-breaks instead of ' / '

with open('TMDB.API_KEY', 'r') as key_file:
    tmdb.API_KEY = key_file.read().strip()

delim='@ ' # using commas messes up some movies e.g. The Good, The Bad, and The Ugly

def print_movie_info(movie, year=None):
    search = tmdb.Search()
    response = search.movie(query=movie, year=year)

    # get first hit of search result (make sure title is accurate)
    # TODO: check release date or popularity to prevent remake errors
    #       e.g. Moana (2026) only has 1 cast member. I want Moana (2016)
    try:
        hit = search.results[0]     # or use response['results'] ?
    except IndexError:
        print( 'MOVIE NOT FOUND',' ',movie, year, sep=delim, end=delim)
        return

    year = hit['release_date'][:4]
    # original_title, overview, vote_average(?), vote_count(?)

    hit = tmdb.Movies( hit['id'] )
    cast = hit.credits()['cast'] # actors - name, character_name, gender, adult, etc
    crew = hit.credits()['crew'] # job, name, department, etc
    info = hit.info()            # production_companies, genres, budget, runtime, etc
    keywords = hit.keywords()    #  dystopia, etc?
    # info, 

    # print genres 'genre1 [/ genre2...], '
    # print sub-genre: Musical, Romance, Thriller/Mystery/Noir, Biopic
    genres = []
    subgenres = []
    for genre in hit.info()['genres']:
        is_subgenre = False
        name = genre['name']
        # TODO: better way to do this for multiple. Dictionary?
        match name:
            case 'Science Fiction':
                name = 'Sci-Fi'
            case 'Action' | 'Adventure':
                name = 'Action/Adventure'
            case 'Music':
                name = 'Musical'
                is_subgenre = True
            case 'Romance':
                is_subgenre = True
            case 'Thriller' | 'Mystery' | 'Noir':
                # TODO: search keywords for Noir
                name = 'Thriller/Mystery/Noir'
                is_subgenre = True
            case 'Noir':
                # TODO: search keywords
                is_subgenre = True

        if is_subgenre:
            subgenres.append( name )
        else:
            genres.append( name )

    genres = set(genres) # remove duplicates - doesn't preserve order
    subgenres = set(subgenres) # remove duplicates - doesn't preserve order
    print( *genres, sep='/', end=delim)
    print( *subgenres, sep='/', end=delim)

    # print 'Title, Tagline, Year, '
    tagline = hit.info()['tagline']
    print( movie, tagline, year, sep=delim, end=delim)

    # Actor categories: adult, gender, id, name, original_name, character, etc

    # print top 3 billed actors as 'Actor : Character, '
    small_cast = False
    separator=' : '
    try:
        print( cast[0]['name'], cast[0]['character'] , sep=separator, end=delim)
    except IndexError:
        print( 'CAST NOT FOUND - check movie', end=delim)
        return
    try:
        print( cast[1]['name'], cast[1]['character'] , sep=separator, end=delim)
    except IndexError:
        small_cast = True
        print(' ',end=delim)
    try:
        print( cast[2]['name'], cast[2]['character'] , sep=separator, end=delim)
    except IndexError:
        small_cast = True
        print(' ',end=delim)

    # print Notable non-male actor (gender /= 2)
    blank_fourth = True # if none found
    if not small_cast:
        count = 0
        for actor in cast:
            count += 1
            if actor['gender'] and actor['gender'] != 2:
                if count <= 3: 
                    first_non_male = actor['name'], actor['character']
                    continue # skip if actor is already in top 3
                print( actor['name'], actor['character'], sep=separator, end=delim)
                blank_fourth = False
                break # exit loop once found
    if blank_fourth:
        print(' ',end=delim)

    # print notable child actor
    # TODO: move this into the previous loop to save time
    blank_child = True
    for actor in cast:
        # id, info, latest, movie_credits, tv_credits, etc
        person = tmdb.People( actor['id'] ).info() # also_known_as, biography, birthday, deathday, gender, place_of_birth
        try:
            yob = person['birthday'][:4]
        except TypeError:
            break

        age_at_filming = int(year) - int(yob)
        if age_at_filming < 18:
            print( actor['name'], actor['character'], sep=separator, end=delim)
            blank_child = False
            break
    if blank_child:
        print(' ',end=delim)


    # print director(s), writer(s)
    directors = []
    writers = [] # job == 'Screenplay'
    producers = []
    for item in crew:
        if item['job'] == 'Director':
            directors.append(item['name'])
        elif item['job'] == 'Screenplay':
            writers.append( item['name'] )
        #elif item['job'] == 'Producer':
        #    producers.append( item['name'] )
    print( *directors, sep=' / ', end=delim)
    print( *writers, sep=' / ', end=delim)
    #print( *producers, sep=' / ', end=delim)

    # TODO: 
    # print Sequel 
    #print(' ', end=delim)
    # print Remake/Reboot
    #print(' ', end=delim)
    # print Franchise or IP
    # Pixar, Disney, Marvel, DC, Steven King, 007, Neil Gaiman, Wizarding World, Star Wars, Star Trek
    #producers = []
    #for item in info['production_companies']:
    #    producers.append( item['name'] )
    #print( *producers, sep=' / ', end=delim)
    #print(' ', end=delim)
    # Protagonist
    #print(' ', end=delim)
    # Antagonist
    #print(' ', end=delim)
    # Setting: Wild West, Space, Dystopia
    #print(' ', end=delim)
    # Based On: Novel/Novella, Play, Comic

    # Oscar Winner: yes or no 
    # TODO: Wikipedia API? 

    # TODO: review Keywords


# read list of movies
year_match = re.compile("[12][0-9][0-9][0-9]")
with open('movie_list.txt') as movie_list:
    for line in movie_list:
        movie = line.strip()

        # check if year info is present as last 4 characters
        year = None
        last4 = movie[-4:]
        if year_match.match(movie[-4:]):
            year = movie[-4:]
            movie = movie[:-4].strip()

        print_movie_info( movie, year )
        print('')


# keywords: woman director, 

# use Discover to query windows of years etc
# e.g. films made before 1920-03-011, sorted by popularity, genre 27
#https://api.themoviedb.org/3/discover/movie?api_key=<<api_key>>&language=en-US&sort_by=popularity.desc&page=1&primary_release_date.lte=1920-03-11&with_genres=27
