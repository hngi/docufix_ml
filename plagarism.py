from nltk.corpus import stopwords
import nltk
import pytesseract as pt
from PIL import Image
from googleapiclient.discovery import build
import PyPDF2
from bs4 import BeautifulSoup
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from gensim import corpora
import gensim
from difflib import SequenceMatcher

stop_words = stopwords.words("english")
extensions1 = ['jpg','png','jpeg','bmp','svg']
extensions2= ['pdf']
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
    file = open(filename, 'rb')
    filereader = PyPDF2.PdfFileReader(file)
    c = filereader.numPages
    d = ''
    for i in range(c):
        pageObj = filereader.getPage(i)
        d = d+' '+ pageObj.extractText()
    return d
def google_search(search_term, api_key, cse_id, **kwargs):
          service = build("customsearch", "v1", developerKey=api_key)
          res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
          return res['items']
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
   NUM_TOPICS = 15
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
        c =''
        for j in i:
            c=c+' '+j
        tp.append(c)
   my_api_key = "AIzaSyCaugQenN9PpH5I6agQTcFlkf8hbyAEOKw"
   my_cse_id = "000757437883487112859:wtcjp5mwqmu"
   gg =[]
   for m in tp:     
       results= google_search(m,my_api_key,my_cse_id,num=5)
       j = []    
       for result in results:   
           url=result["link"]   
           # Make a GET request to fetch the raw HTML content
           html_content = requests.get(url).text    
            # Parse the html content
           soup = BeautifulSoup(html_content, "lxml")
           v = soup.body.text# print the parsed data of html
           j.append(v)
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
    c=[]
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
    c.append(l)
    if max(c)>=0.5:
        pp = 'Plagiarised'
    else:
        pp = 'No Plagiarised info found'
    return pp
        
