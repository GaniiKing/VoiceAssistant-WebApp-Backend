
import spacy



nlp = spacy.load("en_core_web_sm")


def check_query_for_urls_2(query_str):
        print(f"{type(query_str)} in check.py page")
        doc = nlp(query_str)
        urls = [token.text for token in doc if token.like_url]
        print(f'The available URLs in the query are in check.py {urls}')
        return urls
    

check_query_for_urls_2("open amazon.com")