What's inside?
1. Data Collection (Building my own dataset)
Instead of just downloading a ready-made Kaggle dataset, I wanted to build my own from scratch. I wrote custom Python scripts (like vericek.py) using spotipy and the Spotify Web API to pull acoustic metadata (danceability, energy, loudness, valence, etc.) for thousands of tracks. Note: I also ended up using redis for caching to handle the API request limits smoothly.

2. Data Cleaning
Raw API data is usually pretty messy. I used pandas and numpy to drop duplicates, handle missing values, and structure everything into clean .csv files so I could actually run tests on them.

3. Statistical Analysis
This is where the math happens. I used scipy and statsmodels to run regression models and post-hoc tests. The goal was to prove if the differences between the subgenres were statistically significant, and to see which acoustic features correlate the most with the "popularity" metric. I also used matplotlib to visualize the results.

4. The Final Report
I wrote the final project report using LaTeX (because formatting regression tables in Word is a nightmare). You can find the .tex files and the final PDF in the docs/ folder.

Tech Stack & Libraries I Used
Data Wrangling: pandas, numpy

API & Scraping: spotipy, requests

Math & Stats: scipy, statsmodels

Data Viz: matplotlib, pillow

Other: redis (for queuing/caching during data extraction)

Folder Structure
Plaintext
├── data/       # My custom raw and cleaned Spotify datasets (.csv)
├── docs/       # The final LaTeX report and exported plots
├── src/        # All my Python scripts for fetching, cleaning, and analyzing the data
└── requirements.txt  # List of dependencies to run the code

How to run it
Clone this repo to your local machine.

Install the required libraries:

Bash
pip install -r requirements.txt
You'll need your own Spotify API credentials (Client ID and Secret). Set them up as environment variables, and you should be good to run the scripts in the src/ folder!

Disclaimer: This is a student project created for academic and portfolio purposes to practice data pipelines and statistical analysis.


