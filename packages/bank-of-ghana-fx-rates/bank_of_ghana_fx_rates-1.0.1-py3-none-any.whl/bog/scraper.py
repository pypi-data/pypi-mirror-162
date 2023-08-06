import csv
import os
from _datetime import datetime
from time import sleep
import click
import requests
import urllib3
from bs4 import BeautifulSoup as bs
from pyfiglet import Figlet

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class BankOfGhanaFX:
    VERSION = '1.0.1'

    def __init__(self, url: str):
        if url is None:
            raise ValueError("URL is missing!")
        self.url = url
        self.__BASE_URL = "https://www.bog.gov.gh/wp-admin/admin-ajax.php?action=get_wdtable&table_id"

    @property
    def url(self):
        return self._url
    @url.setter
    def url(self, val):
        # 'val' should be str
        if not isinstance(val, str):
            raise TypeError("Expected: string")
        self._url = str(val)

    def mkdir(self, path):
        """Create directory"""
        try:
            if not os.path.exists(path):
                os.mkdir(path)
            else:
                print(f' * Directory %s already exists = {path}')
        except OSError as err:
            raise OSError(f"{err}")

    def get_table_info(self):
        """Get table information"""
        print('Loading table ID...')
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
                          " Chrome/85.0.4183.121 Safari/537.36"
        }
        html = requests.get(self.url, headers=headers, verify=False).text
        soup = bs(html, 'lxml')
        table = soup.find('table', id='table_1')
        input_wdt = soup.find('input', id='wdtNonceFrontendEdit')
        if table is None or input_wdt is None:
            print('Non-generic table url. Please contact developer.')
            return None
        if self.url[-1] in '/':
            name = self.url.split('/')[-2]
        else:
            name = self.url.split('/')[-1]
        table_id = table['data-wpdatatable_id']
        headers = []
        for header in table.find('thead').find('tr').find_all('th'):
            headers.append(header.get_text().strip())
        wdt_nonce = input_wdt['value']
        table_info = {'name': name, 'id': table_id, 'wdtNonce': wdt_nonce, 'headers': headers}
        print(f'Table id is {table_id}')
        return table_info

    def send_request(self, wdt, table_id, draw, start, length):
        """send request to scrape page"""
        print('Scraping data from API...')
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
                          " Chrome/85.0.4183.121 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Accept": "application/json, text/javascript, */*; q=0.01",
        }
        data = {
            "draw": draw,
            "wdtNonce": wdt,
            "start": start,
            "length": length
        }
        response = requests.post(f'{self.__BASE_URL}={table_id}', headers=headers, data=data, verify=False)
        return response.json()

    def scrape_table(self):
        """scrape table definition"""
        table = self.get_table_info()
        if table is None:
            return
        draw = 1
        start = 0
        length = 10000
        lines = []
        while True:
            try:
                response = self.send_request(table['wdtNonce'], table['id'], draw, start, length)
                if len(response['data']) > 0:
                    for line in response['data']:
                        lines.append(line)
                    start += length
                else:
                    break
            except requests.exceptions.HTTPError as err:
                print(f'Unsuccessful request. Trying again in few seconds: {err}')
                sleep(5)
        try:
            lines.sort(key=lambda x: datetime.strptime(x[0], '%d %b %Y'), reverse=True)
        except:
            pass
        return {'name': table['name'], 'data': lines, 'headers': table['headers']}

    def save_csv(self, name, headers, lines):
        """save scraped data to csv"""
        print('Saving results in csv...')
        file_path = os.getcwd()
        print(f"File will be saved to : {file_path}")
        # make a directory at the current working directory
        self.mkdir(file_path)

        with open(f"{file_path}/{name}.csv", "w", newline='', encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
            writer.writerow(headers)
            for line in lines:
                writer.writerow(line)
        print(f'{file_path}/{name}.csv saved! Total records: {len(lines)}')

    def run(self):
        """Run Application"""
        if 'https://' in self.url:
            table = self.scrape_table()
        else:
            table = self.scrape_table()
        if table is not None:
            self.save_csv(table['name'], table['headers'], table['data'])

    @staticmethod
    def info():
        """Info About eXchange App """
        f = Figlet(font='standard', width=90)
        click.echo(f.renderText('eXchange Rate-APP'))
        click.secho("eXchange rate data: A simple API for tracking exchange rates in Ghana", fg='cyan')
        click.echo("Source of Data: Bank of Ghana [https://bog.gov.gh] ")
        click.echo("Author: Theophilus Siameh")
        click.echo("Email: theodondre@gmail.com")
