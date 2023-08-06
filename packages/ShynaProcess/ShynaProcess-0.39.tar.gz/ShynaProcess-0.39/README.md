# ShynaProcess

***Suggested: Not to use***

This  package contains multiple classes which take care of minor processes Shyna need.

## ShynaJokes
Use Rapid API- jokes API  
URL: https://rapidapi.com/Sv443/api/jokeapi-v2/  
There is no limitation but there are chances of repetition. stay alert.  
There are below method to use:  
shyna_random_jokes : any random jokes with no filter whatsoever.  
shyna_joke_contains: takes one parameter 'contains_string'. It will return any random jokes with that string contained in it.  
shyna_programming_joke : Random jokes based on programming.  
shyna_pun_joke : Random jokes pun intended.  
shyna_spooky_joke: Random jokes on ghosts.  
shyna_christmas_joke: Random Christmas jokes.

## ShynaGreetings
I am using a Message API. The messages are filter as per the categories.  
['Love','quotes','friendship','Good night','Good morning','funny','Birthday','Sad','Sweet','Random']  
  
API URL: https://rapidapi.com/ajith/api/messages/  
There are no limitation in use, but sometimes it doesn't return a response, in such case False will be returned.  
  
Below methods available:  
greet_good_morning  
greet_good_night  
greet_friend_ship_day  
greet_birthday  
greet_love  
greet_quotes  
greet_funny  
greet_sweet  
greet_custom: provide from any above category.

## ShynaSentenceAnalyzer

Using nltk.sentiment.vader sentence_analysis : provide sentence to check the polarity. There is nothing like neutral either it is positive or negative sentence.  
This will help in case running a command and there is a follow-up question.  Response the way you like as per the sentence polarity it will be decided to perform the command or not.  
  
We have below method:  
sentence_analysis: Provide sentence to this method

## ShynaSpeak

Using google_speech library https://pypi.org/project/google-speech/ and nltk to tokenize every sentence and speak.  
make sure the dependencies for google_speech is installed before using this class.  
sox effect are in place, keep Shyna voice same across the devices.  
  
There are two methods:   
 shyna_speaks: provide sentence(s) to speak out loud  
 test_shyna_speaks: run to test everything working fine

## GetQuotes
We will get quotes form the API I got form Rapid API website link is  
https://rapidapi.com/martin.svoboda/api/quotes15/pricing  
It allows us to request 1 per second, unlimited. we need to get the quotes and analyse them right away

I will be using this class as Shyna communication protocol. This will help in inititating the conversation and drive conversations. (Finger crossed)

method available is :
get_quotes

## ShynaNews
This will help in extract the news for the provided url. I have URL(s) stacked in database with their sources (TOI, Zee news)  
  
We have two method as per the sources:  
get_news_toi  
get_news_zee  
  
Define url at class level and call the function as per the URL source.

## ShynaWeather
Define either lon/lat or city_name at class level. 

get_weather_lon_lat: return weather details in dict as per lat/lon  
get_astronomy_lon_lat: return astro details in dict as per lat/lon  
get_weather_city: return weather details in dict as per city name  
get_astronomy_city : return astro details in dict as per city name  
get_weather: this will return the complete details. astro and weather.

P.S for Shyna the lat and lon will be fetched from the database. 

## BroadcastMessageDecision

broadcast_morning_decision: return greetings message ready to forward or just greet.
Method name is : broadcast_morning_decision

## ShynaMailClient
Make sure define a default path of image file. it will use that image or any other file instead of that image.  
Below value need to be defined:  
path = ""  
sender_gmail_account_id = ""  
sender_gmail_account_pass = ""  
master_email_address_is = ""  
email_subject = ""  
email_body = ""  
  
method  
send_email_with_attachment_subject_and_body: Need email_subject and email_body

## ShynaRegexExtraction

Define string first and then run the needed method(s):  
re_for_cr_db_from_email_body  
get_link_and_data_from_summary  
clean_apostrophe