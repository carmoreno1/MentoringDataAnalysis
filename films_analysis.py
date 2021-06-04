import csv
import time
import operator
from collections import Counter, defaultdict
from functools import reduce


class MoviesAnalysis(object):

    def __init__(self, path):
        self.path = path
        self.movies = self.get_movies()

    def get_dict_reader_movies(self):
        try:
            self.file = open(file=self.path, mode='r', encoding="utf8", newline='')
            dict_reader_movie = csv.DictReader(self.file)
            return dict_reader_movie
        except csv.Error as csv_error:
            raise csv.Error(f"Error in csv: {csv_error}")
        except OSError as os_error:
            raise OSError(f"Cannot open the file {os_error}")
        except Exception as exception:
            raise Exception(f"Error unexpected {exception}")

    def get_movies(self):
        try:
            movies = [row for row in self.get_dict_reader_movies()]
            return movies
        except Exception as exception:
            raise Exception(f"Error unexpected {exception}")

    def filter_movies_by_color(self, color):
        try:
            movies_by_color = filter(lambda row: row["color"].lower().strip() == color, self.movies)
            return len(list(movies_by_color))
        except Exception as exception:
            raise Exception(f"Error unexpected {exception}")

    def movies_by_director(self):
        directors = {row["director_name"] for row in self.movies}
        response = []
        for director in directors:
            movies_by_director = filter(lambda row: row["director_name"] == director, self.movies)
            output = f"- {director if director != '' else 'Empty Director'}: {len(list(movies_by_director))} movies"
            response.append(output)
        return response

    def movies_less_criticized(self, limit=10):
        movies_with_criticized = filter(lambda row: row["num_critic_for_reviews"] != '', self.movies)
        movies_order_by_criticized = sorted(movies_with_criticized, key=lambda movie: int(movie['num_critic_for_reviews']))
        response = [
            f"{row['movie_title'].strip()}: {row['num_critic_for_reviews']} review(s)" for row in movies_order_by_criticized[:limit]
        ]
        return response

    def movies_longest_duration(self, limit=20):
        movies_with_duration = filter(lambda row: row["duration"] != '', self.movies)
        movies_order_by_duration = sorted(movies_with_duration, key=lambda movie: int(movie['duration']), reverse=True)
        response = [
            f"{row['movie_title'].strip()}: {row['duration']} duration" for row in movies_order_by_duration[:limit]
        ]
        return response

    def movies_raised_movies(self, field="gross", winnings=True, limit=5):
        movies_with_gross = filter(lambda row: row[field] != '', self.movies)
        movies_order_by_gross = sorted(movies_with_gross, key=lambda movie: int(movie[field]), reverse=winnings)
        response = [
            f"{row['movie_title'].strip()}: ${row[field]}" for row in movies_order_by_gross[:limit]
        ]
        return response

    def movies_by_year(self, more_releases=True):
        movies_with_title_year = filter(lambda row: row["title_year"] != '', self.movies)
        years = [row["title_year"] for row in movies_with_title_year]
        count_movies_by_year = Counter(years)
        year = max(count_movies_by_year, key=count_movies_by_year.get) if more_releases else min(count_movies_by_year, key=count_movies_by_year.get)
        return year

    def get_social_media(self, actor):
        social_media_actor_1 = [
            row["actor_1_facebook_likes"] for row in self.movies if row["actor_1_name"] == actor]

        social_media_actor_2 = [
            row["actor_2_facebook_likes"] for row in self.movies if row["actor_2_name"] == actor]

        social_media_actor_3 = [
            row["actor_3_facebook_likes"] for row in self.movies if row["actor_3_name"] == actor]

        if len(social_media_actor_1) > 0:
            return social_media_actor_1[0]
        elif len(social_media_actor_2) > 0:
            return social_media_actor_2[0]
        else:
            return social_media_actor_3[0]

    def get_best_film(self, actor):
        best_movie_actor_1 = [
            row["imdb_score"] for row in self.movies if row["actor_1_name"] == actor]

        best_movie_actor_2 = [
            row["imdb_score"] for row in self.movies if row["actor_2_name"] == actor]

        best_movie_actor_3 = [
            row["imdb_score"] for row in self.movies if row["actor_3_name"] == actor]

        if len(best_movie_actor_1) > 0:
            return max(best_movie_actor_1)
        elif len(best_movie_actor_2) > 0:
            return max(best_movie_actor_2)
        else:
            return max(best_movie_actor_3)

    def get_actors(self):
        actors_by_movie = [[row["actor_1_name"], row["actor_2_name"],row["actor_3_name"]] for row in self.movies]

        all_actors = [] #List of unique actors.
        for a in actors_by_movie:
            all_actors = all_actors + a
        actors_number_performance = Counter(all_actors)
        all_actors = filter(lambda a: a != '', all_actors)
        actors_unique = list(set(all_actors))
        actor_information = []
        for actor in actors_unique:
            actor_information.append({
                "actor_name": actor,
                "social_media": self.get_social_media(actor),
                "best_film": self.get_best_film(actor),
                "number_performance": actors_number_performance.get(actor, None)
            })

        actor_information_order = sorted(actor_information, key=lambda actor: (int(actor["social_media"]), float(actor["best_film"]), actor["number_performance"]))
        return actor_information_order

    def get_actor_by(self, field='number_performance', limit=5, winning=True):
        actors = self.get_actors()
        actors_ordered = sorted(actors, key=lambda actor: int(actor[field]), reverse=winning)[:limit]
        response = [f"{row['actor_name']}: {row[field]}" for row in actors_ordered]
        return response

    def get_genre_information(self, winning=True):
        years = [row['title_year'] for row in self.movies if row["title_year"] and row["gross"]]
        years = list(set(years))
        movies_with_year = [row for row in self.movies if row["title_year"]]
        genre_information = [{row["title_year"]: {row["genres"]: int(row["gross"])}} for row in movies_with_year if row["gross"] and row["title_year"]]
        genre_information_by_years = defaultdict(list)

        for info in genre_information:
            for year, genres_info in info.items():
                info[year] = {genres.split('|')[index]: genres_info[genres] for index, genres in enumerate(genres_info)}
                info[year] = Counter(info[year])


        for info in genre_information:
            for year, genre in info.items():
                genre_information_by_years[year].append(genre)

        for year in years:
            genre_information_by_years[year] = reduce(operator.add, genre_information_by_years[year])
            genre = max(genre_information_by_years[year], key=genre_information_by_years[year].get) if winning\
                        else min(genre_information_by_years[year], key=genre_information_by_years[year].get)
            genre_information_by_years[year] = genre

        response = [f"{year}: {genre}" for year, genre in genre_information_by_years.items()]
        return response

    def get_genre_favorite(self):
        movies_with_facebook_likes = [row for row in self.movies if row["movie_facebook_likes"]]
        genre_likes_togethers = [{row["genres"]: int(row["movie_facebook_likes"])} for row in movies_with_facebook_likes]
        for index, info in enumerate(genre_likes_togethers):
            for genres, likes in info.items():
                genre_likes_togethers[index] = [Counter({g: likes}) for g in genres.split('|')]

        genres_likes = reduce(operator.add, genre_likes_togethers, [])
        genres_likes = reduce(operator.add, genres_likes, Counter())
        genre_favorite = max(genres_likes, key=genres_likes.get)
        return genre_favorite

    def get_director_by(self, field='director_facebook_likes', limit=5, winning=True):
        movies_with_director = filter(lambda row: row['director_name'] != '', self.movies)
        directors_likes = [{'director_name': row['director_name'], field: int(row[field])} for row in movies_with_director]
        director_likes = [director_info for index, director_info in enumerate(directors_likes)
                            if director_info not in directors_likes[index + 1:]]
        director_order_by_reputation = sorted(director_likes, key=lambda director: director[field], reverse=winning)
        director_order_by_reputation = director_order_by_reputation[:limit]
        response = [
            f"{row['director_name'].strip()}: {row[field]} likes" for row in director_order_by_reputation
        ]
        return response
        #return response

    def screen_results(self):
        new_line = '\n\t'
        results = f"""
**************** Movies Data Analysis ****************
1. How many Black & White and color movies are in the list?
    - Color Movies: {self.filter_movies_by_color('color')}
    - Black & White Movies: {self.filter_movies_by_color('black and white')}
    
2. How many movies were produced by director in the list?
    {new_line.join(movie_analysis.movies_by_director())}
    
3. Which are the 10 less criticized movies in the list?
    {new_line.join(movie_analysis.movies_less_criticized())}

4. Which are the 20 longest-running movies in the list?
    {new_line.join(movie_analysis.movies_longest_duration())}

5. Which are the top 5 movies that raised more money in the list?
    {new_line.join(movie_analysis.movies_raised_movies())}
    
6. Which are the top 5 movies that made the least money in the list?
    {new_line.join(movie_analysis.movies_raised_movies(winnings=False))}

7. Which are the top 3 movies that expend more money to be produced in the list?
    {new_line.join(movie_analysis.movies_raised_movies(field='budget', winnings=True, limit=3))}
    
8. Which are the top 3 movies that expend less money to be produced in the list?
    {new_line.join(movie_analysis.movies_raised_movies(field='budget', winnings=False, limit=3))}

9. What year was the one who had more movies released ?
    {self.movies_by_year()}

10. What year was the one who had less movies released ?
    {self.movies_by_year(more_releases=False)}

12. What movie genre raised more money per year?
    {new_line.join(movie_analysis.get_genre_information())}

13. What movie genre raised less money per year?
    {new_line.join(movie_analysis.get_genre_information(winning=False))}

15. Top five ranking of actors by performance and popularity
    **Top five number of performance**:
    {new_line.join(movie_analysis.get_actor_by())}
    
    **Top five popularity**:
    {new_line.join(movie_analysis.get_actor_by(field="social_media"))}
    
16 What movie genre does the public like most?
    {movie_analysis.get_genre_favorite()}
    
17 Which are the top five best reputation directors?
    {new_line.join(movie_analysis.get_director_by())}
"""
        print(results)

    def __del__(self):
        self.file.close()

if __name__ == '__main__':
    start_time = time.time()
    movie_analysis = MoviesAnalysis('resources/movie_metadata.csv')
    movie_analysis.screen_results()
    print(f"{time.time() - start_time}.3f Seconds")
