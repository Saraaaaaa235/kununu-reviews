def parse_all_reviews(html_document):
    return html_document.xpath('//*[starts-with(@class, "index__reviewBlock")]')

def parse_review_date(review_document):
    return review_document.css('[class^="index__dateBlock"]').xpath('./time[1]//@datetime').extract_first()

def parse_review_employment_info(review_document):
    employment_info = review_document.css('[class^="index__employmentInfoBlock"]')
    return {
        'angestelltenVerhaeltnis': employment_info.xpath('./b/text()').extract_first(),
        'status': employment_info.xpath('./span[contains(@class, "index__sentence")]/text()').extract_first()
    }

def parse_review_rating(review_document):
    return review_document.css('[class^="index__ratingBlock"]').xpath('./div[1]/span[1]/text()').extract_first()

def parse_all_factors(review_document):
    return review_document.css('[class^="index__factor"]')

def parse_factor_label(factor_document):
    return factor_document.xpath('./h4/text()').extract_first()

def parse_factor_score(factor_document):
    return factor_document.xpath('./div[contains(@class, "index__scoreBlock")]/span/@data-score').extract_first()

def parse_factor_comment(factor_document):
    return factor_document.xpath('./p[contains(@class, "index__plainText")]/text()').extract_first()
