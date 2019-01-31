import requests
import lxml.html
import re
from pymongo import MongoClient

db_client = MongoClient('mongo', 27017)

def crawl_movies_urls():
    genres = (["action"]);
    movies_urls = []
    for genre in genres:
        print("Crawling {} movies...".format(genre))
        for i in range(1,100,100):
            url = "https://www.imdb.com/search/title?title_type=feature&release_date=,2018-12-31&genres={}&view=simple&count=50&start={}".format(genre,str(i))
            print(url)
            response = requests.get(url)
            doc = lxml.html.fromstring(response.content)
            links = doc.xpath('//span[@class="lister-item-header"]/span/a')
            for link in links:
                if 'href' in link.attrib:
                    if '/title/tt' in link.attrib['href']:
                        movies_urls.append({
                            'link' : "http://www.imdb.com" + link.attrib['href'].rpartition("/")[0]
                        })

    return  store_movies_urls(movies_urls)

def store_movies_urls(movies_urls):
    for movie in movies_urls:
        if db_client.imdb_data.movies_urls.find_one({'link': movie['link']}) is None:
            # Let's print it out to verify that we added the new post
            print("Storing new movie url: ", movie['link'])
            db_client.imdb_data.movies_urls.insert(movie)

def crawl_movies_data():
    directors_data = []
    movies_urls = db_client.imdb_data.movies_urls.find({})
    movies = []
    for url in movies_urls:
        print ("Extracting {} data...".format(url['link']))
        movie_data = {}
        directors_ids = []
        response = requests.get(url['link'])
        doc = lxml.html.fromstring(response.content)
        movie_id = re.search('/title/tt(\d{7}$)', url['link']).group(1)
        try:
            title = doc.xpath('//div[@class="title_wrapper"]/h1/text()')[0]
        except:
            title = []

        year = int(doc.xpath('//span[@id="titleYear"]/a/text()')[0])

        try:
            genres = doc.xpath('//div[@class="subtext"]/a/text()')[0:-1]
        except:
            genres = []
        try:
            imdb_rating = float(doc.xpath('//span[@itemprop="ratingValue"]/text()')[0])
        except:
            imdb_rating = []
        try:
            metascore = int(doc.xpath('//div[@class="titleReviewBarItem"]/a/div/span/text()')[0])
        except:
            metascore = []

        try:
            runtime = int(doc.xpath('//time[1]/text()')[1].rpartition("min")[0])
        except:
            runtime = {}

        try:
            budget = doc.xpath('//*[@id="titleDetails"]/div[7]/text()')[1].rpartition("\n")[0]
        except:
            budget = []

        countrys = doc.xpath('//*[@id="titleDetails"]/div[2]/a/text()')

        directors = doc.xpath('//div[@class="credit_summary_item"][1]/a')
        for director in directors:
            if director.attrib['href'] and '/name/' in director.attrib['href']:
                directors_ids.append(re.search('/name/nm(.+?)/', director.attrib['href']).group(1))
                directors_data.append({
                    'id' : re.search('/name/nm(.+?)/', director.attrib['href']).group(1),
                    'movie_id' : movie_id
                })

        for i in ('movie_id','title', 'year', 'genres', 'imdb_rating', 'metascore', 'directors_ids', 'runtime', 'budget', 'countrys'):
            movie_data[i] = locals()[i]
        movies.append(movie_data)
    store_movies_data(movies)
    crawl_directors_data(directors_data)

def store_movies_data(movies):
    for movie in movies:
        if db_client.imdb_data.movies_data.find_one({'movie_id': movie['movie_id']}) is None:
            # Let's print it out to verify that we added the new post
            print("Storing new movie: ", movie['title'])
            db_client.imdb_data.movies_data.insert(movie)



def crawl_directors_data(directors):
    directors_data = []
    for director in directors:
        data = {}
        url = "https://www.imdb.com/name/nm" + director['id']
        print ("Extracting {} data...".format(url))
        id = director['id']
        response = requests.get(url)
        doc = lxml.html.fromstring(response.content)

        name = doc.xpath('//h1/span/text()')[0]
        try:
            born_date = doc.xpath('//*[@id="name-born-info"]/time')[0].attrib['datetime']
        except:
            born_date = []
        try:
            nationality = doc.xpath('//*[@id="name-born-info"]/a/text()')[0].rpartition(",")[-1].strip()
        except:
            nationality = "Unknown"
        gender_male_url = "https://www.imdb.com/search/name?name={}&gender=male&roles={}".format(name, director['movie_id'])
        response_male = requests.get(gender_male_url)
        gender_female_url = "https://www.imdb.com/search/name?name={}&gender=female&roles={}".format(name, director['movie_id'])
        response_female = requests.get(gender_female_url)
        if not "No results." in str(response_male.content):
            gender = 'Male'
        elif not "No results." in str(response_female.content):
            gender = 'Female'
        else:
            gender = "Unknown"
        for i in ('id', 'name', 'born_date', 'nationality', 'gender'):
            data[i] = locals()[i]
        directors_data.append(data)
    store_directors_data(directors_data)


def store_directors_data(directors):
    for director in directors:
        if db_client.imdb_data.directors_data.find_one({'id': director['id']}) is None:
            # Let's print it out to verify that we added the new post
            print("Storing new director: ", director['name'])
            db_client.imdb_data.directors_data.insert(director)

if __name__ == '__main__':
    if  not "movies_urls" in db_client.imdb_data.collection_names():
        crawl_movies_urls()
    if not "movies_data" in db_client.imdb_data.collection_names():
        crawl_movies_data()
