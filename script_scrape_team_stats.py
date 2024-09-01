"""

Preseason and Regular Season Team Statistics Scraper.
Written by reddit: u/geauxpackgo, github: andrewr7
Sep 1, 2024

"""

import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import time


def is_playoff_team(Tm):
    if '*' in Tm or '+' in Tm:
        return True
    else:
        return False

def is_division_winner(Tm):
    if '*' in Tm:
        return True
    else:
        return False

def match_team(Tm):
    Tml = Tm.lower()
    if 'cardinal' in Tml:
        return 'Arizona Cardinals'
    if 'falcon' in Tml:
        return 'Atlanta Falcons'
    if 'raven' in Tml:
        return 'Baltimore Ravens'
    if 'bills' in Tml:
        return 'Buffalo Bills'
    if 'panther' in Tml:
        return 'Carolina Panthers'
    if 'bear' in Tml:
        return 'Chicago Bears'
    if 'bengal' in Tml:
        return 'Cincinnati Bengals'
    if 'brown' in Tml:
        return 'Cleveland Browns'
    if 'cowboy' in Tml:
        return 'Dallas Cowboys'
    if 'bronco' in Tml:
        return 'Denver Broncos'
    if 'lion' in Tml:
        return 'Detroit Lions'
    if 'packer' in Tml:
        return 'Green Bay Packers'
    if 'texan' in Tml:
        return 'Houston Texans'
    if 'colt' in Tml:
        return 'Indianapolis Colts'
    if 'jaguar' in Tml:
        return 'Jacksonville Jaguars'
    if 'chief' in Tml:
        return 'Kansas City Chiefs'
    if 'raider' in Tml:
        return 'Las Vegas Raiders'
    if 'charger' in Tml:
        return 'Los Angeles Chargers'
    if 'rams' in Tml:
        return 'Los Angeles Rams'
    if 'dolphin' in Tml:
        return 'Miami Dolphins'
    if 'viking' in Tml:
        return 'Minnesota Vikings'
    if 'patriot' in Tml:
        return 'New England Patriots'
    if 'saint' in Tml:
        return 'New Orleans Saints'
    if 'giant' in Tml:
        return 'New York Giants'
    if 'jets' in Tml:
        return 'New York Jets'
    if 'eagle' in Tml:
        return 'Philadelphia Eagles'
    if 'steeler' in Tml:
        return 'Pittsburgh Steelers'
    if '49er' in Tml or 'forty' in Tml or 'niner' in Tml:
        return 'San Francisco 49ers'
    if 'seahawk' in Tml:
        return 'Seattle Seahawks'
    if 'buccaneer' in Tml:
        return 'Tampa Bay Buccaneers'
    if 'titan' in Tml or 'oiler' in Tml:
        return 'Tennessee Titans'
    if 'redskin' in Tml or 'washington' in Tml or 'commander' in Tml:
        return 'Washington Commanders'
    
    print(f'No match for {Tm}')
    raise ValueError
    

def extract_table_data(table, year, season_type='reg'):
    headers = []
    rows_pre = []
    thead = table.find_all('thead')
    if thead:
        for header_rows in thead:
            for row in header_rows.find_all('tr'):
                cells = [cell.text for cell in row.find_all(['th','td'])]
                headers.append(cells)
        
        for thead_element in thead:
            thead_element.decompose()

    for row in table.find_all('tr'):
        cells = [cell.text for cell in row.find_all(['th','td'])]
        rows_pre.append(cells)


    assert len(headers) == 1
    header = headers[0]
    num_columns = len(header)
    rows = [row for row in rows_pre if len(row) == num_columns]
    df = pd.DataFrame(rows,columns=header)
    exclude_columns = ['Tm']
    for col in df.columns:
        if col not in exclude_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    if 'T' not in df.columns:
        df['T'] = 0
    if 'PA' not in df.columns and 'Pts' in df.columns:
        df = df.rename(columns={'Pts': 'PA'})
    df['G'] = df.apply(lambda row: row['W'] + row['L'] + row['T'], axis=1)
    df['W-L%'] = df.apply(lambda row: round((row['W'] + 0.5*row['T']) / row['G'], 3), axis=1)
    df['PD/G'] = df.apply(lambda row: round(row['PD'] / row['G'], 2), axis=1)
    df['Plf'] = df['Tm'].apply(is_playoff_team)
    df['Div'] = df['Tm'].apply(is_division_winner)
    df['Yr'] = year
    df['Ssn'] = season_type
    df['Tm'] = df['Tm'].apply(match_team)
    return header, rows, df


def get_preseason_df(year):
    url = f"https://www.pro-football-reference.com/years/{year}/preseason.htm"
    table_ids = ['NFC', 'AFC']

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    combined_df = None
    for table_id in table_ids:
        table = soup.find('table', id=table_id)
        if table:
            _, _, df = extract_table_data(table, year, 'pre')
            if combined_df is None:
                combined_df = df
            else:
                combined_df = pd.concat([combined_df, df], axis=0, ignore_index=True)

    df_sorted = combined_df.sort_values(by='Tm').reset_index(drop=True)
    return df_sorted

def get_regseason_df(year):
    url = f"https://www.pro-football-reference.com/years/{year}/"
    table_ids = ['NFC', 'AFC']

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    combined_df = None
    for table_id in table_ids:
        table = soup.find('table', id=table_id)
        if table:
            header, rows, df = extract_table_data(table, year, 'reg')
            if combined_df is None:
                combined_df = df
            else:
                combined_df = pd.concat([combined_df, df], axis=0, ignore_index=True)

    df_sorted = combined_df.sort_values(by='Tm').reset_index(drop=True)
    return df_sorted


overall_df = None
for year in np.arange(1983,2024)[::-1]:
    print(f"YEAR {year}")
    if overall_df is None:
        overall_df = get_regseason_df(year)
    else:
        overall_df = pd.concat([overall_df, get_regseason_df(year)], axis=0, ignore_index=True)
    if year != 2020: #2020 has no preseason
        overall_df = pd.concat([overall_df, get_preseason_df(year)], axis=0, ignore_index=True) 

    overall_df.to_excel(f'pre_and_reg_season_stats_1983-2023.xlsx', index=False, sheet_name='Sheet1') #rewrite every year so if theres an error fetching data you don't lose all previous data
    time.sleep(5) #sleep to prevent getting throttled


