# -*- coding: utf-8 -*-
#!/usr/bin/env python3.6.3

try:
	from nltk.corpus import stopwords
except:
	nltk.download("stopwords")
	from nltk.corpus import stopwords
import nltk
from nltk.util import ngrams
import re

def remove_stopwords(words):
	""" Remove all the stop words from the list of words.

	Args:
		words: The list of words.

	Returns:
		The list of words without stopwords.

	"""
	return [word for word in words if word.lower() not in stopwords.words('spanish')]

def get_words_count(tweets, text_column=0):
	""" Generate the list of words with their respective count from a tweet.

	Args:
		tweets: The list of tweets.

	Returns:
		The list of words with their respective count.

	"""
	words_count = {}
	for tweet in tweets:
		t = re.sub(r"http\S+", "", tweet[text_column].rstrip(), flags=re.UNICODE)
		mentions = re.findall(r'\S*@\S*', t)
		t = re.sub(r'\S*@\S*', '', t, re.UNICODE)
		hashtags = re.findall(r'(?:^|\s)[＃#]{1}(\w+)', t)
		hashtags = ["#" + elem for elem in hashtags]
		t = re.sub(r'(?:^|\s)[＃#]{1}(\w+)', '', t, re.UNICODE)
		try:
			words = nltk.word_tokenize(t)
		except:
			nltk.download('punkt')
			words = nltk.word_tokenize(t)
		words = remove_stopwords(words)
		words = mentions + hashtags + words
		for w in words:
			w = w.lower() if not "@" in w and not "#" in w else w
			if "@" in w:
				w = re.sub(r'[^@\w\s]', '', w, re.UNICODE)
			elif "#" in w:
				w = re.sub(r'[^#\w\s]', '', w, re.UNICODE)
			elif not "@" in w or not "#" in w:
				w = re.sub(r'[^\w\s]', '', w, re.UNICODE)

			if w == "rt" or w == "" or len(w) <= 1:
				continue
			try:
				words_count[w] += 1
			except:
				words_count.update({w: 1})

	words_count = [[word, count] for word, count in words_count.items()]
	return sorted(words_count, key=lambda x: x[1], reverse=True)

# def get_bigrams_trigrams(tweets, text_column=0):
# 	""" Generate the list of words with their respective count from a tweet.

# 	Args:
# 		tweets: The list of tweets.

# 	Returns:
# 		The list of words with their respective count.

# 	"""
# 	words_count = {}
# 	for tweet in tweets:
# 		t = re.sub(r"http\S+", "", tweet[text_column].rstrip(), flags=re.UNICODE)

if __name__ == "__main__":

	tweets = [
		["Y entonces? Colón le dicen ahora a @Miguel_Pizarro https://t.co/anfxz2ntiI", 247],
		["Parece una foto mas bien https://t.co/4zdvlfCO56", 247],
		["@FONASA hola buen día. Consulta, mis padres son extranjeros y ya tiene rut pero aun están desempleados, podrían cot… https://t.co/AeRReRr6G6", 247],
		["@chunachokstillo Tonto, gracias por la info",247],
		["@chunachokstillo Tonto, gracias por la info #ajajajaj jaja asdasda asdasda asdasda;...",247],
		["Buenos días, ya sabemos que murió Hawking, no hay necesidad de que todo el mundo lo publique.", 247],
		["No es alegría, solo que no esperen contemplación con él RT @nelsonbocaranda: RT @felixseijasr: Nadie debe alegrarse… https://t.co/KXx2eRBAQW", 247],
		["Jajajajaja RT @DTVTotal: RT @TurcoHusain: Nobleza obliga hoy daré la cara en @DTVTotal y aguantare todo los golpes.… https://t.co/yCbRmZOQyV", 247]
	]

	print (get_words_count(tweets))