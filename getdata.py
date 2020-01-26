from bs4 import BeautifulSoup
import requests
import re

requests.utils.default_headers()
headers = requests.utils.default_headers()
headers.update({ 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'})

url = "https://www.facebook.com/pg/secretsuchicago/posts/"   
req = requests.get(url, headers)
soup = BeautifulSoup(req.content, 'html.parser')  
all_comments = soup.find_all('p') 
i = 1
for comment in all_comments:
	comment = comment.getText()
	if re.findall("https://submit.crush.ninja/secretsuchicago", comment) == []: #r/
		print("Post", str(i))
		print(comment)
		i += 1



#ref: https://hackersandslackers.com/scraping-urls-with-beautifulsoup/