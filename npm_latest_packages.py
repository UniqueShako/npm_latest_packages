import csv
import requests
import os
import time
from datetime import datetime
from os.path import exists
import argparse


#NOTE THIS PROGRAM WILL NOT WORK IF YOU DO NOT HAVE A LIBRARIES.IO API KEY AND HAVE IT INSERTED INTO THE api_key VARIABLE ON LINE 21. SEE BELOW ON HOW TO OBTAIN API KEY

#This program queries the libraries.io API for new and newly updated NPM packages for today. It then takes the package name, date published, and version number and adds them to a CSV file
#in the current directory. If the CSV file does not exist it will be created automatically. Finally it will remove duplicate entries from the CSV file and output the _final CSV file.

#To run this program yourself you will need a libraries.io API key, which can be obtained by signing up for a freee libraries.io acocunt and checking your account settings page.
#This program depends on the "requests" library which you may need to install using "pip install requests"

#This may take several minutes to run depending on how much load is being put on the libraries.io servers. It will handle errors and wait 2 minutes between each error code returned from the server.
#If it encounters 10 error messages over the course of running, the program will clean up duplicates and end.

#IN ORDER FOR THE DOWNLOADER TO WORK YOU MUST CREATE THE "packages_dl" directory in the directory you are running the scraper from



api_key = '' #PUT YOUR API KEY HERE SURROUNDED BY QUOTES eg. 'thisisyourapikey'
counter = 0 #used to increase page count
failcount = 0 #keep track of failures
keepgoing = True #looper, set set to false if date does not equal today
ossgadgetpath = '.\ossgadget' #path to ossgadget folder. By default it looks at current directory


parser = argparse.ArgumentParser(description='A program that interacts with the Libraries.io API to pull down NPM packages for analysis')

parser.add_argument("-d","--download", help="Downloads found packages to ./packages_dl, disabled by default", action="store_true")
parser.add_argument("-p","--package", help="Download a specific package. Must be exact name eg. @types/node")
parser.add_argument("-t","--time", help="Usage: -t [date] Specify date that packages should be downloaded from. Format: yyyy-mm-dd eg. 2022-09-21")


args = parser.parse_args()

specify_time = args.time
specify_download = args.download
specify_package = args.package

if (specify_time):
    today = [specify_time]
else:
    today = str(datetime.today()).split(" ")

def single_dl(input_package):
    if '@' in input_package:
            input_package = input_package.replace('@', '%40').replace('/', '%2F')
    os.system('cmd /k "{}\oss-download -c -e -x ./packages_dl pkg:npm/{} & exit"'.format(ossgadgetpath, input_package))

if(specify_package):
    single_dl(specify_package)
    exit()

if exists('.\packages{}.csv'.format(today[0])): #checks if the packages have already been scraped today, if it has then it deletes the old file and starts fresh. need to build some logic in so that it only scrapes new updates instead of all updates for the day.
    os.remove('.\packages{}.csv'.format(today[0]))

def remove_duplicates(): #iterates through csv file and outputs _final csv file with duplicates removed

    inFile = open('.\packages{}.csv'.format(today[0]),'r')
    outFile = open('.\packages{}_final.csv'.format(today[0]),'w')
    listLines = []
    for line in inFile:
        if line in listLines:
            continue
        else:
            outFile.write(line)
            listLines.append(line)
    outFile.close()
    inFile.close()

while keepgoing:
    response = requests.get("https://libraries.io/api/search?order=desc&page={}&per_page=99&platforms=npm&sort=latest_release_published_at&api_key={}".format(counter+1, api_key))
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
        oldname = raw[package]['name']
        if '@' in raw[package]['name']:
            name = raw[package]['name'].replace('@', '%40').replace('/', '%2F')
        else:
            name = raw[package]['name']
        date = raw[package]['latest_release_published_at']
        version_number = raw[package]['latest_release_number'] #assign variables and split dates so they are in the same format
        header = ['name', 'date', 'version']
        final_data = [oldname, date, version_number]
        pubdate = date.split("T") #npm packages have a T delimiter for the time, so split at that

        with open('.\packages{}.csv'.format(today[0]), 'a') as f: #create packages{date}.csv and write data to it
            writer = csv.writer(f)
            if package==0 and counter==0: #write header to csv file on first iteration
                writer.writerow(header)
            if pubdate[0] > today[0]:
                continue
            if pubdate[0] == today[0]: #check if package was published today, if so, write it to the csv. Uses the [0] index because the date is split into a list [date, time] and we only need the first element
                writer.writerow(final_data)
                if(specify_download):
                    os.system('cmd /k "{}\oss-download -c -e -x ./packages_dl pkg:npm/{} & exit"'.format(ossgadgetpath, name)) #downloads package and puts it into "packages_dl" which you will need to create manually
            elif pubdate[0] != today[0]: #if package was not published today, break the loop and finish.
                print("All packages published today {} have been added to the packages.csv file".format(today[0]))
                remove_duplicates()
                keepgoing = False


    counter+=1