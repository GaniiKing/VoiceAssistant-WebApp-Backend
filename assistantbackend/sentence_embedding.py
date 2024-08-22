from flask import Flask 
import spacy 


app = Flask(__name__)

nlp = spacy.load("en_core_web_sm")
    
@app.route("/get_sentence_embedding/<sentence>",methods=['GET'])
def get_embeddings(sentence):
    doc = nlp(sentence)
    sentence_embedding = doc.vector
    sentence_embedding=sentence_embedding.tolist()
    return sentence_embedding

if(__name__)=="__main__":
    app.run()