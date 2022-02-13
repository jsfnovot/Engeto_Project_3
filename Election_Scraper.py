import csv
import sys
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup


def request_bs4(url: str) -> BeautifulSoup:
    return BeautifulSoup(requests.get(url).text, "html.parser")


def check_args() -> bool:
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


def get_town_codes(soup: BeautifulSoup) -> list:
    """
    filtering data from soup str,
    returns lists of town direct urls
    """
    codes = []
    for x in soup.find_all("td", class_="cislo"):
        for a in x.find_all("a"):
            codes.append(int(a.get_text()))
    return codes


def get_town_urls(soup: BeautifulSoup, url: str) -> list:
    """
    filtering data from soup str,
    returns lists of town codes
    """
    base_url = url.split("ps3")[0]
    urls = []
    for x in soup.find_all("td", class_="cislo"):
        for a in x.find_all("a"):
            urls.append(urljoin(base_url, a.get("href")))
    return urls


def get_political_parties(soup: BeautifulSoup) -> list:
    """
    filtering data from soup str,
    returns list of all parties which participated the elections
    """
    parties = []
    i = 1
    while soup.find_all("td", headers=f"t{i}sb2"):
        for party in soup.find_all("td", headers=f"t{i}sb2"):
            parties.append((party.get_text()))
        i += 1
    return parties


def votes_to_int(lists_in_list: list) -> list:
    """
    changing scraped votes data from str to int
    """
    for e_list in lists_in_list:
        e_list[2:] = list(map(int, e_list[2:]))
    return lists_in_list


def write_to_csv(file: str, header: list, details: list) -> csv:
    """
    csv writing function, 3 arguments required:
    > desired file name
    > list with header and parties names
    > list of scraped election data
    """
    with open(file, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(header)
        writer.writerows(details)


def scraper():
    if not check_args():
        quit()
    default_url = sys.argv[1]
    file_name = sys.argv[2]
    # default_url = "https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2102"
    # file_name = "vysledky_beroun.csv"
    print(f"Downloading data from selected URL: {default_url}")
    print(f"Saving data in file: {file_name}")

    soup_1 = request_bs4(default_url)
    codes = get_town_codes(soup_1)
    urls = get_town_urls(soup_1, default_url)

    soup_2 = request_bs4(urls[0])

    csv_header = ["Town code", "Town name", "Registered", "Envelopes", "Valid votes"]
    for party in get_political_parties(soup_2):
        csv_header.append(party)

    rows = []
    for code, url in zip(codes, urls):
        soup_3 = request_bs4(url)

        town_name = soup_3.find(text=lambda text: text and "Obec:" in text).split("Obec: ")[1].replace("\n", "")
        registered = soup_3.find("td", headers="sa2").get_text().replace("\xa0", "")
        envelopes = soup_3.find("td", headers="sa3").get_text().replace("\xa0", "")
        valid_votes = soup_3.find("td", headers="sa6").get_text().replace("\xa0", "")
        row = [code, town_name, registered, envelopes, valid_votes]

        i = 1
        while soup_3.find_all("td", headers=f"t{i}sb3"):
            for votes in soup_3.find_all("td", headers=f"t{i}sb3"):
                row.append(votes.get_text().replace("\xa0", ""))
            i += 1
        rows.append(row)

    csv_rows = votes_to_int(rows)

    write_to_csv(file_name, csv_header, csv_rows)


if __name__ == "__main__":
    scraper()
    print("Quitting Election_Scraper...")
