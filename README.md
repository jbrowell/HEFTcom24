# Hybrid Energy Forecasting and Trading Competition

This repository contains some basic utilities and an example to help teams get started with the Hybrid Energy Forecasting and Trading Competition. Full details of the competition can be found on the [IEEE DataPort](https://dx.doi.org/10.21227/5hn0-8091).

## Prepare your python environment

This example was developed using anaconda. You can use the file `environment.yml` create an environment with the same packages and version of Python. In anaconda prompt, run
```
conda env create -f environment.yml
conda activate comp23
```
to install all packages and dependencies, and activate the `comp23` environment.

## Download data

Historic data for use in the competition can be downloaded from the competition [IEEE DataPort page](https://dx.doi.org/10.21227/5hn0-8091) and should placed in the `data` folder.

More recent data can be downloaded via the competition API, which will be necessary to generate forecasts during the evaluation phase of the competition. Teams are advised to test this functionality early and automate submissions.

API documentation can be found on the [rebase.energy website](https://api.rebase.energy/challenges/redoc#tag/Data), and some basic wrappers are included in `comp_utils.py`.


## Utilities module

The python module `comp_utils.py` contains some useful functions for the competition, including

1. Set-up of authentication to access the competition API
2. Wrappers for the API endpoints to download the latest data
3. Functions to prepare and send submissions 

## Getting Started Example

An minimal example showing how to load and combine data, produce a forecasting model, and generate an competition submission is included in the jupyter notebook `Getting Started.ipynb`.

This example only uses a subset of data provided by the competition organisers. The following files are required:
```
data/dwd_icon_eu_hornsea_1_20200920_20230920.nc
data/dwd_icon_eu_pes10_20200920_20230920.nc
data/Energy_Data.csv
```

### Setting up your authentication

An API key will be sent to the email address used when registering for the competition. This key is linked to your team, and it is essential that you use it when submitting your entires. Do not share your API key!

Your API key should be stored in a text file called `team_key.txt` in the root directory of this repository. This file is listed in `.gitignore` and is therefore ignored by git. If you change the filename, make sure you add the new name to `.gitignore`.

## Submissions

During the competition period, daily submissions are required. Forecasts and market bids for the day-ahead must be submitted before gate closure of the day-ahead auction at 9:20AM UTC. Hence, automation is encouraged. Submission is via push API, documentation of which is available on the [rebase.energy website](https://api.rebase.energy/challenges/redoc#tag/Challenge/operation/post_submission_challenges__challenge_id__submit_post).

The python script `auto_submitter.py` provides an example of one way of setting this up. The script downloads new data, loads and runs models, and submits the resulting forecasts and market bid to the competition platform using the same approach as in `Getting Started.ipynb`. It can be run from the command line  
```
[...]\Getting Started> "C:\Users\[user name]\Anaconda3\envs\comp23\python.exe" auto_submitter.py
```
and will save a text file in the `logs/` directory containing the API response.

This process can be automated in many ways, and will depend on your operating system or cloud environment.

#### Windows Scheduler

Create a batch file `scheduled_task.bat` containing the following text (similar to the command above)
```
"C:\Users\[user name]\Anaconda3\envs\comp23\python.exe"
"[...]\Getting Started\auto_submitter.py"
pause
```
Navigate to thorough Control Panel to the Task Scheduler and schedule this batch file to be run each day in time to make your submission before the 9:20AM UTC deadline.