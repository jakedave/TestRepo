import requests, sys, os
from collections import deque
from bs4 import BeautifulSoup


def normalize_link(URL):
	"""Get rid of extraneous URL endings"""
	newURL = URL
	if newURL.endswith('/'):
		newURL = newURL[:-1]

	fragment = newURL.rfind('#')
	if fragment != -1:
		newURL = newURL[0:fragment]

	return newURL


def init():
	"""Initalize list of seen URLs"""
	global pastURLs
	pastURLs = []


def is_html(URL):
	"""Check if html file"""
	# Check if google and .cgi
	if ('google' in URL) or ('.cgi' in URL) or ('.php' in URL):
		return False

	# Check file extensions
	extensions = ['.pdf', '.jpg', '.png', '.ogv', '.mp4', '.mov', '.doc', '.jpeg', '.tar.bz', '.tar.gz', '.zip', '.ppsx', '.JPG', '.JPEG']
	for ext in extensions:
		if URL.endswith(ext):
			return False

	# Else return True (.html or .htm)
	return True


def valid_URL(URL):
	"""Check if URL is in domain of accepted URLs"""
	valid = ['https://www.hvst.com', 'http://www.hvst.com', 'https://www.hvst.com', 'http://www.hvst.com']
	for ext in valid:
		if URL.startswith(ext):
			return True
	return False


def visited(URL):
	"""Check if URL has been seen before"""
	if URL in pastURLs:
		return True

	elif URL == "/":
		return True

	else:
		check = URL.replace('s', '', 1)
		if check in pastURLs:
			return True
		else: 
			return False


def find_links(soup, baseURL, size, URL_Frontier, tag, attribute, URL):
	"""BFS search for links"""
	newSize = size
	for link in soup.find_all(tag):
		newURL = link.get(attribute)

		if newURL != "" and newURL != None:
			if newURL.startswith('/'):
				newURL = baseURL + newURL

			if newURL.startswith('http'):
				newURL = normalize_link(newURL)
				newSize += 1

				URL_Frontier.append(newURL)

	return newSize


def crawl(URL_Frontier, maxURLs):

	"""Crawl baby, crawl!"""
	baseURL = "https://www.hvst.com"
	size = len(URL_Frontier)
	count = 0
	while (size > 0) and (count < maxURLs):
		# Pop URL from front
		URL = URL_Frontier.popleft()
		size -= 1

		# Check if URL is 'html'
		if not is_html(URL):
			continue

		# Check if from 'eecs.umich' domain
		if not valid_URL(URL):
			continue

		# Check if URL has already been visited
		if visited(URL):
			continue

		# Download web page (except if 404 error)
		try:
			print count, " ", URL
			count += 1

			r = requests.get(URL)
			soup = BeautifulSoup(r.text, 'html.parser')

			try:
				if URL.startswith("https://www.hvst.com/users") and URL.endswith("/about"):
					print "HEREEEEEEEEEEEEEEEEEEEEEEEEEEEEE"
					print soup.title.get_text()
			except:
				pass


			# Find anchor (href) links
			size = find_links(soup, baseURL, size, URL_Frontier, 'a', 'href', URL)
		except requests.exceptions.ConnectionError as e:
			continue

		# Add URL to already visited URLs
		pastURLs.append(URL)


def main():
	URL_Frontier = deque()

	seedFile = sys.argv[1]
	maxURLs = int(sys.argv[2])

	infile = open(seedFile, "r")
	for URL in infile:
		URL = normalize_link(URL)
		URL_Frontier.append(URL)
	infile.close()

	init()
	crawl(URL_Frontier, maxURLs)




if __name__ == "__main__":

	try:
		main()

	except KeyboardInterrupt:
		print "\nShutting Down..."
		print "Goodbye!"
		sys.exit(0)


