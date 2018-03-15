# Twitter Bubble Chart

Project to create a Bubble Chart using D3JS from a CSV file generated from the Twitter API.

### How to install & Run
1. Download & Install python 3.6.3: https://www.python.org/downloads/.
2. `cd` into this repository and install the project dependencies by running: `pip install -r requirements.txt`.
3. Navigate to the twitter_datamining directory and run: `python generate_csv_files.py -W <keyword> -n <number>` to generate the csv file. The keyword will be used by the Twitter search API and the number will indicate how many tweets you want to pull from each account.
3. Start the server by running: `python -m http.server`.
4. Navigate to the following URL: http://localhost:8000.
