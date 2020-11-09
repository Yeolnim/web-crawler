from selenium import webdriver
import time


def login_weibo(username, password):
    driver = webdriver.Chrome()
    driver.get("https://weibo.com/")

    time.sleep(10)
    # 定位用户名密码文本框
    username_field = driver.find_element_by_xpath('//*[@id="loginname"]')
    password_field = driver.find_element_by_xpath('//*[@id="pl_login_form"]/div/div[3]/div[2]/div/input')

    # 输入用户名密码:
    username_field.send_keys(username)
    time.sleep(10)
    password_field.send_keys(password)
    time.sleep(10)

    driver.find_element_by_xpath('//*[@id="pl_login_form"]/div/div[3]/div[6]/a').click()
    driver.find_element_by_xpath('//*[@id="pl_login_form"]/div/div[3]/div[3]/div/input').send_keys(input("输入验证码： "))
    # time.sleep(10)
    driver.find_element_by_xpath('//*[@id="pl_login_form"]/div/div[3]/div[6]/a').click()  # 再次点击登陆
    # time.sleep(10)
    return driver


username = ' '  # 用户名
password = ' '  # 密码
driver = login_weibo(username, password)
