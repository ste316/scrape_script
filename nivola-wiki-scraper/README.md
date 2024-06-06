# Easily scrape all infos from [Nivola's Read the Docs](https://nivola-userguide.readthedocs.io/it/latest/)
## The scraper loop through each link, identify `<section>` tags and retrieve all valueble infos from it.

#### Each record has:
1. Text's Hash as unique identifier
2. Direct Link to the section inside a page
3. Title
4. Category
5. List of keywords, that are provided from
    - section's title
    - most used word in section's text
6. Table's data
7. Stripped Text of section

### Here is an example of a record in the output file: `db.json`
```json
[   
    {
        "hash": "string",
        "link": "string",
        "title": "aggiunta sg a istanza vmstring",
        "category": "string",
        "keywords": "string",
        "list": [
            "string",
            "string"
        ],
        "table": {"key":"value"},
        "required_role": ["string"],
        "text": "string",
        "category_en": "string",
        "keywords_en": "string",
        "text_en": "string"
    },
    {
        "hash": "66935d8c41f40d277341f45dacb5a261cdc648673f841ad99ba997f2d0a99e90",
        "link": "https://nivola-userguide.readthedocs.io/it/latest/Come_fare_per/11.12_Aggiungere_SG.html#aggiunta-sg-a-istanza-vm",
        "title": "aggiunta sg a istanza vm",
        "category": "come_fare_per/aggiunta_sg_a_istanza_vm",
        "keywords": "clic, parte, security, istanza",
        "list": [
            "Individuare il sever dall'Elenco VM, mettendo una spunta a fianco del nome;",
            "Fare clic sul pulsante:"
        ],
        "table": {},
        "required_role": [],
        "text": "la funzione ...",
        "category_en": "how_to/addition_sg_to_instance_vm",
        "keywords_en": "click, part, security, instance",
        "text_en": "the function ..."
    }
]
```

## Get Started

1. [Install Python](https://www.python.org/downloads/)
    - make sure to check `Install PIP` option in the installation wizard \
        NOTE: this script was developed with Python 3.12.2 on Windows 11, older versions may works anyway
2. Set up libraries
    - run `pip install -r requirements.txt -U`
    - wait to finish and run `spacy download it_core_news_sm`
3. OPTIONAL
    - edit `settings.json` file fields
    - `blacklist`: is the list of links to not scrape, I mainly excluded links containing list of links, such as indexes
    - `override`: 
        - *true* to delete all record and re-scrape
        - *false* to add only new records 
    - turn `enable_en_translation` to `true` if you need the translated version of: 
        - category
        - keywords
        - text
    - to actually translate, DeepL API is used, fill `deepl_api_key` with yours
4. Run the Scraper
    - `python scraper.py` or `python3 scraper.py`
5. Extend features / Debug
    - replace the code in the bottom with this:
    ```python
    if __name__ == '__main__':
    wiki = Wiki(debug_mode=True)
    # wiki.main() ; exit()
    wiki.testMain(
        [
            'https://nivola-userguide.readthedocs.io/it/latest/Glossario/Glossario.html', 
            'https://nivola-userguide.readthedocs.io/it/latest/Come_fare_per/40.1_Consultare_costi_e_consumi.html',
            'https://nivola-userguide.readthedocs.io/it/latest/Come_fare_per/04_Master_di_Division.html',
            'https://nivola-userguide.readthedocs.io/it/latest/Linee_guida/1_Modelli_di_rete.html#private-cloud-internet',
            'https://nivola-userguide.readthedocs.io/it/latest/Come_fare_per/30.7_Servizio_di_Log_Management.html#modalita-di-accesso',
            'https://nivola-userguide.readthedocs.io/it/latest/Overview_Nivola/2_Concetti_Base.html#le-availability-zones',
            'https://nivola-userguide.readthedocs.io/it/latest/Come_muovere_primi_passi/10_Passaggi_necessari.html',
            'https://nivola-userguide.readthedocs.io/it/latest/Come_fare_per/03_Master_di_Organizzazione.html',
            'https://nivola-userguide.readthedocs.io/it/latest/Come_fare_per/8.13_Cancellare_Avvisi.html',
            'https://nivola-userguide.readthedocs.io/it/latest/Come_fare_per/11.14_Rimuovere_SG.html',
        ]
    )
    ```