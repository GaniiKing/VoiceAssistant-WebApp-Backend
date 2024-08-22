from flask import Flask,jsonify
import spacy 

app = Flask(__name__)

nlp = spacy.load("en_core_web_sm")



@app.route("/get_sentence_embedding/<sentence>")
def get_embeddings(sentence):
    doc = nlp(sentence)
    sentence_embedding = doc.vector
    sentence_embedding=sentence_embedding.tolist()
    return jsonify(sentence_embedding)



@app.route("/bookNameExtract/<query>")
def bookNameExtract(query):
    doc = nlp(query)
    phrases_to_remove = ['textbook about', 'me', 'text','textbook', 'book', 'show', 'about', 'regarding', 'on', 'a', 'give','open']
    filtered_tokens = [token.text for token in doc if token.text.lower() not in map(str.lower, phrases_to_remove)]
    if len(filtered_tokens) == 1:
        filtered_sentence = ''.join(filtered_tokens)
    else:            
       filtered_sentence = '+'.join(filtered_tokens)
    return jsonify(filtered_sentence)

@app.route("/analyseandSearchList/<sentence>")
def getListOfAnalysation(sentence):
    doc = nlp(sentence)
    entities=[token.text for token in doc.ents]
    if entities:
        return jsonify(entities)
    else:
        return jsonify('None')
    
@app.route("/checkForURLs/<urlsentence>")
def checkForURLs(urlsentence):
    doc = nlp(urlsentence)
    urls = [token.text for token in doc if token.like_url]
    return jsonify(urls)


if(__name__)=="__main__":
    app.run()
