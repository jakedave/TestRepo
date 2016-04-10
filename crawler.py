import requests, sys, os
from collections import deque
from bs4 import BeautifulSoup
import csv

#SOURCE: http://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console?rq=1
def printProgress (iteration, total, prefix = '', suffix = '', decimals = 2, barLength = 100):
	"""
	Call in a loop to create terminal progress bar
	@params:
		iterations  - Required  : current iteration (Int)
		total       - Required  : total iterations (Int)
	prefix      - Optional  : prefix string (Str)
	suffix      - Optional  : suffix string (Str)
	"""
	filledLength    = int(round(barLength * iteration / float(total)))
	percents        = round(100.00 * (iteration / float(total)), decimals)
	bar             = '#' * filledLength + '-' * (barLength - filledLength)
	sys.stdout.write('%s [%s] %s%s %s\r' % (prefix, bar, percents, '%', suffix)),
	sys.stdout.flush()
	if iteration == total:
		print("\n")

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

	# Get rid of extra info
	fullInfo = fullInfo.replace(' Role ', '`')
	fullInfo = fullInfo.replace(' Firm Type ', '`')
	fullInfo = fullInfo.replace(' Web Address ', '`')

	# Get rid of company description
	fullInfo = fullInfo.replace(' Company Description ', "^&")
	fullInfo = fullInfo.replace(' Professional Details  Company ', '')
	fullInfo = fullInfo.split("^&")
	fullInfo = fullInfo[0]

	# csv iterable list format
	fullInfo = fullInfo.split('`')

	# Normalize list
	while (len(fullInfo) < 5):
		fullInfo.append('N/A')

	return fullInfo

def parse(soup):
	"""harvest specific parse based on soup"""
	name = soup.title.get_text()
	name = name.replace(' - About - Harvest', '`')

	info = soup.find('div', class_="padding-top-bottom border-top-purple") # Area where info found
	info = info.get_text()

	name += info

	return csv_prep(name)



def crawl(URL_Frontier, maxURLs, c):
	"""Crawl baby, crawl!"""
	baseURL = "https://www.hvst.com"
	size = len(URL_Frontier)
	count = 0
	infoCount = 0
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
			count += 1

			r = requests.get(URL, timeout=0.5, allow_redirects=False)
			soup = BeautifulSoup(r.text, 'html.parser')

			try:
				if URL.startswith("https://www.hvst.com/users") and URL.endswith("/about"):
					info = parse(soup)
					#print info # COMMENT THIS OUT IF YOU WISH FOR NO TERMINAL OUTPUT
					c.writerow([info[0], info[1], info[2], info[3], info[4]])
					infoCount += 1
			except:
				#print "INFO NOT WRITTEN - IMPROPER FORMAT"
				pass

			# Find anchor (href) links
			size = find_links(soup, baseURL, size, URL_Frontier, 'a', 'href', URL)

		# 404
		except requests.exceptions.ConnectionError as e:
			#print e
			continue
		# timeout
		except requests.exceptions.Timeout as e:
			#print e
			continue

		# Add URL to already visited URLs
		printProgress (count, maxURLs, prefix = '', suffix = 'Complete', decimals = 2, barLength = 100)
		pastURLs.append(URL)

	return infoCount


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
	

	print "Starting Crawl...\n"

	infoCount = crawl(URL_Frontier, maxURLs, c)

	print "Crawl Complete"
	print "\n", infoCount, "names + info grabbed"
	print "Shutting Down..."
	print "Goodbye!"

	sys.exit(0)




if __name__ == "__main__":

	try:
		main()

	except KeyboardInterrupt:
		print infoCount, "names + info grabbed"
		print "\nShutting Down..."
		print "Goodbye!"
		sys.exit(0)


