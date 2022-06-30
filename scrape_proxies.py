import re
import os
import time
import js2py
import string
import random
import asyncio
import requests
import zipcodes
import itertools
import pandas as pd
import multiprocessing
import undetected_chromedriver.v2 as uc
from pprint import pprint
from termcolor import colored
from bs4 import BeautifulSoup
from PyPDF2 import PdfFileReader
from fake_useragent import UserAgent
from requests_html import HTMLSession
from requests_html import AsyncHTMLSession
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC

def browser():
	# Get random user agent
	ua = UserAgent()
	user_agent = ua.random
	# Instantiate undetected_chromedriver with options
	options = uc.ChromeOptions()
	options.add_argument("--headless")
	options.add_argument(f"user-agent={user_agent}")
	driver = uc.Chrome(options=options, use_subprocess=True)
	return driver

def scrape_proxies():
	url = "https://spys.one/en/anonymous-proxy-list/"

	# Instantiate driver
	driver = browser()
	driver.get(url)
	time.sleep(5)

	# Select 500 entries
	select_show = Select(driver.find_element(By.ID, "xpp"))
	select_show.select_by_visible_text("500")
	time.sleep(5)

	# Select HTTP type
	select_type = Select(driver.find_element(By.ID, "xf5"))
	select_type.select_by_visible_text("HTTP")
	time.sleep(5)

	# Get rows of table
	rows = driver.find_elements(By.TAG_NAME, "tr")

	# Filter out unnecessary rows
	rows = rows[9:len(rows)-4:2]

	# Loop through rows of table
	ip_addresses = []
	for row in rows:
		columns = row.find_elements(By.TAG_NAME, "td")
		data = {"Proxy address":"", "Proxy type":"", "Uptime":""}
		# Check proxy type and add to dictionary accordingly
		if "HTTPS" in columns[1].text.strip():
			data["Proxy address"] = columns[0].text.strip()
			data["Proxy type"] = "https"
			if "new" not in columns[8].text:
				data["Uptime"] = columns[8].text.strip().split("%")[0]
			else:
				data["Uptime"] = "0"
		else:
			data["Proxy address"] = columns[0].text.strip()
			data["Proxy type"] = "http"
			if "new" not in columns[8].text:
				data["Uptime"] = columns[8].text.strip().split("%")[0]
			else:
				data["Uptime"] = "0"
		ip_addresses.append(data)

	# Quit the chromedriver headless browser
	driver.quit()

	# Add IP addresses to pandas DataFrame
	df = pd.DataFrame(ip_addresses)

	# Filter out proxies with uptime < 20%
	df["Uptime"] = df["Uptime"].astype("int")
	df = df[df["Uptime"] >= 20]

	print(len(df))
	print(df.dtypes)
	print(df.head())

	# Save to CSV file
	df.to_csv("spys-proxy-list-500-uptime-20.csv")

def get_random_proxy():
	ip_addresses = scrape_proxies()
	proxy_index = random.randint(0, len(ip_addresses) - 1)
	#proxy = {"http": ip_addresses[proxy_index]["Proxy type"] + "://" + ip_addresses[proxy_index]["Proxy address"], 
	#		 "https": ip_addresses[proxy_index]["Proxy type"] + "://" + ip_addresses[proxy_index]["Proxy address"]}
	proxy = {"http": ip_addresses[proxy_index]["Proxy address"], "https": ip_addresses[proxy_index]["Proxy address"]}
	#proxy = {ip_addresses[proxy_index][1]: ip_addresses[proxy_index][1] + "://" + ip_addresses[proxy_index][0]}
	print(proxy)
	return proxy

def get_random_proxy_csv():
	df = pd.read_csv("spys-proxy-list-500.csv")
	proxy_index = random.randint(0, len(df) - 1)
	#proxy = {"http": df.loc[proxy_index, "Proxy type"] + "://" + df.loc[proxy_index, "Proxy address"], 
	#		 "https": df.loc[proxy_index, "Proxy type"] + "://" + df.loc[proxy_index, "Proxy address"]}
	proxy = {"http": df.loc[proxy_index, "Proxy address"], "https": df.loc[proxy_index, "Proxy address"]}
	print("proxy: ", proxy)
	return proxy

def test_proxy():
	ua = UserAgent()
	user_agent = ua.random
	headers = {"User-Agent":user_agent}
	proxy = get_random_proxy()
	r = requests.get("http://icanhazip.com", headers=headers, proxies=proxy)
	print(r.content)

def test_proxy_csv():
	df = pd.read_csv("spys-proxy-list-500-uptime-20.csv")
	proxy_index = random.randint(0, len(df) - 1)
	#proxy = {"http": df.loc[proxy_index, "Proxy type"] + "://" + df.loc[proxy_index, "Proxy address"], 
	#		 "https": df.loc[proxy_index, "Proxy type"] + "://" + df.loc[proxy_index, "Proxy address"]}
	proxy = {"http": df.loc[proxy_index, "Proxy address"], "https": df.loc[proxy_index, "Proxy address"]}
	print("proxy: ", proxy)
	ua = UserAgent()
	user_agent = ua.random
	headers = {"User-Agent":user_agent}
	r = requests.get("http://icanhazip.com", headers=headers, proxies=proxy)
	print(r.content)

def main():
	start = time.time()

	scrape_proxies()
	#get_random_proxy()
	#test_proxy()
	#test_proxy_csv()

	end = time.time()
	execution_time = end - start
	print("Execution time: {} seconds".format(execution_time))

if __name__ == "__main__":
	main()
