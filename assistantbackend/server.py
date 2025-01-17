import langcodes
from langdetect import detect
from unidecode import unidecode
from transformers import BertTokenizer, BertModel,pipeline
import nltk
from nltk.tokenize import word_tokenize
import torch.nn.functional as F
import tkinter as tk
import torch
import pyttsx3
from googlesearch import Search
import time
import platform
from summarize_pdf import analyze_pdf
import datetime
import wolframalpha
import time
import wikipedia
import spacy
import requests
import speech_recognition as sr
import webbrowser
import numpy as np
import subprocess
from googletrans import Translator
from unidecode import unidecode
from pydantic import BaseModel
from check import check_query_for_urls_2




nlp = spacy.load("en_core_web_sm")

nltk.download('punkt_tab')
nltk.download('punkt')

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
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        self.engine.setProperty('volume', 1) 
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



    @staticmethod
    def find_most_similar_sentence(self, sentence_array, test_sentence_embedding, most_similar_index, eligibility):
        most_similar_index = -1
        cosine_similarities_values = self.check_accurate(sentence_array, test_sentence_embedding, eligibility)
        print(f'The cosine similarities are {cosine_similarities_values}')

        for i, item in enumerate(cosine_similarities_values):
            if item >= 0.780 and item == np.max(cosine_similarities_values):
                print(item)
                most_similar_index = i
        
        return most_similar_index
    
    
    
    @staticmethod
    def preprocess_query(self, sentence_test):
        well_being = "how are you"       
        enquire_self = "who are you"     
        browser_open = "open amazon.com" 
        news_teller = "Tell me news"     
        turn_sentence = "translate the sentence how are you into telugu"   
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
        summarize= "summarize my pdf" 
        exit_="turn off"    

        
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
                         summarize,
                         exit_
                         ]
        most_similar_index = None
        eligibility = []
        test_embedding = self.get_sentence_embedding(self,sentence_test)
        most_similar_index = self.find_most_similar_sentence(self,sentencearray, test_embedding, most_similar_index, eligibility)

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
        if(last_word.lower() =='youtube'):
           webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
        elif(last_word.lower() =='spotify'):
            webbrowser.open( f"https://open.spotify.com/search/{query}")
        else:
            return 'opening or playing in only youtube and spotify are available for instance'

            
            
    def open_process(self, file):
        path = r"C:\Program Files\Google\Chrome\Application"  # Path to the Chrome folder
        file_path = f"{path}\\{file}"  # Combining the path with the file name
        
        # Open the file (chrome.exe or another file)
        subprocess.run([file_path])
            
        
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

    @staticmethod
    def check_query_for_urls(query_str):
        doc = nlp(query_str)
        urls = [token.text for token in doc if token.like_url]
        print(f'The available URLs in the query are {urls}')
        return urls
    



    def open_book(self, query):
        doc = self.nlp(query)
        phrases_to_remove = ['textbook about', 'me', 'text','textbook', 'book', 'show', 'about', 'regarding', 'on', 'a', 'give','ok','open','display']
        filtered_tokens = [token.text for token in doc if token.text.lower() not in map(str.lower, phrases_to_remove)]
        print("Filtered Tokens:", filtered_tokens)
        if len(filtered_tokens) == 1:
            filtered_sentence = ''.join(filtered_tokens)
        else:            
            filtered_sentence = '+'.join(filtered_tokens)
        print(filtered_sentence)
        return f"https://openlibrary.org/search?q={filtered_sentence}&mode=everything"
        

    
    def is_valid_language(self, lang_name2):
        """Check if the language name corresponds to a valid language code using langcodes."""
        lang_name = lang_name2.lower()
        try:
            # Validate the language using langcodes
            language = langcodes.Language.get(lang_name)
            print(f"the langcode of the {lang_name} is {language}")
            if language.is_valid():
                return language.language
            else:
                return None
        except Exception as e:
            print(f"Error validating language: {e}")
            return None
        

        
    def translate(self, text):
        """Translate the given text into the target language."""
        if 'quit translator' in text.lower():
            print("Exiting translator...")
            return "Translator has been turned off."

        try:
            # Step 1: Detect source language
            source_lang = self.detect_language(text)
            if not source_lang:
                return "Could not detect source language."

            print(f"Detected source language: {source_lang}")

            # Step 2: Ask user for target language
            print("Please say the target language for translation.")
            target_lang_name = self.recognize_speech()  # Get the target language via speech recognition
            print(f"detetcted target language is {target_lang_name}")
            if target_lang_name:
                # Step 3: Check if the target language is valid using langcodes
                target_lang = self.is_valid_language(target_lang_name)
                if target_lang:

                # Step 4: Translate text to the target language
                    translation = self.translator.translate(text=text, src=source_lang, dest=target_lang)
                    translated_text = translation.text
                else:
                    print(f"Invalid target lang code observed {target_lang}")

                # Handle non-None translation result
                if translated_text:
                    print(f"Translated text: {translated_text}")
                    english_version = unidecode(translated_text)  # Remove accents for clearer English version
                    print(f"Translated into English (simplified): {english_version}")
                    return english_version
                else:
                    print("Translation failed: Result is None")
                    return "Translation Failed"
            else:
                print("No target language specified.")
                return "Target language not recognized."

        except Exception as e:
            print(f"Translation failed: {e}")
            return "Translation Error"


    def detect_language(self, text):
        """Detect the source language of the input text."""
        try:
            lang = detect(text)
            return lang
        except Exception as e:
            print(f"Error detecting language: {e}")
            return None

    def recognize_speech(self):
        """Listen to the user's speech and return it as text."""
        with sr.Microphone() as source:
            self.speak("tell the target language sir")
            
            try:
                self.listener.adjust_for_ambient_noise(source)
                input_speech = self.listener.listen(source)
                print("Recognizing speech...")
                query = self.listener.recognize_google(input_speech, language='en_gb')
                print(f"You said: {query}")
                return query
            except sr.UnknownValueError:
                print("Sorry, I could not understand the audio.")
                return None
            except sr.RequestError:
                print("Error with the speech recognition service.")
                return None




    def get_news_titles(self):
        # Construct the API URL
        url = f'https://newsapi.org/v2/everything?q=tesla&from=2024-11-14&sortBy=publishedAt&apiKey=c8834b21ea0a4533906d2ed0ae697e10'

        try:
            response = requests.get(url)

            # Check if the response is successful
            if response.status_code != 200:
                error_message = response.json().get('message', 'Unknown error')
                print(f"Error: {error_message}")
                return f"API Error: {error_message}"

            # Parse the response JSON
            data = response.json()
            print(data)
            articles = data.get('articles', [])

            # Extract titles
            titles = [article.get("title") for article in articles if article.get("title")]

            if not titles:
                print("No titles found for the given parameters.")
                return "No titles found for the specified criteria."

            # Print the titles
            for i, title in enumerate(titles[:3], start=1):
                print(f"{i}. {title}")

            return titles[:2]

        except requests.exceptions.RequestException as e:
            print(f"Network error: {e}")
            return "Network error occurred. Please check your connection and try again."
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return "An unexpected error occurred. Please try again later."



    
    def analyse_and_search(self,query):
        doc = self.nlp(query)
        entities=[token.text for token in doc.ents]
        if entities:
            search_sentence = ''.join(entities)
            listOfSeraches = Search(search_sentence,num=5,stop=5,pause=3)
            return listOfSeraches
        else:
            print('No results found')
            return 'None'


    def speak(self,text):        
        self.engine.say(text)
        self.engine.runAndWait()
    @staticmethod
    def process_index_value(self,index_value,query):
                if  index_value == 1:
                    index_value = None
                    self.speak('I am an AI voice assistant being developed by Ganii and Srikar')
                    return 'I am an AI voice assistant being developed by Ganii and Srikar' 
                    

                if  index_value == 0:
                    index_value = None
                    self.speak("I am fine, what about you, sir")
                    return "I am fine, what about you, sir"

                if  index_value == 2:
                    index_value = None
                    check_url_command = check_query_for_urls_2(query)
                    print(f"the urls in fi statement is {check_url_command}")
                    if check_url_command:
                        url = check_url_command[0]
                        print(type(url))
                        print(f"the url is {url}")
                        self.speak(f"Opening {check_url_command}")
                        self.Open_browser(url)
                        return url
                    else:
                        self.speak("Unable to track the address of the required webpage, please speak clearly")
                        return 'Unable to track the address of the required webpage, please speak clearly'

                if  index_value == 3:
                    index_value = None
                    News_data = self.get_news_titles()
                    self.speak(News_data)
                    

                if  index_value == 4:
                    index_value = None
                    doc = nlp(query)
                    print(doc)
                    tokens = [token.text for token in doc]
                    if 'translate' in tokens:
                        print(f"the doc is {doc}")
                        self.translate(query)
                        return "Translator Turned on"
                    else:
                        return "Analyzer turned on"

                if  index_value == 5:
                    index_value = None
                    print(type(query))
                    lastword_of_query = word_tokenize(query)[-1]
                    print(type(lastword_of_query))
                    print(lastword_of_query)
                    content = self.play_on_text_divide(query)
                    sample = self.search_and_play_on_source(content, lastword_of_query)

                if  index_value == 6 or  index_value == 7 or  index_value == 8:
                    index_value = None
                    returnValue = self.search_wolfram_alpha(query)
                    self.speak(returnValue)
                    return returnValue
                


                if  index_value == 9:
                    index_value = None
                    jokeReturn = self.tell_me_a_joke()
                    self.speak(jokeReturn)
                    return jokeReturn

                if  index_value == 10:
                    index_value = None
                    retuRnStateMent = self.open_book(query)
                    self.speak("opening book")
                    print(retuRnStateMent)
                    return retuRnStateMent
                    

                if  index_value == 11:
                    index_value = None
                    self.speak("Opening clock")
                    subprocess.run("start ms-clock:", shell=True)
                    return "ms-clock:"

                if  index_value == 12:
                    index_value = None
                    time = self.tell_time()
                    self.speak(time)
                    return time

                if  index_value == 13:
                    index_value = None
                    self.speak("Opening chrome for you")
                    self.open_process("chrome.exe")
                    return "chrome.exe"

                if  index_value == 14:
                    index_value = None
                    self.speak("Opening notepad for you")
                    self.open_process("notepad.exe")
                    return "notepad.exe"

                if  index_value == 15:
                    index_value = None
                    self.speak("Opening Microsoft Word for you")
                    self.open_process("WINWORD.exe")
                    return "WINWORD.EXE"

                if  index_value == 16:
                    index_value = None
                    self.speak("Opening Microsoft Excel for you")
                    self.open_process("EXCEL.exe")
                    return "EXCEL.EXE"

                if  index_value == 17:
                    index_value = None
                    self.speak("Opening Microsoft Powerpoint for you")
                    self.open_process("POWERPNT.exe")
                    return "POWERPNT.EXE"

                if  index_value == 18 or  index_value == -3:
                    index_value = None
                    self.speak("Opening calculator for you")
                    self.open_process("calc.exe")
                    return "calc.exe"
                
                if index_value == 19 or index_value== -2:
                    index_value= None
                    analyze_pdf()

                if  index_value == 20 or  index_value == -1:
                    self.speak("Turning off Good bye sir")
                    return "Good bye sir"

            
    def speak_text_main(query_2:str,index: int):
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


    def Open_browser(self,url):
        webbrowser.open(url=url)
    
    def RecordVoice(self):
        print('Listening for commands...')
        while True:
            query = None
            try:
                with sr.Microphone() as source:
                    print("Adjusting for ambient noise... Please wait.")
                    self.listener.adjust_for_ambient_noise(source, duration=1)
                    print("Listening...")
                    self.listener.pause_threshold = 2
                    input_speech = self.listener.listen(source)
                    print("Recognizing speech...")
                    query = self.listener.recognize_google(input_speech, language='en_gb')
                    print(f"The input speech was: {query}")
                    index = self.preprocess_query(self,query)
                    response = self.process_index_value(self,index, query)
                    print(f"Response: {response}")
                    if query.lower() in ["exit", "quit", "stop"]:
                        print("Exiting the continuous listening mode.")
                        return "Goodbye!"
                    return query
            except sr.UnknownValueError:
                print("Speech Recognition could not understand audio. Please try again.")
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")
            except Exception as exception:
                print(f"An error occurred: {exception}")

            

    emotion_mapping = {
        "joy": {"reply_low": "Feeling happy? That's great!", "reply_medium": "You seem quite joyful!", "reply_high": "Wow, you're really spreading joy!"},
        "sadness": {"reply_low": "Cheer up! Things will get better.", "reply_medium": "I'm sorry you're feeling this way.", "reply_high": "It's okay to feel sad. I'm here for you."},
        "fear": {"reply_low": "It's okay to be cautious.", "reply_medium": "Feeling a bit fearful? I understand.", "reply_high": "Let's talk about what's causing fear."},
        "love": {"reply_low": "I love you too!", "reply_medium": "You're feeling quite affectionate!", "reply_high": "You're overflowing with love!"},
        "surprise": {"reply_low": "That's a bit unexpected!", "reply_medium": "You seem surprised. What happened?", "reply_high": "You're really surprised, aren't you?"},
        "anger": {"reply_low": "Take a deep breath. It'll be okay.", "reply_medium": "Feeling a bit angry? Let's talk it out.", "reply_high": "Seems like you're quite angry. Let's find a solution."}
    }

    def process_emotion_statement(self,statement):
        print(f"The given statement is: {statement}")
        prediction = self.classifier(statement, top_k=1)

        if prediction:
            predicted_emotion = prediction[0]['label']
            emotion_score = prediction[0]['score']

            emotion_info = self.emotion_mapping.get(predicted_emotion, {"reply_low": "I'm not sure how to respond."})

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

    def speak_sentiment_reply(self,sentence_2:str):
        print(f"the sentece to sepak for sentiment is {sentence_2}")
        self.gui_instance.update_ring()
        return sentence_2


    def textanalyseFunc(self,text_analyse):
        print(text_analyse)
        listOfReturnValues = list(self.analyse_and_search(text_analyse))
        for result in listOfReturnValues:
            print(result)
        print(type(listOfReturnValues))
        return listOfReturnValues
        


            
if __name__ == "__main__":
    # Initialize the voice assistant
    assistant = MyAssistant()
    while True:
        assistant.RecordVoice()

    # Start the Tkinter GUI
    
    
