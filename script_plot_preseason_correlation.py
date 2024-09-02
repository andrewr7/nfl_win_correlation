"""

Preseason correlation plotting script. 
Written by reddit: u/geauxpackgo, github: andrewr7
Sep 1, 2024

"""

import numpy as np
import pandas as pd
import os

import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from scipy import stats
from scipy.signal import savgol_filter
from scipy.ndimage import gaussian_filter1d
import statsmodels.api as sm
from scipy.stats import pearsonr

np.set_printoptions(precision=5, suppress=True)

plot_folder = 'correlation_plots'
if not os.path.exists(plot_folder):
    os.makedirs(plot_folder)

# List of team names
team_names = [
    'Arizona Cardinals',
    'Atlanta Falcons',
    'Baltimore Ravens',
    'Buffalo Bills',
    'Carolina Panthers',
    'Chicago Bears',
    'Cincinnati Bengals',
    'Cleveland Browns',
    'Dallas Cowboys',
    'Denver Broncos',
    'Detroit Lions',
    'Green Bay Packers',
    'Houston Texans',
    'Indianapolis Colts',
    'Jacksonville Jaguars',
    'Kansas City Chiefs',
    'Las Vegas Raiders',
    'Los Angeles Chargers',
    'Los Angeles Rams',
    'Miami Dolphins',
    'Minnesota Vikings',
    'New England Patriots',
    'New Orleans Saints',
    'New York Giants',
    'New York Jets',
    'Philadelphia Eagles',
    'Pittsburgh Steelers',
    'San Francisco 49ers',
    'Seattle Seahawks',
    'Tampa Bay Buccaneers',
    'Tennessee Titans',
    'Washington Commanders'
]

# Sort the team names alphabetically
sorted_team_names = sorted(team_names)

# Create the dictionary with alphabetical index
team_index_dict = {team: index + 1 for index, team in enumerate(sorted_team_names)}

df = pd.read_excel('pre_and_reg_season_stats_1983-2023.xlsx', sheet_name='Sheet1')

year_dict = {}
for index, row in df.iterrows():
    if not row['Yr'] in year_dict:
        year_dict[row['Yr']] = {}
    if not row['Tm'] in year_dict[row['Yr']]:
        year_dict[row['Yr']][row['Tm']] = {'W-L%':[None, None], 'PD/G':[None, None], 'Plf':None, 'Div':None}
    if row['Ssn'] == 'pre':
        year_dict[row['Yr']][row['Tm']]['W-L%'][0] = row['W-L%']
        year_dict[row['Yr']][row['Tm']]['PD/G'][0] = row['PD/G']
    elif row['Ssn'] == 'reg':
        year_dict[row['Yr']][row['Tm']]['W-L%'][1] = row['W-L%']
        year_dict[row['Yr']][row['Tm']]['PD/G'][1] = row['PD/G']
        year_dict[row['Yr']][row['Tm']]['Plf'] = row['Plf']
        year_dict[row['Yr']][row['Tm']]['Div'] = row['Div']


## uncomment the split you're interested in
# splits = np.arange(1984,2024) #1 year splits
# splits = [1984, 1986, 1988, 1990, 1992, 1994, 1996, 1998, 2000, 2002, 2004, 2006, 2008, 2010, 2012, 2014, 2016, 2018, 2020, 2022, 2024] #2 year splits
# splits = [1984, 1987, 1990, 1993, 1996, 1999, 2002, 2005, 2008, 2011, 2014, 2017, 2020, 2024] #3 year splits
# splits = [1984, 1989, 1994, 1999, 2004, 2009, 2014, 2019, 2024] #5 year splits
# splits = [1984, 1994, 2004, 2014, 2024] #10 year splits
splits = [1984, 2004, 2024] #20 year splits
# splits = [1984,2024] #40 year splits (entire span of data)

splits_folder = f"{plot_folder}/split_range_{splits[1]-splits[0]}_years"
if not os.path.exists(splits_folder):
    os.makedirs(splits_folder)

trend_array = np.zeros((5,len(splits)))
num_clusters = 0
span = splits[-1] - splits[0]
for split_idx in range(len(splits)):
    first_year = splits[split_idx]
    if split_idx+1 < len(splits):
        last_year = splits[split_idx+1] - 1
    else:
        last_year = splits[split_idx]
    years_of_interest = np.arange(first_year,last_year+1)
    num_datapoints = 0
    for year in years_of_interest:
        if (not year in [2020]) and (year - 1 in year_dict) and year in year_dict:
                for team in year_dict[year]:
                    if (team in year_dict[year]) and (team in year_dict[year - 1]):
                        num_datapoints += 1

    if num_datapoints == 0:
        trend_array[:,split_idx] = None
        continue

    num_clusters += 1
    data_array = np.zeros((8,num_datapoints))
    index = 0
    years_printed = []
    for year in years_of_interest:
        if (not year in [2020]) and (year - 1 in year_dict) and year in year_dict:
                for team in year_dict[year]:
                    if (team in year_dict[year]) and (team in year_dict[year - 1]):
                        if not year in years_printed:
                            print(f"year {year}")
                        years_printed.append(year)
                        data_array[0,index] = year_dict[year - 1][team]['W-L%'][1] #last years win%
                        data_array[1,index] = year_dict[year - 1][team]['PD/G'][1] #last years PD/G
                        data_array[2,index] = year_dict[year][team]['W-L%'][0] #this preseason win%
                        data_array[3,index] = year_dict[year][team]['PD/G'][0] #this preseason PD/G
                        data_array[4,index] = year_dict[year][team]['W-L%'][1] #this season win%
                        data_array[5,index] = year_dict[year][team]['PD/G'][1] #this season PD/G
                        data_array[6,index] = year
                        data_array[7,index] = team_index_dict[team]
                        index += 1


    cov_matrix = np.cov(data_array)
    std_devs = np.sqrt(np.diag(cov_matrix))
    correlation_matrix = cov_matrix / np.outer(std_devs, std_devs)
    trend_array[0,split_idx] = correlation_matrix[0,4]
    trend_array[1,split_idx] = correlation_matrix[1,4]
    trend_array[2,split_idx] = correlation_matrix[2,4]
    trend_array[3,split_idx] = correlation_matrix[3,4]
    trend_array[4,split_idx] = last_year

    print(f'-----Range {first_year}-{last_year}-----')
    print(correlation_matrix[:-2,:-2])
    # continue #uncomment this to avoid plotting

    for y_idx in [4,5]:
        for x_idx in [0,1,2,3]:
            fig, ax = plt.subplots()

            if x_idx == 0:
                x_data_idx = 0; x_name = 'Prev Season Win%'
            if x_idx == 1:
                x_data_idx = 1; x_name = 'Prev Season Point Diff.'
            if x_idx == 2:
                x_data_idx = 2; x_name = 'Preseason Win%'
            if x_idx == 3:
                x_data_idx = 3; x_name = 'Preseason Point Diff.'
            if x_idx == 4:
                x_data_idx = 4; x_name = 'Win%'
            if x_idx == 5:
                x_data_idx = 5; x_name = 'Point Diff.'

            if y_idx == 0:
                y_data_idx = 0; y_name = 'Prev Season Win%'
            if y_idx == 1:
                y_data_idx = 1; y_name = 'Prev Season Point Diff.'
            if y_idx == 2:
                y_data_idx = 2; y_name = 'Preseason Win%'
            if y_idx == 3:
                y_data_idx = 3; y_name = 'Preseason Point Diff.'
            if y_idx == 4:
                y_data_idx = 4; y_name = 'Win%'
            if y_idx == 5:
                y_data_idx = 5; y_name = 'Point Diff.'

            x_arr = data_array[x_data_idx,:]
            y_arr = data_array[y_data_idx,:]

            r, p_value = pearsonr(x_arr, y_arr)
            if "Win" in y_name and ("Win" in x_name or "Diff" in x_name):
                print(f"{x_name} vs {y_name}")
                print("Pearson's r:", r)
                print("p-value:", p_value)

            ax.scatter(x_arr,y_arr, marker='o')
            correlation = np.correlate(x_arr, y_arr)
            ax.set_xlabel(x_name)
            ax.set_ylabel(y_name)
            title_first_line = f'{x_name} vs {y_name}\n{first_year}-{last_year} seasons'
            if first_year <= 2020 and last_year >= 2020:
                title_first_line += ' (excluding 2020)'
            whole_title = title_first_line + '\nCorrelation: ' + r"$\bf{{{x}}}$".format(x={round(correlation_matrix[x_data_idx,y_data_idx],4)})
            whole_title = whole_title + '\np-value: ' + r"$\bf{{{x}}}$".format(x={round(p_value,5)})
            ax.set_title(whole_title)
            if "Win%" in y_name:
                ax.yaxis.set_major_locator(MultipleLocator(0.25))
                ax.set_ylim([0,1.0])
            if "Win%" in x_name:
                ax.xaxis.set_major_locator(MultipleLocator(0.25))
                ax.set_xlim([0,1.0])
            ax.grid(True, which='both', linestyle='--', linewidth=0.7)
            plt.tight_layout()
            fig.savefig(f'{splits_folder}/{x_name} v {y_name} {first_year}-{last_year}.png', format='png')
            # plt.show() #if you want to see each plot before its erased uncomment this
            plt.close('all')


# Compute the moving average
def moving_average(data, window_size):
    return np.convolve(data, np.ones(window_size)/window_size, mode='valid')

fig, ax = plt.subplots()
x_array = trend_array[4,:]
for y_array, label, color in [(trend_array[1,:],'Prev Season Point Diff','b'),(trend_array[0,:],'Prev Season win%','g'),(trend_array[3,:],'Preseason Point Diff','y'),(trend_array[2,:],'Preseason win%','r'),]:
    # ax.plot(x_array,y_array, marker='o', linestyle='None', label=label, color=color, markersize=3) #get rid of line if you're going to plot a curve fit separately
    ax.plot(x_array,y_array, marker='o', linestyle='dashed', label=label, color=color, markersize=3)

    ## uncomment this section to plot a curve fit or de-noised curve if you want
    # mask = ~np.isnan(x_array) & ~np.isnan(y_array)
    # x_filtered = x_array[mask]
    # y_filtered = y_array[mask]
    # x = x_filtered
    # y = y_filtered


    # coefficients = np.polyfit(x_filtered, y_filtered, 1)
    # polynomial = np.poly1d(coefficients)
    # polynomial_x = np.linspace(min(x_filtered), max(x_filtered), 100)
    # polynomial_y = polynomial(polynomial_x)
    # trend_x = polynomial_x
    # trend_y = polynomial_y


    # # Fit a linear trend line
    # slope, intercept, r_value, p_value, std_err = stats.linregress(x_filtered, y_filtered)
    # # Create a line for the fitted line
    # polynomial_x = np.linspace(min(x_filtered), max(x_filtered), 100)
    # polynomial_y = slope * polynomial_x + intercept
    # trend_x = polynomial_x
    # trend_y = polynomial_y

    # window_size = 5
    # y_smoothed = moving_average(y, window_size)
    # x_smoothed = x[(window_size-1)//2:-(window_size-1)//2]
    # trend_x = x_smoothed
    # trend_y = y_smoothed


    # window_size = 3  # window size must be odd
    # poly_order = 2    # polynomial order
    # y_smoothed = savgol_filter(y, window_size, poly_order)
    # trend_x = x
    # trend_y = y_smoothed


    # # Apply Gaussian filter
    # sigma = 1  # Standard deviation of the Gaussian kernel
    # y_smoothed = gaussian_filter1d(y, sigma)
    # trend_x = x
    # trend_y = y_smoothed


    # # Apply LOWESS smoothing
    # lowess = sm.nonparametric.lowess
    # y_smoothed = lowess(y, x, frac=0.3)[:, 1]  # frac is the smoothing parameter
    # trend_x = x
    # trend_y = y_smoothed

    # ax.plot(trend_x,trend_y, linestyle='dashed', label=f"{label} trend line", color=color)


ax.set_ylabel('Correlation to Win%')
ax.set_xlabel('Year (endpoint of cluster)')
ax.legend()
year_cluster = int(round(span/num_clusters))
ax.set_title(f'Correlation to Win% over time\n{year_cluster}-year clusters')

ax.yaxis.set_major_locator(MultipleLocator(0.1))
x_ticks = x_array[~np.isnan(x_array)]
if len(x_ticks) < 15:
    ax.set_xticks(ticks=x_ticks)
ax.grid(True, which='both', axis='y', linestyle='--', linewidth=0.7)
plt.tight_layout()
fig.savefig(f'{splits_folder}/correlation_v_time_{year_cluster}.png', format='png')
plt.show()
plt.close('all')

