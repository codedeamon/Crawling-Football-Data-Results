# Crawling-Football-Results

In get_bet_res.py I implement a simple web crawler using **Selenium** which navigates a betting website in order to download football matches result history. When each web page is downloaded, **BeautifulSoup** is used to extract the desired data.

The excel files are named after each country and it's championship and the results encoding is: 1 if the team won the match, -1 for loss and 0 for draw. When a cell contain -7 this means that that game was cancelled.

## Programme structure

You can choose to test a url, each means that you can either provide a new url to download a new page of football results and test beautifulsoup parameters there or to work with the latest downloaded page and don't downloaded anything new. This was done because many countries have different championship systems, eg. in greek championship every team plays two games with the rest, which means that if there are 18 teams, every team will play 17x2 = 34 games in total. But in, for example, albanian championship a team can have more games with the rest so I had to take this difference into consideration. 

On the other hand if you press **m**, the programme will start navigating and downloading results of every country in alphabetic order. The data downloaded will then be saved in excel files.

'''

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

'''

## runMain() 

This function navigates all the countries and starts downloading from the year 2013. If you want to download all the tournaments of each country, delete `if tID > 0: 
                            break`

in line 542 because in my case only the main championship was needed. 

'''

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


'''

## Data analysis </br>
In data_analysis.py a simple strategy is implemented for betting on football matches. Basically, the strategy bets on the draw and if it loses, it bets again on the same team and the same result. Having collected data from multiple championships and having a program that watches every week, every team we can easily test if our initial hypothesis would work if we were to bet those years. 

