# Depends on twint working.    Use : python3 twintsearch7.py <username> 
import twint
import nest_asyncio
import pandas as pd
import datetime
import csv
from datetime import datetime, timedelta
import time
import sys
nest_asyncio.apply()



sleeptime=(5)
c = twint.Config()
c.Store_csv = True
c.Profile_full = True    #Very important, includes shadowbanned accounts!!!
c.User_full = True
search = str(sys.argv[1])  #set the argument of the command to the search string (user or subject to scrape)
c.User = search   #if you need just the tweets of a specific user, change this to c.User = search.   To get all replies, c.Search = search.
c.Since = '2009-04-01 00:00:00'  #This gets ignored in this version of twint but can be compared against so I use it to stop the loop.   Set it to the earliest date to scrape, or a date before the 1st tweet.

c.Until = (datetime.now().strftime("%Y-%m-%d %H:%M:%S"))  #Date of the latest tweet to scrape, set it to current time to get everything  (datetime.now().strftime("%Y-%m-%d %H:%M:%S")) or like "2023-03-01 00:00:00"
c.Pandas = True

prevuntil=c.Until
exceptioncount=0


twint.run.Search(c)
df = twint.storage.panda.Tweets_df
flag=False
csv_header=["id", "conversation_id", "created_at", "date", "timezone", "nlikes", "link", "tweet"]


while(datetime.strptime(c.Until, '%Y-%m-%d %H:%M:%S')>datetime.strptime(c.Since, '%Y-%m-%d %H:%M:%S')):      #   Stops the search when we reach c.Since
    c.Until=datetime.strftime(datetime.strptime(c.Until, '%Y-%m-%d %H:%M:%S')-timedelta(minutes=10),'%Y-%m-%d %H:%M:%S') #Deals with gaps between tweets
    print("c.Until:" + str(datetime.strptime(c.Until, '%Y-%m-%d %H:%M:%S')))
    print("prevuntil :" + str(datetime.strptime(prevuntil, '%Y-%m-%d %H:%M:%S')))
    if((datetime.strptime(c.Until, '%Y-%m-%d %H:%M:%S')<datetime.strptime(prevuntil, '%Y-%m-%d %H:%M:%S'))):
        print("c.Until:" + str(c.Until) + " was less than prevuntil:" + str(prevuntil))
        #flag=True
        print("set prevuntil to c.Until")
        prevuntil=c.Until
    if((datetime.strptime(c.Until, '%Y-%m-%d %H:%M:%S')>datetime.strptime(prevuntil, '%Y-%m-%d %H:%M:%S'))):
        print("c.Until:" + str(c.Until) + " was greater than prevuntil:" + str(prevuntil))
        flag=True
        print("set c.Until to prevuntil")
        c.Until=prevuntil
    else:flag=False

    if(sleeptime>18):sleeptime=4    #found the backoff policy of 100 ws too lax so dropped it to 4, feel free to experiment
    try:
        twint.run.Search(c)
        df = twint.storage.panda.Tweets_df
        exceptioncount=0
    except:
        print ("Exception while running search, blanking df")
        df=''           #  If Twitter denies your request for data, blank the dataframe and try again after a pause

    if(len(df)>1):
        if (not flag):
            c.Until=(df.iloc[[-1]].iloc[0].date)    #Get the date of the last tweet and carry on searching from there
        print ("Setting c.Until and prevuntil to : " + str(c.Until) + " from last tweet")
        if(datetime.strptime(c.Until, '%Y-%m-%d %H:%M:%S')>datetime.strptime(prevuntil, '%Y-%m-%d %H:%M:%S')):
            print("c.Until time of " + str(c.Until) + " greater than prevuntil of : " + str(prevuntil) + "Putting pack to prevuntil and taking off 10 minutes")
            c.Until=prevuntil
            c.Until=datetime.strftime(datetime.strptime(c.Until, '%Y-%m-%d %H:%M:%S')+timedelta(minutes=-10), '%Y-%m-%d %H:%M:%S')
        print("writing dataframe to " + str(sys.argv[1]) + ".csv")
        #new_df=df.tweet.apply(lambda x: str(x.replace(',','\\,')))  #bodge to try to get it working with commas, didn't work, went with tabs instead.  Hence sep='\t' 3 lines down
        #df.update(new_df)
        #print(df.tweet)
        df.to_csv((sys.argv[1]+".csv"), mode='a', index=False, header=False, columns=csv_header, sep='\t', quoting=csv.QUOTE_NONE, escapechar='\\')
        if(sleeptime>5):sleeptime-=1      #  Staggered backoff policy
    else:
        exceptioncount=exceptioncount+1
        print("blank list, sleeping for "+str(sleeptime))
        print("c.Until = "+str(c.Until+"setting to prevuntil of "+str(prevuntil)))
        c.Until=prevuntil
        time.sleep (sleeptime)
        sleeptime+=1
        if(exceptioncount>1):      #Deals with gaps between tweets.
            print("more than one excpetion, taking an hour from c.Until")
            c.Until=datetime.strftime(datetime.strptime(c.Until, '%Y-%m-%d %H:%M:%S')-timedelta(hours=1),'%Y-%m-%d %H:%M:%S')
            print("c.Until = "+str(c.Until))

