import requests, sys, os
from collections import deque
from bs4 import BeautifulSoup


def normalize_link(url):
	"""Get rid of extraneous URL endings"""
	newurl = url
	if newurl.endswith('/'):
		newurl = newurl[:-1]
	fragment = newurl.rfind('#')
	if fragment != -1:
		newurl = newurl[0:fragment]
	return newurl


def init():
	"""Initalize list of seen URLs"""
	global pasturls
	pasturls = []


def is_html(url):
	"""Check if html file"""
	# Check if google and .cgi
	if ('google' in url) or ('.cgi' in url) or ('.php' in url):
		return False
	# Check file extensions
	extensions = ['.pdf', '.jpg', '.png', '.ogv', '.mp4', '.mov', '.doc', '.jpeg', '.tar.bz', '.tar.gz', '.zip', '.ppsx', '.JPG', '.JPEG']
	for ext in extensions:
		if url.endswith(ext):
			return False
	# Else return True (.html or .htm)
	return True


def valid_URL(url):
	"""Check if URL is in domain of accepted URLs"""
	valid = ['https://en.wikipedia.org', 'http://en.wikipedia.org', 'http://en.wikipedia.org', 'https://en.wikipedia.org']
	for ext in valid:
		if url.startswith(ext):
			return True
	return False


def visited(url):
	"""Check if URL has been seen before"""
	if url in pasturls:
		return True
	elif url == "/":
		return True
	else:
		check = url.replace('s', '', 1)
		if check in pasturls:
			return True
		else: 
			return False


def find_links(soup, baseurl, size, urlFrontier, tag, attribute, url):
	"""BFS search for links"""
	newSize = size
	for link in soup.find_all(tag):
		newurl = link.get(attribute)
		if newurl != "" and newurl != None:
			if newurl.startswith('/'):
				newurl = baseurl + newurl
			if newurl.startswith('http'):
				newurl = normalize_link(newurl)
				newSize += 1
				urlFrontier.append(newurl)


	return newSize


def crawl(urlFrontier, maxurls):
	"""Crawl baby, crawl!"""
	baseurl = "http://en.wikipedia.org"
	size = len(urlFrontier)
	count = 0
	while (size > 0) and (count < maxurls):
		# Pop url from front
		url = urlFrontier.popleft()
		size -= 1

		# Check if url is 'html'
		if not is_html(url):
			continue

		# Check if from 'eecs.umich' domain
		if not valid_URL(url):
			continue

		# Check if url has already been visited
		if visited(url):
			continue

		# Download web page (except if 404 error)
		try:
			print count, " ", url
			count += 1

			r = requests.get(url)
			soup = BeautifulSoup(r.text, 'html.parser')

			try:
				print soup.title.get_text()
			except:
				pass


			# Find anchor (href) links
			size = find_links(soup, baseurl, size, urlFrontier, 'a', 'href', url)
		except requests.exceptions.ConnectionError as e:
			continue

		# Add url to already visited urls
		pasturls.append(url)


if __name__ == "__main__":

	urlFrontier = deque()

	seedFile = sys.argv[1]
	infile = open(seedFile, "r")
	for url in infile:
		url = normalize_link(url)
		urlFrontier.append(url)
	infile.close()



	maxurls = int(sys.argv[2])

	init()

	crawl(urlFrontier, maxurls)


