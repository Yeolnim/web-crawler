# -*- coding: utf-8 -*-
import requests
import execjs
import http.client
import hashlib
import json
import urllib
import time
import random
import xml.etree.ElementTree as et

tree = et.parse('AmazonReview.xml')
root = tree.getroot()


def baidu_translate(content, fromLang='zh', toLang='en'):
    appid = '20151113000005349'
    secretKey = 'osubCEzlGjzvw8qdQc41'
    httpClient = None
    myurl = '/api/trans/vip/translate'
    q = content
    # fromLang = 'ru'  # 源语言
    # toLang = 'zh'  # 翻译后的语言
    salt = random.randint(32768, 65536)
    sign = appid + q + str(salt) + secretKey
    sign = hashlib.md5(sign.encode()).hexdigest()
    myurl = myurl + '?appid=' + appid + '&q=' + urllib.parse.quote(
        q) + '&from=' + fromLang + '&to=' + toLang + '&salt=' + str(
        salt) + '&sign=' + sign

    try:
        httpClient = http.client.HTTPConnection('api.fanyi.baidu.com')
        httpClient.request('Get', myurl)
        # response是HTTPResponse对象
        response = httpClient.getresponse()
        jsonResponse = response.read().decode("utf-8")  # 获得返回的结果，结果为json格式
        js = json.loads(jsonResponse)  # 将json格式的结果转换字典结构
        dst = str(js["trans_result"][0]["dst"])  # 取得翻译后的文本结果
        return dst
    except Exception as e:
        return e
    finally:
        if httpClient:
            httpClient.close()
            time.sleep(1)


class Py4Js():

    def __init__(self):
        self.ctx = execjs.compile(""" 
		function TL(a) { 
		var k = ""; 
		var b = 406644; 
		var b1 = 3293161072; 

		var jd = "."; 
		var $b = "+-a^+6"; 
		var Zb = "+-3^+b+-f"; 

		for (var e = [], f = 0, g = 0; g < a.length; g++) { 
			var m = a.charCodeAt(g); 
			128 > m ? e[f++] = m : (2048 > m ? e[f++] = m >> 6 | 192 : (55296 == (m & 64512) && g + 1 < a.length && 56320 == (a.charCodeAt(g + 1) & 64512) ? (m = 65536 + ((m & 1023) << 10) + (a.charCodeAt(++g) & 1023), 
			e[f++] = m >> 18 | 240, 
			e[f++] = m >> 12 & 63 | 128) : e[f++] = m >> 12 | 224, 
			e[f++] = m >> 6 & 63 | 128), 
			e[f++] = m & 63 | 128) 
		} 
		a = b; 
		for (f = 0; f < e.length; f++) a += e[f], 
		a = RL(a, $b); 
		a = RL(a, Zb); 
		a ^= b1 || 0; 
		0 > a && (a = (a & 2147483647) + 2147483648); 
		a %= 1E6; 
		return a.toString() + jd + (a ^ b) 
	}; 

	function RL(a, b) { 
		var t = "a"; 
		var Yb = "+"; 
		for (var c = 0; c < b.length - 2; c += 3) { 
			var d = b.charAt(c + 2), 
			d = d >= t ? d.charCodeAt(0) - 87 : Number(d), 
			d = b.charAt(c + 1) == Yb ? a >>> d: a << d; 
			a = b.charAt(c) == Yb ? a + d & 4294967295 : a ^ d 
		} 
		return a 
	} 
	""")

    def getTk(self, text):
        return self.ctx.call("TL", text)


def google_szn_trans_sentence(sentence, sl="zh-CN", tl="en"):
    # 中：zh-CN，英：en
    headers = {
        'cookie': '_ga=GA1.3.1163951248.1511946285; NID=131=XX0_dJsOrF47GXs2WNtO1MXyKVCK39bW4HXS0XZZ3ZYHTvMGOz8CVJe1G2XVwAJNF9MYOb1ngCqa_NegB6db2kgJ5A9hT3SScy0ag_L41wvtXHiPpNZweONFGHFNtWR_; 1P_JAR=2018-6-7-15',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36',
    }

    url = 'https://translate.google.cn/translate_a/single?client=t&sl=' + sl + '&tl=' + tl + '&hl=' + tl \
          + '&dt=at&dt=bd&dt=ex&dt=ld&dt=md&dt=qca&dt=rw&dt=rm&dt=ss&dt=t&ie=UTF-8&oe=UTF-8&otf=1&ssel=0&tsel=0&kc=2&tk={tk}&q=' + sentence

    js = Py4Js()
    tk = js.getTk(sentence)
    url = url.format(tk=tk)
    # while
    result = ""
    try:
        s = requests.get(url, headers=headers)
        sj_lst = s.json()
        if len(sj_lst[0]) == 1:
            result = sj_lst[0][0][0]
        else:
            for x in sj_lst[0][:-1]:
                result += x[0]
    except:
        pass
    return result


if __name__ == '__main__':

    for item in root.findall('item'):
        summary = item.find('summary').text
        text = item.find('text').text
        num = item.find('num').text
        # print(summary, '\n', text)

        try:
            if text == None:
                summary_trans = google_szn_trans_sentence(summary, tl="en")
                text_trans = ""
            else:
                summary_trans = google_szn_trans_sentence(summary, tl="en")
                text_trans = google_szn_trans_sentence(text, tl="en")
                if text_trans == "":
                    text_trans = baidu_translate(text, fromLang='zh', toLang='en')

            print(num, '\n', summary_trans, '\n', text_trans)

            summarytrans = et.Element("summary_trans")
            texttrans = et.Element("text_trans")

            summarytrans.text = summary_trans
            texttrans.text = text_trans

            summarytrans.tail = '\n'
            texttrans.tail = '\n'

            item.append(summarytrans)
            item.append(texttrans)

            tree.write("AmazonReview.xml", encoding="utf-8", xml_declaration=True)
        except Exception as e:
            print(e)
