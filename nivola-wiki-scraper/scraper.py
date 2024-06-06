from sys import version_info

if version_info[0] != 3 and version_info[1] != 12:
    print('Enure you are using Python 3.12, if necessary download it!')
    exit(1)
    
import requests as r
from bs4 import BeautifulSoup
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, SoftwareType
from json import dumps, load
from spacy import load as sc_load
from re import sub
from Crypto.Hash.keccak import new
from deepl import Translator

class Wiki:
    def __init__(self, debug_mode: bool = False) -> None:
        self.debug_mode = debug_mode # if True shows logs, it's slower, only recommended for developing purpose
        # self.data = [] # the final output, will be printed into db.json file
        self.nlp = sc_load('it_core_news_sm') # pip install spacy & python -m spacy download it_core_news_sm
        self.settings = self.getSettings() # load settings
        self.useragent = self.userAgentGen(1).get_random_user_agent()
        self.db = self.loadDB()
        self.added_count = 0
        if self.settings['deepl_api_key']: self.translator = Translator(self.settings['deepl_api_key'])
        print(f'Override mode: {self.settings["override"]}')

    def main(self):
        """
        Main function to scrape all links and save the data to the database JSON file.

        This function retrieves all links from the guide, removes blacklisted ones, and then proceeds to scrape each link.
        The scraped data is saved to the database JSON file.

        """
        # get all links and remove blacklisted ones
        override = self.settings['override']
        if override:
            self.db = dict()
        all = set(self.getAllLinks()) - set(self.settings['blacklist'])
        len_all = len(all)
        print(f'Found {len_all} links, proceding to scrape...')

        try:
            for i, link in enumerate(all):
                print(f'Scraping item: {i+1}/{len_all} {"--------------------------------------------" if self.debug_mode else ""}', 
                        end='\r')
                self.scrapePage(link, override)
        except KeyboardInterrupt:
            print('CTRL+C detected, exiting...')
            open('db.json', 'w', encoding='UTF-8').write(dumps(list(self.db.values()), indent=4, ensure_ascii=False))
            print(f'Successfully saved db.json, sections found: {len(self.db.keys())}, new sections found: {self.added_count}')
            exit()

        open('db.json', 'w', encoding='UTF-8').write(dumps(list(self.db.values()), indent=4, ensure_ascii=False))
        print(f'Successfully saved db.json, sections found: {len(self.db.keys())}, new sections found: {self.added_count}')

    def testMain(self, urls: list[str]):
        """
        Test function to scrape specified URLs and save the data to the database JSON file.

        Args:
            urls (list[str]): A list of URLs to scrape.
            override (bool, optional): Flag to override existing data in the database. Defaults to False.

        """
        # get all links and remove blacklisted ones
        override = self.settings['override']
        if override:
            self.db = dict()
        all = set(urls) - set(self.settings['blacklist'])
        len_all = len(all)
        print(f'Found {len_all} links, proceding to scrape...')

        for i, link in enumerate(all):
            print(f'Scraping item: {i+1}/{len_all} {"--------------------------------------------" if self.debug_mode else ""}', 
                    end='\r')
            self.scrapePage(link, override)

        open('db.json', 'w', encoding='UTF-8').write(dumps(list(self.db.values()), indent=4, ensure_ascii=False))
        print(f'Successfully saved db.json, sections found: {len(self.db.keys())}, new sections found: {self.added_count}')

    def deepSpaceCleaning(self, text: str):
        """
        Perform deep cleaning of whitespace in the given text.

        This function iterates three times to replace consecutive whitespace characters
        (including spaces, tabs, and newlines) with a single space character. It helps
        normalize the spacing within the text.

        Args:
            text (str): The input text to be cleaned.

        Returns:
            str: The text with consecutive whitespace characters replaced by a single space.

        """
        for _ in range(3): text = sub(r'\s+', ' ', text)

        return text

    def cleared(self, text: str, lower: bool = False, final_clean: bool = False) -> str:
        """
        Clean the input text by removing unwanted characters and replacing special characters.

        Args:
            text (str): The input text to be cleaned.

        Returns:
            str: The cleaned text.
        """
        text = text.replace('\n', ' ') # new line
        text = self.deepSpaceCleaning(text).strip() # delete spaces
        text = text.replace('\uf0c1', '') # jappo char
        text = text.replace('\u201D', '\'') # ”
        text = text.replace('\u201C', '\'') # “
        text = text.replace('\u2019', '\'') # ’
        text = text.replace('\u2013', '-') # –
        text = text.replace('«', '<') # strange char
        text = text.replace('»', '>') # strange char
        text = text.replace('\u00a0', ' ') # weird scape
        text = text.replace('\u200b', '') # useless space
        if final_clean:
            text = text.replace('<', '[')
            text = text.replace('>', ']')
        if lower: text = text.lower()
        return text

    def keccak256(self, text: str) -> str:
        """
        Generate the Keccak-256 hash of the input text.

        Args:
            text (str): The input text to be hashed.

        Returns:
            str: The hexadecimal representation of the Keccak-256 hash of the input text.
                If the input text is empty or not of type str, an empty string is returned.
        """
        # Ensure text is bytes (str is actually bytes)
        if isinstance(text, str):
            if len(self.cleared(text)) > 0:
                text = text.encode()
            else: return ''
        else: return ''

        # Create a Keccak hash object and add text
        h = new(digest_bits=256)
        h.update(text)

        # Get the digest (hash) of the text, convert it to Hexadecimal value
        digest_hex = h.digest().hex()
        return digest_hex

    def getSettings(self) -> dict:
        """
        Load the settings from the 'settings.json' file and return them as a dictionary.

        Returns:
            dict: A dictionary containing the settings loaded from the file.
        """
        return self.loadJsonFile(f'settings.json')

    def loadJsonFile(self, file: str) -> dict:
        """
        Load data from a JSON file and return it as a dictionary.

        Args:
            file (str): The path to the JSON file.

        Returns:
            dict: A dictionary containing the data loaded from the JSON file.
        """
        with open(file,'r', encoding='utf-8') as f:
            if(f.readable()):
                return load(f) # json.load
            else: 
                print(f'Error while reading {file}')
                exit()

    def getSections(self, soup: BeautifulSoup):
        """
        Retrieve <section> tags from the BeautifulSoup object, excluding those with an empty id or with id 'wy-nav-shift'.

        Args:
            soup (BeautifulSoup): The BeautifulSoup object representing the HTML content.

        Returns:
            ResultSet: A ResultSet containing <section> tags with non-empty id attributes, excluding 'wy-nav-shift'.
        """
        return soup.find_all(
            lambda tag: tag.name == 'section' and 
                        tag.has_attr('id') and 
                        tag['id'] != "" and 
                        tag['id'] != 'wy-nav-shift'
            ) 

    def getAtags(self, soup: BeautifulSoup):
        """
        Retrieve <a> tags with class='reference internal' from the BeautifulSoup object.

        Args:
            soup (BeautifulSoup): The BeautifulSoup object representing the HTML content.

        Returns:
            ResultSet: A ResultSet containing <a> tags with class='reference internal'.
        """
        return soup.find_all('a', {'class': 'reference internal'}) 

    def userAgentGen(self, num_of_UA: int = 500):
        """
        Generate Chrome User Agents.

        Args:
            num_of_UA (int, optional): Number of User Agents to generate. Defaults to 500.

        Returns:
            UserAgent: A UserAgent object for generating Chrome User Agents.
        """
        return UserAgent(
            software_names=[SoftwareName.CHROME.value],
            # operating_systems=[OperatingSystem.WINDOWS.value],
            limit=num_of_UA,
            browser_types=[SoftwareType.WEB_BROWSER.value]
        )

    def genHeaders(self):
        """
        Generate headers for HTML requests.

        Returns:
            dict: A dictionary containing headers for HTML requests.
        """
        return {
            'User-Agent': self.useragent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1'
        }

    def makeGet(self, url: str):
        """
        Make a GET request to the specified URL.

        Args:
            url (str): The URL to make the GET request to.

        Returns:
            Response: The response object containing the result of the GET request.
        """
        return r.get(url, headers=self.genHeaders())

    def getMostUsedWords(self, text: str):
        """
        Return a list of the three most used words in the given text.

        Args:
            text (str): The text to analyze.

        Returns:
            list: A list containing the three most used words in the text.
        """
        doc = self.nlp(text)
        
        # Extract nouns and adjectives into a set()
        nouns_and_adjectives = {token.text for token in doc if token.pos_ in ['NOUN', 'ADJ']}
        text_lower = text.lower()
        word_counts = {}
        
        # Split the text into words
        for word in text_lower.split(): 
            if word not in nouns_and_adjectives: continue
            # Remove punctuation and other non-alphabetic characters
            clean_word = ''.join(c for c in word if c.isalpha())
            # increase count
            word_counts[clean_word] = word_counts.get(clean_word, 0) + 1

        # Sort the word counts based on occurrences in descending order
        sorted_word_counts = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        retu = [word for word, _ in sorted_word_counts]
        if self.debug_mode: print(f'[getMostUsedWords] {retu}')
        return retu

    def retrieveLists(self, sec, text):
        """
        Retrieve lists from HTML section and text.

        Args:
            sec (BeautifulSoup): The BeautifulSoup section object.
            text (str): The text to search for lists.

        Returns:
            list: A list containing the items found in lists.
        """
        # found 3 ways to scrape lists
        #       - li tag
        #       - line that start with "- "
        #       - line that start with "● "
        list_item = []
        lis = sec.find_all('li') # search all <li>

        if lis:
            for li in lis:
                txt = li.text.strip()
                if self.debug_mode: print('[retrieveLists 1]', txt)
                list_item.append(txt)
        
        for line in text.split('\n'):
                # some list are wrote with - instead of <li>
            if line.startswith('-  '):
                txt = line.replace('-  ', '').strip()
                if self.debug_mode: print('[retrieveLists 2]', txt)
                list_item.append(txt)
                continue
            
                # some list are wrote with ● instead of <li>
            if '●' in line: 
                # line that starts with ● contain a list in it
                temp_list = line.split('●')[1:]
                for i, line in enumerate(temp_list):
                    temp_list[i] = line.split('    ')[0].strip()
                if self.debug_mode: print('[retrieveLists 3]', ' '.join(temp_list))
                list_item.extend(temp_list)
                continue

        return list_item
    
    def getSectionTitle(self, soup: BeautifulSoup):
        """
        Return the title of the section.

        Args:
            soup (BeautifulSoup): The BeautifulSoup object.

        Returns:
            str: The title of the section, or an empty string if not found.
        """
        def clear(text: str) -> str:
            return text.replace(',', '').replace('\'', ' ').replace(' - ', ' ').lower()
        
        strong = soup.find('strong')
        if strong: 
            return clear(strong.text), strong.text
        return ''

    # retrieve keyword to enhance the search speed
    # it uses title and the top 3 used words in section's text 
    def retriveKeywords(self, text, title) -> list:
        """
        Retrieve keywords to enhance search speed.

        Args:
            text (str): The text of the section.
            title (str): The title of the section.

        Returns:
            list: A list of keywords extracted from the text and title.
        """
        keys = self.getMostUsedWords(text) 
        title = title.lower()
        doc = self.nlp(title)
    
        # Extract nouns and adjectives into a set()
        nouns_and_adjectives = {token.text for token in doc if token.pos_ in ['NOUN', 'ADJ']}
        for w in title.split():
            if w not in nouns_and_adjectives: continue
            keys.append(w)
        
        return ', '.join(set(keys))

    # retrieve data from Glossario tables
    def retrieveTableData(self, sec) -> dict[str, str]:
        """
        Retrieve data from Glossario tables.

        Args:
            sec (BeautifulSoup): The BeautifulSoup object of the section.

        Returns:
            dict[str, str]: A dictionary containing the data extracted from the tables.
        """
        # Find the table by its tag name
        tables = sec.find_all('table')
        all_tables_data = dict()

        if tables: # exist and it's not None
            # Iterate through each table
            for table in tables:
                # Iterate through rows and columns to extract data
                for row in table.find_all('tr'):
                    # skip table headers
                    if 'acronimo/termine' in row.get_text().lower(): continue
                    # Extract data from each cell in the row
                    columns = row.find_all('td')
                    
                    # Ensure there are at least two columns
                    if len(columns) >= 2:
                        key = columns[0].text.strip()
                        value = columns[1].text.strip()
                        # Add key-value pair to the dictionary
                        all_tables_data[key] = value
                        if self.debug_mode: print(f'[retrieveTableData] {key=}: {value=}')
        return all_tables_data

    # gen the category
    def handleCategory(self, url, title: str) -> list:
        """
        Generate the category for the given URL and title.

        Args:
            url (str): The URL from which the category is extracted.
            title (str): The title to be included in the category.

        Returns:
            list: A list containing the generated category.
        """
        # https://nivola-userguide.readthedocs.io/it/latest/Come_fare_per/index_come_fare_per.html
        # for example: it uses 'come_fare_per' + title
        return url.split('/')[5].lower().replace('_', ' ') +'/'+ title

    def loadDB(self) -> dict:
        """
        Load the database from the JSON file and return it as a dictionary.

        Returns:
            dict: A dictionary where keys are text hashes and values are corresponding objects.
        """
        db_dict = dict()
        try:
            file = self.loadJsonFile('db.json')
            for obj in file:
                db_dict[obj['hash']] = obj
        except Exception as e:
            print(f'An error occured during {self.loadDB.__name__} runtime: {e}')
        return db_dict
    
    def scrapePage(self, url : str, override: bool = False):
        """
        Scrape the content of the given URL and process its sections.

        Args:
            url (str): The URL of the page to scrape.
            override (bool, optional): Flag indicating whether to override existing items. Defaults to False.
        """
        res = self.makeGet(url)

        if res.status_code == 200:
            soup = BeautifulSoup(self.cleared(res.text), 'html.parser')
            sections_list = self.getSections(soup)
            if len(sections_list) > 1:
                # if there are multiple sections into a single page
                # delete the first one, because it wrap up all sections
                del sections_list[0]

            if self.debug_mode: print(f'\n[scrapePage] Sections found: {len(sections_list)}')

            for sec in sections_list:
                text = sec.get_text()
                if text == '': continue

                text_hash = self.keccak256(text)
                add = False
                '''If the override flag is True, it will add the item regardless of whether it already exists in the list. 
                If override is False, it will only add the item if it's not already present in the list. 
                The decision to add the item is stored in the add variable.''' 
                if override:
                    add = True
                else:
                    if text_hash not in self.db.keys():
                        add = True
                
                if not add: continue

                list_item = self.retrieveLists(sec, text)
                anchor_href = ''
                try:
                    anchor_href = sec.select_one('a')['href']
                except: pass

                if 'releasenotes' in url.lower():
                    title = anchor_href.replace('-', '_').replace('#', '')
                elif 'glossario' not in url.lower():
                    title, title_not_cleared = self.getSectionTitle(sec)
                    # select only the content, excluding the title
                    # title_not_cleared is the original title without removing any chars
                    text = text.replace(title_not_cleared, title).strip()[len(title)+1:]
                else:
                    title = ''

                required_role: list[str] = self.getRequiredRole(title)
                if len(required_role) > 0:
                    # if any role is required, remove role requirements from title
                    title = sub(r'\([^)]*\)', '', title)
                    title = self.deepSpaceCleaning(title).strip()

                if 'glossario' in url.lower():
                    title = 'glossario '+anchor_href.replace('#', '').replace('id', 'id ')

                category = self.handleCategory(url, title)
                table = self.retrieveTableData(sec)

                if 'glossario' in category and len(table) == 0:
                    # skip useless glossario without any content
                    continue
                
                if add:
                    self.added_count += 1 
                    keywords = self.retriveKeywords(text, title)
                    final_text = self.cleared(text, True, True)
                    self.db[text_hash] = {
                        'hash': text_hash,
                        'link': url.split('#')[0]+anchor_href,
                        'title': title,
                        'category': category,
                        'keywords': keywords,
                        'list': list_item,
                        'table': table,
                        'required_role': required_role,
                        'text': final_text,
                    }
                    if self.settings['enable_en_translation']: 
                        self.db[text_hash]['category_en'] = self.translateCategory(category)
                        self.db[text_hash]['keywords_en'] = self.translateKeywords(keywords)
                        self.db[text_hash]['text_en'] = self.useDeeplApi(final_text)
        else:
            print(f'Page not reached, status code: {res.status_code}, URL: {url}')

    def getRequiredRole(self, title: str = '') -> list[str]:
        """Detect if the title contain any Role Requirements

        Args:
            title (str): section's Title. Defaults to ''.

        Returns:
            list[str]: A list containing the potential required roles, if any. Example: ['master di account', 'amministratore di backoffice']
        """
        if title == '': return []

        # detect if the section has any role infos
        checklist = ['master', 'account', 'amministratore', 'backoffice']
        if '(' in title and ')' in title:
            role_specified = False
            for word in checklist: 
                if word in title: role_specified = True; break

            if self.debug_mode: print(f'getRequiredRole: is role required: {role_specified}')
            if role_specified:
                start_index = title.find('(')
                end_index = title.find(')')
                if start_index != -1 and end_index != -1:
                    roles: str = title[start_index + 1: end_index]

                if roles:
                    if self.debug_mode: print(f'getRequiredRole: role found: {roles}')
                    # handle string and return a list
                    if ' e ' in roles:
                        return roles.split(' e ')
                    else:
                        return [roles]
        return []

    def useDeeplApi(self, text: str):
        """Translate text from Italian to English (US) using DeepL service

        Args:
            text (str): 

        Returns:
            str: English version of text
        """
        if text == '': return ''

        result = self.translator.translate_text(
            text=text, 
            target_lang="EN-US",
            source_lang='IT',
            preserve_formatting=True,
            context='The text is a Cloud Provider documentation or a fraction of it, may only consist of a series of words.'
        )
        if self.debug_mode: print(f'useDeeplApi: {result.text}')
        return result.text

    def translateKeywords(self, keywords: str) -> str:
        keywords_en = self.useDeeplApi(keywords)

        return keywords_en.replace('\n', ', ')

    def translateCategory(self, category: str) -> str:
        """Given a Category get the English version correctly formatted

        Args:
            category (str): example of a valid category: come_fare_per/uso_dei_filtri

        Returns:
            str: category in English
        """
        category_mapping = {
            'service_portal': 'service_portal', 
            'come_fare_per': 'how_to', 
            'usare_cli': 'use_cli',
            'come_muovere_primi_passi': 'how_to_move_first_steps',
            'glossario': 'glossary',
            'overview_nivola': 'overview_nivola', 
            'notes': 'notes',
            'linee_guida': 'guidelines'
            }
        
        cat = category.split('/')
        try:
            cat[0] = category_mapping[cat[0]]
        except KeyError:
            pass # for any mapping problem: use the Italian version

        return f'{cat[0]}/{self.useDeeplApi(cat[1])}'

    def getAllLinks(self):
        """
        Retrieve all links from the guide.

        Returns:
            set: A set containing all the links found in the guide.
        """
        # retrieve all link in the guide
        url = self.settings['wiki_index']
        res = self.makeGet(url)
        links = set() # store each link by using set instead of list
        if res.status_code == 200:
            soup = BeautifulSoup(self.cleared(res.text), 'html.parser')
            a_tag = self.getAtags(soup)
            for a in a_tag:
                links.add(f'{url}{a["href"].split("#")[0]}')

            if self.debug_mode: print(f'[getAllLinks] Found {len(links)} links:\n' ,links)
        else:
            raise Exception(f'Cannot reach {self.settings["wiki_index"]}')
        return links

if __name__ == '__main__':
    wiki = Wiki(debug_mode=False)
    # wiki.main() ; exit()
    wiki.testMain(
        [ 
            'https://nivola-userguide.readthedocs.io/it/latest/Come_fare_per/04_Master_di_Division.html',
            'https://nivola-userguide.readthedocs.io/it/latest/Come_fare_per/40.1_Consultare_costi_e_consumi.html',
		    'https://nivola-userguide.readthedocs.io/it/latest/Glossario/Glossario.html',
            'https://nivola-userguide.readthedocs.io/it/latest/Linee_guida/1_Modelli_di_rete.html#private-cloud-internet',
            'https://nivola-userguide.readthedocs.io/it/latest/Come_fare_per/30.7_Servizio_di_Log_Management.html#modalita-di-accesso',
            'https://nivola-userguide.readthedocs.io/it/latest/Overview_Nivola/2_Concetti_Base.html#le-availability-zones',
            'https://nivola-userguide.readthedocs.io/it/latest/Come_muovere_primi_passi/10_Passaggi_necessari.html',
            'https://nivola-userguide.readthedocs.io/it/latest/Come_fare_per/03_Master_di_Organizzazione.html',
            'https://nivola-userguide.readthedocs.io/it/latest/Come_fare_per/8.13_Cancellare_Avvisi.html',
            'https://nivola-userguide.readthedocs.io/it/latest/Come_fare_per/11.14_Rimuovere_SG.html',
            'https://nivola-userguide.readthedocs.io/it/latest/Linee_guida/9.8_utenti_privilegiati_Ruoli_e_diritti.html'
        ]
    )
    '''
    '''

# DONE - function to divide text into sub categories
# DONE - function to properly scrape list
# DONE - scrape index to get every url https://nivola-userguide.readthedocs.io/it/latest/
# DOME - handle section title 
# DONE - develop a method to assign Keyword to each sub sections
# DONE - add support for ol tag and every types of list
# DONE - strip correctly every text fields 
# DONE - fix glossario's titles
# DONE - assing a category foreach url
# DONE - scrape table's data
# DONE - add blacklist url
# DONE - comment and clean code 
# DONE - incremental adding, add only new docs
#        hash the text field, compare it, if exist do not add
#        NOTE: if the text/section handling gets modified, the incremental adding may not works properly
#              it is advised to hard refresh the db.json every while the character handling is changed.
# DONE - re-structure db.json data
#           - DONE add text_en, category_en, keywords_en
#           - DONE make texts lower
#           - DONE add a flag for backoffice admin only
#           - DONE remove strange chars from title and category; eg: .replace(',', '').replace('\'', '_')
#           - DONE find other things that has to be changed
#           - DONE test execution
#           - DONE removed < and > as may seems xml-like tags
#           - DONE removed _ from category to correctly translate it