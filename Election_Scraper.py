import csv
import sys
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup


def request_bs4(url):
    return BeautifulSoup(requests.get(url).text, "html.parser")


def check_args():
    if len(sys.argv) != 3:
        print("Two arguments expected, can't run scraper.")
        return False
    elif "https://volby.cz/pls/ps2017nss/" not in sys.argv[1]:
        print("First argument should be URL, second argument name of csv file.")
        return False
    elif ".csv" not in sys.argv[2]:
        print("Second argument should be a name of csv file.")
        return False
    else:
        return True


def town_details(soup, url):
    """
    filtering data from soup str
    returns lists of direct urls
    and codes of all towns
    """
    base_url = url.split("ps3")[0]
    urls = []
    codes = []
    for x in soup.find_all("td", class_="cislo"):
        for a in x.find_all("a"):
            urls.append(urljoin(base_url, a.get("href")))
            codes.append(int(a.get_text()))
    return urls, codes


def get_political_parties(soup):
    """
    filtering data from soup str
    returns list of all parties
    which participated the elections
    """
    parties = []
    a = 1
    while soup.find_all("td", headers=f"t{a}sb2"):
        for party in soup.find_all("td", headers=f"t{a}sb2"):
            parties.append((party.get_text()))
        a += 1
    return parties


def votes_to_int(lists_in_list):
    """
    changing scraped votes data
    from str to int
    """
    for e_list in lists_in_list:
        e_list[2:] = list(map(int, e_list[2:]))
    return lists_in_list


def write_to_csv(file, header, details):
    """
    csv writing function, 3 arguments required
    > file name
    > list with header and parties names
    > list of scraped election data
    """
    with open(file, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(header)
        writer.writerows(details)


def scraper():
    # if not check_args():
    #     quit()
    # # default_url = sys.argv[1]
    # # file_name = sys.argv[2]
    default_url = "https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2102"
    file_name = "vysledky_beroun.csv"
    print(f"Downloading data from selected URL: {default_url}")
    print(f"Saving data in file: {file_name}")
    print("Quitting Election_Scraper...")

    soup_1 = request_bs4(default_url)
    urls = town_details(soup_1, default_url)[0]
    codes = town_details(soup_1, default_url)[1]

    soup_2 = request_bs4(urls[0])

    csv_header = ["Town code", "Town name", "Registered", "Envelopes", "Valid votes"]
    for x in get_political_parties(soup_2):
        csv_header.append(x)

    rows = []
    for code, url in zip(codes, urls):
        soup_3 = request_bs4(url)

        town = soup_3.find(text=lambda text: text and "Obec:" in text).split("Obec: ")[1].replace("\n", "")
        registered = soup_3.find("td", headers="sa2").get_text().replace("\xa0", "")
        envelopes = soup_3.find("td", headers="sa3").get_text().replace("\xa0", "")
        valid = soup_3.find("td", headers="sa6").get_text().replace("\xa0", "")
        row = [code, town, registered, envelopes, valid]

        a = 1
        while soup_3.find_all("td", headers=f"t{a}sb3"):
            for votes in soup_3.find_all("td", headers=f"t{a}sb3"):
                row.append(votes.get_text().replace("\xa0", ""))
            a += 1
        rows.append(row)
    csv_rows = votes_to_int(rows)
    write_to_csv(file_name, csv_header, csv_rows)


if __name__ == "__main__":
    scraper()
