#coding:utf-8
import re
import time
from os.path import abspath, dirname, join
from operator import itemgetter

import _env
from spider.spider import route, Handler, spider

PREFIX = join(dirname(abspath(__file__)))
HTTP = 'http://www.huxiu.com/%s'

tag_info = {}
tag_names = {}

@route('/tagslist/all.html')
class tagslist(Handler):
    def get(self):
        id_list = []
        for link in self.extract_all('<a href="/tags/', '</a>'):
            tag_id = link.split('.')[0]
            tag_name = link.split('>')[1]
            tag_names[int(tag_id)] = tag_name
            id_list.append(tag_id)
        for t_id in id_list:
            newlink = 'tags/' + t_id + '.html'
            spider.put(HTTP%newlink)

@route('/tags/\d+.*\.html')
class article(Handler):
    def get(self):
        url = str(self.url)
        r = re.compile(r'\d+')
        tag_id = int(r.findall(url)[0])

        # 获取文章标题
        names = self.extract_all('<h3><a href="/article/', '</a></h3>')
        for n in names:
            title = n.split('>')[1]
            if tag_id not in tag_info.keys():
                tag_info[tag_id] = [title]
            else:
                tag_info[tag_id].append(title)

        # 分页跳转，如果有下一页就继续进行抓取，没有下一页则进行打印
        pages = self.extract('<span class="next"><a href="http://www.huxiu.com/tags/', '.html">')
        if pages:
            link = "tags/%d/%d.html" % (int(pages.split('/')[0]), int(pages.split('/')[1]))
            spider.put(HTTP%link)
        else:
            self.show_title(tag_id)

    def show_title(self, tag_id):
        if tag_id not in tag_info.keys():
            tag_info[tag_id] = []
        print tag_names[tag_id]
        i = 1
        for item in tag_info[tag_id]:
            print '\t%d' % i, item
            i += 1
        raw_input()


if __name__ == '__main__':
    spider.put('http://www.huxiu.com/tagslist/all.html')
    #10个并发抓取线程 , 网页读取超时时间为30秒
    spider.run(10, 30)

