# Put the use case you chose here. Then justify your database choice:
#	HackerNews
#	I chose MongoDB because it is document-oriented and
#	very easy to categorize data with.
#	MongoDB supports field and range queries, and
#	regex searches, and the aggregation framework
#	makes it relatively easy to group data.

# Explain what will happen if coffee is spilled on one of the servers in your cluster, causing it to go down.
#	When a primary does not communicate with the other members of the
#	set for more than the configured electionTimeoutMillis period,
#	an eligible secondary calls for an election to nominate itself
#	as the new primary.  The cluster then attempts to complete the
#	election of a new primary and resume normal operations.
#
#	source: https://docs.mongodb.com/manual/replication/#automatic-failover

# What data is it not ok to lose in your app? What can you do in your commands to mitigate the risk of lost data?
#	It is not "ok" to lose any data, but depending on the actual
#	goals and implementation of the app, either user data or
#	article data could be "ok" to lose.  For example, 4chan wouldn't
#	be losing a whole lot if users lost all their data, considering everyone
#	posts anonymously.
#
#	Now regarding my wannabe-Reddit/HackerNews clone: user data is absolutely
#	NOT ok to lose.
#	To safeguard this data, ensure have a working replica set and resync any
#	server with the primary in the event of a crash

import pymongo
from pymongo import MongoClient
import datetime
from pprint import pprint

client = MongoClient()

db = client['TEST_DB']

def new_user(username):
	user = {"name" : username}

	if db["users"].find({"name": username}).count() == 0:
		db["users"].insert(user)
		return 0
	return -1

def del_user(username):
	db["users"].remove({"name": username})

def print_users():
	cursor = db["users"].find({}, {"name":1, '_id':0})
	print(	"********************************\n" \
		"Users\n" \
		"********************************")
	for document in cursor:
		print(document)

def new_article(article_name, link, user):
	date = datetime.datetime.utcnow()
	votes = 0

	article = {
		"name"	: article_name,
		"link"	: link,
		"user"	: user,
		"date"	: date,
		"votes"	: votes
		}

	if db["articles"].find({"name": article_name}).count() == 0:
		db["articles"].insert(article)
		return 0
	return -1

def print_articles():
	cursor = db["articles"].find({}, {"name":1, '_id':0})
	print(	"********************************\n" \
		"Articles\n" \
		"********************************")
	for document in cursor:
		print(document)

def upvote(article, user):
	uvote_pipe = [{'$match':{'$and':[{"name": user},{"upvoted": article}]}}]
	dvote_pipe = [{'$match':{'$and':[{"name": user},{"downvoted": article}]}}]

	# if user already upvoted the article
	cursor = db["users"].aggregate(uvote_pipe)
	for document in cursor:
		print("[$s] already upvoted [%s]" % user, article)
		return -1

	# if user had previously downvoted the article
	cursor = db["users"].aggregate(dvote_pipe)
	for document in cursor:
		db["users"].update_one(
			{"name": user},
			{'$pull': {"downvoted": article}}
			)

	db["users"].update_one(
		{"name": user},
		{'$push': {"upvoted" : article}}
		)

	db["articles"].update_one(
		{"name": article},
		{'$inc': {"votes" : 1}}
		)

	return 0

def downvote(article, user):
	uvote_pipe = [{'$match':{'$and':[{"name": user},{"upvoted": article}]}}]
	dvote_pipe = [{'$match':{'$and':[{"name": user},{"downvoted": article}]}}]

	# if user already downvoted the article
	cursor = db["users"].aggregate(dvote_pipe)
	for document in cursor:
		print("[$s] already downvoted [%s]" % user, article)
		return -1

	# if user had previously upvoted the article
	cursor = db["users"].aggregate(uvote_pipe)
	for document in cursor:
		db["users"].update_one(
			{"name": user},
			{'$pull': {"upvoted": article}}
			)

	db["users"].update_one(
		{"name": user},
		{'$push': {"downvoted" : article}}
		)

	db["articles"].update_one(
		{"name": article},
		{'$inc': {"votes" : -1}}
		)

	return 0

# Twitch-style unsorted comments, top-level only
# As such, you may comment on the same article with
# the same comment repeatedly (ie "spam" the comments)
def insert_comment(article, user, comment):
	db["articles"].update_one(
		{"name": article},
		{'$push': {"comments" : {user : comment}}}
		)

	db["users"].update_one(
		{"name": article},
		{'$push': {"comments" : {article : comment}}}
		)

def top(k):
	cursor = db["articles"].find({}, {"name":1, '_id':0, "votes":1}).sort(
					"votes",pymongo.DESCENDING).limit(k)

	print(	"********************************\n" \
		"Top %s Articles:\n" \
		"********************************" % k)
	for document in cursor:
		pprint(document)

def top_by_date(start, end, k):
	cursor = db["articles"].find({"date":{'$lt':end,'$gte':start}},
				{"name":1,'_id':0,"votes":1,"date":1}).sort(
					"votes",pymongo.DESCENDING).limit(k)

	print(	"********************************\n" \
		"Top %s Articles:\n" \
		"********************************" % k)
	for document in cursor:
		pprint(document)

if __name__ == '__main__':
	print_users()	# print to show no users and articles
	print_articles()

	new_user("Nasty Nate")
	new_user("David")
	new_user("Billy")
	new_user("Emily Stolfo")
	new_user("Cassandra")

	new_article("I have big biceps",
			"http://www.nytimes.com",
			"Emily Stolfo")
	new_article("Aliens have landed",
			"http://www.wapo.com",
			"David")
	new_article("Trump Elected For Fourth Term",
			"http://www.theonion.com",
			"Billy")
	new_article("Calories in, calories out",
			"http://www.mensfitness.com",
			"Nasty Nate")

	print_users()	# print to show new users and articles
	print_articles()

	upvote("I have big biceps", "Nasty Nate")
	upvote("Aliens have landed", "Emily Stolfo")
	upvote("Trump Elected For Fourth Term", "Billy")
	upvote("Aliens have landed", "David")
	upvote("Calories in, calories out", "David")
	upvote("Trump Elected For Fourth Term", "Nasty Nate")

# Action 1: AS A person, I WANT to make an account
	new_user("Squirrel Master")

# Action 2: AS A user, I WANT to post an article
	new_article("Glenn Beck:  Man Behind The Legend",
			"http://www.youtube.com/rickastley",
			"Squirrel Master")

	print_users()	# print to show new user and article
	print_articles()

# Action 3: AS A user, I WANT to upvote an article
	upvote("I have big biceps", "Squirrel Master")

# Action 4: AS A user, I WANT to downvote an article
	downvote("Trump Elected For Fourth Term", "Squirrel Master")

# Action 5: AS A user, I WANT to comment on an article
	insert_comment("I have big biceps", "Squirrel Master",
			"A funny thing is if you're out hiking and your " \
			"friend gets bit by a poisonous snake, tell him " \
			"you're going for help, then go about ten feet " \
			"and pretend YOU got bit by a snake. Then start " \
			"an argument about who's going to get help. A " \
			"lot of guys will start crying. That's why it " \
			"makes you feel good when you tell them it was " \
			"just a joke.")

	# This is for verification of comment insertion
	cursor = db["articles"].find({},{"name":1,
					'_id':0,
					"comments":1})
	for document in cursor:
		pprint(document)

# Action 6: AS A user, I WANT to find the top 3 articles
	top(3)

# Action 7: AS A user, I WANT to find the top 3 articles in last week
	start	= datetime.datetime(2018,5,2,12)
	end	= datetime.datetime(2018,5,9,12)
	top_by_date(start, end, 10)

# Action 8: AS A user, I WANT to delete my account
	del_user("Squirrel Master")

	# This is for verification of user deletion
	print_users()
