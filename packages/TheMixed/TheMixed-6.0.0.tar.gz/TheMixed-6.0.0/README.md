# TEXT_ANALYSIS_extracting_diseases_places_keywords
This repository contains code used gensim,en_core_web_sm and en_ner_bc5cdr_md to Generate pictures and word clouds of diseases, locations, key words in a paper.
## Content
1.a pipeline to detect chimeric reads from direct RNA-seq data  
2.a custom script to verify insertion with raw sequencing data  
3.codes to generate Figures
## Prerequisites
All codes were run and tested on Linux

* Python >=3.8  
* scispacy 
* en-ner-bc5cdr-md
* en-core-web-sm 
* beautifulsoup4
* wordcloud
* gensim 
* nltk
## Workflow for direct diseases, locations, key words in a paper
### Input:
"PMC"+Complete number
### Output:
#### 1. The histogram and word clouds of top3 words about diseases : 
The abscissa of the bar graph represents the word, and the ordinate represents the number of times the word appears in the text  
The size of the word in the word cloud depends on the frequency of the word in the text
#### 2. The histogram and word clouds of top3 words about locations : 
The abscissa of the bar graph represents the word, and the ordinate represents the number of times the word appears in the text  
The size of the word in the word cloud depends on the frequency of the word in the text
#### 3. The histogram and word clouds of top3 words about key words : 
The abscissa of the bar graph represents the word, and the ordinate represents weight(tf_idf) of the word,the weight=word_freq*log(the number of total text/Number of texts containing the word)
The size of the word in the word cloud depends on the weight(tf_idf) of the word in the text
### Steps:
* Step.1: Enter the PMC number you want to query.
* Step.2: Use beautifulsoup to crawl the web page information of the paper, and then use xml etree. Elementtree package to transform web page information into XML for analysis.
* Step.3: Extract thesis information from XML file
>* Step.3.1: ABOUT KEY_WORD:  
   > Extract the text information from the converted XML file: filter the text information of 'abstract', 'intro','methods','discuss','results','case','concl','abbr','fig','table' attributes in the XML file, because the keywords in the article mainly come from the 'Abstract','concl'parts in the XML file. In order to highlight the information of' Abstract','concl' parts and improve the weight of this part(Because of the tfidfmodel algorithm, all other articles that need to call the article library extract the words in the article for analysis.)
>* Step.3.2: ABOUT DISEASE:   
   >  Extract body information from the converted XML file: filter the text information of 'Abstract','intro','methods','exclude','results','case','concl','abbr','fig','table'attributes in the XML file
>* Step.3.3: ABOUT LOCATION:  
> Extract body information from the converted XML file: filter the text information of 'Abstract','intro','methods','exclude','results','case','concl','abbr','fig','table'attributes in the XML file
* Step.4:Conduct preliminary text analysis
>* Step.4.1: ABOUT KEY_WORD:  
> Remove redundant spaces, line breaks, numbers and some punctuation in the text. Then morpheme all words in the text (convert all words into prototypes),In order to improve the efficiency of program analysis, the stopworld package of nltk library is loaded to remove useless high-frequency words.
 >* Step.4.2: ABOUT DISEASE:  
> Remove redundant spaces, line breaks, numbers and some punctuation in the text. And reduce all words to lowercase,In order to improve the efficiency of program analysis, the stopworld package of nltk library is loaded to remove useless high-frequency words.
>* Step.4.3: ABOUT LOCATION:   
> Remove redundant spaces, line breaks, numbers and some punctuation in the text. And reduce all words to lowercase,In order to improve the efficiency of program analysis, the stopworld package of nltk library is loaded to remove useless high-frequency words.
* Step.5: Text analysis
>* Step.5.1: ABOUT KEY_WORD:  
> Use trigram to enumerate all the possibilities and turn the individual words in the article into three word phrases,Tfidfmodel algorithm is used to allocate the weight of trigram.
>* Step.5.2: ABOUT DISEASE:  
> Use the en_ ner_ bc5cdr_ MD model of the scispacy  to find out the special medical words in the text, and then select the words with "labs" as DISEASE,and count the number of times words appear in the article.
>* Step.5.3: ABOUT LOCATION:  
> Use NLP to process documents and analyze the part of speech of all words in a sentence and find the word whose key value is ' GPE ',count the number of times words appear in the article.
* Step.6: Generate histogram and word cloud.
>* Step.6.1: ABOUT KEY_WORD:  
> Generate histogram using Matplotlib, The abscissa of the bar graph represents the word, and the ordinate represents weight(tf_idf) of the word,the weight=word_freq*log(the number of total text/Number of texts containing the word)  
Generate word cloud using wordcloud, The size of the word in the word cloud depends on the weight(tf_idf) of the word in the text
>* Step.6.2: ABOUT DISEASE:  
> Generate histogram using Matplotlib, The abscissa of the bar graph represents the word, and the ordinate represents the number of times the word appears in the text  
Generate word cloud using wordcloud, The size of the word in the word cloud depends on the frequency of the word in the text
>* Step.6.3: ABOUT LOCATION:
> Generate histogram using Matplotlib, The abscissa of the bar graph represents the word, and the ordinate represents the number of times the word appears in the text  
Generate word cloud using wordcloud, The size of the word in the word cloud depends on the frequency of the word in the text
## Usage
```
import os
import nltk
import gensim
import re
import spacy
from bs4 import BeautifulSoup 
import re 
import urllib.request, urllib.error
import scispacy
import en_ner_bc5cdr_md
from MainWord import ForTheMainWord 

MainWord.To_Generate_Disease(6988269)
MainWord.To_Generate_Location(6988269)
MainWord.To_Generate_Key_Word(6988269)

```
## Citation
Base the en-ner-bc5cdr-md,en-core-web-sm and gensim 
## Acknowledgements
We would like to thank *********** and *********** for their code on how to perform permutation tests and plot the results provided at TEXT_ANALYSIS which was adjusted and used in this project.


