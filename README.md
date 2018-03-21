# Twitter Bubble Chart

Project to create Bubble Charts using D3js from csv files generated from the Twitter API.

### How to install & Run
1. Download & Install python 3.6.3: https://www.python.org/downloads/.
2. `cd` into this repository and install the project dependencies by running: `pip install -r requirements.txt`.
3. To generate the csv files `cd` into the twitter_datamining directory and run: `python generate_csv_files.py -W <keyword> -n <number>`. The `keyword` will be used by the Twitter search API and the `number` will indicate how many tweets you want to pull from each account.
4. Go to the root folder of the project and start the server by running: `python -m http.server`.
5. Use your web browser and navigate to the following URL: http://localhost:8000.
