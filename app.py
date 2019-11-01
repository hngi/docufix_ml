from nltk.corpus import stopwords
import nltk
import pytesseract as pt
from PIL import Image
from googleapiclient.discovery import build
import PyPDF2
import fitz
from bs4 import BeautifulSoup
import requests
from gensim import corpora
import gensim
from difflib import SequenceMatcher
from gingerit.gingerit import GingerIt
from flask import Flask, request,render_template

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg','bmp','pdf','svg','epub'])
app = Flask(__name__,template_folder='C:/Users/Ademola/OneDrive/folder/OneDrive/Documents/template')
#UPLOAD_FOLDER = '/templates/uploads/'

stop_words = stopwords.words("english")
extensions1 = ['jpg','png','jpeg','bmp','svg']
extensions2= ['pdf','xps','epub']
pt.pytesseract.tesseract_cmd = '/app/.apt/usr/bin/tesseract'
#picture function
# route and function to handle the upload page
@app.route('/',methods=['POST','GET'])
def home():
    return render_template('home.html')
@app.route('/upload', methods=['GET', 'POST'])
def upload_page():
    if request.method == 'POST':
        # check if there is a file in the request
        if 'file' not in request.files:
            return render_template('upload.html', msg='No file selected')
        file = request.files['file']
        # if no file is selected
        if file.filename == '':
            return render_template('upload.html', msg='No file selected')

        if file and allowed_file(file.filename):
            try:
                if file.filename.rsplit('.',1)[1].lower() in extensions1:
                    c = picture(file.filename)
                elif file.filename.rsplit('.',1)[1].lower() in extensions2:
                   c = pdf(file.filename)
                else:
                   c = txt(file.filename)
            except IndexError:
                c= txt(file)
            extracted_text = sim(c)
            if extracted_text == '':
                replyy = 'Sorry Character could not be clearly recognized'
                return render_template('upload.html',
                                   msg=replyy)
            # extract the text and display it
            return render_template('upload.html',
                                   msg='Result',
                                   extracted_text=extracted_text)
    
    return render_template('upload.html')
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
def picture(filename):
    s = Image.open(filename)
    text = pt.image_to_string(s)
    return text
#text function
def txt(text):
    t = open(text)
    return t
def pdf(filename):
    file = open(filename,'rb')
    filereader = PyPDF2.PdfFileReader(file)
    doc = fitz.open(filename)
    c = filereader.numPages
    d = ''
    for i in range(c):
        pageObj = doc.loadPage(i)
        d = d+' '+ pageObj.getText("text")
    return d
def google_search(search_term, api_key, cse_id, **kwargs):
    try:
          service = build("customsearch", "v1", developerKey=api_key)
          res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
          return res['items']
    except KeyError:
        return 'Bad Request'
def check(text):
         p = GingerIt()
         q = p.parse(text)
         return q['result']
#get the words
def word(c):
   tok_text = nltk.sent_tokenize(c)
   f_text=[]
   for s in tok_text:
       tk_txt = nltk.word_tokenize(s)
       final_text = []
       for i in tk_txt:
           if i not in stop_words:
               final_text.append(i)
       f_text.append(final_text)
   dictionary = corpora.Dictionary(f_text)
   corpus = [dictionary.doc2bow(text) for text in f_text]
   import pickle
   pickle.dump(corpus, open('corpus.pkl', 'wb'))
   dictionary.save('dictionary.gensim') 
   NUM_TOPICS = 20
   ldamodel = gensim.models.ldamodel.LdaModel(corpus, num_topics = NUM_TOPICS, id2word=dictionary, passes=15)
   ldamodel.save('model1.gensim')
   from gensim.parsing.preprocessing import preprocess_string, strip_punctuation,strip_numeric
   lda_topics = ldamodel.show_topics(num_words=5)
   topics = []
   filters = [lambda x: x.lower(), strip_punctuation, strip_numeric]
   for topic in lda_topics:
    topics.append(preprocess_string(topic[1], filters))
   tp = []
   for i in topics:
        y =''
        for j in i:
            y=y+' '+j
        tp.append(y)
   my_api_key = "AIzaSyCaugQenN9PpH5I6agQTcFlkf8hbyAEOKw"
   my_cse_id = "000757437883487112859:wtcjp5mwqmu"
   gg =[]
   for m in tp:
       e = check(m)
       results= google_search(e,my_api_key,my_cse_id,num=5)
       j = []    
       for result in results:   
           url=result["link"]   
           html_content = requests.get(url) 
           soup = BeautifulSoup(html_content.content, 'html.parser',from_encoding="iso-8859-1")
           v = soup.findAll('p')
           bb=''
           for x in range(len(v)):
               vv = soup.find_all('p')[x].get_text()
               bb = bb+' '+vv
           j.append(bb)
       gg.append(j)
   return gg
def cosine(a,b):
    return SequenceMatcher(None, a, b).ratio()
    
def sim(c):
    m = word(c)        
    cc=[]
    for i in m:
       b =[]
       xt = []
       for j in i:
           if j not in stop_words:
               xt.append(j)
       fil = [x for x in xt if x.strip()]
       for k in fil:
           cosine_sim = cosine(c,k)
           b.append(cosine_sim)
       l= max(b)
    cc.append(l)
    if max(c)>=0.4:
        pp = 'Warning! Plagiarised text detected'
    else:
        pp = 'No Plagiarised info found'
    return pp

if __name__ == '__main__':
    app.run()
        