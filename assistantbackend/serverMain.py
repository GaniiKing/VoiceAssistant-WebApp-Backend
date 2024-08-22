from transformers import BertTokenizer, BertModel,pipeline
import nltk
from nltk.tokenize import word_tokenize
import torch.nn.functional as F
import torch
from googlesearch import search
import time
import platform
import datetime
import wolframalpha
import wikipedia
import spacy
import requests
import speech_recognition as sr
import webbrowser
import numpy as np
from googletrans import Translator
from unidecode import unidecode
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware




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
        nltk.download('punkt')
        self.classifier = pipeline("text-classification",model='bhadresh-savani/roberta-base-emotion', return_all_scores=True)
        self.translator = Translator()
        self.listener = sr.Recognizer()
        self.nlp = spacy.load("en_core_web_sm")
        self.indexValue = None
        self.chrome_path = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
        webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(self.chrome_path))
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        self.model = BertModel.from_pretrained('bert-base-uncased')
        self.model.eval()
        self.app_id = 'T7X889-YYLEJYT3HH'
        self.wolfram_client = wolframalpha.Client(self.app_id)
        self.system = platform.system().lower()
        
        
        

    @staticmethod
    def get_sentence_embedding(self, sentence):
        if not isinstance(sentence, str):
            sentence = str(sentence)

        tokens = self.tokenizer(sentence, return_tensors='pt')
        with torch.no_grad():
            outputs = self.model(**tokens)
        
        cls_embedding = outputs.last_hidden_state[:, 0, :]

        return cls_embedding



    @staticmethod
    def final_cosine_similarity(embedding1, embedding2):
        cosine_similarity = F.cosine_similarity(embedding1, embedding2).item()
        return cosine_similarity



    def check_accurate(self, sentence_array, test_embedding, eligibility):
        for sentence in sentence_array:
            sentence_embedding = self.get_sentence_embedding(self,sentence)
            similarity = self.final_cosine_similarity(test_embedding, sentence_embedding)
            eligibility.append(similarity)
        return eligibility




    def find_most_similar_sentence(self, sentence_array, test_sentence_embedding, most_similar_index, eligibility):
        most_similar_index = -1

        cosine_similarities_values = self.check_accurate(sentence_array, test_sentence_embedding, eligibility)
        print(f'The cosine similarities are {cosine_similarities_values}')

        for i, item in enumerate(cosine_similarities_values):
            if item >= 0.780 and item == np.max(cosine_similarities_values):
                print(item)
                most_similar_index = i

        return most_similar_index
    
    
    

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
        eligibility = []

        test_embedding = self.get_sentence_embedding(self,sentence_test)
        most_similar_index = self.find_most_similar_sentence(sentencearray, test_embedding, most_similar_index, eligibility)

        print(f"The most similar sentence is at index {most_similar_index}: {sentencearray[most_similar_index]}")
        self.indexValue = most_similar_index
        return most_similar_index
        
        
    
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
        

    
    def translate(self,text):
        if 'quit translator' in text:
            quit()
        else:
            try:
                print("translate_and_speak is executing upon receiving text from rec_to_translate")
                translation = self.translator.translate(text=text,src='en',dest='te')
                translated_text = translation.text
                if translated_text is not None:
                    print(type(translated_text))
                    print(f'Translated text: {translated_text}')
                    english_version = unidecode(translated_text)
                    print(f"Translated into english {english_version}")
                    return english_version
                else:
                    print("Translation failed: Result is None")
                    return "Translation Failed"

            except Exception as e:
                print(f"Translation failed: {e}")


    
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
            
           

   
            
    

voice_assistant = MyAssistant()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
                doc = voice_assistant.nlp(query)
                tokens = [token.text for token in doc]
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
                index_value = None
                return "ms-clock:"

            if  index_value == 12:
                index_value = None
                time = voice_assistant.tell_time()
                return time

            if  index_value == 13:
                index_value = None
                return "chrome.exe"

            if  index_value == 14:
                index_value = None
                return "notepad.exe"

            if  index_value == 15:
                index_value = None
                return "WINWORD.EXE"

            if  index_value == 16:
                index_value = None
                return "EXCEL.EXE"

            if  index_value == 17:
                index_value = None
                return "POWERPNT.EXE"

            if  index_value == 18 or  index_value == -2:
                index_value = None
                return "calc.exe"

            if  index_value == 19 or  index_value == -1:
                return "Good bye sir"

@app.get("/textanalysis")
async def voice_assistant_endpoint(query:str):
            print(f"the recieved query in text analysis is {query}")
            indexValue=voice_assistant.preprocess_query(query)
            ReturnValue=process_index_value(indexValue,query)
            print(ReturnValue)
            FinalReturn={'index':indexValue,'text':ReturnValue}
            return FinalReturn
        
@app.get("/speaktext")
async def speak_text_main(query_2:str,index: int):
    print(f'Received Query: {query_2}, Index: {index}')
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

@app.get('/recvoiceOnclick')
async def RecordVoice():
        print('Listening for a command in recieveOnclick function...')
        query = None
        with sr.Microphone() as source:
            voice_assistant.listener.pause_threshold = 2
            input_speech = voice_assistant.listener.listen(source)
        try:
            print('Recognizing speech...in recieve on click function...')
            query = voice_assistant.listener.recognize_google(input_speech, language='en_gb')
            print(f"the input speech was:{query} in recieve on click function...")
            return query
        except sr.UnknownValueError:
            print("Speech Recognition could not understand audio")
            return "Couldnot understand the audio try again"
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
            return "Could not understand the audio at the moment"
        except Exception as exception:
            print(f'I haven\'t caught that, would you mind trying again? {exception}')
            return 'I haven\'t caught that, would you mind trying again?'
        

emotion_mapping = {
    "joy": {"reply_low": "Feeling happy? That's great!", "reply_medium": "You seem quite joyful!", "reply_high": "Wow, you're really spreading joy!"},
    "sadness": {"reply_low": "Cheer up! Things will get better.", "reply_medium": "I'm sorry you're feeling this way.", "reply_high": "It's okay to feel sad. I'm here for you."},
    "fear": {"reply_low": "It's okay to be cautious.", "reply_medium": "Feeling a bit fearful? I understand.", "reply_high": "Let's talk about what's causing fear."},
    "love": {"reply_low": "I love you too!", "reply_medium": "You're feeling quite affectionate!", "reply_high": "You're overflowing with love!"},
    "surprise": {"reply_low": "That's a bit unexpected!", "reply_medium": "You seem surprised. What happened?", "reply_high": "You're really surprised, aren't you?"},
    "anger": {"reply_low": "Take a deep breath. It'll be okay.", "reply_medium": "Feeling a bit angry? Let's talk it out.", "reply_high": "Seems like you're quite angry. Let's find a solution."}
}

@app.get('/personalSentenceAnalysis')
async def process_emotion_statement(statement):
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

@app.get('/SentimentSpeak')
async def speak_sentiment_reply(sentence_2:str):
    print(f"the sentece to sepak for sentiment is {sentence_2}")
    return sentence_2

@app.get('/analyseText')
async def textanalyseFunc(text_analyse):
    print(text_analyse)
    listOfReturnValues = list(voice_assistant.analyse_and_search(text_analyse))
    for result in listOfReturnValues:
        print(result)
    print(type(listOfReturnValues))
    return listOfReturnValues
    


        
if __name__ == '__main__':
        app.run(app,host='127.0.0.1',port=8000)
        
