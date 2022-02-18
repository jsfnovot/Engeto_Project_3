import csv
import sys
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup


def request_bs4(url: str) -> BeautifulSoup:
    try:
        req = requests.get(url)
    except Exception as ex:
        print(f"An error occurred: {ex}.")
        sys.exit()
    return BeautifulSoup(req.text, "html.parser")


def check_args() -> bool:
    if len(sys.argv) != 3:
        print("Two arguments expected, can't run scraper.")
        return False
    elif "https://volby.cz/pls/ps2017nss/" not in sys.argv[1]:
        print("First argument should be a valid district URL.")
        return False
    else:
        return True


def check_file_name(name, soup):
    """
    checking if name contains a name of district and suffix ".csv"
    """
    district = soup.find(text=lambda text: text and 'Okres:' in text).split('Okres: ')[1].replace('\n', '')
    if district.lower() not in name.lower() or ".csv" not in name:
        print("File name must contain a district name and .csv suffix.\n"
              f"Renaming to '{district.lower()}.csv'")
        file = f"{district.lower()}.csv"
        return str(file)
    else:
        return name.lower()


def get_town_codes(soup: BeautifulSoup) -> list:
    """
    returns lists of town direct urls in chosen district
    """
    codes = []
    for x in soup.find_all("td", class_="cislo"):
        for a in x.find_all("a"):
            codes.append(int(a.get_text()))
    return codes


def get_town_urls(soup: BeautifulSoup, url: str) -> list:
    """
    returns lists of all town codes in chosen district
    """
    base_url = url.split("ps3")[0]
    urls = []
    for x in soup.find_all("td", class_="cislo"):
        for a in x.find_all("a"):
            urls.append(urljoin(base_url, a.get("href")))
    if urls:
        return urls
    else:
        print(f"An error occurred.")
        sys.exit()


def get_political_parties(soup: BeautifulSoup) -> list:
    """
    returns list of all parties which participated the elections
    """
    parties = []
    i = 1
    while soup.find_all("td", headers=f"t{i}sb2"):
        for party in soup.find_all("td", headers=f"t{i}sb2"):
            parties.append((party.get_text()))
        i += 1
    return parties


def get_town_details(town_codes: list, town_urls: list) -> list:
    """
    returns list of election details from every town in chosen district
    """
    rows = []
    for town_code, url in zip(town_codes, town_urls):
        soup_3 = request_bs4(url)

        town_name = soup_3.find(text=lambda text: text and "Obec:" in text).split("Obec: ")[1].replace("\n", "")
        registered = soup_3.find("td", headers="sa2").get_text().replace("\xa0", "")
        envelopes = soup_3.find("td", headers="sa3").get_text().replace("\xa0", "")
        valid_votes = soup_3.find("td", headers="sa6").get_text().replace("\xa0", "")
        row = [town_code, town_name, registered, envelopes, valid_votes]

        i = 1
        while soup_3.find_all("td", headers=f"t{i}sb3"):
            for votes in soup_3.find_all("td", headers=f"t{i}sb3"):
                row.append(votes.get_text().replace("\xa0", ""))
            i += 1
        rows.append(row)
    return rows


def make_header(soup: BeautifulSoup) -> list:
    """
    returns list with header and parties names
    """
    header = ["Town code", "Town name", "Registered", "Envelopes", "Valid votes"]
    for party in get_political_parties(soup):
        header.append(party)
    return header


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
        sys.exit()
    default_url = sys.argv[1]
    print(f"Downloading data from selected URL: {default_url}")
    soup_1 = request_bs4(default_url)
    file_name = check_file_name(sys.argv[2], soup_1)

    codes = get_town_codes(soup_1)
    urls = get_town_urls(soup_1, default_url)

    soup_2 = request_bs4(urls[0])

    csv_header = make_header(soup_2)
    csv_rows = votes_to_int(get_town_details(codes, urls))

    print(f"Saving data in file: {file_name}")
    write_to_csv(file_name, csv_header, csv_rows)


if __name__ == "__main__":
    scraper()
