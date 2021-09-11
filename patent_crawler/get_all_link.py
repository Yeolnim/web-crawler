import re
import time
import pandas as pd
import math
from selenium import webdriver


# 说明
# 选择语言在初始网址后加&language=（英文大写）
def refresh_page():
    time.sleep(3)
    search_window = browser.current_window_handle
    browser.switch_to.window(search_window)


def is_exist_element1(elem):
    button = browser.find_elements_by_css_selector(elem)
    if len(button) == 0:
        return False
    if len(button) == 1:
        return True


chrome_options = webdriver.ChromeOptions()
prefs = {"profile.managed_default_content_settings.images": 2, "profile.managed_default_content_settings.videos": 2}
chrome_options.add_experimental_option("prefs", prefs)
browser = webdriver.Chrome(chrome_options=chrome_options)
browser.get(
    'https://patents.glgoo.top/?q=energy+conservation+environmental+protection&oq=energy+conservation+and+environmental+protection&language=ENGLISH')
initial_link = 'https://patents.glgoo.top/?q=energy+conservation+environmental+protection&oq=energy+conservation+and+environmental+protection&language=ENGLISH'
time.sleep(3)

# 获取每个专利的链接
last_page_num = re.sub(r'\D', "", browser.find_element_by_xpath('//*[@id="numResultsLabel"]').text)
# print(last_page_num)
page_num = math.ceil(int(last_page_num) / 10)
# print(page_num)
page_link = []
page_link.append(initial_link)
for i in range(1, page_num):
    page_link.append(initial_link + '&page=' + str(i))

patent_url = []
for i in page_link:
    browser.get(i)
    refresh_page()
    patent_sum = browser.find_elements_by_tag_name('article')
    for j in range(1, len(patent_sum) + 1):
        a1 = browser.find_element_by_xpath(
            "/html/body/search-app/search-results/search-ui/div/div/div/div/div/div[1]/section/search-result-item[" + str(
                j) + "]/article/state-modifier/a").get_attribute(
            'href')

    for z in range(3, 2 * len(patent_sum) + 2, 2):
        if is_exist_element1('#resultsContainer > section > search-result-item:nth-child(' + str(
                z) + ') > article > div > div > div > div.flex.style-scope.search-result-item > h4.metadata.style-scope.search-result-item > span.bullet-before.style-scope.search-result-item > a > span') == True:
            a2 = browser.find_element_by_css_selector(
                '#resultsContainer > section > search-result-item:nth-child(' + str(
                    z) + ') > article > div > div > div > div.flex.style-scope.search-result-item > h4.metadata.style-scope.search-result-item > span.bullet-before.style-scope.search-result-item > a > span').text
            print(a1[:26] + 'patent/' + a2 + '/en' + a1[26:])
        else:
            continue
# print(patent_url)
# print(len(patent_url))
test = pd.DataFrame(data=patent_url)
test.to_csv('allpatentlink-en.csv', encoding='utf-8', index=False, header=False)
f1 = open('allpatentlink-en.csv', encoding='utf-8')
s1 = pd.read_csv(f1, header=None)
s1 = s1[0].tolist()
for i in s1:
    print(i)
