import re
import time
import datetime
import codecs

from bs4 import BeautifulSoup
from selenium import webdriver
from xml.dom.minidom import Document
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import StaleElementReferenceException

# 设置代理，登录
def login_weibo(username, password):
    driver = webdriver.Chrome()
    driver.get("https://weibo.com/")

    time.sleep(10)
    # 定位用户名密码文本框
    username_field = driver.find_element_by_xpath('//*[@id="loginname"]')
    password_field = driver.find_element_by_xpath('//*[@id="pl_login_form"]/div/div[3]/div[2]/div/input')

    # 输入用户名密码:
    username_field.send_keys(username)
    time.sleep(5)
    password_field.send_keys(password)
    time.sleep(2)

    driver.find_element_by_xpath('//*[@id="pl_login_form"]/div/div[3]/div[6]/a').click()

    return driver


# 搜索模块有多页结果时对页面自动滚动事件的处理
class wait_for_more_than_n_elements_to_be_present(object):
    def __init__(self, locator, count):
        self.locator = locator
        self.count = count

    def __call__(self, driver):
        try:
            elements = ec._find_elements(driver, self.locator)
            return len(elements) > self.count
        except StaleElementReferenceException:
            return False


def format_time(time_text):
    pattern = re.compile('[0-9:]+')
    figure = pattern.findall(time_text)  # 可能是5：45 或2，1 ，50等
    '''
    sina中使用的时间格式：1-60分钟前    2017-9-7 00:49 今天6:23    9月3日16:59   
    '''
    if '今天' in time_text:
        result = (datetime.datetime.now()).strftime("%Y-%m-%d") + ' ' + figure[0]
    elif '分钟前' in time_text:
        result = (datetime.datetime.now() - datetime.timedelta(minutes=int(figure[0]))).strftime("%Y-%m-%d %H:%M")
    elif '月' in time_text:
        time_list = re.split('[月日]', time_text)
        result = datetime.datetime.now().strftime('%Y') + '-' + time_list[0] + '-' + time_list[1].strip() + ' ' + \
                 time_list[2].strip()
    elif '-' in time_text:
        result = time_text
    elif '秒前' in time_text:
        result = (datetime.datetime.now() - datetime.timedelta(seconds=int(figure[0]))).strftime("%Y-%m-%d %H:%M")
    else:
        result = datetime.datetime.now().strftime("%Y-%m-%d %H:%M") + ' ' + time_text

    return result


def write_xml(post_dic, reply_list, outfile):
    doc = Document()
    post = doc.createElement('weibo_timescope')
    doc.appendChild(post)
    for k, v in post_dic.items():
        temp = doc.createElement(k)
        post.appendChild(temp)
        try:
            temp.appendChild(doc.createTextNode(v))
        except:
            print(k, v)

    replylist = doc.createElement('weibolist')
    post.appendChild(replylist)

    # 回复数据列表构建dom对象
    for c in reply_list:
        reply = doc.createElement('weibo')
        replylist.appendChild(reply)

        for k, v in c.items():
            # 这种方式得到的xml，没有以k命名的标签显示，只有值
            temp = doc.createElement(k)
            reply.appendChild(temp)
            try:
                temp.appendChild(doc.createTextNode(v))
            except:
                print(k, v)
    # type(doc.toprettyxml(indent='\t', encoding='utf-8'))返回的是bytes类型，写入文件时，需要以'wb+'方式打开文件

    with open(outfile, 'wb+') as f:
        f.write(doc.toprettyxml(indent='\t', encoding='utf-8'))


# 生成时间
def next_time(start, interval):
    date = datetime.datetime.strptime(start, '%Y-%m-%d-%H')
    new_date_str = (date + datetime.timedelta(hours=interval)).strftime("%Y-%m-%d-%H")
    return new_date_str


# 返回true,time1比time2大，否则返回1
def bijiao_time(time1, time2):
    date1 = datetime.datetime.strptime(time1, '%Y-%m-%d-%H')
    date2 = datetime.datetime.strptime(time2, '%Y-%m-%d-%H')
    if (date1 - date2).days >= 0 and (date1 - date2).seconds > 0:
        return True
    else:
        return False


def crawl_one_topic_all(driver, query, topicid, start_time, stop_time, interval):
    driver.get("http://s.weibo.com/")
    time.sleep(5)

    # 定位搜索框，输入关键字并提交
    # box = driver.find_element_by_class_name("search-input")#searchInp_form
    box = driver.find_element_by_xpath('//*[@id="pl_homepage_search"]/div/div[2]/div/input')
    # box = box.find_element_by_name('input')
    box.clear()
    box.send_keys(query)
    time.sleep(2)
    # 单击搜索按钮， 获取搜索的url
    # driver.find_element_by_xpath('//*[@id="pl_searchHead"]/div[1]/div/div/div[1]/a').click()
    driver.find_element_by_xpath('//*[@id="pl_homepage_search"]/div/div[2]/button').click()
    time.sleep(5)

    # 拼接url
    url = driver.current_url
    url_search = url.split('&')[0]

    end_time = next_time(start_time, interval)

    while True:
        # 判断 start_time 和stop_time区别 ？？？
        if bijiao_time(start_time, stop_time):
            break
        # 产生爬取数据的时间区间：
        outfile = topicid + '/' + start_time + '-' + end_time + '.xml'  # '2018-09-02-0' '2018-09-02-6' 包含00-6:59的所有微博
        print(outfile)
        time.sleep(10)
        while True:
            try:
                flag = crawl_one_timescope(driver, start_time, end_time, url_search, query, outfile)
            except:
                time.sleep(60)
                continue
            else:
                break

        if flag == 1:
            start_time = next_time(end_time, 1)
            end_time = next_time(start_time, interval)
        if flag == 0:
            if interval == 0:
                print('间隔不能再减少了！')
            else:
                print('间隔缩减')
                start_date = datetime.datetime.strptime(start_time, '%Y-%m-%d-%H')
                end_date = datetime.datetime.strptime(end_time, '%Y-%m-%d-%H')
                interval_hour = (end_date - start_date).days * 24 + (end_date - start_date).seconds // 60 // 60
                interval = interval_hour // 2
                end_time = next_time(start_time, interval)
        if flag == 2:
            print('间隔增加')
            start_date = datetime.datetime.strptime(start_time, '%Y-%m-%d-%H')
            end_date = datetime.datetime.strptime(end_time, '%Y-%m-%d-%H')
            interval_hour = (end_date - start_date).days * 24 + (end_date - start_date).seconds // 60 // 60
            interval = interval_hour * 2
            start_time = next_time(end_time, 1)
            end_time = next_time(start_time, interval)

    print('爬取结束')


def crawl_one_timescope(driver, start_time, end_time, url_search, topic, outfile):
    timescope = start_time + ':' + end_time
    # scope = ori 表明只爬取原创的
    url_pre = url_search + '&scope=ori&suball=1&timescope=custom:' + timescope + '&page=1'
    driver.get(url_pre)
    time.sleep(15)
    try:
        # page_num = len(driver.find_element_by_css_selector('div.layer_menu_list.W_scroll').find_elements_by_tag_name('li'))
        page_num = len(driver.find_element_by_class_name('s-scroll').find_elements_by_tag_name('li'))

    except:
        page_num = 1
    # 按标签名查找by_tag_name
    if (page_num >= 50):
        print('总共' + str(page_num) + '页需要缩减')
        return 0  # 0表示搜索结果超过50页，请重新设定搜索区间，1表示成功爬取此时间段的微博
    else:
        print('总共' + str(page_num) + '页')

    time.sleep(5)
    weibo_list = []
    num = 0
    while True:
        # 在解析weibo之前，要找到所有展开全文的按钮，单击,都能成功展开，不会涉及到页面刷新的问题。
        # zhankaibtns = driver.find_elements_by_class_name('WB_text_opt')
        zhankaibtns = driver.find_elements_by_partial_link_text('展开全文')

        print(len(zhankaibtns))
        for btn in zhankaibtns:
            btn.click()
            time.sleep(2)
        time.sleep(10)
        parse_one_search_page(driver.page_source, weibo_list)
        num += 1
        print('第' + str(num) + '页')
        print(len(weibo_list))
        # time.sleep(5)
        try:
            # 打开下一页
            next_btn = driver.find_element_by_class_name('next')
        except:
            break
        else:
            next_btn.click()
            time.sleep(5)

    # 生成字典
    dic = {'start_time': start_time, 'end_time': end_time, 'num': str(len(weibo_list)), 'topic': topic}
    # 将爬取内容写入文件
    write_xml(dic, weibo_list, outfile)
    print(weibo_list)
    # page_num<15 增加interval
    if page_num < 15:
        return 2
    else:
        return 1


# 爬取一个搜索页面上的所有微博，所有需打开的内容都打开了，当成静态页面使用bs4处理
def parse_one_search_page(page_source, weibo_list):
    soup = BeautifulSoup(page_source, 'html.parser')
    weibo_block = soup.find('div', {'class': 'search_feed'})
    # 查找所有微博块
    # weibo_elements = weibo_block.select('div.WB_cardwrap.S_bg2.clearfix') 20181202
    weibo_elements = soup.find_all('div', {'class': 'card-wrap'})
    print("当前页微博数", len(weibo_elements))
    for weibo in weibo_elements:
        if '&' not in weibo.div['tbinfo']:  # 此部分只处理源weibo，回复微博暂时不爬取
            weibo_id = weibo.div['mid']
            content = weibo.select('div.content.clearfix')[0].find('div', {'class': 'feed_content'})
            user_name = content.a.get_text()
            user_url = content.a['href']
            try:
                user_approved = content.a.find_next_sibling('a')['title']
            except:
                user_approved = ''

            # 处理有文档比较长的情况
            texts_ele = content.find_all('p', {'class': 'comment_txt'})
            tag = 0
            if len(texts_ele) == 1:
                tag = 0
            elif len(texts_ele) == 2:
                tag = 1
            else:
                print('找到多余2个的文本')

            # 爬取、处理微博正文
            result = ''
            for txt_tag in texts_ele[tag].contents:
                if txt_tag.name == None:  # 微博内容，字符串
                    result += txt_tag
                elif txt_tag.name == 'em':  # 检索关键字
                    result += txt_tag.get_text()
                elif txt_tag.name == 'br':  # 换行符
                    result += '\n'
                elif txt_tag.name == 'img':  # 表情符
                    if txt_tag.has_attr('title'):
                        result += txt_tag['title'] + ' '
                    else:
                        result += '[img]'
                    if txt_tag.has_attr('src'):
                        result += ' ' + txt_tag['src'] + ' '
                elif txt_tag.name == 'a':  # 有四种情况，一种是链接，另一种是topic # #封装起来的，最后是@，收起全文或展开全文
                    # 根据class属性值判断这四种情况
                    # 有一种情况是没有class属性的情况
                    if txt_tag.has_attr('class'):
                        class_att_list = txt_tag['class']
                        if 'a_topic' in class_att_list:  # topic
                            # 有可能在主题词里有检索词，会用em标签封装
                            result += ''.join(txt_tag.find_all(text=True))
                        elif 'W_linkb' in class_att_list:  # @开头的
                            result += txt_tag.get_text() + ' '
                        elif 'W_btn_c6' in class_att_list:  # 网页链接
                            result += ' ' + txt_tag['href'] + ' '
                        elif 'video_link' in class_att_list:  # 视频
                            result += ' ' + txt_tag['href'] + ' '
                        elif 'WB_text_opt' in class_att_list:
                            pass
                        else:
                            print("----------发现没有处理的a标签,且包含class属性")
                            print(txt_tag)
                            print(weibo_id)
                    else:
                        result += '(' + re.sub('\s', '', txt_tag.get_text()) + ')' + ' ' + txt_tag['href'] + ' '
                        # 有个特殊字符，正方形的
                else:
                    print('*****发现新tag' + txt_tag.name)

            sub_time = format_time(weibo.find('a', {'class': 'W_textb'}).get_text())
            weibo_url = weibo.find('a', {'class': 'W_textb'})['href']
            # 可能没有发布客户端显示，所以找不到就为空
            try:
                pub_client = weibo.find('a', {'class': 'W_textb'}).find_next_sibling('a').get_text()
            except:
                pub_client = ''

            # 在这里面爬取点赞、评价、'feed_action clearfix'
            act = weibo.select('div.feed_action.clearfix')[0].find_all('li')
            favorite_num = ''.join(act[0].find_all(text=True))  # 收藏
            forward_num = ''.join(act[1].find_all(text=True))  # 转发
            comment_num = ''.join(act[2].find_all(text=True))  # 评论
            if len(act[3].find_all(text=True)) == 0:  # 赞
                like_num = '0'
            else:
                like_num = act[3].find_all(text=True)[0]

            weibo_list.append({'weibo_id': weibo_id,
                               'weibo_url': weibo_url,
                               'text': result,
                               'user_name': user_name,
                               'user_url': user_url,
                               'user_approved': user_approved,
                               'sub_time': sub_time,
                               'pub_client': pub_client,
                               'favorite_num': favorite_num,
                               'forward_num': forward_num,
                               'comment_num': comment_num,
                               'like_num': like_num})


def get_topic_tweeturl(pagesource, topicid):
    soup = BeautifulSoup(pagesource, 'html.parser')
    tweets = soup.select('li.js-stream-item.stream-item.stream-item')
    print(len(tweets))
    tweet_url_list = []
    for tweet in tweets:
        tweet_url_list.append(tweet.div['data-permalink-path'])
    result = ','.join(tweet_url_list)

    outfile = codecs.open(topicid + '_tweet_urllist' + ".txt", "w", "utf-8")
    outfile.write(result)
    outfile.close()
    return tweet_url_list


username = '***'
password = '***'
driver = login_weibo(username, password)
topic = '***'

start_time = '2018-11-21-00'
interval = 18
stop_time = '2018-12-01-23'
crawl_one_topic_all(driver, topic, 'topic', start_time, stop_time, interval)
