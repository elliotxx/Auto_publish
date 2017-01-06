#coding=utf8
import os
import re
import json
import urllib,urllib2
import cookielib


class Auto_Publish:
    # 成员变量
    opener = None
    items = []
    i = 0
    cookie_file = 'cookie.txt'      # 保存cookie的文件
    question_file = '题库.txt'      # 题库文件
    host = 'http://www.anoah.com/'  # host地址

    # 成员函数
    def __init__(self):

        # 模拟登录系统，生成cookie
        print '登录中……'.decode('utf8').encode('gbk')
        #声明一个MozillaCookieJar对象实例来保存cookie，创建opener
        cookie = cookielib.MozillaCookieJar(self.cookie_file)
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))

        #登录系统的URL
        login_url = 'http://www.anoah.com/ebag/index.php?r=user/ajaxlogin'
        #POST数据
        postdata = urllib.urlencode({       # 坑爹的地方，还要套上一层列表
                'LoginForm[username]':'填写用户名',
                'LoginForm[password]':'填写密码',
                'LoginForm[rememberMe]':'0'
        })
        #模拟登录，并把cookie保存到变量
        result = self.opener.open(login_url,postdata).read()
        result = json.loads(result[1:-2])
        if result['status']==1:
            print '账户登录成功！'.decode('utf8').encode('gbk')
        else:
            raise Exception,'账户登录失败！请检查用户名和密码！'.decode('utf8').encode('gbk')

        #保存cookie到cookie.txt中
        #cookie.save(ignore_discard=True, ignore_expires=True)
        #从文件中加载cookie
        #cookie.load(ignore_discard=True, ignore_expires=True)

        # 读取本地题库到items
        fp = open(self.question_file.decode('utf8').encode('gbk'), 'r')
        cont = fp.read().decode('gbk')
        self.items = re.split('\n', cont)
        self.i = 0
        fp.close()


    def question_pulish(self,type_name,**kw):
        # 发布题目
        # 上传链接
        url = 'http://e.anoah.com/index.php?r=qti/rmaker/saveQti'
        # 加入标签信息
        kw['qdata[body]'] = kw['qdata[body]'].encode('utf8')

        # 单选题特殊选项
        if 'qdata[options][]' in kw.keys():
            for i,q in enumerate(kw['qdata[options][]']):
                kw['qdata[options][]'][i] = '<p>%s</p>'%q.encode('utf8')
        # 填空题特殊选项
        if 'qdata[answer][]' in kw.keys():
            for i,a in enumerate(kw['qdata[answer][]']):
                kw['qdata[answer][]'][i] = '<p>%s</p>'%a.encode('utf8')

        #POST题目数据
        postdata = {
        'qid':'0',
        'qdata[intro]':'',
        'qdata[tips]':'',
        'qdata[explain]':'',
        'qdata[difficulty]':'0',
        'qdata[comment]':'',
        'qdata[kps]':'',
        'qdata[period_id]':'',
        'qdata[book_id]':'',
        'qdata[chapter_id]':'',
        'qdata[grade]':'0',
        'qdata[subject_id]':'0',
        'qdata[is_public]':'0',
        'qdata[status]':'2',
        'need_dcom':'1',
        'saveType':'1',
        'userType':'0',
        'saveMode':'2'
        }
        # 合并字典
        postdata=dict(postdata,**kw)

        postdata = urllib.urlencode(postdata,True)
        # 头部信息
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
        }
        request = urllib2.Request(url,postdata,headers=headers)
        result = self.opener.open(request).read()
        result = json.loads(result)
        if result['error']:
            raise Exception,'访问页面请求被拒绝！'.decode('utf8').encode('gbk')
        else:
            print '【资源编号】'.decode('utf8').encode('gbk'),result['qid']
            print '【资源类型】'.decode('utf8').encode('gbk'),type_name.decode('utf8').encode('gbk')
            print '【资源名称】'.decode('utf8').encode('gbk'),result['resourceName']
            print '发布成功！'.decode('utf8').encode('gbk')



    def getNextLine(self):
        # 获得题库的下一行内容
        if self.i>=len(self.items):
            return None
        while self.items[self.i]=='':
            self.i+=1
            if self.i>=len(self.items):
                return None
        self.i+=1
        return self.items[self.i-1]

    def getAnswer(self):
        # 从题库文件中解析答案数据
        answers = []
        item = self.getNextLine()
        while item!=None:
            item = item.strip()
            if len(item.split())>1:
                answers.append(item.split())
            else:
                answers.append(item)
            item = self.getNextLine()
        return answers

    def getDanxuan(self):
        # 从题库文件中解析单选题
        type = 'danxuan'
        question = []
        item = self.getNextLine()
        # 找到题干，匹配阿拉伯数字，以及所有封闭式数字符号
        m = re.match(u'[\d+|\u2460-\u24FE]',item)
        while m==None:
            item = self.getNextLine()
            m = re.match(u'[\d+|\u2460-\u24FE]',item)

        while m!=None:     # 匹配到题目
            #print item
            item = item[len(m.group()):]
            # 清理无效前缀（. 、．等）
            m = re.match(u'[.|\u3001|\uff0e]',item)
            if m!=None:     # 匹配到无效前缀
                item = item[len(m.group()):]    # 清除
            #print item,
            # 提取题干
            body = item
            while True:
                item = self.getNextLine().strip()
                if re.match(u'[A-Z|\uff21-\uff3a]',item)!=None:
                    break
                body += '<br>' + item
            #print body
            # 匹配选项
            opt = []
            while re.match(u'[\uff21-\uff3a|A-Z]',item[0])!=None:
                item_gourp = re.split(u'[\uff21-\uff3a|A-Z]',item)
                #print item_gourp
                for item in item_gourp:
                    if item!='':
                        item = item.strip()
                        # 清理无效前缀（. 、．等）
                        m = re.match(u'[.|\u3001|\uff0e]',item)
                        if m!=None:     # 匹配到无效前缀
                            item = item[len(m.group()):]    # 清除
                        opt.append(item)
                        #print item
                item = self.getNextLine().strip()
            # 记录题目
            question.append({'type':type,'body':body,'opt':opt})

            # item = self.getNextLine()
            m = re.match(u'[\d+|\u2460-\u24FE]', item)
        self.i-=1
        return question

    def getTiankong(self):
        # 从题库文件中解析填空题
        type = 'tiankong'
        question = []
        item = self.getNextLine()
        # 找到题干，匹配阿拉伯数字，以及所有封闭式数字符号
        m = re.match(u'[\d+|\u2460-\u24FE]',item)
        while m==None:
            item = self.getNextLine()
            m = re.match(u'[\d+|\u2460-\u24FE]',item)

        while m!=None:     # 匹配到题目
            #print item
            item = item[len(m.group()):]
            # 清理无效前缀（. 、．等）
            m = re.match(u'[.|\u3001|\uff0e]',item)
            if m!=None:     # 匹配到无效前缀
                item = item[len(m.group()):]    # 清除

            # 处理题干
            item = item.split()
            body = item[0]
            for i,x in enumerate(item):
                if i>0:
                    body += '<pos class="">%d</pos>%s'%(i,x)
            body = '<p>%s</p>'%body

            # 记录题目
            question.append({'type':type,'body':body})

            item = self.getNextLine()
            m = re.match(u'[\d+|\u2460-\u24FE]', item)
        self.i-=1
        return question

    def main(self):
        # 解析、发布题目
        # 局部变量
        answers = []
        question = []

        # 解析题目和答案数据
        print '正在解析题库文件……'.decode('utf8').encode('gbk')
        print '正在解析题目……'.decode('utf8').encode('gbk')
        item = self.getNextLine()
        while self.i<len(self.items):
            # 读取到答案区
            if item.find(u'参考答案')!=-1:
                print '正在解析答案……'.decode('utf8').encode('gbk')
                answer = self.getAnswer()
            elif item.find(u'单选题')!=-1:
                print '正在解析单选题……'.decode('utf8').encode('gbk')
                question+=self.getDanxuan()
            elif item.find(u'填空题')!=-1:
                print '正在解析填空题……'.decode('utf8').encode('gbk')
                question+=self.getTiankong()
            item = self.getNextLine()

        # 发布题目
        print '解析完毕，准备发布所有题目'.decode('utf8').encode('gbk')
        #print len(question) , len(answer)
        if len(question)==len(answer):
            i = 1
            for q,a in zip(question,answer):
                print ''
                info = '正在发布题库中的第【%d】题……'%i
                print info.decode('utf8').encode('gbk')
                if q['type']=='danxuan':
                    self.question_pulish('单选题',**{'qtype':q['type'],
                                            'qdata[qtype]':q['type'],
                                            'qdata[body]':q['body'],
                                            'qdata[options][]':q['opt'],
                                            'qdata[answer]':a})
                elif q['type']=='tiankong':
                    kw = {  'qtype':q['type'],
                            'qdata[qtype]':q['type'],
                            'qdata[body]':q['body'],
                            'qdata[answer][]':a,
                            'qdata[aorder]':0
                            }
                    self.question_pulish('填空题',**kw)
                i+=1
            print ''
            info = '总共【%d】道题目已发布完毕'%len(question)
            print info.decode('utf8').encode('gbk')
        else:
            raise Exception,'解析到的题目数量与答案数量不符合！请检查题库文件！'.decode('utf8').encode('gbk')




if __name__ == '__main__':
    try:
        Auto_Publish().main()
    except Exception,e:
        print '[ERROR]:%s'%e
    os.system('pause')
    #Auto_Publish().main()


