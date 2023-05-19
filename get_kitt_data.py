import pandas as pd
import gspread
from params import *
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from oauth2client.service_account import ServiceAccountCredentials
from df2gspread import df2gspread as d2g
from getpass import getpass

ghuser = input('Github login: ')
ghpassword = getpass('Github password: ')

browser = webdriver.Chrome()

# Load the login page
browser.get('https://kitt.lewagon.com/users/sign_in')

# Click the login with github button
login_button = browser.find_element(By.XPATH , '//a[@href="/users/auth/github?type=student"]')
login_button.click()

# Fill in the login form
login = browser.find_element(By.XPATH , '//input[@id="login_field"]')
login.send_keys(ghuser)

password = browser.find_element(By.XPATH , '//input[@id="password"]')
password.send_keys(ghpassword)

submit = browser.find_element(By.XPATH , '//input[@name="commit"]')
submit.click()

# get html
browser.get('https://kitt.lewagon.com/camps/1243/lectures')

html = browser.page_source

# Parse html
soup = BeautifulSoup(html, 'html.parser')

titles = soup.find_all('h3', class_='lecture-title')
titles = [title.text.replace('\n', '').strip().split('        ')[0] for title in titles]
links_soup = soup.find_all('a', class_='lecture-card-link')
links =['https://kitt.lewagon.com' + link_soup.get('href') for link_soup in links_soup]

titles_links = zip(titles, links)
titles_links = list(titles_links)

lectures_df = pd.DataFrame({
    'title' : [],
    'link' : [],
    'n_slides' : [],
    'n_videos' : [],
    'video_0_in_eng' : [],
    'video_1_in_eng' : [],
    'video_2_in_eng' : [],
    'video_3_in_eng' : [],
    'video_4_in_eng' : [],
    'video_5_in_eng' : [],
    'video_6_in_eng' : []
    })

for index, (title, link) in enumerate(titles_links):
    browser.get(link)
    page_html = browser.page_source
    page_soup = BeautifulSoup(page_html, 'html.parser')

    a_tags = page_soup.find_all('a', class_='nav-link iframe-lecture-tab')
    n_slides = len([a_tag.get('href') for a_tag in a_tags])
    n_videos = sum(['Video' in video.text for video in page_soup.find_all('span', class_='d-none d-md-inline')])

    lectures_df.loc[index, ['title']] = title
    lectures_df.loc[index, ['link']] = link
    lectures_df.loc[index, ['n_slides']] = n_slides
    lectures_df.loc[index, ['n_videos']] = n_videos

    for video_n in range(n_videos):
        browser.get(link + f'#video-{video_n}')
        langs = browser.find_elements(By.XPATH , '//span[@class="d-none d-sm-inline small"]')
        video_langs = [lang.text for lang in langs]
        lectures_df.loc[index, f'video_{video_n}_in_eng'] = 'English' in video_langs

# Upload to google sheets
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    ACCESS_JSON, scope)
gc = gspread.authorize(credentials)

wks_name = 'Master'
d2g.upload(lectures_df, SPREADSHEET_KEY, wks_name, credentials=credentials, row_names=True)

print('All done!')
print(LINK)
