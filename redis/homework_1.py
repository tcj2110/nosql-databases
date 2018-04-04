import urllib2
import json

# Set up the url and send a GET request to it. The base url is:
# "https://api.nasa.gov/planetary/apod?api_key=uGanMPC95ggJHXFio0TS6JaWmJ8jeQeZ8VVLKspz"
# Note:  I am using a different API key than was provided

url = 'https://api.nasa.gov/planetary/apod?api_key=uGanMPC95ggJHXFio0TS6JaWmJ8jeQeZ8VVLKspz&date=2017-02-16'
response = urllib2.urlopen(url)

# create Python dictionary from json dataset
data = json.loads(response.read().decode("utf-8"))
print data['url']
