# nba_allstar
The purpose of this project is to predict an NBA player's future success based on past performance. The metric I used to measure success is whether an player became an allstar or not the following year. The project has undergone a few different changes and so I have consolidated all my work into this repo. The project is laid out as follows:

## Original: contains the first build of this model
`capstone-1-final-report.ipynb`
- Full overview of entire project from start to finish including Data Wrangling, Exploratory Data Analysis, Model Selection, Model Comparison, and Future Steps and Improvements.

`data-storytelling.ipynb`
- Notebook outlining my plan for the project and how I would approach exploring the data.

`EDA.ipynb`
- Notebook displaying my process of Exploratory Data Analysis. This was used to better understand what direction I should take my final investigation.

`indepth-analysis.ipynb`
- Notebook with my entire In-Depth Analysis process. This involved testing multiple Machine Learning algorithms as well as Feature Selection and Model Comparisons.

`scrape-basketball-reference.ipynb`
- Jupyter notebook outlining the entire scraping process. This produces the raw data that I used in the report and that was cleaned using manual work as well as `cleaning.py`

`all-stats-clean.csv`
- Cleaned data used for final analysis

`all-stats-sample.csv`
- Example of format raw data was in before cleaning

`cleaning.py`
- Code used to clean the dataset programmatically. This performed a great deal of datatype conversions and adjustments needed due to anomalies in the data caused by players missing seasons or midseason trades.

`scrape_bask_ref.py`
- Script that can be run to scrape data directly from www.basketball-reference.com and export it to a .csv file.

## Update:
### bball_code
- `__init__.py'`
- `data_grabbing.py`
### Data
- `all_season.csv`
- `cleaned_data.csv`
- `model_data.csv`
- `players.txt`
- `scaled_model_data.csv`
- `super_advanced.csv`
### Graveyard
- `redo-scrape.ipynb`
- `scrape-hundos.ipynb`
### notebooks
- `data_cleaning.ipynb`
- `EDA.ipynb`
- `get_allstars.ipynb`
- `grab_players.ipynb`
- `model_building.ipynb`
- `scrape-advanced-stats.ipynb`
