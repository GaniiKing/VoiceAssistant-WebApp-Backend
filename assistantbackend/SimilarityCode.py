from flask import Flask
from sklearn.metrics.pairwise import cosine_similarity
from transformers import BertTokenizer, BertModel,pipeline
import numpy as np
import spacy
import requests
from ast import literal_eval

app=Flask(__name__)


class CosineSmilarityClass:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.classifier = pipeline("text-classification",model='bhadresh-savani/roberta-base-emotion', return_all_scores=True)
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        self.model = BertModel.from_pretrained('bert-base-uncased')
        self.model.eval()
    
    def preprocess_query(self, sentence_test):
        well_being = "how are you"       
        enquire_self = "who are you"     
        browser_open = "open amazon.com" 
        news_teller = "Tell me news"     
        turn_sentence = "turn on translator"   
        youtube_play_sentence="play something on youtube" 
        calculate_sentence = "calculate the value of something" 
        what_is_sentence="what is the something"   
        who_is_sentence="who is narendramodi"
        joke_sentence = "tell me a joke"    
        text_book_sentence = "open a text book about html"
        set_alarm="open clock"    
        time_sentence="what is the time"    
        open_chrome= "open chrome"  
        open_notepad="open notepad" 
        open_word="open microsoft word"
        open_excel="open microsoft excel"   
        open_powerpoint="open microsoft power point"
        open_calc="open calculator" 
        exit_="exit"            
        sentencearray = [well_being, enquire_self, 
                         browser_open,news_teller,
                         turn_sentence,
                         youtube_play_sentence
                         ,calculate_sentence
                         ,what_is_sentence,
                         who_is_sentence,
                         joke_sentence,
                         text_book_sentence,
                         set_alarm,
                         time_sentence,
                         open_chrome,
                         open_notepad,
                         open_word,
                         open_excel,
                         open_powerpoint,
                         open_calc,
                         exit_
                         ]
        most_similar_index = None
        test_embedding = self.get_sentence_embedding(sentence_test)
        most_similar_index = self.find_most_similar_sentence(sentencearray, test_embedding)

        print(f"The most similar sentence is at index {most_similar_index}: {sentencearray[most_similar_index]}")
        self.indexValue = most_similar_index
        return most_similar_index

    def get_sentence_embedding(self, sentence):
        url = f"http://your_ip_address/get_sentence_embedding/{sentence}"
        response = requests.get(url)
        print(response.status_code)
        print(f"the body of response is {response.text}")

        embedding_list = literal_eval(response.text)

        body = np.array(embedding_list)

        print(type(response))
        print(type(body))
        return body
    

    def find_most_similar_sentence(self, sentence_array, test_sentence_embedding):
        most_similar_index = -1

        cosine_similarities_values = self.check_accurate(sentence_array, test_sentence_embedding)
        print(f'The cosine similarities are {cosine_similarities_values}')

        for i, item in enumerate(cosine_similarities_values):
            if item >= 0.780 and item == np.max(cosine_similarities_values):
                print(item)
                most_similar_index = i

        return most_similar_index

    def check_accurate(self, sentence_array, test_embedding):
        eligibility = []
        for sentence in sentence_array:
            sentence_embedding = self.get_sentence_embedding(sentence)
            similarity = self.final_cosine_similarity(test_embedding, sentence_embedding)
            eligibility.append(similarity)
        return eligibility
    
    @staticmethod
    def final_cosine_similarity(embedding1, embedding2):
        similarity = cosine_similarity([embedding1], [embedding2])[0][0]
        return similarity
    

local_instance = CosineSmilarityClass()

@app.route("/samplesentence/<sentence>",methods=['GET'])
def samplecheck(sentence):
    indexValue = local_instance.preprocess_query(sentence)
    print(f"the returned value from proccessing query is {indexValue}")
    return f"{indexValue}"


if __name__=="__main__":
    app.run(host='127.0.0.1',port=8000)
    

        