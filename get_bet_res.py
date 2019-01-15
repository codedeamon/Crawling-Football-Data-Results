import requests
import re
import urllib.request
import sys
import csv
from bs4 import BeautifulSoup 
import pandas as pd
import numpy as np
import string
from pandas import ExcelWriter # from pandas.io.parsers import ExcelWriter
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from time import sleep
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException


def save_xls(list_dfs, year, country, tournament, rounds=0):

    xls_path = country + '_' + tournament + '.xlsx'
    writer = ExcelWriter(xls_path)
    workbook  = writer.book

    for n, df in enumerate(list_dfs):

        df.to_excel(writer,'res_%s' % year, index=False)
        worksheet = writer.sheets['res_%s' % year]
        worksheet.write(len(df) + 1, 0, "Rounds = %s" %rounds)
        year += 1

    writer.save()
    
    with open("files.txt", "a") as myfile:
        myfile.write(xls_path)
        myfile.write('\n')

def save_test_xls(list_dfs, rounds):

    xls_path = 'testFile_xc.xlsx'
    writer = ExcelWriter(xls_path, engine='xlsxwriter')
    workbook  = writer.book

    for n, df in enumerate(list_dfs):
        df.to_excel(writer,'sheet%s' % n, index=False)
        #df.to_excel(writer,'sheet1', index=False)
        worksheet = writer.sheets['sheet%s' % n]
        worksheet.write(len(df) + 1, 0, "Rounds %s" %rounds)

    writer.save()


def testExcel():
    a = np.ones((3,4))
    dfList = []
    resultDf = pd.DataFrame(a)
    for i in range(0,4):
        dfList.append(resultDf)

    save_xls(dfList,2015, 'kakaka', 'lalala', 5 )



'''
def save_xls(list_dfs, xls_path):
    writer = ExcelWriter(xls_path, engine='xlsxwriter')

    workbook  = writer.book

    for n, df in enumerate(list_dfs):
        #df.to_excel(writer,'sheet%s' % n, index=False)
        df.to_excel(writer,'s15-16', index=False)

    #worksheet = writer.sheets['s15-16']
    #worksheet.write(len(df) + 1, 0, "xssxs")
    writer.save()

'''

def init_driver():

    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Firefox(firefox_options=options, executable_path='/home/alexander/PycharmProjects/geckodriver')
    #driver = webdriver.Firefox(executable_path='/home/alexander/PycharmProjects/geckodriver')
    driver.wait = WebDriverWait(driver, 5)
    return driver

def get_data(driver, url=None, year=0, country=None, tournament=None):

    if url == None:
        url = 'https://www.flashscore.com/football/'+ country +'/' + tournament + '-'+ str(year) + '-' + str(year+1) + '/results'
        print(url)

    try:
        driver.get(url)
    except:
        return (-1,1)
        
    sleep(4)
    #showMore_cssS = '#tournament-page-results-more'
    #element = driver.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, showMore_cssS)))
    #element.click()
    #element = driver.wait.until(EC.visibility_of((By.CSS_SELECTOR, showMore_cssS)))

    i = 0

    try:
        element=driver.find_element_by_css_selector("#tournament-page-results-more > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(1) > a:nth-child(1)")
    except NoSuchElementException:
        print("element not found exception")
        return (-1,1)

    try:
        driver.execute_script("loadMoreGames();")
        sleep(4)
    except:
        print("button not found exception")
        return (-1,1)

    while (i < 5):

        driver.execute_script("loadMoreGames();")
        sleep(5)
        i += 1
   
    sleep(5)
    html = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
    return (html,0)
 
def findCountries(countryList):

    teamList = []
    country = []
    flag = 1
    #df = pd.DataFrame(data,columns=['Name','Age'])

    for idx, team in enumerate(countryList):
        temp = team
        temp = temp.replace(u'\xa0', u'')
        if team == "africa":
            break

        for x in teamList:

            if(x == temp):
                flag = 0
                break

        if(flag == 1 and temp !='More'):

            teamList.append(temp)
        flag = 1

    print(teamList)
    print('number of countries is ', len(teamList))

    return teamList



def getCountries(siteUrl, driver=None):

    driver.get(siteUrl)
    driver.execute_script("cjs.dic.get('Helper_Tab').showMoreMenu('.tournament-menu'); return false;")
    sleep(5)
    r = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
    #class="menu country-list tournament-menu

    soup = BeautifulSoup(r, 'lxml')
    body = soup.body
    container = body.find('div', class_='container')
    countries = container.div.find_all('ul', class_='menu country-list tournament-menu')
    countryList = []

    for i in countries:

        co = i.find_all('a')
        for h in co:
            c = h.get('href').split("/")
            if(len(c) >= 2):
                countryList.append(c[2])
                #print(c[2])

    countries = findCountries(countryList)
    #countries = list(set(countryList))

    return countries




def findTeams(teams):

    teamList = []
    flag = 1
    #df = pd.DataFrame(data,columns=['Name','Age'])

    for idx, team in enumerate(teams):
        temp = team.text
        temp = temp.replace(u'\xa0', u'')

        for x in teamList:

            if(x == temp):
                flag = 0
                break

        if(flag == 1):

            teamList.append(temp)
        flag = 1

    print(teamList)
    print('number of teams is ', len(teamList))

    return teamList

def getScores(nGames, scores):

    array = np.zeros((nGames, 2))

    for idx, x in enumerate(scores):

        if len(x.text.split(':')) > 2:
            print("The score was: ",x.text)
            x = x.text.replace(u'\xa0', u'')
            y = x.split("(")
            z = y[1].split(")")
            print(z[0])
            array[idx,:] = z[0].split(':')


        else:
            #print("i: ",idx,", score: ",x.text)
            try:
                array[idx,:] = x.text.split(':')
            except:
                array[idx,:] = [17,17]
        

    return array


def teamLocations(matches, teamList, ground, teamMatchesList=None, teamGroundList=None):

    #firstHalf = int(numberOfRounds/2)-1

    numberOfTeams = len(teamList)

    if ground == 1:

        teamMatchesList = []
        teamGroundList = []

        for i in range(0,len(teamList)):
            teamMatchesList.append([])
            teamGroundList.append([])


    for idxN, name in enumerate(teamList):

        for idxG, game in enumerate(matches):

            game = game.text.replace(u'\xa0', u'')

            if(name == game):
                teamMatchesList[idxN].append(idxG)
                teamGroundList[idxN].append(ground)

    #print(teamMatchesList)
    return (teamMatchesList, teamGroundList)
    
def sortThe2Lists(teamMatchesList, teamGroundList, numberOfTeams):

    for i in range(0,numberOfTeams):
        s = sorted(zip(teamMatchesList[i],teamGroundList[i]))
        teamMatchesList[i],teamGroundList[i] = map(list, zip(*s))

    return teamMatchesList, teamGroundList


def WinDrawLoss(teamMatchesList, teamGroundList, scores, numberOfTeams):

    # now teamGroundList will contain -1,0,1 instead of 0,1 (ground)

    for column in range(0, numberOfTeams):

        for index in range(0, len(teamMatchesList[column])):

            sc1,sc2 = scores[int(teamMatchesList[column][index])]
            ground = teamGroundList[column][index]
            
            if(sc1 > sc2):
                teamGroundList[column][index] = ground * 2 - 1
                #resultArray[1,index, column] = ground * 2 - 1

            elif(sc1 < sc2):
                teamGroundList[column][index] = 1 - 2 * ground
                #resultArray[1,index, column] = 1 - 2 * ground

            else:
               teamGroundList[column][index] = 0

    return (teamMatchesList, teamGroundList)


def print_scores(teamMatchesList, scores, wantCol):

    for index in range(0, len(teamMatchesList[wantCol])):

        sc1,sc2 = scores[int(teamMatchesList[index][wantCol])]
        print(index, ":",sc1,sc2)

def print_positions(teamMatchesList, wantCol, secCol):

    print("printing positions for col ", str(wantCol), "_______________")
    for index in range(0, len(teamMatchesList[wantCol])):
        print(index, ": " ,teamMatchesList[wantCol][index])

    print("printing positions for col ", str(secCol), "_______________")
    for index in range(0, len(teamMatchesList[secCol])):
        print(index, ": " ,teamMatchesList[secCol][index])
    

def write2File(r, fileName):
    fileName += ".txt"
    f = open(fileName,"w")
    f.write(r)
    f.close()

def readFromFile(filename):

    filename += ".txt"
    f = open(filename,"r")
    r = f.read()
    f.close()
    return r

def getTournaments(url, country, driver):

    url = url + country + '/'
    print(url)
    driver.get(url)
    driver.execute_script("cjs.dic.get('Helper_Tab').showMoreMenu('.tournament-menu'); return false;")
    sleep(4)
    r = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
    #r = readFromFile(country)
    #write2File(r,country)

    soup = BeautifulSoup(r, 'lxml')
    body = soup.body
    container = body.find('div', class_='container')
    tournaments = container.div.find_all('ul', class_='menu selected-country-list')
    print(tournaments)
    tournamentList = []

    for tour in tournaments:
        href = tour.find_all('a')
        for h in href:
            c = h.get('href').split("/")
            try:
                #print(c[-2])
                tournamentList.append(c[-2])
            except:
                break

    return tournamentList


def sort_3d_array(a):
    for l in range(0,len(a[0,0,:])):
        k = a[:,:,l]
        c = k[1,:]
        i = np.argsort(c)
        a[:,:,l] = k[:,i]
    return a

def reverse_2dlist(list1, list2):

    for i in range(0, len(list1)):
        list1[i] = list(reversed(list1[i]))

    for i in range(0, len(list2)):
        list2[i] = list(reversed(list2[i]))

    return (list1, list2)

def maxLengthOfLists(list1):

    maxL = 0

    for i in list1:
        k = len(i)
        #print(i)
        if k > maxL:
            maxL = k
            #print("maxL ", str(k))

    return maxL 



def findNRounds(html):
    temp = html.div.find_all('tr', class_='event_round')
    flag = 0
    maxR = 0
    maxPos = 0

    for idg,game in enumerate(temp):

        #print(game.text)

        g = game.text.split(" ")
        if g[0] == "Round":
            #print(g)
            number = int(g[1])
            if number > maxR:
                maxR = number
                maxPos = idg

    return maxR

def transposeLists(list1):
    map(list, zip(*list1))

    return list1

def testURL(f, url=None, driver=None):
    print("testing url results")

    if f == 'r':
        r = readFromFile("testFile")

    else:
        r,yearFlag = get_data(driver, url)
        if r == -1:
            print("r == -1, returning")
            return -1
        try:
            write2File(r,"testFile")
        except:
            print("could not write to test file")

    soup = BeautifulSoup(r, 'lxml')
    body = soup.body
    container = body.find('div', class_='container')

    numberOfRounds = findNRounds(container)
    print("number of rounds = ", str(numberOfRounds))


    teamGround = container.div.find_all('span', class_='padr')
    teamHost = container.div.find_all('span', class_='padl')
    scores = container.div.find_all('td', class_='cell_sa score  bold ')

    scoreArray = getScores(len(teamGround), scores)

    teams = findTeams(teamGround)
    print("Total matches: ", len(teamGround))

    teamLocList, groundLocList = teamLocations(teamGround,teams,1)
    teamLocList, groundLocList = teamLocations(teamHost,teams,0,teamLocList, groundLocList)
    teamLocList, groundLocList = sortThe2Lists(teamLocList, groundLocList, len(teams))
   
    print("++++ printing positions after sorting")
    print_positions(teamLocList, 0, 1)
    print("__________________________")

    groundLocList = WinDrawLoss(teamLocList, groundLocList, scoreArray, len(teams))
    #maxLen = maxLengthOfLists(groundLocList[0])
    groundLocList= reverse_2dlist(groundLocList[0],groundLocList[1]) 

    maxLen = len(max(groundLocList[1],key=len))
    if maxLen < numberOfRounds:
        maxLen = numberOfRounds
        print("prosoxh malakies maxLen = ", str(maxLen))

    print("Max length of lists: ", str(maxLen))
    print("len of groundLocList: ", len(groundLocList), " ", len(groundLocList[1]))

    resultArray =  np.full((maxLen, len(teams)), 7)

    for i,team in enumerate(groundLocList[1]):
        for j,res in enumerate(groundLocList[1][i]):
            resultArray[j,i] = res

    print("Result array is now\n")
    print(resultArray)

    resultDf = pd.DataFrame(resultArray, columns=teams)

    list_dfs = []

    list_dfs.append(resultDf)
    save_test_xls(list_dfs, numberOfRounds)


def main():

    ans = input("press: t to test a url, m for main programme\n")

    if ans == 'm':
        driver = init_driver()
        runMain(driver)

    elif ans == 't':

        fromFile = input("press: r to read from the last test file, u to download new\n")

        if fromFile == 'r':
            testURL(fromFile)

        elif fromFile == 'u':
            url = input("insert the url\n")
            driver = init_driver()
            testURL(fromFile, url, driver)
        else:
            print("wrong input, try again")
    driver.close()


def runMain(driver):
    url = 'https://www.flashscore.com/'

    countries = getCountries(url, driver)

    url = url + 'football/'
    firstYear = 2013

    for cID,country in enumerate(countries):

        yearFlag = 0

        tournaments = getTournaments(url, country,driver)
        print("Tournaments: ",tournaments)

        for tID,tournament in enumerate(tournaments):

            if tID > 0:
                break

            list_dfs = []
            numberOfRounds = 0

            for year in range(2013,2018):
                
                r,yearFlag = get_data(driver,None,year,country, tournament)

                if r == -1:
                    continue

                soup = BeautifulSoup(r, 'lxml')
                body = soup.body
                container = body.find('div', class_='container')

                numberOfRounds = findNRounds(container)
                print("number of rounds = ", str(numberOfRounds))


                teamGround = container.div.find_all('span', class_='padr')
                teamHost = container.div.find_all('span', class_='padl')
                scores = container.div.find_all('td', class_='cell_sa score  bold ')

                scoreArray = getScores(len(teamGround), scores)

                teams = findTeams(teamGround)
                #print("Total matches: ", len(teamGround))

                teamLocList, groundLocList = teamLocations(teamGround,teams,1)
                teamLocList, groundLocList = teamLocations(teamHost,teams,0,teamLocList, groundLocList)
                teamLocList, groundLocList = sortThe2Lists(teamLocList, groundLocList, len(teams))
                groundLocList = WinDrawLoss(teamLocList, groundLocList, scoreArray, len(teams))
                groundLocList = reverse_2dlist(groundLocList[0],groundLocList[1]) 
                maxLen = len(max(groundLocList[1],key=len))    
               
                resultArray =  np.full((maxLen, len(teams)), 7)

                for i,team in enumerate(groundLocList[1]):
                    for j,res in enumerate(groundLocList[1][i]):
                        resultArray[j,i] = res

                resultDf = pd.DataFrame(resultArray, columns=teams)

                list_dfs.append(resultDf)

            if numberOfRounds != 0: 
                save_xls(list_dfs, firstYear, country, tournament, numberOfRounds)



main()
