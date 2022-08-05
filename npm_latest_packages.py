import csv
import requests
import os
import time
from datetime import datetime
from os.path import exists

#NOTE THIS PROGRAM WILL NOT WORK IF YOU DO NOT HAVE A LIBRARIES.IO API KEY AND HAVE IT INSERTED INTO THE api_key VARIABLE ON LINE 21. SEE BELOW ON HOW TO OBTAIN API KEY

#This program queries the libraries.io API for new and newly updated NPM packages for today. It then takes the package name, date published, and version number and adds them to a CSV file
#in the current directory. If the CSV file does not exist it will be created automatically. Finally it will remove duplicate entries from the CSV file and output the _final CSV file.

#To run this program yourself you will need a libraries.io API key, which can be obtained by signing up for a free libraries.io account and checking your account settings page.
#This program depends on the "requests" library which you may need to install using "pip install requests"

#This may take several minutes to run depending on how much load is being put on the libraries.io servers. It will handle errors and wait 2 minutes between each error code returned from the server.
#If it encounters 10 error messages over the course of running, the program will clean up duplicates and end.



api_key = 'yourapikeyhere' #PUT YOUR API KEY HERE SURROUNDED BY QUOTES eg. 'thisisyourapikey'
counter = 0 #used to increase page count
failcount = 0 #keep track of failures
keepgoing = True #looper, set set to false if date does not equal today
today = str(datetime.today()).split(" ") #gets today's date and splits it at the time
if exists('.\packages{}.csv'.format(today[0])): #checks if the packages have already been scraped today, if it has then it deletes the old file and starts fresh. need to build some logic in so that it only scrapes new updates instead of all updates for the day.
    os.remove('.\packages{}.csv'.format(today[0]))

def remove_duplicates(): #iterates through csv file and outputs _final csv file with duplicates removed

    inFile = open('.\packages{}.csv'.format(today[0]),'r')
    outFile = open('.\packages{}_final.csv'.format(today[0]),'w')
    listLines = []
    for line in inFile:
        if line in listLines:
            print("Skipped line {}".format(line))
            continue
        else:
            outFile.write(line)
            listLines.append(line)
    outFile.close()
    inFile.close()


while keepgoing:
    response = requests.get("https://libraries.io/api/search?order=desc&page={}&per_page=100&platforms=npm&sort=latest_release_published_at&api_key={}".format(counter+1, api_key))
    print("Scraping page {}".format(counter+1)) #queries the api for most recent packages with 100 per page. Iterates through pages using counter. Prints debug info
    print("HTTP status code: {}".format(response.status_code))
    if str(response.status_code) == '200':
        raw = response.json()
    elif str(response.status_code)!='200':
        print("Hit error response code {}, retrying in 120 seconds...".format(response.status_code)) #checks if response code is not 200-OK, if not it waits 60 seconds and tries again
        failcount+=1 #increment fail count
        print("Fail count: {}".format(failcount))
        time.sleep(120)
        if failcount >=10:
            print("All available packages have been scraped for today.")
            remove_duplicates()
            break
        continue

    for package in range(len(raw)): #iterates through each package that was returned on the page (100)
        name = raw[package]['name']
        date = raw[package]['latest_release_published_at']
        version_number = raw[package]['latest_release_number'] #assign variables and split dates so they are in the same format
        header = ['name', 'date', 'version']
        final_data = [name, date, version_number]
        today = str(datetime.today()).split(" ") #datetime has a space delimiter for the time, so split at that
        pubdate = date.split("T") #npm packages have a T delimiter for the time, so split at that

        with open('.\packages{}.csv'.format(today[0]), 'a') as f: #create packages{date}.csv and write data to it
            writer = csv.writer(f)
            if package==0 and counter==0: #write header to csv file on first iteration
                writer.writerow(header)
            if pubdate[0] == today[0]: #check if package was published today, if so, write it to the csv. Uses the [0] index because the date is split into a list [date, time] and we only need the first element
                writer.writerow(final_data)
            elif pubdate[0] != today[0]: #if package was not published today, break the loop and finish.
                print("All packages published today {} have been added to the packages.csv file".format(today[0]))
                remove_duplicates()
                keepgoing = False


    counter+=1
