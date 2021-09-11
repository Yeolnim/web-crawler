import time
import re
import pandas as pd
from selenium import webdriver

chrome_options = webdriver.ChromeOptions()
prefs = {"profile.managed_default_content_settings.images": 2, "profile.managed_default_content_settings.videos": 2}
chrome_options.add_experimental_option("prefs", prefs)
browser = webdriver.Chrome(chrome_options=chrome_options)


def refresh_page():
    time.sleep(6)
    search_window = browser.current_window_handle
    browser.switch_to.window(search_window)


def is_exist_element(elem):
    button = browser.find_elements_by_xpath(elem)
    if len(button) == 0:
        return False
    if len(button) == 1:
        return True


f1 = open('allpatentlink.csv', encoding='utf-8')
s1 = pd.read_csv(f1, header=None)
all_patent_link = s1[0].tolist()

for i in all_patent_link:
    browser.get(i)
    refresh_page()
    title = browser.find_element_by_xpath('//*[@id="title"]').text
    if is_exist_element('//*[@id="text"]/abstract/div') == True:
        abstract = browser.find_element_by_xpath('//*[@id="text"]/abstract/div').text
        print(abstract)
    if is_exist_element("//*[contains(text(),'Application filed by')]") == True:
        s = browser.find_element_by_css_selector("[class='title-text style-scope application-timeline']").text
        organization = s.replace('Application filed by ', 'Applicationfiledby')
    else:
        organization = ''
    if browser.find_element_by_xpath('//*[@id="classifications"]/h3/div[1]').text == 'Classifications':
        classifications = []
        if is_exist_element('//*[@id="classifications"]/classification-viewer/div/div/div[1]') == True:
            count_classifications = re.sub(r'\D', "", browser.find_element_by_xpath(
                '//*[@id="classifications"]/classification-viewer/div/div/div[1]').text)
            click1 = browser.find_element_by_xpath(
                '//*[@id="classifications"]/classification-viewer/div/div/div[1]').click()
            refresh_page()
            classification1 = browser.find_element_by_xpath(
                '//*[@id="classifications"]/classification-viewer/div/classification-tree').text
            classifications.append(classification1)
            for i in range(1, int(count_classifications) + 1):
                classification2 = browser.find_element_by_xpath(
                    '//*[@id="classifications"]/classification-viewer/div/div/classification-tree[' + str(i) + ']').text
                classifications.append(classification2)
        else:
            classifications.append(browser.find_element_by_xpath(
                '//*[@id="classifications"]/classification-viewer/div/classification-tree').text)

    description = browser.find_element_by_xpath('//*[@id="descriptionText"]/div').text
    print(description)
    granted_patent = browser.find_element_by_xpath('//*[@id="pubnum"]').text
    country = browser.find_element_by_xpath('//*[@id="wrapper"]/div[1]/div[2]/section/header/p').text
    other_languages = browser.find_element_by_xpath(
        '//*[@id="wrapper"]/div[1]/div[2]/section/dl[1]/dd[1]/state-modifier').text

    inventor = browser.find_element_by_xpath('//*[@id="wrapper"]/div[1]/div[2]/section/dl[1]/dd[2]/state-modifier').text

    priority_year = browser.find_element_by_xpath(
        '//*[@id="wrapper"]/div[1]/div[2]/section/application-timeline/div/div[2]/span[1]/span[1]').text

    # 根据规律设置计数器
    div_num_count = 0

    # Patent Citation
    if is_exist_element('//*[@id="patentCitations"]') == True:
        div_num_count = div_num_count + 1

        patent_citations = []
        count_patent_citations = re.sub(r'\D', "", browser.find_element_by_xpath('//*[@id="patentCitations"]').text)
        if int(count_patent_citations) == 1:
            patent_citations.append(browser.find_element_by_xpath(
                '//*[@id="wrapper"]/div[3]/div[' + str(div_num_count) + ']/div/div[2]/div').text)
        else:
            for i in range(1, int(count_patent_citations) + 2):
                if is_exist_element('//*[@id="wrapper"]/div[3]/div[' + str(div_num_count) + ']/div/div[2]/div[' + str(
                        i) + ']') == True and browser.find_element_by_xpath(
                    '//*[@id="wrapper"]/div[3]/div[' + str(div_num_count) + ']/div/div[2]/div[' + str(
                        i) + ']').text != "Family To Family Citations":
                    patent_citations_detail = browser.find_element_by_xpath(
                        '//*[@id="wrapper"]/div[3]/div[' + str(div_num_count) + ']/div/div[2]/div[' + str(i) + ']').text
                    patent_citations.append(patent_citations_detail)
                else:
                    continue

    # Non-Patent Citations
    if is_exist_element('//*[@id="nplCitations"]') == True and div_num_count == 0:
        div_num_count = div_num_count + 1
        non_patent_citations = []

        count_non_patent_citations = re.sub(r'\D', "", browser.find_element_by_xpath('//*[@id="nplCitations"]').text)
        if int(count_non_patent_citations) == 1:
            non_patent_citations.append(browser.find_element_by_xpath(
                '//*[@id="wrapper"]/div[3]/div[' + str(div_num_count) + ']/div/div[2]/div').text)
        else:
            for i in range(1, int(count_non_patent_citations) + 2):
                if is_exist_element('//*[@id="wrapper"]/div[3]/div[' + str(div_num_count) + ']/div/div[2]/div[' + str(
                        i) + ']') == True and browser.find_element_by_xpath(
                    '//*[@id="wrapper"]/div[3]/div[' + str(div_num_count) + ']/div/div[2]/div[' + str(
                        i) + ']').text != "Family To Family Citations":
                    non_patent_citations_detail = browser.find_element_by_xpath(
                        '//*[@id="wrapper"]/div[3]/div[' + str(div_num_count) + ']/div/div[2]/div[' + str(i) + ']').text
                    non_patent_citations.append(non_patent_citations_detail)
                else:
                    continue

    if is_exist_element('//*[@id="nplCitations"]') == True and div_num_count != 0 and is_exist_element(
            '//*[@id="patentCitations"]') == True:
        div_num_count = div_num_count + 2
        non_patent_citations = []

        count_non_patent_citations = re.sub(r'\D', "", browser.find_element_by_xpath('//*[@id="nplCitations"]').text)
        if int(count_non_patent_citations) == 1:
            non_patent_citations.append(browser.find_element_by_xpath(
                '//*[@id="wrapper"]/div[3]/div[' + str(div_num_count) + ']/div/div[2]/div').text)
        else:
            for i in range(1, int(count_non_patent_citations) + 2):
                if is_exist_element('//*[@id="wrapper"]/div[3]/div[' + str(div_num_count) + ']/div/div[2]/div[' + str(
                        i) + ']') == True and browser.find_element_by_xpath(
                    '//*[@id="wrapper"]/div[3]/div[' + str(div_num_count) + ']/div/div[2]/div[' + str(
                        i) + ']').text != "Family To Family Citations":
                    non_patent_citations_detail = browser.find_element_by_xpath(
                        '//*[@id="wrapper"]/div[3]/div[' + str(div_num_count) + ']/div/div[2]/div[' + str(i) + ']').text
                    non_patent_citations.append(non_patent_citations_detail)
                else:
                    continue

    # Cited_by
    # 字段是一次性加进去 还是分开？之后再考虑
    if is_exist_element('//*[@id="citedBy"]') == True and div_num_count == 0:
        div_num_count = div_num_count + 1

        cited_by = []
        count_cited_by = re.sub(r'\D', "", browser.find_element_by_xpath('//*[@id="citedBy"]').text)
        if int(count_cited_by) == 1:
            cited_by.append(browser.find_element_by_xpath(
                '//*[@id="wrapper"]/div[3]/div[' + str(div_num_count) + ']/div/div[2]/div').text)
        else:
            for i in range(1, int(count_cited_by) + 2):
                if is_exist_element('//*[@id="wrapper"]/div[3]/div[' + str(div_num_count) + ']/div/div[2]/div[' + str(
                        i) + ']') == True and browser.find_element_by_xpath(
                    '//*[@id="wrapper"]/div[3]/div[' + str(div_num_count) + ']/div/div[2]/div[' + str(
                        i) + ']').text != "Family To Family Citations":
                    cited_by_detail = browser.find_element_by_xpath(
                        '//*[@id="wrapper"]/div[3]/div[' + str(div_num_count) + ']/div/div[2]/div[' + str(i) + ']').text
                    cited_by.append(cited_by_detail)
                else:
                    continue
        print(cited_by)

    if is_exist_element('//*[@id="citedBy"]') == True and div_num_count != 0 and is_exist_element(
            '//*[@id="patentCitations"]') == True or is_exist_element('//*[@id="nplCitations"]') == True:
        div_num_count = div_num_count + 2

        cited_by = []
        count_cited_by = re.sub(r'\D', "", browser.find_element_by_xpath('//*[@id="citedBy"]').text)
        if int(count_cited_by) == 1:
            cited_by.append(browser.find_element_by_xpath(
                '//*[@id="wrapper"]/div[3]/div[' + str(div_num_count) + ']/div/div[2]/div').text)
        else:
            for i in range(1, int(count_cited_by) + 2):
                if is_exist_element('//*[@id="wrapper"]/div[3]/div[' + str(div_num_count) + ']/div/div[2]/div[' + str(
                        i) + ']') == True and browser.find_element_by_xpath(
                    '//*[@id="wrapper"]/div[3]/div[' + str(div_num_count) + ']/div/div[2]/div[' + str(
                        i) + ']').text != "Family To Family Citations":
                    cited_by_detail = browser.find_element_by_xpath(
                        '//*[@id="wrapper"]/div[3]/div[' + str(div_num_count) + ']/div/div[2]/div[' + str(i) + ']').text
                    cited_by.append(cited_by_detail)
                else:
                    continue
        print(cited_by)

    # Similar Documents
    if is_exist_element('//*[@id="similarDocuments"]') == True and div_num_count == 0:
        div_num_count = div_num_count + 1
        similar_documents = []
        similar_documents_len = len(
            browser.find_elements_by_xpath('//*[@id="wrapper"]/div[3]/div[' + str(div_num_count) + ']/div/div[2]/div'))

        for i in range(1, similar_documents_len + 1):
            if is_exist_element('//*[@id="wrapper"]/div[3]/div[' + str(div_num_count) + ']/div/div[2]/div[' + str(
                    i) + ']') == True and browser.find_element_by_xpath(
                '//*[@id="wrapper"]/div[3]/div[' + str(div_num_count) + ']/div/div[2]/div[' + str(
                    i) + ']').text != "Family To Family Citations":
                similar_documents_detail = browser.find_element_by_xpath(
                    '//*[@id="wrapper"]/div[3]/div[' + str(div_num_count) + ']/div/div[2]/div[' + str(i) + ']').text
                similar_documents.append(similar_documents_detail)
            else:
                continue

    if is_exist_element('//*[@id="similarDocuments"]') == True and div_num_count != 0 and is_exist_element(
            '//*[@id="patentCitations"]') == True or is_exist_element(
        '//*[@id="nplCitations"]') == True or is_exist_element('//*[@id="citedBy"]') == True:
        div_num_count = div_num_count + 2
        similar_documents = []
        similar_documents_len = len(
            browser.find_elements_by_xpath('//*[@id="wrapper"]/div[3]/div[' + str(div_num_count) + ']/div/div[2]/div'))

        for i in range(1, similar_documents_len + 1):
            if is_exist_element('//*[@id="wrapper"]/div[3]/div[' + str(div_num_count) + ']/div/div[2]/div[' + str(
                    i) + ']') == True and browser.find_element_by_xpath(
                '//*[@id="wrapper"]/div[3]/div[' + str(div_num_count) + ']/div/div[2]/div[' + str(
                    i) + ']').text != "Family To Family Citations":
                similar_documents_detail = browser.find_element_by_xpath(
                    '//*[@id="wrapper"]/div[3]/div[' + str(div_num_count) + ']/div/div[2]/div[' + str(i) + ']').text
                similar_documents.append(similar_documents_detail)
            else:
                continue

    # -----------------------------------------------------------------------------------------------#
    div_num_count1 = div_num_count
    # Child Applications
    if is_exist_element('//*[@id="applicationChildApps"]') == True and is_exist_element(
            "//*[contains(text(),'Child Applications')]") == True:
        div_num_count1 = div_num_count1 + 1

        applicationChildApps = []
        count_applicationChildApps = re.sub(r'\D', "",
                                            browser.find_element_by_xpath('//*[@id="applicationChildApps"]').text)
        if int(count_applicationChildApps) == 1:
            applicationChildApps.append(
                browser.find_element_by_xpath(
                    '//*[@id="wrapper"]/div[3]/div[' + str(div_num_count1) + ']/div/div[2]/div').text)
        else:
            for i in range(1, int(count_applicationChildApps) + 2):
                if is_exist_element('//*[@id="wrapper"]/div[3]/div[' + str(div_num_count1) + ']/div/div[2]/div[' + str(
                        i) + ']') == True and browser.find_element_by_xpath(
                    '//*[@id="wrapper"]/div[3]/div[' + str(div_num_count1) + ']/div/div[2]/div[' + str(
                        i) + ']').text != "Family To Family Citations":
                    applicationChildApps_detail = browser.find_element_by_xpath(
                        '//*[@id="wrapper"]/div[3]/div[' + str(div_num_count1) + ']/div/div[2]/div[' + str(
                            i) + ']').text
                    applicationChildApps.append(applicationChildApps_detail)
                else:
                    continue

    # Priority Applications
    if is_exist_element('//*[@id="applicationPriorityApps"]') == True and is_exist_element(
            "//*[contains(text(),'Priority Applications')]") == True:
        div_num_count1 = div_num_count1 + 1
        applicationPriorityApps = []
        count_applicationPriorityApps = re.sub(r'\D', "",
                                               browser.find_element_by_xpath('//*[@id="applicationPriorityApps"]').text)
        if int(count_applicationPriorityApps) == 1:
            applicationPriorityApps.append(
                browser.find_element_by_xpath(
                    '//*[@id="wrapper"]/div[3]/div[' + str(div_num_count1) + ']/div/div[2]/div').text)
        else:
            for i in range(1, int(count_applicationPriorityApps) + 2):
                if is_exist_element('//*[@id="wrapper"]/div[3]/div[' + str(div_num_count1) + ']/div/div[2]/div[' + str(
                        i) + ']') == True and browser.find_element_by_xpath(
                    '//*[@id="wrapper"]/div[3]/div[' + str(div_num_count1) + ']/div/div[2]/div[' + str(
                        i) + ']').text != "Family To Family Citations":
                    applicationPriorityApps_detail = browser.find_element_by_xpath(
                        '//*[@id="wrapper"]/div[3]/div[' + str(div_num_count1) + ']/div/div[2]/div[' + str(
                            i) + ']').text
                    applicationPriorityApps.append(applicationPriorityApps_detail)
                else:
                    continue

    # Applications Claiming Priority
    if is_exist_element('//*[@id="appsClaimingPriority"]') == True and is_exist_element(
            "//*[contains(text(),'Applications Claiming Priority')]") == True:
        div_num_count1 = div_num_count1
        appsClaimingPriority = []
        count_appsClaimingPriority = re.sub(r'\D', "",
                                            browser.find_element_by_xpath('//*[@id="appsClaimingPriority"]').text)
        if int(count_appsClaimingPriority) == 1:
            appsClaimingPriority.append(browser.find_element_by_xpath(
                '//*[@id="wrapper"]/div[3]/div[' + str(div_num_count1) + ']/div/div[2]/div').text)
        else:
            for i in range(1, int(count_appsClaimingPriority) + 2):
                if is_exist_element('//*[@id="wrapper"]/div[3]/div[' + str(div_num_count1) + ']/div/div[2]/div[' + str(
                        i) + ']') == True and browser.find_element_by_xpath(
                    '//*[@id="wrapper"]/div[3]/div[' + str(div_num_count1) + ']/div/div[2]/div[' + str(
                        i) + ']').text != "Family To Family Citations":
                    appsClaimingPriority_detail = browser.find_element_by_xpath(
                        '//*[@id="wrapper"]/div[3]/div[' + str(div_num_count1) + ']/div/div[2]/div[' + str(
                            i) + ']').text
                    appsClaimingPriority.append(appsClaimingPriority_detail)
                else:
                    continue

    # Legal Events
    if is_exist_element('//*[@id="legalEvents"]') == True:
        div_num_count1 = div_num_count1 + 1
        legalEvents = []
        legalEvents_len = len(
            browser.find_elements_by_xpath('//*[@id="wrapper"]/div[3]/div[' + str(div_num_count1) + ']/div/div[2]/div'))

        for i in range(1, legalEvents_len + 1):
            if is_exist_element('//*[@id="wrapper"]/div[3]/div[' + str(div_num_count1) + ']/div/div[2]/div[' + str(
                    i) + ']') == True and browser.find_element_by_xpath(
                '//*[@id="wrapper"]/div[3]/div[' + str(div_num_count1) + ']/div/div[2]/div[' + str(
                    i) + ']').text != "Family To Family Citations":
                legalEvents_detail = browser.find_element_by_xpath(
                    '//*[@id="wrapper"]/div[3]/div[' + str(div_num_count1) + ']/div/div[2]/div[' + str(i) + ']').text
                legalEvents.append(legalEvents_detail)
            else:
                continue

# Concepts(未爬取)
