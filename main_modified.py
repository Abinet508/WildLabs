import datetime
import os
import re
import time
import urllib
import urllib.parse
import urllib.request
from playwright.sync_api import sync_playwright
import requests
from thefuzz import fuzz, process
from requests_html import HTML
import pandas as pd
from multiprocessing.pool import ThreadPool
import pandas as pd
import os
import time
import urllib.parse
from playwright.sync_api import sync_playwright
from requests_html import HTML
import pandas as pd
import pygsheets


class GoogleSearch:
    def __init__(self) -> None:
        """
        Initializes a GoogleSearch object.

        Attributes:
            urls (list): A list to store the URLs.
            results (list): A list to store the scraped results.
            df (DataFrame): A DataFrame to store the final results.
            current_dir (str): The current directory path.
            output_file (str): The path of the output Excel file.
            input_file (str): The path of the input text file.
        """
        self.urls = []
        self.results = []
        self.df = pd.DataFrame(columns=['PAGE', 'WEBSITE', 'LINK', 'HAS_PRODUCT', 'SCORE', 'TEXT'])
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.output_file = os.path.join(self.current_dir,'results', 'wildlabs_v1.xlsx')
        self.input_file = os.path.join(self.current_dir,'Source', 'input.txt')
        os.makedirs(os.path.join(self.current_dir, 'CREDENTIALS'), exist_ok=True)
        os.makedirs(os.path.join(self.current_dir, 'Source'), exist_ok=True)
        os.makedirs(os.path.join(self.current_dir, 'results'), exist_ok=True)
        self.bing_q = False
        self.sheet_name = "Zoom Add on List"
        self.current_path = os.path.dirname(os.path.abspath(__file__))
        self.sheet_key = ""
        self.file_path = os.path.join(self.current_dir, 'results')
    
    def timer(self):
        """
        This function is used to calculate the time taken by the function to execute.

        Returns:
            None
        """
        start_time = time.time()
        yield
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Execution time: {execution_time} seconds")

    def progress_bar(self, iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', printEnd="\r"):
        """
        This function is used to display the progress bar.

        Args:
            iteration (int): The current iteration number.
            total (int): The total number of iterations.
            prefix (str): The prefix string for the progress bar.
            suffix (str): The suffix string for the progress bar.
            decimals (int): The number of decimals to display.
            length (int): The length of the progress bar.
            fill (str): The character used to fill the progress bar.
            printEnd (str): The character used to print the end of the progress bar.

        Returns:
            None
        """
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=printEnd)
        if iteration == total:
            print(flush=True)

    def add_to_df(self):
        """
        Adds the scraped results to the DataFrame.

        Returns:
            None
        """
        self.df = pd.DataFrame(self.results)
        # if take is True, then add the link to Has Product as hyperlink of YES else add the PAGE as hyperlink of NO
        self.df['HAS_PRODUCT'] = self.df.apply(lambda x: f'=HYPERLINK("{x["LINK"]}","YES")' if x['TAKE'] else f'=HYPERLINK("{x["LINK"]}","NO")', axis=1)
        self.df['PAGE'] = self.df.apply(lambda x: f'=HYPERLINK("{x["WEBSITE"]}","{x["PAGE"]}")', axis=1)
        self.df = self.df[['MEMBER NAME', 'LOCATION', 'USERNAME', 'PAGE', 'HAS_PRODUCT', 'SCORE', 'TEXT', 'EMAIL']]
        #drop duplicates leaving the first row
        self.df.drop_duplicates(subset=['PAGE'], keep='first', inplace=True)
        self.df.reset_index(drop=True, inplace=True)
        self.df.to_excel(self.output_file, index=False)
    
    def read_excel_file(self, file_path):
        """
        Reads the URLs from an Excel file.

        Args:
            file_path (str): The path of the Excel file.

        Returns:
            None
        """
        df = pd.read_excel(file_path)
        self.urls = df['WEBSITE'].tolist()

    def write_to_excel(self):
        """
        Writes the final results to an Excel file.

        Returns:
            None
        """
        
        self.df.to_excel(self.output_file, index=False)

    def read_txt_file(self):
        """
        Reads the URLs from a text file.

        Args:
            file_path (str): The path of the text file.

        Returns:
            list: A list of URLs read from the text file.
        """
        lines = []
        with open(self.input_file, 'r') as file:
            for line in file:
                lines.append(line.strip())  # Remove newline characters
        return lines

    def create_google_search_url(self, query):
        """
        Creates a Google search URL for the given query.

        Args:
            query (str): The search query.

        Returns:
            str: The Google search URL.
        """
        if self.bing_q:
            base_url = "https://www.bing.com/search?q="
        else:
            base_url = "https://www.google.com/search?q="
    
        encoded_query = urllib.parse.quote(query)
        full_url = base_url + encoded_query
        return full_url
    
    def setup_playwright(self):
        """
        Sets up the Playwright browser and context.
        """
        try:
            os.remove(os.path.join(self.current_dir, 'CREDENTIALS', 'storage_state.json'))
        except FileNotFoundError:
            pass
        try:
            context.close()
            browser.close()
        except:
            pass
        p = sync_playwright().start()
        browser = p.chromium.launch(headless=False,channel='msedge')
        if os.path.exists(os.path.join(self.current_dir, 'CREDENTIALS', 'storage_state.json')):
            context = browser.new_context(storage_state=os.path.join(self.current_dir, 'CREDENTIALS', 'storage_state.json'))
        else:
            context = browser.new_context()
        page = context.new_page()
        return page, context
    
    def scrape_data(self,):
        """
        Scrapes data from the given URLs.

        Args:
            urls (list): A list of URLs to scrape.

        Returns:
            None
        """
        
        response_list = []
        #urls = urls[:25]
        page, context = self.setup_playwright()
        try:
            url_counter = 0
            df  = pd.read_excel(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wildlabs.xlsx'))
            df = df.dropna(subset=['MEMBER NAME'])
            #replace nan with empty string
            df = df.fillna('')
            df = df.head(10)
            new_df = pd.DataFrame(columns=['MEMBER NAME', 'EMAIL', 'LINK', 'CONTENT'])
            total_urls = len(df)
            for index, row in df.iterrows():
                try:
                    url_counter += 1
                    self.name = row['MEMBER NAME'].strip()
                    location = row['LOCATION']
                    username = row['USERNAME']
                    key_Words = f'{self.name}'
                    if username and  len(str(self.name).split(sep=' ')) < 2:
                        username = username.split('@')[1]
                        key_Words += f' + {username}'
                    if location:
                        key_Words += f' + {location}'
                    key_Words += ' + [EMAIL]'
                    google_q = f'''{key_Words}'''
                    bing_q = f'''{key_Words}'''
                    #q = f'''inurl:{url} ("photovoltaic cable" OR "photovoltaic" OR "photovoltaic connector" OR "photovoltaic cable assembly" OR PV OR "PV cable assembly") (product OR buy OR shop OR store OR price OR catalog OR specifications)'''

                    response = page.goto(self.create_google_search_url(google_q))
                    robot = page.locator('[id="captcha-form"]').all()
                    if robot:
                        print("Robot detected")
                        new_url = page.url
                        while robot:
                            time.sleep(1)
                            robot = page.locator('[id="captcha-form"]').all()
                        try:
                            os.remove(os.path.join(self.current_dir, 'CREDENTIALS', 'storage_state.json'))
                        except FileNotFoundError:
                            pass
                        os.makedirs(os.path.join(self.current_dir, 'CREDENTIALS'), exist_ok=True)
                        
                        context.storage_state(path=os.path.join(self.current_dir, 'CREDENTIALS', 'storage_state.json'))
                        page.goto(new_url)
                        response = page.goto(self.create_google_search_url(google_q))
                    html_body = response.body()
                    html = HTML(html=html_body)
                    response_list.append(html_body)
                    if not self.bing_q:
                        texts = html.xpath('//div[@id="search"]//div[contains(@jscontroller,"") and contains(@lang,"en")]')
                    else:
                        texts = html.xpath('//ol[@id="b_results"]/li[contains(@class,"b_algo")]')
                    found = False
                    index = 1
                    for text in texts:
                        link = text.xpath('//a')[0].attrs['href']
                        link_text = text.text
                        email = re.search(r'[\w\.-]+@[\w\.-]+', text.text)
                        # page1 = context.new_page()
                        # page1.goto(link, timeout=60000, wait_until='domcontentloaded')
                        
                        # print(f"Link: {page1.url}")
                        # page1.close()
                        # link_text = text.xpath('//a')[0].text
                        
                        score = 0
                        with ThreadPool() as pool:
                            results = pool.map(lambda x: fuzz.partial_ratio(self.name.lower(), x.lower()), [link_text])
                            score = max(results)
                        if score > 50:
                            found = True
                            data = {
                                'PAGE': index,
                                'WEBSITE': link,
                                'LINK': link,
                                'HAS_PRODUCT': True,
                                'TAKE': True,
                                "EMAIL": email.group() if email else None,
                                'MEMBER NAME': self.name,
                                'LOCATION': location,
                                'USERNAME': username,
                                'SCORE': score,
                                'TEXT': link_text
                            }
                        else:
                            data = {
                                'PAGE': index,
                                'WEBSITE': link,
                                'LINK': link,
                                'HAS_PRODUCT': False,
                                'TAKE': False,
                                "EMAIL": None,
                                'MEMBER NAME': self.name,
                                'LOCATION': location,
                                'USERNAME': username,
                                'SCORE': score,
                                'TEXT': link_text
                            }
                        self.results.append(data)    
                    self.progress_bar(url_counter, total_urls, prefix='CROWLING PROGRESS:', suffix=f'{url_counter}/{total_urls} URLS COMPLETED ', length=50)
                except Exception as e:
                    pass
            self.add_to_df()
        except KeyboardInterrupt:
            print("Script terminated by user.")

    def main(self):
        """
        The main function to execute the scraping process.

        Args:
            urls (list): A list of URLs to scrape.

        Returns:
            None
        """
        self.scrape_data()
        self.write_to_excel()
        
if __name__ == '__main__':
    gs = GoogleSearch()
    gs.main()