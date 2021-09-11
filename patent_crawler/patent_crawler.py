# coding=utf-8
from bs4 import BeautifulSoup
from selenium import webdriver
import time
from xml.dom.minidom import Document, parse


def search(keyword):
    driver = webdriver.Chrome()
    driver.get("https://patents.glgoo.top/")

    time.sleep(5)
    username_field = driver.find_element_by_xpath('//*[@id="searchInput"]')

    username_field.send_keys(keyword)
    time.sleep(6)

    driver.find_element_by_xpath('//*[@id="searchButton"]/iron-icon').click()  # 再次点击登陆
    time.sleep(5)
    return driver


def get():
    try:
        data = driver.page_source
        soup2 = BeautifulSoup(data, 'html.parser')
        grades = soup2.find('div', {'class': 'style-scope classification-tree'})
        a = grades.find_all('span', {'class': 'description style-scope classification-tree'})
        b = grades.find_all('a', {'class': 'style-scope state-modifier'})
        classifications_cont1 = a[-1].text
        classifications_num1 = b[-1].text


        abstract1 = driver.find_element_by_xpath('//*[@id="text"]/abstract/div').text  # abstract
        PatentCitations1 = driver.find_element_by_xpath('//*[@id="wrapper"]/div[3]/div[1]/div').text  # Patent Citations
        CitedBy1 = driver.find_element_by_xpath('//*[@id="wrapper"]/div[3]/div[3]/div').text  # Cited By
        claims1 = driver.find_element_by_xpath('//*[@id="claims"]/patent-text/div').text  # claims
        Description1 = driver.find_element_by_xpath('//*[@id="descriptionText"]/div').text  # Description
    except:
        abstract1 = '未找到'
        classifications_num1 = '未找到'
        classifications_cont1 = '未找到'
        PatentCitations1 = '未找到'
        CitedBy1 = '未找到'
        claims1 = '未找到'
        Description1 = '未找到'

    return abstract1, classifications_num1, classifications_cont1, PatentCitations1, CitedBy1, claims1, Description1


def save():
    rootNode = domTree.documentElement
    item = domTree.createElement('item')
    rootNode.appendChild(item)

    abstract = doc.createElement('abstract')
    abstract_text = doc.createTextNode(get()[0])  # abstract1) #元素内容写入
    abstract.appendChild(abstract_text)
    item.appendChild(abstract)

    classification = doc.createElement('classification')
    item.appendChild(classification)

    classification_cont = doc.createElement('classification_cont')
    classification_num = doc.createElement('classification_num')
    classification_cont_text = doc.createTextNode(get()[2])  # classifications_cont1)
    classification_nume_text = doc.createTextNode(get()[1])  # classifications_num1)
    classification.appendChild(classification_cont)
    classification.appendChild(classification_num)
    classification_cont.appendChild(classification_cont_text)
    classification_num.appendChild(classification_nume_text)
    item.appendChild(classification)

    PatentCitations = doc.createElement('PatentCitations')
    PatentCitations_text = doc.createTextNode(get()[3])  # PatentCitations1) #元素内容写入
    PatentCitations.appendChild(PatentCitations_text)
    item.appendChild(PatentCitations)

    CitedBy = doc.createElement('CitedBy')
    CitedBy_text = doc.createTextNode(get()[4])  # CitedBy1) #元素内容写入
    CitedBy.appendChild(CitedBy_text)
    item.appendChild(CitedBy)

    Claims = doc.createElement('Claims')
    Claims_text = doc.createTextNode(get()[5])  # claims1) #元素内容写入
    Claims.appendChild(Claims_text)
    item.appendChild(Claims)

    Description = doc.createElement('Description')
    Description_text = doc.createTextNode(get()[6])  # Description1) #元素内容写入
    Description.appendChild(Description_text)
    item.appendChild(Description)

    f = open('a.xml', 'w', encoding='utf-8')
    domTree.writexml(f, indent='\t', newl='\n', addindent='\t', encoding='utf-8')


if __name__ == '__main__':
    keyword = '文化'
    driver = search(keyword)
    driver.find_element_by_xpath('//*[@id="htmlContent"]').click()
    time.sleep(3)

    doc = Document()  # 创建DOM文档对象
    DOCUMENT = doc.createElement('Pantents')  # 创建根元素
    # DOCUMENT.setAttribute('content_method',"full")#设置命名空间
    doc.appendChild(DOCUMENT)
    f = open('a.xml', 'w', encoding='utf-8')
    doc.writexml(f, indent='\t', newl='\n', addindent='\t', encoding='utf-8')
    f.close()
    domTree = parse("a.xml")
    for i in range(50):
        get()
        save()
        driver.find_element_by_xpath('//*[@id="nextResult"]').click()
        driver.get(driver.current_url)
