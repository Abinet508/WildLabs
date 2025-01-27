import os
import time
import requests
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
from multiprocessing.pool import ThreadPool

class WildLabsScraper:
    """
    This class is used to scrape data from the WildLabs website.
    """
    def __init__(self):
        """
        This function initializes the class.
        """
        self.cookies = {
            'cf_clearance': 'tl1AxuM6miAxP1kxmFlzc534Z.TYWWgMxsvfWeWRaMQ-1737966907-1.2.1.1-jEYaE9y_dP4gkZKR2e_iwohu1IH1N8QcWtrxkVLObZWqJF4sNGTsyDZoxy7OeSdMD1YD4y_dqxaXfkv.TsUHu5xuC4bNviAXTzQ5RwTe9C9l8EwxiwxplzlpqfnPSP.bXcdSd6GkzdV0dB3zLKm_o5hwLkSHDvCq4ABpGyMsfMa3z1EOolIrkt.xz9yYIe26ipWmoE4nGQ.BhIsbg84d9fTjmwPX6fcSmc9Fw4HtZxMpahYUHE0ymxH4mgSZJvhAs5zeLivZ_RkcPuJIxYv3GRNajYQxNzx_NwjpEyRHdZ4',
        }

        self.headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'accept-language': 'en-US,en;q=0.8',
            'priority': 'u=0, i',
            'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Brave";v="132"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'sec-gpc': '1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
        }

    def get_last_page(self, page=1, first_page=False):
        """
        This function scrapes the last page of the members page.

        Args:
            page (int, optional): The page number. Defaults to 1.
            first_page (bool, optional): If True, returns the last page number. Defaults to False.

        Returns:
            (int, list): The last page number or the list of members.
        """
        params = {
            'page': page,
        }
        while True:
            try:
                response = requests.get('https://wildlabs.net/members', params=params, cookies=self.cookies, headers=self.headers)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    if first_page:
                        last_page = int(soup.find('a', title="Go to last page").get('href').split('=')[-1])
                        return last_page
                    else:
                        main = soup.find('div', class_='fm__cards--long base-grid xl:justify-items-start')
                        members = main.find_all('article')
                        members = [{"LINK":f"https://wildlabs.net{member.find('a').get('href')}"} for member in members]
                        results = []
                        with ThreadPool(len(members)) as pool:
                            results = pool.map(self.get_member_info, members)
                        results = [result for result in results if result]
                        return results
                else:
                    time.sleep(5)
                    continue
            except Exception as e:
                print(e)
                time.sleep(5)
                
    def get_member_info(self, member):
        """
        This function scrapes the member information from the member page.

        Args:
            member (dict): The member dictionary containing the member link.

        Returns:
            dict: The member dictionary containing the member information.
        """
        while True:
            try:
                response = requests.get(member['LINK'], cookies=self.cookies, headers=self.headers)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    member_name = soup.find('h2', id='usernameField')
                    if member_name:
                        member['MEMBER NAME'] = member_name.text.strip()
                    userpic = soup.find('img', id='userPic')
                    member['USER PIC'] = None
                    if userpic:
                        member['USER PIC'] = f"https://wildlabs.net{userpic.get('src')}"
                    details = soup.find('ul', class_='user__details')
                    member['USERNAME'] = None
                    if details:
                        member['USERNAME'] = details.find_all('li')[0].text.strip()
                        
                    organisation = soup.find('a', class_='user__organisation_link')
                    member['ORGANISATION'] = []
                    if organisation:
                        member['ORGANISATION'] =[{"LINK":f"https://wildlabs.net{organisation.get('href')}","NAME":organisation.text.strip()}]
                    bio = soup.find('p', id='biographyField')
                    member['BIO'] = None
                    if bio:
                        member['BIO'] = bio.text.strip()
                    member['LOCATION'] = None
                    country = soup.find('ul', id='country_list_items')
                    if country:
                        member['LOCATION'] = country.find('a').text.strip()
                    groups = soup.find('ul', class_='relatedGroups__list')
                    member['GROUPS'] = []
                    if groups:
                        Links = []
                        for group in groups.find_all('a'):
                            Links.append({"LINK":group.get('href'), "NAME":group.text.strip()})
                        member['GROUPS'] = Links
                    socials = soup.find('div', class_='userSidebar__socialMedia')
                    member['SOCIALS'] = []
                    if socials:
                        Links = []
                        ul = socials.find('ul')
                        for social in ul.find_all('a'):
                            Links.append({"LINK":social.get('href'), "NAME":social.get('title')})
                        member['SOCIALS'] = Links
                    langs = soup.find('ul', id='lang_list_items')
                    member['LANGS'] = []
                    if langs:
                        Links = []
                        for lang in langs.find_all('a'):
                            Links.append(lang.text.strip())
                        member['LANGS'] = Links
                    badges = soup.find('div', class_='userSidebar__badges')
                    member['BADGES'] = []
                    if badges:
                        Links = []
                        for badge in badges.find_all('img'):
                            Links.append({"LINK":f"https://wildlabs.net{badge.get('src')}", "NAME":badge.get('alt')})
                        member['BADGES'] = Links
                    return member   
                else:
                    time.sleep(5)
                    continue
            except Exception as e:
                print(e)
                time.sleep(5)
                
if __name__ == "__main__":
    scraper = WildLabsScraper()
    last_page = scraper.get_last_page(first_page=True)
    members = []
    with ThreadPool(10) as pool:
        for result in tqdm(pool.imap_unordered(scraper.get_last_page, range(1, last_page+1)), total=last_page, desc='SCRAPING MEMBERS...',colour='green', smoothing=0.1, position=0, leave=True):
            members.extend(result)
    df = pd.DataFrame(members)
    df.to_excel(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wildlabs.xlsx'), index=False)