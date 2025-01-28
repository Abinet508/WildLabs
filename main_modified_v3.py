import json
import re
import time
from tqdm import tqdm
import pandas as pd
from bs4 import BeautifulSoup
import requests
import os
from thefuzz import fuzz
from multiprocessing.pool import ThreadPool
from urllib.parse import quote_plus, urlparse
import pathlib

class MultiUrlScraper:
    def __init__(self):
        self.base_dir = pathlib.Path(__file__).parent.resolve()
        self.results_dir = self.base_dir / "results"
        self.results_dir.mkdir(exist_ok=True)
        
        self.session = requests.Session()
        self.headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'accept-language': 'en-US,en;q=0.9',
            'priority': 'u=0, i',
            'referer': 'https://www.bing.com/search?q=Thiago+Sanna+Freire+Silva+%2B+%5BEMAIL%5D&form=QBLH&sp=-1&ghc=1&lq=0&pq=thiago+sanna+freire+silva+%2B+%5Bemail%5D&sc=9-35&qs=n&sk=&cvid=466CDFC74AB5452D81B4BFBD79E23FFD&ghsh=0&ghacc=0&ghpl=',
            'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Brave";v="132"',
            'sec-ch-ua-arch': '"x86"',
            'sec-ch-ua-bitness': '"64"',
            'sec-ch-ua-full-version-list': '"Not A(Brand";v="8.0.0.0", "Chromium";v="132.0.0.0", "Brave";v="132.0.0.0"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-model': '""',
            'sec-ch-ua-platform': '"Windows"',
            'sec-ch-ua-platform-version': '"15.0.0"',
            'sec-fetch-dest': 'iframe',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'sec-gpc': '1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
        }
        self.session.headers.update(self.headers)
        
        # Initialize dynamic cookies (example structure - should be updated dynamically)
        self.session.cookies.update({
            'MUID': '3C598660B39A6004014D9300B27261D8',
            'MUIDB': '3C598660B39A6004014D9300B27261D8',
            '_EDGE_V': '1',
            'SRCHD': 'AF=NOFORM',
            'SRCHUID': 'V=2&GUID=D827BFA743164959AFF7AED15BC94EDE&dmnchg=1',
            'ak_bmsc': '00EDABA85172568145DA3F0CB3607EA8~000000000000000000000000000000~YAAQhXQQAgprcmqUAQAA4LKMpxo8It10ZUS6nuuEypZVDEy/9kYHdt4MzZ05kPujpsJysj2k0XRm6fGxjzRinLIqsIqdFf1TAAJMqmoAhjAEVH6c5QV5xPfWjeFCml1PvKAS911JQGTwcEFHHOUij8Qacob/a5nVdQISOYejBtw4N4BTr2p40HNrkhLi5LP1LKW2WNfrTdBSNHVTAlzc7YmHBbdDfiD2XfVMErx7Z0pscaZCmQkQsleicdkERS5Szb+CrZI3Mrve8o9hktv8+VSwgKsxNhp55NWZxgy1GYVbrxcot/npr4vubRt1kDk7aV1uvUNEb10K9JkS3dNZwbHu+bEAxA7z957/ZSDEbfbNOhpeTL/wo6EHQ+tHS42oC4fZliQKI3HnTeOz/yU2kgl/tiFY6g==',
            '_EDGE_S': 'SID=024B86503B9B69F607F493D13A816838&mkt=am-et',
            '_UR': 'QS=0&TQS=0&Pn=0',
            '_HPVN': 'CS=eyJQbiI6eyJDbiI6MSwiU3QiOjAsIlFzIjowLCJQcm9kIjoiUCJ9LCJTYyI6eyJDbiI6MSwiU3QiOjAsIlFzIjowLCJQcm9kIjoiSCJ9LCJReiI6eyJDbiI6MSwiU3QiOjAsIlFzIjowLCJQcm9kIjoiVCJ9LCJBcCI6dHJ1ZSwiTXV0ZSI6dHJ1ZSwiTGFkIjoiMjAyNS0wMS0yN1QwMDowMDowMFoiLCJJb3RkIjowLCJHd2IiOjAsIlRucyI6MCwiRGZ0IjpudWxsLCJNdnMiOjAsIkZsdCI6MCwiSW1wIjoyLCJUb2JuIjowfQ==',
            '_Rwho': 'u=d&ts=2025-01-27',
            'ipv6': 'hit=1737981405186&t=6',
            'ANON': 'A=DA71FB82EE40A14D7C53F174FFFFFFFF&E=1ec2&W=1',
            'NAP': 'V=1.9&E=1e68&C=y33vu5yv7jm37msNbG7c6HFiC4t15n8iXLnOFbAcvMLT4pS8Cu05pQ&W=1',
            'PPLState': '1',
            'KievRPSSecAuth': 'FABqBBRaTOJILtFsMkpLVWSG6AN6C/svRwNmAAAEgAAACJBGVS6HwqeTKARueVBXcSiU3FUrMg5D4BhJkzJeNd3T8g+xhwYRnMU4VA9hHOIdfDFaSEklFnfMqZIN+qwGjW03hhMgQZkST1H0NfUKwmCHGeRJPR73yGckWeah1HrbYzOHQJme9GguLqLorYEdI+ib8Bi8c/Qfq2aZsZ5Y2CiWRD+FWWFUmMvmeVrtSmYOds38jibgQjDvpffhcdZ5QPLnl+emyOyy/rLnyp+uLgEJheDhtZ8uZyQsGka4P6Q60NARVeto8QemzZssESl/aaiWMomG5I8EzKoFgp/wCXXgCExVAZgLax8sDmkbnpNMQ2h8E/c+bKkTggzUI3TTpCGBqEHcUf6OELyZtYEYjGfpWnMchiupg4fxVMb1p/1uGC3yBwi1Mvq8fqc036fttNsZfB6dRVPkpxjVzTgYl1Bd6VFVOCKPSi9+CEqvc67mZXO1vUIVCspG9Hh55saMP7vOinQM6cG6z35uCtartDrE6aPZg/9Q6XLNwwrzBAVLoOUnD1X0OFcyd4Q8kaGDY/lYgDRCGkDb1yxBQFbLhBYRbH8mRKDJSZvpjAE6bQuvMZvcP0HQDdg3A9s98XkLDkPj5JxEp8NZeM/sJ1+LeGoH/RMWwVK4WFAyR8Jzcem/O4QCSGV5c8GZkv/ystrrUWtrNaqdbnO6/gzOgGTCZpqlhQJPRqTdQjrG+GCKAi8XFspFdebK3OVriEhOVqLJi1fr813DrM4WPzDqNNPNqWVMtMn/vSA1lyB8S9I662nXiOyHTJLeJ9ua61a4tMCa/+znPkQwYTrjI76uXRA5bLc+EcZsOGFPLhMoyr6z4Vr6sId7ldk3MLc3wzzN1MrrWcxRM6GMlUFL0Q/iCrTBvqLHkAqXChCL4cfsynwrFF0P32SStAmisDZFvVqwuCdGHowdMVZkI8hK0t4jy8l1q/vowCbTzeVeeoiZ2SAOJ8GRNxIVhT4hWJypx51WmxU+nFskoolc5DoT1I1/CaY71tJY69JCvZhsTVgJ9+xzLSRcNddBlljvRI4IZLtHKdXcbzaD/X8qpiPk2wQhYKxV3q2HU2yUGI+aCsNwG5MaHgNlzRiPlsVGCDAdxrXZ6990+wnaB+7qUMXC9xc56XBswLNSpiVa6QQ46O5Oh4PKrNLc/7t3qad0iRzbBbhV3UQ9XtlOzNWG1ZDc08s/mQ9TBy6xeZfIBw0igXh3t4gC5Qb+kJSqTfZYPbxlECeu9LfW65YGoWEHCKJ9Gmh60ms0vnoIrbe7O0H+E6Ntb+L3gq9cK8UoFauN7+Vmh/9vqCJHBd1oiQaH2B25OI82jfBI5UCHzD0w2Df8PrgKZ8rOFZQdQDgmPZ8cfqWku/pBRAkufoCjpWH0iJgM1W320c3Dg1/kpsx4JAbrYJ98DTHw8wP5MKmLDlsAAu9blUtfJKUUZ/T8/RQAY8Uoevz/p98rkgL+ZtFp7PH3z6Y=',
            '_U': '1X-cdUErS_LczY43CYjoVFmIiElSba1kApzyJ9jRqvUq-7Wp6ZEld5TU1gr_hFQpsi6FV6qsd7BtfbkYFzN60NhCu6sNmiNVfKW6iKApbR93CWZHzpTlFMUV5xr0E6E0FjqJvT4Av5XzaK-z9XcLGbf0ZUtSDz6-6oHwy66p0nmVmDSQyrmqCbew-4qcj3q-CStqP9fdIGdjhSxCdpQMB-Q',
            'WLS': 'C=aab2c68f3b2a3271&N=Abinet',
            'SRCHUSR': 'DOB=20250127&T=1737977803000&POEX=W',
            'WLID': 'wm9DVeqsn7dSINyvREXWGpv4DaN9tHvFHQM0tcFlk45M0e4Wgb3bHf11Ma6siVcrH8TbtinE/K29/qfURLgYlCaEyDlLt0CaUC6l5+UWQvM=',
            'USRLOC': 'HS=1&ELOC=LAT=9.05068302154541|LON=38.76408004760742|N=Addis%20Ababa%2C%20Addis%20Ababa|ELT=1|',
            '_SS': 'SID=024B86503B9B69F607F493D13A816838&R=1319&RB=1319&GB=0&RG=0&RP=0',
            '_RwBf': 'r=1&ilt=2&ihpd=1&ispd=0&rc=1319&rb=1319&gb=0&rg=0&pc=0&mtu=0&rbb=0.0&g=0&cid=&clo=0&v=2&l=2025-01-27T08:00:00.0000000Z&lft=0001-01-01T00:00:00.0000000&aof=0&ard=0001-01-01T00:00:00.0000000&rwdbt=1696241709&rwflt=1694759874&rwaul2=0&o=0&p=EdgeCMQ1&c=MY01XA&t=7804&s=2022-04-02T18:03:59.1716746+00:00&ts=2025-01-27T11:37:01.3032820+00:00&rwred=0&wls=2&wlb=0&wle=0&ccp=2&cpt=0&lka=0&lkt=0&aad=0&TH=&mta=0&e=yd1nRB4ER-iiXlrS9PQ9hwu-AYzAWkUQlpJ0wNhnNn_lQD2t5H8K23bxWjK1DZ1cXAGlYncPkfy2q9gCzUR3hg&A=DA71FB82EE40A14D7C53F174FFFFFFFF',
            'SRCHHPGUSR': 'SRCHLANG=en&IG=CE348E01BD584EA8BACB30371158E7D1&PV=15.0.0&DM=1&BRW=XW&BRH=S&CW=1536&CH=150&SCW=1519&SCH=1701&DPR=1.3&UTC=180&WTS=63873574603&HV=1737977821&PRVCW=1536&PRVCH=748&EXLTT=1',
        })

    def validate_email(self, email):
        """Improved email validation using regex"""
        if not email:
            return None
        pattern = r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)"
        match = re.search(pattern, email)
        return match.group(1) if match else None

    def extract_emails(self, text, hrefs):
        """Extract emails from both text content and hrefs"""
        emails = set()
        
        # Extract from text content
        text_emails = re.findall(r"[\w\.+-]+@[\w-]+\.[\w\.-]+", text)
        emails.update([self.validate_email(e) for e in text_emails])
        
        # Extract from hrefs
        for href in hrefs:
            if href.startswith('mailto:'):
                email = href.split(':', 1)[-1].split('?')[0]
                if self.validate_email(email):
                    emails.add(email)
        
        return list(filter(None, emails))

    def construct_query(self, row):
        """Build search query with proper encoding"""
        name = row['MEMBER NAME'].strip()
        location = row.get('LOCATION', '')
        username = row.get('USERNAME', '')
        
        query_parts = [name]
        
        if username:
            try:
                domain = username.split('@')[1]
                query_parts.append(domain)
            except IndexError:
                pass
        
        if location:
            query_parts.append(location)
        
        query_parts.append("[EMAIL]")
        return quote_plus(' '.join(query_parts))

    def process_result(self, result):
        """Process individual search result with improved email extraction"""
        try:
            text_content = result.get_text(separator=' ', strip=True)
            hrefs = [a['href'] for a in result.find_all('a', href=True)]
            
            # Fuzzy match validation
            if fuzz.partial_ratio(self.current_name.lower(), text_content.lower()) < 80:
                return None
            
            emails = self.extract_emails(text_content, hrefs)
            if not emails:
                return None
            
            main_link = next((href for href in hrefs if 'mailto:' not in href), None)
            
            return {
                "MEMBER NAME": self.current_name,
                "EMAIL": emails[0],  # Take first valid email
                "LINK": main_link,
                "CONTENT": text_content[:500]  # Store first 500 chars
            }
        except Exception as e:
            print(f"Error processing result: {e}")
            return None

    def scrape_page(self, query):
        """Scrape a single Bing search page"""
        params = {
            'q': query,
            'form': 'QBRE',
            'sp': '-1',
            'first': '1',
            'count': '10'
        }
        
        try:
            response = self.session.get('https://www.bing.com/search', params=params)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            results = soup.select('ol#b_results li.b_algo')
            
            with ThreadPool(len(results)) as pool:
                processed = pool.map(self.process_result, results)
            
            return [p for p in processed if p]
        except Exception as e:
            print(f"Error scraping page: {e}")
            return []

    def scrape(self):
        """Main scraping function"""
        input_path = self.base_dir / 'wildlabs.xlsx'
        output_path = self.results_dir / 'wildlabs_results.xlsx'
        
        try:
            df = pd.read_excel(input_path).dropna(subset=['MEMBER NAME'])
            #replace nan with empty string
            df = df.fillna('')
        except FileNotFoundError:
            print(f"Input file not found: {input_path}")
            return
        
        results = []
        
        for _, row in tqdm(df.iterrows(), total=len(df), desc='Processing members'):
            self.current_name = row['MEMBER NAME'].strip()
            query = self.construct_query(row)
            
            page_results = self.scrape_page(query)
            results.extend(page_results)
            
            time.sleep(2.5)  # Respect crawl delay
            
        if results:
            result_df = pd.DataFrame(results)
            result_df.to_excel(output_path, index=False)
            print(f"Results saved to: {output_path}")
        else:
            print("No results found")

if __name__ == "__main__":
    scraper = MultiUrlScraper()
    scraper.scrape()