# -*- coding: utf8 -*-
from flask import Flask, request, abort, render_template
from flask.ext.cache import Cache
import requests
import re
import json
import time
import threading

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'filesystem',
                           'CACHE_DEFAULT_TIMEOUT': 60 * 60 * 24,
                           'CACHE_DIR': 'E:\project\miaopai-thief.git\cache'})
time_out = 60
index_doc = {
    'update_time': 0,
    'doc': {},
}


@app.route('/')
@cache.cached(timeout=60 * 10)
def index():
    if index_doc['doc'] == {}:
        index_doc['doc'] = get_index_doc()
        index_doc['update_time'] = int(time.time())
    else:
        now_time = int(time.time())
        if now_time - index_doc['update_time'] > 3600:
            threading.Thread(target=update_index_doc).start()

    return render_template('index.html',
                           hot_videos=index_doc['doc']['hot_videos'],
                           star_videos=index_doc['doc']['star_videos'],
                           redian_videos=index_doc['doc']['redian_videos'],
                           nvshen_videos=index_doc['doc']['nvshen_videos'],
                           chuangyi_videos=index_doc['doc']['chuangyi_videos'],
                           gaoxiao_videos=index_doc['doc']['gaoxiao_videos'],
                           baobao_videos=index_doc['doc']['baobao_videos'],
                           mengchong_videos=index_doc['doc']['mengchong_videos'],
                           shuishoupai_videos=index_doc['doc']['shuishoupai_videos'],
                           huatis=index_doc['doc']['huatis'],
                           )


@app.route('/clear/cache')
@cache.cached()
def clear_cache():
    cache.clear()
    return 'cache clear success!'


@app.route('/u/<path>')
@cache.cached()
def user(path):
    req = requests.session()
    req.cookies.clear()
    if request.query_string:
        url = 'http://www.miaopai.com/u/' + path + '?' + request.query_string
    else:
        url = 'http://www.miaopai.com/u/' + path
    res = req.get(url, timeout=time_out)
    html = replace_html(res.text)

    # 转发页面的title优化
    if request.query_string == 'type=fwded':
        html = html.replace(u'的秒拍视频', u'的转发视频')
        pass
    if request.query_string == 'type=like':
        html = html.replace(u'的秒拍视频', u'的点赞视频')
        pass

    return html


@app.route('/u/<path>/relation/follow.htm')
@cache.cached()
def follow(path):
    req = requests.session()
    req.cookies.clear()
    url = 'http://www.miaopai.com/u/' + path + '/relation/follow.htm'
    res = req.get(url, timeout=time_out)
    html = replace_html(res.text)
    html = html.replace(u'的秒拍关注', u'的QQ秒拍关注')
    return html


@app.route('/u/<path>/relation/fans.htm')
@cache.cached()
def fans(path):
    req = requests.session()
    req.cookies.clear()
    url = 'http://www.miaopai.com/u/' + path + '/relation/fans.htm'
    res = req.get(url, timeout=time_out)
    html = replace_html(res.text)
    html = html.replace(u'的秒拍粉丝', u'的QQ秒拍粉丝')
    return html


@app.route('/show/<path>')
@cache.cached()
def show(path):
    req = requests.session()
    req.cookies.clear()
    url = 'http://www.miaopai.com/show/' + path
    res = req.get(url, timeout=time_out)
    html = replace_html(res.text)
    title = get_center_str(u'的秒拍视频。', '">', html)
    html = html.replace(u'<title>秒拍视频</title>', '<title>' + title + u'视频_QQ秒拍网</title>')
    return html


@app.route('/stpid/<path>')
@cache.cached()
def stpid(path):
    req = requests.session()
    req.cookies.clear()
    url = 'http://www.miaopai.com/stpid/' + path
    res = req.get(url, timeout=time_out)
    html = replace_html(res.text)
    return html


@app.route('/miaopai/<path>')
@cache.cached()
def topic(path):
    req = requests.session()
    req.cookies.clear()
    if request.url.find('topic') > 0:
        url = 'http://www.miaopai.com/miaopai/topic?' + request.query_string
    elif request.url.find('plaza') > 0:
        url = 'http://www.miaopai.com/miaopai/plaza?' + request.query_string
    else:
        abort('404')
    res = req.get(url, timeout=time_out)
    html = replace_html(res.text)
    return html


def update_index_doc():
    index_doc['doc'] = get_index_doc()
    index_doc['update_time'] = int(time.time())


def get_index_doc():
    req = requests.session()

    # 获取热门视频
    url = 'http://www.miaopai.com/miaopai/index_api?cateid=2002&per=20&page=1'
    req.cookies.clear()
    res = req.get(url, timeout=time_out)
    hot_video = json.loads(res.text)
    hot_videos = hot_video.get('result')

    # 获取明星视频
    url = 'http://www.miaopai.com/miaopai/index_api?cateid=124&per=20&page=1'
    req.cookies.clear()
    res = req.get(url, timeout=time_out)
    star_video = json.loads(res.text)
    star_videos = star_video.get('result')

    # 获取热点视频
    url = 'http://www.miaopai.com/miaopai/index_api?cateid=4&per=20&page=1'
    req.cookies.clear()
    res = req.get(url, timeout=time_out)
    redian_video = json.loads(res.text)
    redian_videos = redian_video.get('result')

    # 获取女神视频
    url = 'http://www.miaopai.com/miaopai/index_api?cateid=132&per=20&page=1'
    req.cookies.clear()
    res = req.get(url, timeout=time_out)
    nvshen_video = json.loads(res.text)
    nvshen_videos = nvshen_video.get('result')

    # 获取创意视频
    url = 'http://www.miaopai.com/miaopai/index_api?cateid=160&per=20&page=1'
    req.cookies.clear()
    res = req.get(url, timeout=time_out)
    chuangyi_video = json.loads(res.text)
    chuangyi_videos = chuangyi_video.get('result')

    # 获取搞笑视频
    url = 'http://www.miaopai.com/miaopai/index_api?cateid=128&per=20&page=1'
    req.cookies.clear()
    res = req.get(url, timeout=time_out)
    gaoxiao_video = json.loads(res.text)
    gaoxiao_videos = gaoxiao_video.get('result')

    # 获取宝宝视频
    url = 'http://www.miaopai.com/miaopai/index_api?cateid=144&per=20&page=1'
    req.cookies.clear()
    res = req.get(url, timeout=time_out)
    baobao_video = json.loads(res.text)
    baobao_videos = baobao_video.get('result')

    # 获取萌宠视频
    url = 'http://www.miaopai.com/miaopai/index_api?cateid=140&per=20&page=1'
    req.cookies.clear()
    res = req.get(url, timeout=time_out)
    mengchong_video = json.loads(res.text)
    mengchong_videos = mengchong_video.get('result')

    # 获取随手拍视频
    url = 'http://www.miaopai.com/miaopai/index_api?cateid=9&per=20&page=1'
    req.cookies.clear()
    res = req.get(url, timeout=time_out)
    shuishoupai_video = json.loads(res.text)
    shuishoupai_videos = shuishoupai_video.get('result')

    # 获取热门话题
    url = 'http://api.miaopai.com/m/hottopic_web.json?per=16&page=1'
    req.cookies.clear()
    res = req.get(url, timeout=time_out)
    huati = json.loads(res.text)
    huatis = huati.get('result')
    doc = {
        'hot_videos': hot_videos,
        'star_videos': star_videos,
        'redian_videos': redian_videos,
        'nvshen_videos': nvshen_videos,
        'chuangyi_videos': chuangyi_videos,
        'gaoxiao_videos': gaoxiao_videos,
        'baobao_videos': baobao_videos,
        'mengchong_videos': mengchong_videos,
        'shuishoupai_videos': shuishoupai_videos,
        'huatis': huatis,
    }
    return doc


def replace_html(html):
    html = html.replace(u'秒拍-10秒拍大片', u'QQ秒拍网')
    html = html.replace('http://www.miaopai.com/u/', '/u/')
    html = html.replace('http://www.miaopai.com/show/', '/show/')
    html = html.replace('/cc/checkcookie', 'http://www.miaopai.com/cc/checkcookie')
    html = html.replace('<a href=\'http://www.miaopai.com/\'><b class="head_logo"></b></a>',
                        '<a href="/"><b class="head_logo"></b></a>')
    html = html.replace(u'<li ><a href=\'http://www.miaopai.com/\'>首页</a></li>', u'<li ><a href="/">首页</a></li>')
    html = html.replace('http://www.miaopai.com/miaopai/topic?topicname', '/miaopai/topic?topicname')
    html = html.replace('http://www.miaopai.com/miaopai/topic?topic=', '/miaopai/topic?topic=')
    html = html.replace('http://www.miaopai.com/miaopai/plaza', '/miaopai/plaza')
    html = html.replace('http://www.miaopai.com/stpid', '/stpid')
    html = html.replace(u'''京ICP备12022740号 京公网安备11010502026918 炫一下（北京）科技有限公司 Copyright © MiaoPai All rights reserved.<br />
北京市朝阳区红军营南路瑞普大厦15层1503室 010-64828268''', u'本站视频均来源于网络，如有版权问题请联系我们删除（QQ秒拍网 www.qqfans.com.cn）渝ICP备12003008号-10')
    html = html.replace(u'''        <div style="width:300px;margin:0 auto; padding:20px 0;">
          <a target="_blank" href="http://www.beian.gov.cn/portal/registerSystemInfo?recordcode=11010502030231" style="display:inline-block;text-decoration:none;height:20px;line-height:20px;">
            <img src="http://wsacdn2.miaopai.com/static20131031/miaopai20140729/img/ba.png" style="float:left;"/>
            <p style="float:left;height:20px;line-height:20px;margin: 0px 0px 0px 5px; color:#939393;clear: none;">京公网安备 11010502030231号</p>
          </a>
        </div>''', '')
    html = html.replace('<b class="head_logo"></b>', '<img class="head_logo" src="/static/logo.jpg">')
    html = html.replace('119px', '69px')
    html = html.replace(u'''<!-- <div class="clearfix" style="color: #b1b1b1; margin: auto; padding: 10px 0 6px 0;text-align:center; position: relative; font-size:14px;color: #b1b1b1;">
           <a style="color: #b1b1b1;padding:0 6px;" target="_blank" href="http://www.miaopai.com/miaopai/introduction"> 公司简介 </a> | <a style="color: #b1b1b1;padding:0 6px;" target="_blank" href="http://www.miaopai.com/miaopai/contactus"> 联系方式 </a> | <a style="color: #b1b1b1;padding:0 6px;" target="_blank" href="http://www.miaopai.com/miaopai/business"> 业务介绍 </a>
        </div> -->''', '')
    html = html.replace(u'''<!-- 		<ul class='clearfix'>
			<li><a href="">关于我们</a></li>
			<li><a href="">意见反馈</a></li>
			<li class='logo_s'><b></b></li>
		</ul> -->''', '')
    html = html.replace(u'''京ICP备12022740号 Copyright © YIXIA All rights reserved.''',
                        u'''本站视频均来源于网络，如有版权问题请联系我们删除（QQ秒拍网 www.qqfans.com.cn）渝ICP备12003008号-10 <script>
var _hmt = _hmt || [];
(function() {
  var hm = document.createElement("script");
  hm.src = "//hm.baidu.com/hm.js?e335e212bf034d1f5f5f52e3efeabbca";
  var s = document.getElementsByTagName("script")[0];
  s.parentNode.insertBefore(hm, s);
})();
</script>
''')
    html = html.replace(u'''<!-- <p style="margin-top:10px;">商务合作： 杨先生  18501264917</p> -->''', '')
    html = html.replace(
        u'''<a class='ts1' href="http://weibo.com/shoujipaike?topnav=1&wvr=5&topsug=1"  target='_blank'> <b class='sina_icon'></b><p style='margin-top: 24px;display: inline;color: #bababa;font-size: 16px;border-bottom: 1px solid #bababa;'>联系我们的微博</p></a>''',
        '')
    html = html.replace('http://ent.v.sina.cn/', '/')
    return html


def get_center_str(left, right, str):
    s = re.compile(left + '(.|[\s\S]*?)' + right).search(str)
    try:
        return s.group(1)
    except:
        return ''


if __name__ == '__main__':
    app.run(debug=False)
