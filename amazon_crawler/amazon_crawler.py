# -*- coding: UTF-8 -*-
import requests
import re
import time
import xml.etree.ElementTree as et
from bs4 import BeautifulSoup
from selenium import webdriver
from lxml import etree

url = "https://www.amazon.cn/%E5%AD%99%E5%AD%90%E5%85%B5%E6%B3%95-%E5%AD%99%E6%AD%A6/product-reviews/B0011CT3HW/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews"
url_detail = "https://www.amazon.cn/%E5%AD%99%E5%AD%90%E5%85%B5%E6%B3%95-%E5%AD%99%E6%AD%A6/dp/B0011CT3HW/ref=cm_cr_arp_d_bdcrb_top?ie=UTF8"

data = requests.get(url_detail).text
s = etree.HTML(data)

html = requests.get(url_detail)

press = re.findall('<b>出版社:</b> (.*?);', html.text, re.S)[0]
name = s.xpath('//*[@id="productTitle"]/text()')[0]
year = s.xpath('//*[@id="title"]/span[3]/text()')[0].replace('– ', '').split("年")[0]
author = s.xpath('//*[@id="bylineInfo"]/span/a/text()')[0]

browser = webdriver.Chrome()
browser.get(url)

review = et.Element("review")
review.tail = '\n'

page = 0
while page < 1000:
    soup = BeautifulSoup(browser.page_source, "html.parser")

    data = requests.get(url).text
    s = etree.HTML(data)

    html = requests.get(url)

    browser.find_element_by_xpath('//*[@id="cm_cr-pagination_bar"]/ul/li[2]/a').click()
    page = page + 1
    time.sleep(2)

    all_divs = soup.find_all(class_='a-section review aok-relative')

    for each_div in all_divs:
        summary = each_div.find(
            class_='a-size-base a-link-normal review-title a-color-base review-title-content a-text-bold').find(
            'span').get_text()
        score = each_div.find(class_='a-icon-alt').get_text().split(".")[0]
        date = each_div.find(class_='a-size-base a-color-secondary review-date').get_text()
        text = each_div.find(class_='a-size-base review-text review-text-content').get_text()

        print(summary, score, date, text)

        item = et.SubElement(review, "item")
        item.tail = '\n'

        press_et = et.SubElement(item, "press")
        name_et = et.SubElement(item, "name")
        year_et = et.SubElement(item, "year")
        author_et = et.SubElement(item, "author")
        summary_et = et.SubElement(item, "summary")
        score_et = et.SubElement(item, "score")
        date_et = et.SubElement(item, "date")
        text_et = et.SubElement(item, "text")

        press_et.text = press
        name_et.text = name
        year_et.text = year
        author_et.text = author
        summary_et.text = summary
        score_et.text = score
        date_et.text = date
        text_et.text = text

        press_et.tail = '\n'
        name_et.tail = '\n'
        year_et.tail = '\n'
        author_et.tail = '\n'
        summary_et.tail = '\n'
        score_et.tail = '\n'
        date_et.tail = '\n'
        text_et.tail = '\n'

        tree = et.ElementTree(review)
        tree.write("AmazonReview.xml", encoding="utf-8", xml_declaration=True)
