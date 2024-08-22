from transformers import BertTokenizer, BertModel,pipeline
from flask import Flask
import nltk
from nltk.tokenize import word_tokenize
from sklearn.metrics.pairwise import cosine_similarity
from googlesearch import search
import time
import spacy
import datetime
import wolframalpha
import wikipedia
import requests
import numpy as np
from pydantic import BaseModel
import re



app = Flask(__name__)

classifier = pipeline("text-classification", model='bhadresh-savani/roberta-base-emotion')



class Query(BaseModel):
    query: str
    index: int
    query_2:str
    sentence:str
    sentence_2:str
    text:str
    srcLang:str
    toLang:str
    text_analyse:str


class MyAssistant:
    def __init__(self):
        self.nlp=spacy.load("en_web_core_sm")
        self.word_token = word_tokenize
        nltk.download('punkt')
        self.classifier = pipeline("text-classification",model='bhadresh-savani/roberta-base-emotion', return_all_scores=True)
        self.indexValue = None
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        self.model = BertModel.from_pretrained('bert-base-uncased')
        self.model.eval()
        self.app_id = 'T7X889-YYLEJYT3HH'
        self.wolfram_client = wolframalpha.Client(self.app_id)
    
    def get_india_news(category='general'):
            url = f'https://newsapi.org/v2/top-headlines'
            news_api_key = 'your_api_key'
            params = {
                'country': 'in',  
                'category': category,
                'apiKey': news_api_key
            }
            try:
                response = requests.get(url, params=params)
                data = response.json()
                returndata = data.get('articles',[])
                element_counter = 0
                if response.status_code == 200:
                    articles = data.get('articles', [])
                    for i, article in enumerate(articles, start=1):
                        if article['source']['name']=='Hindustan Times':
                            print(f"{i}. Title: {article['title']}")
                            print(f"   Source: {article['source']['name']}")
                            print(f"   URL: {article['url']}")
                            print(f"   Published At: {article['publishedAt']}")
                            print('-' * 50)
                            element_counter+=1
                            if element_counter >= 2:
                                break
                else:
                    print(f"Error: {data.get('message', 'Unknown error')}")
                return returndata
            except Exception as e:
                print(f"An error occurred: {e}")

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
        text_book_sentence = "give me a text book about html"
        open_app= r"open ((.+))"    
        time_sentence="what is the time"     
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
                         open_app,
                         time_sentence,
                         exit_
                         ]
        most_similar_index = None
        test_embedding = self.get_sentence_embedding(sentence_test)
        most_similar_index = self.find_most_similar_sentence(sentencearray, test_embedding)

        print(f"The most similar sentence is at index {most_similar_index}: {sentencearray[most_similar_index]}")
        self.indexValue = most_similar_index
        return most_similar_index

    def get_sentence_embedding(self, sentence):
        doc = self.nlp(sentence)
        sentence_embedding = doc.vector
        return sentence_embedding

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
        
    
    def tell_me_a_joke(self):
        try:
            url="https://v2.jokeapi.dev/joke/Any?format=txt&safe-mode"
            response = requests.get(url)
            print(response.status_code)
            if(response.status_code==200):
                print('success joke valued...')   
            else:
                print(response.status_code)
                return "Server connection error"
            print(response.content.decode('utf-8'))
            return response.content.decode('utf-8')
        except Exception as e:
            print(e)
            return "Couldnot compute at the moment.."
    
        
        
    def search_and_play_on_source(self,query,last_word):
        if(last_word=='youtube'):
           return f"https://www.youtube.com/results?search_query={query}"
        elif(last_word=='spotify'):
            return f"https://open.spotify.com/search/{query}"
        else:
            return 'opening or playing in only youtube and spotify are available for instance'
            
            
            
            
        
    def search_wolfram_alpha(self,query):
        self.indexValue=None
        response =self.wolfram_client.query(query)
        print(f'The response id {response}')
        if response['@success'] == False:
           print('not success search in wolfram alfha')
           return "Could not compute"
        else:
            result = ""
            pod0 = response['pod'][0]
            pod1 = response['pod'][1]
            print(pod0)
            print(pod1)
            if pod1 and (('result') in pod1['@title'].lower()) or (pod1.get('@primary', 'false') == 'true') or (
                    'definition' in pod1['@title'].lower()):
                result = self.list_or_dict(pod1['subpod'])
                print(f"the result value is{result}")
                return result
            else:
                question = self.list_or_dict(pod0['subpod'])
                print(f"the retruned question is{question}")
                return question
                
            
            
            
    
    def list_or_dict(self,var):
        if isinstance(var, list) and var:
            return var[0]['plaintext']
        elif isinstance(var, dict):
            return var['plaintext']
        else:
            return ''
        
        
    def tell_time(self):
        say_time= datetime.datetime.now().strftime("%I:%M %p")
        print(type(say_time))
        print(f"sir the time is {say_time}")
        time.sleep(0.5)
        return say_time
        
        
        

    
    def play_on_text_divide(self,query):
        stop_words=['play','on','in','open','show','display','youtube','spotify']
        words=word_tokenize(query)
        filtered_words = [word for word in words if word.lower() not in stop_words]
        filtered_sentence = ''.join(filtered_words)
        print(filtered_sentence)
        return filtered_sentence

        
    

    def search_wikipedia(self, query=""):
        wikipedia.set_lang("en")
        search_results = wikipedia.search(query)
        if not search_results:
            print('No Wikipedia results')
            return 'No results received'

        try:
            wikipage = wikipedia.page(search_results[0])
            print(wikipage.title)
            wiki_summary = str(wikipage.summary)
            return wiki_summary
        except wikipedia.DisambiguationError as error:
            print(f"Disambiguation Error: {error}")
            return f"Disambiguation Error: {error}"
        except wikipedia.PageError as error:
            print(f"Page Error: {error}")
            return f"Page Error: {error}"



    def check_query_for_urls(self, query_str):
        doc = self.nlp(query_str)
        urls = [token.text for token in doc if token.like_url]
        print(f'The available URLs in the query are {urls}')
        return urls
    



    def open_book(self, query):
        doc = self.nlp(query)
        phrases_to_remove = ['textbook about', 'me', 'text','textbook', 'book', 'show', 'about', 'regarding', 'on', 'a', 'give']
        filtered_tokens = [token.text for token in doc if token.text.lower() not in map(str.lower, phrases_to_remove)]
        print("Filtered Tokens:", filtered_tokens)
        if len(filtered_tokens) == 1:
            filtered_sentence = ''.join(filtered_tokens)
        else:            
            filtered_sentence = '+'.join(filtered_tokens)
        print(filtered_sentence)
        return f"https://openlibrary.org/search?q={filtered_sentence}&mode=everything"
        

    def analyse_and_search(self,query):
        doc = self.nlp(query)
        entities=[token.text for token in doc.ents]
        if entities:
            search_sentence = ''.join(entities)
            listOfSeraches = search(search_sentence,num=5,stop=5,pause=3)
            return listOfSeraches
        else:
            print('No results found')
            return 'None'
    
    def app_name_extract(query):
        pattern = r"send a message to (.+?) saying (.+)" 
        pattern2=r"send a text message to (.+?) saying (.+)"
        match = re.match(pattern, query, re.IGNORECASE)
        match2=re.match(pattern2,query,re.IGNORECASE)
        if match:
            name = match.group(1).strip()
            message_content = match.group(2).strip()
            return name, message_content
        elif(match2):
            name = match2.group(1).strip()
            message_content = match2.group(2).strip()
            return name,message_content
        else:
            return None

        
            
           

   
            
    

voice_assistant = MyAssistant()



def process_index_value(index_value,query):
            if  index_value == 1:
                index_value = None
                return 'I am an AI voice assistant being developed by Ganii and Srikar' 
                

            if  index_value == 0:
                index_value = None
                return "I am fine, what about you, sir"

            if  index_value == 2:
                check_url_command = voice_assistant.check_query_for_urls(query)
                index_value = None
                if check_url_command:
                    return check_url_command[0]
                else:
                    return 'Unable to track the address of the required webpage, please speak clearly'

            if  index_value == 3:
                index_value = None
                News_data = voice_assistant.get_india_news()
                print(News_data)
                return News_data

            if  index_value == 4:
                index_value = None
                doc = voice_assistant.word_token(query)
                tokens = [token for token in doc]
                if 'translator' in tokens:
                    return "Translator Turned on"
                else:
                    return "Analyzer turned on"

            if  index_value == 5:
                index_value = None
                print(type(query))
                lastword_of_query = word_tokenize(query)[-1]
                print(type(lastword_of_query))
                print(lastword_of_query)
                content = voice_assistant.play_on_text_divide(query)
                return voice_assistant.search_and_play_on_source(content, lastword_of_query)

            if  index_value == 6 or  index_value == 7 or  index_value == 8:
                index_value = None
                returnValue = voice_assistant.search_wolfram_alpha(query)
                print(f"the returned value is {returnValue}")
                return returnValue
            if  index_value == 9:
                index_value = None
                jokeReturn = voice_assistant.tell_me_a_joke()
                return jokeReturn

            if  index_value == 10:
                index_value = None
                retuRnStateMent = voice_assistant.open_book(query)
                print(retuRnStateMent)
                return retuRnStateMent
                

            if  index_value == 11:
                index_value=None
                result = voice_assistant.app_name_extract(query)
                if(result):
                    name, message_content = result
                    print(f"Name: {name}, Message: {message_content}")
                    return f'{{"Name": "{name}", "Message_extract": "{message_content}"}}'
                else:
                    return "SyntaxError: Send a message to [name] saying [message]"

                

            if  index_value == 12:
                index_value = None
                time = voice_assistant.tell_time()
                return time


            if  index_value == 19 or  index_value == -1:
                return "Good bye sir"

@app.route('/textanalysis/<query>', methods=['GET'])
def voice_assistant_endpoint(query:str):
            print(f"the recieved query in text analysis is {query}")
            indexValue=voice_assistant.preprocess_query(query)
            ReturnValue=process_index_value(indexValue,query)
            print(ReturnValue)
            FinalReturn={'index':indexValue,'text':ReturnValue}
            return FinalReturn
        
@app.route('/speaktext/<query_2>/<index>', methods=['GET'])
def speak_text_main(query_2:str,index: int):
    print(f'Received Query: {query_2}, Index: {index}')
    print(type(index))
    index = int(index)
    print(type(index))
    if index == 1:
        return "I'm an AI voice assistant being developed by Gani and Srikar"
    elif index == 0:
        return "I'm fine. What about you, sir?"
    elif index == 3:
        return 'Here are some of the news I have found on the internet'
    elif index==5:
        return 'Sure'
    elif index==6 or index==7 or index==8:
        return query_2
    elif index==9:
        return query_2
    elif index==10:
        return "Opening book"
    elif index==11:
        return "opening clock on your device"
    elif index==12:
        return f"The time is {query_2}"
    elif index==13:
        return "opening microsoft word"
    elif index==14:
        return "Opening note pad"
    elif index==15:
        return "opening microsoft word"
    elif index==16:
        return "opening microsoft power point"
    elif index==17:
        return "opening calculator"


        

emotion_mapping = {
    "joy": {"reply_low": "Feeling happy? That's great!", "reply_medium": "You seem quite joyful!", "reply_high": "Wow, you're really spreading joy!"},
    "sadness": {"reply_low": "Cheer up! Things will get better.", "reply_medium": "I'm sorry you're feeling this way.", "reply_high": "It's okay to feel sad. I'm here for you."},
    "fear": {"reply_low": "It's okay to be cautious.", "reply_medium": "Feeling a bit fearful? I understand.", "reply_high": "Let's talk about what's causing fear."},
    "love": {"reply_low": "I love you too!", "reply_medium": "You're feeling quite affectionate!", "reply_high": "You're overflowing with love!"},
    "surprise": {"reply_low": "That's a bit unexpected!", "reply_medium": "You seem surprised. What happened?", "reply_high": "You're really surprised, aren't you?"},
    "anger": {"reply_low": "Take a deep breath. It'll be okay.", "reply_medium": "Feeling a bit angry? Let's talk it out.", "reply_high": "Seems like you're quite angry. Let's find a solution."}
}

@app.route('/personalSentenceAnalysis/<statement>',methods=['GET'])
def process_emotion_statement(statement):
    print(f"The given statement is: {statement}")
    prediction = classifier(statement, top_k=1)

    if prediction:
        predicted_emotion = prediction[0]['label']
        emotion_score = prediction[0]['score']

        emotion_info = emotion_mapping.get(predicted_emotion, {"reply_low": "I'm not sure how to respond."})

        if emotion_score < 0.9:
            reply = emotion_info.get("reply_low", "I'm not sure how to respond.")
            image= f"{predicted_emotion}_lv1"
        elif 0.9 <= emotion_score <= 0.95:
            reply = emotion_info.get("reply_medium", "I'm not sure how to respond.")
            image=f"{predicted_emotion}_lv2"
        elif(emotion_score >0.95):
            reply = emotion_info.get("reply_high", "I'm not sure how to respond.")
            image= f"{predicted_emotion}_lv3"

        print(f"Predicted Emotion: {predicted_emotion}")
        print(f"Emotion Score: {emotion_score}")
        print(f"Reply: {reply}")

        return {"image": image,"reply":reply}

    else:
        print("No prediction received.")

@app.route('/SentimentSpeak/<sentence_2>',methods=['GET'])
def speak_sentiment_reply(sentence_2:str):
    print(f"the sentece to sepak for sentiment is {sentence_2}")
    return sentence_2

@app.route('/analyseText/<text_analyse>',methods=['GET'])
def textanalyseFunc(text_analyse):
    print(text_analyse)
    listOfReturnValues = list(voice_assistant.analyse_and_search(text_analyse))
    for result in listOfReturnValues:
        print(result)
    print(type(listOfReturnValues))
    return listOfReturnValues

    


        
if __name__ == '__main__':
        app.run(host='127.0.0.1', port=8000)  