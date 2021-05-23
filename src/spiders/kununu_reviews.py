import scrapy
import logging
import src.parsers.kununu_reviews_parsers as parser

FACTOR_LABELS_TO_FACTOR_KEYS = {
    'Arbeitsatmosphäre': 'arbeitsatmosphaere',
    'Image': 'image',
    'Ausbildungsvergütung': 'ausbildungsverguetung',
    'Die Ausbilder': 'ausbilder',
    'Karrierechancen': 'karrierechancen',
    'Arbeitszeiten': 'arbeitszeiten',
    'Spaßfaktor': 'spassfaktor',
    'Aufgaben/Tätigkeiten': 'aufgaben',
    'Variation': 'variation',
    'Respekt': 'respekt',
    'Wofür möchtest du deinen Arbeitgeber im Umgang mit der Corona-Situation loben?': 'coronaSituationPositives',
    'Was macht dein Arbeitgeber im Umgang mit der Corona-Situation nicht gut?': 'coronaSituationSchlechtes',
    'Wie kann dich dein Arbeitgeber im Umgang mit der Corona-Situation noch besser unterstützen?': 'coronaSituationVerbesserungen',
    'Wo siehst du Chancen für deinen Arbeitgeber mit der Corona-Situation besser umzugehen?': 'coronaSituationVerbesserungen',
    'Was macht dein Arbeitgeber in Corona-Zeiten nicht gut?': 'coronaSituationSchlechtes',
    'Was macht dein Arbeitgeber in Corona-Zeiten gut?': 'coronaSituationPositives',
    'Was sollte dein Unternehmen in Corona-Zeiten (anders) machen?': 'coronaSituationVerbesserungen',
    'Umwelt-/Sozialbewusstsein': 'umweltUndSozialbewusstsein',
    'Kollegenzusammenhalt': 'kollegenzusammenhalt',
    'Vorgesetztenverhalten': 'vorgesetztenverhalten',
    'Kommunikation': 'kommunikation',
    'Gleichberechtigung': 'gleichberechtigung',
    'Work-Life-Balance': 'workLifeBalance',
    'Karriere/Weiterbildung': 'karriereUndWeiterbildung',
    'Umgang mit älteren Kollegen': 'umgangMitAelterenKollegen',
    'Arbeitsbedingungen': 'arbeitsbedingungen',
    'Gehalt/Sozialleistungen': 'gehaltUndSozialleistungen',
    'Interessante Aufgaben': 'interessanteAufgaben',
    'Gut am Arbeitgeber finde ich': 'vorteile',
    'Schlecht am Arbeitgeber finde ich': 'nachteile',
    'Verbesserungsvorschläge': 'verbesserungsvorschlaege',
    'Herausforderung': 'herausforderung'
}


class KununuReviewsSpider(scrapy.Spider):
    name = 'kununu-reviews'
    allowed_domains = ['kununu.com']
    custom_settings = {
        'FEED_URI': 'data/kununu_bundeswehr_%(time)s.json',
        'FEED_FORMAT': 'json'
    }
    # Required because kununu will reject the standard scrapy user agent (Scrapy/{version}(+http://scrapy.org))
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0'}

    def start_requests(self):
        # yield scrapy.Request(url='https://www.kununu.com/de/stadt-koeln/kommentare', callback=self.parse, headers=self.headers)
        # yield scrapy.Request(url='https://www.kununu.com/de/bundesamt-fuer-gueterverkehr9/kommentare', callback=self.parse, headers=self.headers)
        # yield scrapy.Request(url='https://www.kununu.com/de/stadt-nuernberg1/kommentare', callback=self.parse, headers=self.headers)
        yield scrapy.Request(url='https://www.kununu.com/de/deutsche-bundeswehr/kommentare', callback=self.parse, headers=self.headers)

    def parse(self, response):
        reviews = parser.parse_all_reviews(response)
        for review in reviews:
            date = parser.parse_review_date(review)
            employment_info = parser.parse_review_employment_info(review)
            rating = parser.parse_review_rating(review)
            factors = parser.parse_all_factors(review)
            parsed_factors = {}
            for factor in factors:
                parsed_factor = {
                    'label': parser.parse_factor_label(factor),
                    'score': parser.parse_factor_score(factor),
                    'comment':  parser.parse_factor_comment(factor)
                }
                factor_key = FACTOR_LABELS_TO_FACTOR_KEYS[parsed_factor['label']]
                parsed_factors[factor_key] = parsed_factor

            parsed_review = {
                'date': date,
                'employmentInfo': employment_info,
                'rating': rating,
                'factors': parsed_factors 
            }
            yield(parsed_review)

        next_page_url = response.xpath('//*[@id="reviews-read-more-cta"]/@href').extract_first()
        if next_page_url:
            next_page_url = response.urljoin(next_page_url)
            yield(scrapy.Request(url=next_page_url, callback=self.parse, headers=self.headers))
        else:
            logging.info('Last page reached')
