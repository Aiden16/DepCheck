import requests
from bs4 import BeautifulSoup
import sys
import csv
from tabulate import tabulate
from packaging import version
import subprocess
import os
#function to compare version
def comparison(URL):
    r = requests.get(URL)
    soup = BeautifulSoup(r.text,'html.parser')
    li = soup.findAll('div',class_='Box mt-3 position-relative')
    titleDiv = soup.find_all('div',class_="flex-auto min-width-0 width-fit mr-3")
    title = ''
    for i in titleDiv:
        for a in i.findAll('a'):
            title = a.text
    s= ''
    flag = False
    for _,i in enumerate(li):
        for ind,a in enumerate(i.findAll('td')):
            if a.text == '  },':
                flag = False
            if flag:
                s += a.text
            if a.text == ' "dependencies": {':
                flag = True
    redundant = ["{","}",'"',' ']
    processed = ""
    for i in s:
        if i in redundant:
            continue
        else:
            processed+=i
    versions = {}
    processed = processed.split(',')
    for i in processed:
        lis = i.split(':')
        versions[lis[0]] = lis[1][1:]
    for dependency in versions:
        if dependency == sys.argv[3]:
            isTrue = False
            if version.parse(str(sys.argv[4]))<=version.parse(str(versions[sys.argv[3]])):
                isTrue = True
            myData.append([title,row[1],versions[sys.argv[3]],isTrue])
#function for PR
def PR(URL,package):
    wd = os.getcwd()
    subprocess.run(["gh","repo","fork",URL,"--clone"])
    os.chdir(URL)
    subprocess.check_call(' npm install {}@latest'.format(package), shell=True)
    subprocess.run(["git","checkout","-b","Updating-Package"])
    subprocess.run(["git","add","."])
    subprocess.run(["git","commit","-m","updating dependency"])
    subprocess.run(["git","push","origin","Updating-Package"])

#if user wants to compare versions
if sys.argv[1] == '-i':
    csvFile = sys.argv[2]
    with open(csvFile) as file:
        reader = csv.reader(file)
        myData = []
        for ind,row in enumerate(reader):
            if ind>0:
                input_url = row[1]
                URL = input_url+"/blob/master/package.json"
                comparison(URL)
    head = ['name','repo','version','version_satisfied']
    print(tabulate(myData, headers=head, tablefmt="grid"))

#if user wants to compare version and create a PR
elif sys.argv[1] == "-update":
    csvFile = sys.argv[3]
    with open(csvFile) as file:
        reader = csv.reader(file)
        myData = []
        for ind,row in enumerate(reader):
            if ind>0:
                input_url = row[1]
                URL = input_url
                print(sys.argv[4])
                PR(URL,sys.argv[4])
                URL = input_url+"/blob/master/package.json"
                comparison(URL)
                for i in myData:
                    if i[2] == False:
                        PR(i[1],sys.argv[5])
                    i.append('YES')
    head = ['name','repo','version','version_satisfied',"PR_Created?"]
    print(tabulate(myData, headers=head, tablefmt="grid"))
    
