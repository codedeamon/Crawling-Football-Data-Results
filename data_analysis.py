import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys
import random
from pandas import ExcelWriter # from pandas.io.parsers import ExcelWriter

df_per_list = []
teamDyn = []

def save_xls(list_dfs,fileName, year=0, country=None, tournament=None, rounds=0):

    xls_path = "periods_" + fileName
    writer = ExcelWriter(xls_path)
    workbook  = writer.book

    for n, df in enumerate(list_dfs):

        df.to_excel(writer,'res_%s' % n, index=False)
        worksheet = writer.sheets['res_%s' % n]
    
    writer.save()
   
def find_periods(element_list, df):

	periods_list = []
	lastTime = np.zeros((len(element_list),1))

	for i in range(0,len(df.columns)):
		periods_list.append([])

		for j in range(0, len(element_list)):
			periods_list[i].append([])

	for c,column in enumerate(df):
		for i, row_value in df[column].iteritems():

			for el_pos,element in enumerate(element_list):

				if row_value == element:
					periods_list[c][el_pos].append(int(lastTime[el_pos]))
					lastTime[el_pos] = 0

				else:
					lastTime[el_pos] += 1
					if i == len(df) - 1:
						periods_list[c][el_pos].append(int(lastTime[el_pos]*(-1)))
						
		lastTime[:] = 0
	return periods_list


def get_max_min_avg(periods_list):
	
	max_list = []
	min_list = []
	avg_list = []

	for i in periods_list:

		for j in i:
			max_list.append(max(j))
			min_list.append(min(j))
			avg_list.append(sum(j) / float(len(j)))

	return (max_list, min_list, avg_list)

def algo1(data_without_nan_df, dropTeam=None,algo3=0,algo4=0,algo5=0):

	lastTime = np.zeros((1,len(data_without_nan_df.columns)))
	teamDyn = np.zeros((1,len(data_without_nan_df.columns)))
	teamPoints = np.zeros((1,len(data_without_nan_df.columns)))

	playFlag = 0
	playPos = 0
	bet = 1
	losses = 0
	winnings = 0
	totalWinnings = 0
	maxLosses = 0
	thisRound = 0
	
	if dropTeam != None:

		while (1):
			print("the teams are: ", data_without_nan_df.columns)
			dropTeam = input("type a team to remove or 'e' to continue")
			if dropTeam == "e":
				break
			else:
				try:
					data_without_nan_df = data_without_nan_df.drop(dropTeam, 1)
				except:
					print("no column with name ", dropTeam)


	for index, row in data_without_nan_df.iterrows():
		for c,column in enumerate(data_without_nan_df):

			teamDyn[0,c] += data_without_nan_df.iloc[index,c]

			if data_without_nan_df.iloc[index,c] == 0:

				if playPos == c and playFlag == 1:
					#print(data_without_nan_df.iloc[index,c])
					playFlag = 0
					losses += bet
					winnings += 3 * bet - losses
					totalWinnings += winnings
					if losses > maxLosses:
						maxLosses = losses
						if losses > 255:
							print("losses>255 with team: ", data_without_nan_df.columns[c],"max losses = ", maxLosses)

					print("winnings = ", winnings, "max losses = ", losses, "last bet was ", bet, "team = ",data_without_nan_df.columns[c] )
					bet = 1
					losses = 0
					winnings = 0
					thisRound = index

				lastTime[0,c] = 0

			else:

				lastTime[0,c] += 1

				if playPos == c and playFlag == 1:

					losses += bet 
					bet *= 2
					#print("losses are ", losses, "next bet will be ", bet)

		if playFlag == 0:
			maxKey = np.max(lastTime, axis=1)

			if (maxKey > 4 and index < len(data_without_nan_df)-10) or (maxKey > 8 and index < len(data_without_nan_df)-6):

				playFlag = 1
				algo5Flag = 0

				if algo5 == 1:

					for i in range(0,len(lastTime[0,:])):
						if lastTime[0,i] > 4:
							algo5Flag = 1
							print(i," : ",data_without_nan_df.columns[i]," : ", lastTime[0,i], ", dynamics: ",teamDyn[0,i],"#game: ", index)

					if algo5Flag == 1:

						playPos = int(input("pres 1,2,... to choose to follow that team or -1 to pass\n"))
						if playPos == -1:
							playFlag = 0
							break

						bet = int(input("how much for the initial bet? \n"))

					algo5Flag = 0


				if algo3 == 1 and algo5 == 0:

					teamPoints[0,:] = lastTime[0,:]*10 + (6 - abs(teamDyn[0,:])) * 5
					playPos = teamPoints.argmax(axis=1)

				elif algo3 == 0 and algo5 == 0:
					playPos = lastTime.argmax(axis=1)

				if algo4 == 1 and algo5==0:
					if lastTime[0,playPos] > 8:
						bet = 10
				#print("Now will bet on ", data_without_nan_df.columns[playPos], "round = ", index)

	print("Total winnings = ", totalWinnings, "max losses = ", maxLosses)


def algo2(df, previousTeamsDyn,algo3=0,algo4=0,algo5=0, dropTeam=None):

	previousTeamsDyn.reset_index(drop=True, inplace=True)
	
	document = previousTeamsDyn.values.tolist()
	for i in document:
		if i[-1] in df.columns:
			df.drop([i[-1]], axis = 1, inplace = True)

	if algo3 == 0:
		algo1(df,dropTeam)
	elif algo3 != 0 and algo4 == 0:
		algo1(df,dropTeam,1)

	if algo4 != 0 and algo5 ==0:
		algo1(df,dropTeam,1,1)

	if algo5 == 1:

		algo1(df,None,1,1,1)


def getStats(data_without_nan_df, numberOfRounds,teams):
	global df_per_list

	elements2_per = []
	elements2_per.append(0)
	periods_list = find_periods(elements2_per,data_without_nan_df)

	a = np.full((numberOfRounds,len(teams)), -7)
	for posi,i in enumerate(periods_list):
		for posj,j in enumerate(i):
			a[:len(j),posi] = j

	aDf = pd.DataFrame(a, columns=teams)
	df_per_list.append(aDf)

	stat_list = get_max_min_avg(periods_list)

	stats = np.array(stat_list)
	teams_stats_df = pd.DataFrame()
	teams_stats_df['Teams'] = teams
	teams_stats_df['Max'] = stats[0,:]
	teams_stats_df['Min'] = stats[1,:]
	teams_stats_df['Avg'] = stats[2,:]
	temp = np.array(data_without_nan_df.sum(axis=0))
	teams_stats_df['Dynamics'] = temp
	#print(teams_stats_df)
	teams_stats_df = teams_stats_df[(teams_stats_df['Dynamics'] < -10) | (teams_stats_df['Dynamics'] > 10)].copy()
	#print(teams_stats_df)
	teams_stats_df.reset_index(drop=True, inplace=True)
	return teams_stats_df[[0]]



def checkRounds(df):

	maxR = 1

	for column in df:
		counter = 0
		count_nan = len(df[column]) - df[column].count()
		if count_nan > maxR:
			maxR = count_nan
		

	return maxR 

def preprocessData(fileName,sheet):

	print("-------- year ", sheet, " --- ", fileName, " --------------")
	file_data_df = pd.read_excel(fileName,sheet)  # read a specific sheet to DataFrame

	#file_data_df = pd.read_excel("testing.xlsx",1)
	rows, cols = file_data_df.shape

	numberOfRounds = int(file_data_df.iloc[rows-1,0].split(" ")[-1])

	file_data_df = file_data_df.replace(7, np.nan)

	teams = file_data_df.columns
	#print("the teams are ",len(teams),"\n", teams)

	threshold = rows - numberOfRounds
	data_without_nan_df = file_data_df.dropna(thresh=len(file_data_df) - threshold, axis=1).copy()
	numberOfGames = checkRounds(data_without_nan_df)
	data_without_nan_df.drop(data_without_nan_df.tail(rows - (rows - numberOfGames)).index,inplace=True)
	teams = data_without_nan_df.columns
	if numberOfRounds < rows - numberOfGames:
		print("+++++++++ Number of Rounds is False: #Rounds = ", numberOfRounds," : #Games = ", rows - numberOfGames)
	elif numberOfRounds > rows - numberOfGames:
		print("+++ ABORTING ++++++ Number of Rounds is False: #Rounds = ", numberOfRounds," : #Games = ", rows - numberOfGames)
		return pd.DataFrame(), 1

	return data_without_nan_df,(rows - numberOfGames)

def runSelectedChamps(bad_teams_df, all_countr_file=0):



	countryList = []
	if all_countr_file == 0:
		while(1):
			c = input("give a country to input or e to continue")
			if c == "e":
				break

			c += ".xlsx"
			countryList.append(c)

	else:
		all_countries_df = pd.read_csv('wanted_countries.txt', sep="\n", header=None)

		for country in all_countries_df.iterrows():
			#print(country[1][0])
			countryList.append(country[1][0])

	df_list = []
	ok_country_list = []
	numberOfGames = 0
	minNumberOfGames = 100
	
	for country in countryList:
		df = pd.ExcelFile(country)
		if len(df.sheet_names) > 4:
			ok_country_list.append(country)
			sheet_names = df.sheet_names

	for shID,sheet in enumerate(sheet_names):

		countries_df = pd.DataFrame()
		for country in ok_country_list:

			df1,numberOfGames = preprocessData(country,sheet)

			if numberOfGames < minNumberOfGames:
				minNumberOfGames = numberOfGames

			if df1.empty:
				continue

			for team in bad_teams_df.iterrows():
				for t in df1.columns:
					if team[1][0] == t:
						df1.drop([t], axis=1,inplace=True)

			countries_df = pd.concat([countries_df.copy(), df1], axis=1, join='inner')


		teamDyn.append(getStats(countries_df,minNumberOfGames,countries_df.columns))
		print("algo 1:")
		algo1(countries_df)
		if shID > 0:
			print("Algo 2:")
			algo2(countries_df, teamDyn[-2])
			print("Algo 3:")
			algo2(countries_df, teamDyn[-2],1)
			print("algo 4:")
			algo2(countries_df, teamDyn[-2],1,1)
			print("algo 5:")
			algo2(countries_df, teamDyn[-2],1,1,1)


def runTestingFile(bad_teams_df):

	fileName = input("give file name please\n")
	fileName += ".xlsx"
	df = pd.ExcelFile(fileName)

	sheet_names = df.sheet_names
	print(sheet_names)  # see all sheet names
	
	for shID, sheet in enumerate(sheet_names):
		data_without_nan_df,games = preprocessData(fileName,sheet)
		if data_without_nan_df.empty:
			continue

		for team in bad_teams_df.iterrows():
			for var in team[1]:
				print(var)
			for t in data_without_nan_df.columns:
				if team[1][0] == t:
					data_without_nan_df.drop([t], axis=1,inplace=True)


		teamDyn.append(getStats(data_without_nan_df,games,data_without_nan_df.columns))
		print("algo 1:")
		algo1(data_without_nan_df)
		if shID > 0:
			print("Algo 2:")
			algo2(data_without_nan_df, teamDyn[-2])
			print("Algo 3:")
			algo2(data_without_nan_df, teamDyn[-2],1)
			print("algo 4:")
			algo2(data_without_nan_df, teamDyn[-2],1,1)
			print("algo 5:")
			algo2(data_without_nan_df, teamDyn[-2],1,1,1)



	save_xls(df_per_list,fileName)


def main():

	bad_teams = pd.read_csv('bad_teams.txt', sep="\n", header=None)
	print(bad_teams.shape)
	
	ans = input("press test or sel or all\n")

	if ans == "test":
		runTestingFile(bad_teams)

	elif ans == "sel":
		runSelectedChamps(bad_teams)
	else:
		runSelectedChamps(bad_teams,1)

main()