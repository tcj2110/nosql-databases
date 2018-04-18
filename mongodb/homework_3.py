# require the driver package
import pymongo
from pymongo import MongoClient
from pprint import pprint

# Create a client
# client = ...
client = MongoClient()

# A. Update all movies with "NOT RATED" at the "rated" key to be "Pending rating". The operation must be in-place and atomic.
movies_db	=	client.movies
movies_c	=	movies_db.movies

movies_c.update_many( {"rated": "NOT RATED" }, { "$set" : { "rated" : "Pending rating"}} )

# B. Find a movie with your genre in imdb and insert it into your database with the fields listed in the hw description.
if movies_c.find({"title": "Love on a Leash"}).count() == 0:
	movies_c.insert( {
			"title"		:	"Love on a Leash",
			"year"		:	2011,
			"countries"	:	["USA"],
			"genres"	:	["Comedy", "Drama", "Fantasy"],
			"directors"	:	["Fen Tian"],
			"imdb"		:	{"id": 8675309, "rating": 10.0, "votes": 4174},
			} )

# C. Use the aggregation framework to find the total number of movies in your genre.
# Example result:
#  => [{"_id"=>"Comedy", "count"=>14046}]
pipeline = [
	{"$match" : {"genres" : "Comedy"}},
	{"$group" : {"_id": "Comedy", "count": {"$sum":1}}}
	]

cursor = movies_c.aggregate(pipeline)
pprint([(document) for document in cursor])

# D. Use the aggregation framework to find the number of movies made in the country you were born in with a rating of "Pending rating".
# Example result when country is Hungary:
#  => [{"_id"=>{"country"=>"Hungary", "rating"=>"Pending rating"}, "count"=>9}]
pipeline = [
	{
		"$match" : {"$and": [ { "countries" : "USA" } , {"rated" : "Pending rating"} ] }
	},
	{
		"$group" : {"_id" : { "country" : "USA", "rating" : "Pending rating" }, "count" : {"$sum" : 1} }
	}
	]
cursor = movies_c.aggregate(pipeline)
pprint([(document) for document in cursor])


# E. Create an example using the $lookup pipeline operator. See hw description for more info.
#movies_db.create_collection("warhammer_40000")
#movies_db.create_collection("starcraft")

movies_db.orders.insert([
		{ "item" : "milk", "price" : 12, "quantity" : 2 },
		{ "item" : "peanut butter", "price" : 20, "quantity" : 1 }
		])

movies_db.storage.insert([
		{ "sku" : "milk", "description": "product 1", "instock" : 120 },
		{ "sku" : "eggs", "description": "product 2", "instock" : 80 },
		{ "sku" : "bubble gum", "description": "product 3", "instock" : 60 },
		{ "sku" : "peanut butter", "description": "product 4", "instock" : 70 }
		])

pipeline =	[
		{
		"$lookup":
			{
			"from"		: "storage",
			"localField"	: "item",
			"foreignField"	: "sku",
			"as"		: "storage_documents"
			}
		}
		]
cursor = movies_db.orders.aggregate(pipeline)
pprint([(document) for document in cursor])
