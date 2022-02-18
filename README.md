Script for scraping data of Czech parlament elections of 2017.

External packages needed to run the script can be installed using following command: $ pip install -r requirements.txt

How it works:
You have to choose a district from this page (https://volby.cz/pls/ps2017nss/ps3?xjazyk=CZ) by pressing "X" next to it and get it's URL.

Script requires two arguments:
1) URL of district as mentioned above
2) Name of .csv file in which you want to export the data (name must contain a desired district name and .csv suffix)

Following command can be used to get a csv file with same result as you can see in this repository:

python3 Election_Scraper.py "https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2102" "beroun.csv"
