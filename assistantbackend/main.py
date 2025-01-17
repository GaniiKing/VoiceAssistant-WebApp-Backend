import time
import datetime
import platform
import spacy
import requests
import speech_recognition as sr
import numpy as np
from googletrans import Translator
from unidecode import unidecode
from transformers import BertTokenizer, BertModel, pipeline
import torch.nn.functional as F
import torch
from pvporcupine import Porcupine

class MyAssistant:
    def __init__(self):
        # Initialize components
        self.classifier = pipeline("text-classification", model='bhadresh-savani/roberta-base-emotion', return_all_scores=True)
        self.translator = Translator()
        self.listener = sr.Recognizer()
        self.nlp = spacy.load("en_core_web_sm")
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        self.model = BertModel.from_pretrained('bert-base-uncased')
        self.model.eval()
        self.chrome_path = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
        self.system = platform.system().lower()
        self.last_command_time = None  # Track the last command time for timeout

    def get_sentence_embedding(self, sentence):
        if not isinstance(sentence, str):
            sentence = str(sentence)
        tokens = self.tokenizer(sentence, return_tensors='pt')
        with torch.no_grad():
            outputs = self.model(**tokens)
        cls_embedding = outputs.last_hidden_state[:, 0, :]
        return cls_embedding

    def final_cosine_similarity(self, embedding1, embedding2):
        return F.cosine_similarity(embedding1, embedding2).item()

    def preprocess_query(self, sentence_test):
        sentencearray = ["how are you", "who are you", "open amazon.com", "Tell me news", "turn on translator", 
                         "play something on youtube", "calculate the value of something", "what is the something", 
                         "who is narendramodi", "tell me a joke", "open a text book about html", "open clock", 
                         "what is the time", "open chrome", "open notepad", "open microsoft word", "open excel", 
                         "open power point", "open calculator", "exit"]
                         
        test_embedding = self.get_sentence_embedding(sentence_test)
        most_similar_index = -1
        eligibility = []

        cosine_similarities_values = [self.final_cosine_similarity(test_embedding, self.get_sentence_embedding(sentence)) 
                                      for sentence in sentencearray]
        for i, similarity in enumerate(cosine_similarities_values):
            if similarity >= 0.780 and similarity == np.max(cosine_similarities_values):
                most_similar_index = i

        return most_similar_index

    def search_wikipedia(self, query=""):
        import wikipedia
        wikipedia.set_lang("en")
        search_results = wikipedia.search(query)
        if not search_results:
            return 'No results found'
        try:
            wikipage = wikipedia.page(search_results[0])
            return wikipage.summary
        except wikipedia.DisambiguationError as error:
            return f"Disambiguation Error: {error}"
        except wikipedia.PageError as error:
            return f"Page Error: {error}"

    def tell_time(self):
        return datetime.datetime.now().strftime("%I:%M %p")

    def tell_me_a_joke(self):
        try:
            url = "https://v2.jokeapi.dev/joke/Any?format=txt&safe-mode"
            response = requests.get(url)
            if response.status_code == 200:
                return response.content.decode('utf-8')
            else:
                return "Server connection error"
        except Exception as e:
            return "Could not compute at the moment."

    def record_voice(self, wake_word="hey g"):
        print("Listening for the wake word...")
        porcupine = Porcupine(library_path="path_to_pvporcupine_library", model_path="path_to_model", keyword_paths=["path_to_keyword_file"])

        while True:
            try:
                with sr.Microphone() as source:
                    audio = self.listener.listen(source)
                    print("Listening...")
                    detected_word = self.listener.recognize_google(audio)
                    if wake_word.lower() in detected_word.lower():
                        print(f"Wake word '{wake_word}' detected! Listening for command...")
                        query = self.listener.recognize_google(audio)
                        return query
            except sr.UnknownValueError:
                continue
            except sr.RequestError:
                print("Request error from Google Speech Recognition")
                break

    def listen_for_commands(self):
        """ Listen for commands continuously for a minute after the wake word is detected. """
        self.last_command_time = time.time()  # Record the time when the command is received
        while time.time() - self.last_command_time < 60:  # Keep listening for a minute
            query = self.record_voice(wake_word="")  # Just listen for any command
            if query:
                print(f"Received command: {query}")
                index = self.preprocess_query(query)
                response = process_index_value(index, query, self)
                print(f"Response: {response}")
                self.last_command_time = time.time()  # Reset the timeout countdown after a command
        print("No command received for 1 minute. Going back to listening for wake word.")

def process_index_value(index_value, query, assistant):
    if index_value == 0:
        return "I am fine, what about you?"
    elif index_value == 1:
        return 'I am an AI voice assistant being developed by Ganii and Srikar'
    elif index_value == 3:
        return assistant.tell_time()
    elif index_value == 5:
        return assistant.search_wikipedia(query)
    elif index_value == 9:
        return assistant.tell_me_a_joke()
    else:
        return "I didn’t understand that."

if __name__ == "__main__":
    assistant = MyAssistant()
    
    print("Voice assistant activated. Say 'assistant' to wake me up.")
    
    while True:
        # Listen for the wake word 'assistant'
        query = assistant.record_voice(wake_word="assistant")
        
        if query:
            print(f"Received command: {query}")
            index = assistant.preprocess_query(query)
            response = process_index_value(index, query, assistant)
            print(f"Response: {response}")
            # Listen for commands continuously for 1 minute before going back to listening for the wake word
            assistant.listen_for_commands()
