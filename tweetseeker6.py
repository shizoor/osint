import numpy as np
import sys
import os
import time
import math



#   Note it's difficult to search for a specific tweet.   If a user moves around a lot this may not work as intended.
#   Specify a starting point here and a radius the tweet is within, you can put it up to around 4000km.   I've chosen at random Swyncombe, a town outside London.

lat=51.596456
long= -1.005002
rad=300


location=[0.0000,0.00000]

#rad=2000  #it works at 40000

limit=200
radlimit=4 #searches narrower than 4km don't work.
pi=3.14159265359
foundflag=True
delay=3
x=0
y=0

def testcoords(location, radius, outputlimit, username):
    foundflag=False
    commandstring = ("twint -u " + username + " -g " + "\""+f'{location[0]:.10f}'+", "+f'{location[1]:.10f}'+", "+f'{radius:.10f}'+"km\"")  #removed +" --limit "+f'{outputlimit:.0f}' so it works with string
    print ("Command string : " + commandstring)
    process = os.popen(commandstring)
    preprocessed=process.read()
    process.close()
    print ("output : ")
    outputsplit = preprocessed.splitlines()
    print(len(outputsplit[1]))
    if(outputsplit[1][1].isnumeric()):
            print (outputsplit[1])
            foundflag=True
            #rad=rad*0.95
            with open((sys.argv[1]+".txt"), "a") as myfile:
                myfile.write(sys.argv[1] + ","+f'{x:.6f}'+", "+f'{y:.6f}'+", "+f'{rad:.9f}'+"\n \r ")
                myfile.close()
    print (outputsplit[1])
    print (foundflag)
    return foundflag


while(rad>radlimit):
    if(foundflag):
        print("Search string specified = " + str(sys.argv[1]))
        foundflag=False
        commandstring = ("twint -u " + sys.argv[1] + " -g " + "\""+f'{lat:.6f}'+", "+f'{long:.6f}'+", "+f'{rad:.6f}'+"km\"")  #+" --limit "+f'{limit:.0f}')
        print ("Command string : " + commandstring)
        process = os.popen(commandstring)
        preprocessed=process.read()
        process.close()
        print ("output : ")
        #print(preprocessed)
        outputsplit = preprocessed.splitlines()
        #print ("output split : " + outputsplit)
        print (len(outputsplit[1]))
        if(outputsplit[1][1].isnumeric()):
            print (outputsplit[1])
            foundflag=True
            rad=rad*0.95
            with open((sys.argv[1]+".txt"), "a") as myfile:
                myfile.write(sys.argv[1] + ","+f'{x:.6f}'+", "+f'{y:.6f}'+", "+f'{rad:.9f}'+"\n \r ")
                myfile.close()
        print (foundflag)
        time.sleep(delay)
        finalradius=rad
    else:
        #Move the circle round in a circle til it covers the location again
        mov=rad/222   # 1 degree lat/long = 111km.
        angle=0;
        while(angle<2*pi):
            x=lat+math.sin(angle)*mov
            y=long+math.cos(angle)*mov
            print("x="+f'{x:.8f}')
            print("y="+f'{y:.8f}')
            foundflag=False
            commandstring = ("twint -u " + sys.argv[1] + " -g " + "\""+f'{x:.6f}'+", "+f'{y:.6f}'+", "+f'{rad:.6f}'+"km\"") #" --limit "+f'{limit:.0f}' removed limit so it works with string
            print ("Command string : " + commandstring)
            process = os.popen(commandstring)
            preprocessed=process.read()
            process.close()
            print ("output : ")
            #print(preprocessed)
            outputsplit = preprocessed.splitlines()
            #print ("output split : " + outputsplit)
            if(outputsplit[1][1].isnumeric()):
                print (outputsplit[1])
                foundflag=True
                with open((sys.argv[1]+".txt"), "a") as myfile:
                    myfile.write(sys.argv[1] + ","+f'{x:.6f}'+", "+f'{y:.6f}'+", "+f'{rad:.9f}'+"\n \r ")
                    myfile.close()

            print (foundflag)
            if(foundflag):
                print("Now found at x="+f'{x:.8f}'+" y="+f'{y:.8f}')
                lat=x
                long=y
                break
            angle+=pi/4
            time.sleep(delay)

print("Radius of " + f'{radlimit:.8f}' + " reached, now trying to find center of circle by finding the bottom right and left and top successful searches and averaging to triangulate")
for i in range(0, 1, 1):
    tempradlimit = radlimit/444
    outward=1
    xtop=x
    ytop=y
    xbottomleft=x
    ybottomleft=y
    xbottomright=x
    ybottomright=y
    counter=0
    print("finding top")
    location[0]=xtop
    location[1]=ytop
    while((tempradlimit>0.0001) and (counter < 20)):
        print("location :")
        print(location)
        print ("tempradlimit" + f'{tempradlimit:.10f}')
        if (outward==1):
            location[1]=location[1]+tempradlimit
            if(testcoords(location, 4.5, limit, sys.argv[1])):
                print("found going outward, decreasing radius and adding")
                print("tempradlimit = "+f'{tempradlimit:.8f}')
                tempradlimit=tempradlimit*0.75
            else:
                outward=-1
                print("not found going outwards, changing direction to inwards")
                print("tempradlimit = "+f'{tempradlimit:.8f}')
        else:
            location[1]=location[1]-tempradlimit
            if(testcoords(location, 4.5, limit, sys.argv[1])):
                print("found going inwards, changing direction to outwards")
                tempradlimit=tempradlimit*0.75
                outward=1
        time.sleep(delay)
        counter=counter+1
    print ("Top found")
    xtop=location[0]
    ytop=location[1]
    print("xtop="+f'{xtop:.8f}')
    print("ytop="+f'{ytop:.8f}')
    print("counter")
    print(counter)
    print("tempradlimit")
    print(tempradlimit)
    counter=0
    print("finding bottom right")
    tempradlimit = radlimit/444
    outward=1
    location[0]=xbottomright
    location[1]=ybottomright
    while((tempradlimit>0.0001) and (counter<20)):
        print("location :")
        print(location)
        print ("tempradlimit" + f'{tempradlimit:.10f}')
        if (outward==1):
            location[0]=location[0]+(tempradlimit*0.707106781186548)
            location[1]=location[1]+(tempradlimit*-0.707106781186548)
            if(testcoords(location, 4.5, limit, sys.argv[1])):
                print("found going outward, decreasing radius and adding")
                print("tempradlimit = "+f'{tempradlimit:.8f}')
                tempradlimit=tempradlimit*0.75
            else:
                outward=-1
                print("not found going outwards changing direction to inwards")
                print("tempradlimit = "+f'{tempradlimit:.8f}')

        else:
            location[0]=location[0]-(tempradlimit*0.707106781186548)
            location[1]=location[1]-(tempradlimit*-0.707106781186548)
            if(testcoords(location, 4.5, limit, sys.argv[1])):
                print("found going inwards, changing direction to outwards")
                tempradlimit=tempradlimit*0.75
                outward=1
        time.sleep(delay)
        counter=counter+1
    print("bottom right found")
    xbottomright=location[0]
    ybottomright=location[1]
    print("xbottomright="+f'{xbottomright:.8f}')
    print("ybottomright="+f'{ybottomright:.8f}')
    print("counter")
    print(counter)
    print("tempradlimit")
    print(tempradlimit)
    print("finding bottom left")
    tempradlimit = radlimit/444
    outward=1
    location[0]=xbottomleft
    location[1]=ybottomleft
    counter=0
    while((tempradlimit>0.0001) and (counter<20)):
        print("location :")
        print(location)
        print ("tempradlimit" + f'{tempradlimit:.10f}')
        if (outward==1):
            location[0]=location[0]+(tempradlimit*-0.707106781186548)
            location[1]=location[1]+(tempradlimit*-0.707106781186548)
            if(testcoords(location, 4.5, limit, sys.argv[1])):
                print("found going outward, decreasing radius and adding")
                print("tempradlimit = "+f'{tempradlimit:.8f}')
                tempradlimit=tempradlimit*0.75
            else:
                outward=-1
                print("not found, changing direction")
                print("tempradlimit = "+f'{tempradlimit:.8f}')
        else:
            location[0]=location[0]-(tempradlimit*-0.707106781186548)
            location[1]=location[1]-(tempradlimit*-0.707106781186548)
            if(testcoords(location, 4.5, limit, sys.argv[1])):
                print("found going inwards, changing direction to outwards")
                tempradlimit=tempradlimit*0.75
                outward=1
        time.sleep(delay)
        counter=counter+1
    xbottomleft=location[0]
    ybottomleft=location[1]
    print("top:")
    print(f'{xtop:.10f}'+","f'{ytop:.10f}')
    print("bottom right:")
    print(f'{xbottomright:.10f}'+","+f'{ybottomright:.10f}')
    print("bottom left")
    print(f'{xbottomleft:.10f}'+","+f'{ybottomleft:.10f}')
    print("counter")
    print(counter)
    print("tempradlimit")
    print(tempradlimit)
    avgx=(xtop+xbottomleft+xbottomright)/3
    avgy=(ytop+ybottomleft+ybottomright)/3
    print("Endresult : "+f'{avgx:.10f}'+","+f'{avgy:.10f}')
    x=avgx
    y=avgy

