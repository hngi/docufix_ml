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

stop_words = stopwords.words("english")
extensions1 = ['jpg','png','jpeg','bmp','svg']
extensions2= ['pdf','xps','epub']
#pt.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract'
#picture function
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
          service = build("customsearch", "v1", developerKey=api_key)
          res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
          return res['items']
def check(text):
         p = GingerIt()
         q = p.parse(text)
         return q['result']
#get the words
def word(filename_or_text):
   try:
       if filename_or_text.rsplit('.',1)[1].lower() in extensions1:
           c = picture(filename_or_text)
       elif filename_or_text.rsplit('.',1)[1].lower() in extensions2:
           c = pdf(filename_or_text)
       else:
           c = txt(filename_or_text)
   except IndexError:
       c= txt(filename_or_text)
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
    
def sim(filename_or_text):
    try:
       if filename_or_text.rsplit('.',1)[1].lower() in extensions1:
           c = picture(filename_or_text)
       elif filename_or_text.rsplit('.',1)[1].lower() in extensions2:
           c = pdf(filename_or_text)
       else:
           c = txt(filename_or_text)
    except IndexError:
       c= txt(filename_or_text)
    m = word(filename_or_text)        
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
        
