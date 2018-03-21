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
import string

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
		t = re.sub(r"http\S+", "", tweet[text_column].replace("…", ""), flags=re.UNICODE)
		mentions = re.findall(r'@\S*', t)
		t = re.sub(r'@\S*', '', t, re.UNICODE)
		hashtags = re.findall(r'#\S*', t)
		t = re.sub(r'#\S*', '', t, re.UNICODE)
		table = str.maketrans({key: None for key in string.punctuation if key != "@" and key != "#"})
		new_s = t.translate(table)  
		try:
			words = nltk.word_tokenize(new_s)
		except:
			nltk.download("punkt")
			words = nltk.word_tokenize(new_s)

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

def get_ngrams_count(tweets, text_column=0):
	""" Generate the list of ngrams with their respective count from a tweet.

	Args:
		tweets: The list of tweets.

	Returns:
		The list of ngrams with their respective count.

	"""
	ngrams_count = {}
	for tweet in tweets:
		t = re.sub(r"http\S+", "", tweet[text_column].replace("…", ""), flags=re.UNICODE)

		table = str.maketrans({key: None for key in string.punctuation if key != "@" and key != "#"})
		new_s = t.translate(table)
		
		mentions_old = re.findall(r'@\S*', t)
		hashtags_old = re.findall(r'#\S*', t)

		mentions = re.findall(r'@\S*', new_s)
		hashtags = re.findall(r'#\S*', new_s)

		for i in list(range(len(mentions))):
			mention = mentions_old[i]
			if not mention[-1].isalnum() and mention[-1] != "_":
				mention = mention[:-1]
			new_s = new_s.replace(mentions[i], mention)
		for i in list(range(len(hashtags))):
			hashtag = hashtags_old[i]
			if not hashtag[-1].isalnum() and hashtag[-1] != "_":
				hashtag = hashtag[:-1]
			new_s = new_s.replace(hashtags[i], hashtag)

		try:
			words = nltk.word_tokenize(new_s)
		except:
			nltk.download("punkt")
			words = nltk.word_tokenize(new_s)

		i = 0 
		new_words = []
		while i < len(words):
			if words[i].lower() == "rt" or words[i] == "":
				i += 1
				continue
			if words[i] == "#" or words[i] == "@":
				try:
					new_words.append(words[i] + words[i+1])
					i += 2
				except:
					new_words.append(words[i])
			else:
				new_words.append(words[i].lower())
			i += 1
			
		bigrams = ngrams(remove_stopwords(new_words), 2)
		trigrams = ngrams(remove_stopwords(new_words), 3)
		tetragrams = ngrams(remove_stopwords(new_words), 4)
		for t in tetragrams:
			try:
				if (t[0] + " " + t[1] + " " + t[2]) in ngrams_count.keys():
					continue
				ngrams_count[(t[0] + " " + t[1] + " " + t[2] + " " + t[3])] += 1
			except:
				ngrams_count.update({(t[0] + " " + t[1] + " " + t[2] + " " + t[3]): 1})
		for t in trigrams:
			try:
				if (t[0] + " " + t[1]) in ngrams_count.keys():
					continue
				ngrams_count[(t[0] + " " + t[1] + " " + t[2])] += 1
			except:
				ngrams_count.update({(t[0] + " " + t[1] + " " + t[2]): 1})
		for b in bigrams:
			try:
				ngrams_count[(b[0] + " " + b[1])] += 1
			except:
				ngrams_count.update({(b[0] + " " + b[1]): 1})

		
	ngrams_count = [[ngram, count] for ngram, count in ngrams_count.items()]
	return sorted(ngrams_count, key=lambda x: x[1], reverse=True)

if __name__ == "__main__":

	tweets = [
		["Y entonces? Colón le dicen ahora a @Miguel_Pizarro https://t.co/anfxz2ntiI", 247],
		["Parece una foto mas bien https://t.co/4zdvlfCO56", 247],
		["@FONASA hola buen día. Consulta, mis padres son extranjeros y ya tiene rut pero aun están desempleados, podrían cot… https://t.co/AeRReRr6G6", 247],
		["@chunachokstillo @Miguel_pizarro Tonto, gracias por la info",247],
		["@chunachokstillo Tonto, gracias por la info #ajajajaj jaja asdasda asdasda asdasda;...",247],
		["Buenos días, ya sabemos que murió Hawking, no hay necesidad de que todo el mundo lo publique.", 247],
		["No es alegría, solo que no esperen contemplación con él RT @nelsonbocaranda: RT @felixseijasr: Nadie debe alegrarse… https://t.co/KXx2eRBAQW", 247],
		["Jajajajaja RT @DTVTotal: RT @TurcoHusain: Nobleza obliga hoy daré la cara en @DTVTotal y aguantare todo los golpes.… https://t.co/yCbRmZOQyV", 247]
	]

	print (get_words_count(tweets))

	print (get_ngrams_count(tweets))