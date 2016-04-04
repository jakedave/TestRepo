import requests, sys, os
from collections import deque
from bs4 import BeautifulSoup
import csv


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

def csv_prep(fullInfo):
	"""further parse to prep for csv output"""
	fullInfo = fullInfo.replace('\n', ' ')
	fullInfo = fullInfo.replace('               ', ' ') #Why you do this harvest?

	#Get rid of extra info
	fullInfo = fullInfo.replace(' - About - Harvest ', ',')
	fullInfo = fullInfo.replace(' Role ', ',')
	fullInfo = fullInfo.replace(' Firm Type ', ',')
	fullInfo = fullInfo.replace(' Web Address ', ',')

	#Get rid of company description
	fullInfo = fullInfo.replace(' Company Description ', "^&")
	fullInfo = fullInfo.split("^&")
	fullInfo = fullInfo[0]

	#csv iterable list format
	fullInfo = fullInfo.split(',')

	return fullInfo

def parse(soup):
	"""harvest specific parse based on soup"""
	name = soup.title.get_text()

	info = soup.find('div', class_="padding-top-bottom border-top-purple")
	info = info.get_text()

	name += ' ' + info

	return csv_prep(name)



def crawl(URL_Frontier, maxURLs, c):
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
			#print count#, " ", URL
			count += 1

			r = requests.get(URL, timeout=0.5, allow_redirects=False)
			soup = BeautifulSoup(r.text, 'html.parser')

			try:
				if URL.startswith("https://www.hvst.com/users") and URL.endswith("/about"):
					info = parse(soup)
					print info
					c.writerow([info[0], info[1], info[2], info[3], info[4]])
			except:
				print "PASSED"
				pass

			# Find anchor (href) links
			size = find_links(soup, baseURL, size, URL_Frontier, 'a', 'href', URL)

		#404
		except requests.exceptions.ConnectionError as e:
			print e
			continue
		#timeout
		except requests.exceptions.Timeout as e:
			print e
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

	c = csv.writer(open("MYFILE.csv", "wb"))
	c.writerow(["Name","Company","Role","Firm Type","Website"])

	crawl(URL_Frontier, maxURLs, c)

	c.close()

	print "\nCrawl Complete"
	print "Shutting Down..."
	print "Goodbye!"

	sys.exit(0)




if __name__ == "__main__":

	try:
		main()

	except KeyboardInterrupt:
		print "\nShutting Down..."
		print "Goodbye!"
		sys.exit(0)


