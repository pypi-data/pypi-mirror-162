import smtplib
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
import poplib
from email.parser import Parser
from email.header import decode_header
from email.utils import parseaddr
from email.header import Header
import smtplib
import time
import os

class MyEmailTool:
    '''
    发送和收取邮件
    '''
    def __init__(self,numOfSms=1):
        self.numOfsms=numOfSms

    def log(self,contents):
        cur_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print(f'{cur_time} {contents}')
        return f'{cur_time} {contents}'

    def send_mail(self, from_addr, password, to_addrs, title, content, pathList=[]):
        '''
        from_addr = '20182*****@mail.scut.edu.cn' # 打个码，这里输入你自己的邮箱就行
        password = 'scut_827*****' # 输入你的密码（如果是qq或者网易邮箱，这里要输入授权码）
        to_addrs = ['lly****@163.com', '12375947@qq.com'] # 这里就写需要发送的邮箱
        title = '这是一封测试邮件' # 邮件标题
        content = '随便写点东西' # 正文内容
        path:如果需要发送附件，这里填写附件的路径
        '''
        smtp_server = 'smtp.' + from_addr.split('@')[-1]  # 发信服务器
        msg = MIMEMultipart()  # 创建一封空邮件
        msg['From'] = Header(from_addr)  # 添加邮件头信息
        msg['Subject'] = Header(title)  # 添加邮件标题
        msg.attach(MIMEText(content, 'plain', 'utf-8'))  # 正文内容
        if pathList:
            for filePath in pathList:

                # 添加附件
                part = MIMEBase('application', "octet-stream")
                part.set_payload(open(filePath, "rb").read())  # 读取附件
                encoders.encode_base64(part)
                filename=os.path.split(filePath)[-1]
                part.add_header('Content-Disposition', 'attachment',filename=filename)
                msg.attach(part)  # 把附件添加到邮件中



        server = smtplib.SMTP_SSL(smtp_server)  # 开启发信服务，这里使用的是加密传输
        server.connect(smtp_server, 465)  # 登录发信邮箱
        for to_addr in to_addrs:  # 遍历发送给每个账号
            msg['To'] = Header(to_addr)
            server.login(from_addr, password)  # 发送邮件
            server.sendmail(from_addr, to_addr, msg.as_string())
        server.quit()  # 关闭服务器
        self.log('邮件发送成功')

    def receive_mail(self, email, password, path):
        '''
        email:邮箱地址
        password:密码（如果是qq邮箱或者网易邮箱,这里填授权码）
        path:附件保留的位置
        '''

        def decode_str(s): # 解析消息头中的字符串，没有这个函数，print出来是乱码。如'=?gb18030?B?yrXWpL3hufsueGxz?='这种
            value, charset = decode_header(s)[0]
            return value.decode(charset) if charset else value

        # 解码邮件信息分为两个步骤，第一个是取出头部信息:首先取头部信息,主要取出['From','To','Subject']
        def get_header(msg):
            mailFrom=mailTo=emSubject=None
            for header in ('From', 'To', 'Subject'):
                value = msg.get(header, '')
                if value:
                    if header == 'Subject':  # 文章的标题有专门的处理方法
                        emSubject = decode_str(value)
                    else:
                        addr = parseaddr(value)[-1]  # 地址也有专门的处理方法
                        value = decode_str(addr)
                        if header == 'From':
                            mailFrom = value
                        else:
                            mailTo = value
            print(f'From    {mailFrom}\nTo      {mailTo}\nSubject {emSubject}')

        # 邮件正文部分：取附件，邮件的正文部分在生成器中，msg.walk()，如果存在附件，则可以通过.get_filename()的方式获取文件名称
        def get_file(path, msg):
            for part in msg.walk():
                file_name = part.get_filename()
                if file_name:  # 如果存在附件
                    file_name = decode_str(file_name)
                    file_name=os.path.split(file_name)[-1] # 加上这句,因为通过模块发的附件的名称是有原来附件的全文件路径的,通过这段话获取文件名
                    data = part.get_payload(decode=True)  # 取出文件正文内容
                    with open(path + file_name, 'wb') as f:
                        f.write(data)

        # 头部信息已取出,获取邮件的字符编码，首先在message中寻找编码，如果没有，就在header的Content-Type中寻找
        def guess_charset(msg):
            charset = msg.get_charset()
            if charset is None:
                content_type = msg.get('Content-Type', '').lower()
                pos = content_type.find('charset=')
                if pos >= 0:
                    charset = content_type[pos + 8:].strip()
            return charset

        def get_content(msg):
            for part in msg.walk():
                if part.get_filename():  # 如果有附件，则直接跳过
                    continue
                content_type = part.get_content_type()
                charset = guess_charset(part)
                email_content_type,content = '',''
                if content_type == 'text/plain':
                    email_content_type = 'text'
                elif content_type == 'text/html':
                    email_content_type = 'html'
                    # print('html 格式 跳过')
                    # continue #不要html格式的邮件
                if charset:
                    try:
                        content = part.get_payload(decode=True).decode(charset)
                    except AttributeError:
                        print('type error')
                    except LookupError:
                        print("unknown encoding: utf-8")
                if email_content_type == '':
                    continue  # 如果内容为空，也跳过
                if email_content_type == 'html':
                    content = part.get_payload(decode=True).decode(charset)

                print('内容是',content)


        for i in range(self.numOfsms):
            self.log(f'开始第【{i+1}】封邮件的收取'+'-'*100)
            server = poplib.POP3_SSL('pop.' + email.split('@')[-1])  # 修改对应的邮箱服务器
            server.user(email)
            server.pass_(password)
            resp, mails, octets = server.list()  # 登录的过程 # list()返回所有邮件的编号:
            index = len(mails)  # 邮件的总数
            resp, lines, octets = server.retr(index - (self.numOfsms-1-i))  # 读取最近一封邮件,如有多封邮件,由距离现在时间最远的开始读
            # resp, lines, octets = server.retr(index -i)  # 读取最近一封邮件
            msg_content = b'\r\n'.join(lines).decode('utf-8', 'ignore')
            msg = Parser().parsestr(msg_content)
            # server.dele(index) #删除邮件
            get_header(msg)  # 显示邮件信息，包括发件人，收件人，标题
            get_file(path, msg)  # 保留附件d
            get_content(msg)  # 显示文件内容
            server.quit()
            self.log(f'完成第【{i+1}】封邮件的收取'+'-'*100+'\n')


if __name__ == '__main__':

    em = MyEmailTool(3)
    # 发送邮件的部分
    from_addr = 'XXXXXXXXX@qq.com'  # 发件人邮箱
    password = 'XXXXXXXXXX'  # 邮箱密码（如果是qq或者网易邮箱，这里要填授权码）
    to_addrs = ['XXXXXXXXX@qq.com', 'YYYYYYYYYY@qq.com']  # 需要发送的邮箱
    title = 'test标题'  # 邮件标题
    content = 'test内容'  # 正文内容
    pathList = [r'C:\Users\Administrator\Desktop\油猴子.txt',r'C:\Users\Administrator\Desktop\类.py']  # 如果要发送带附件的邮件，这里填附件路径
    em.send_mail(from_addr, password,to_addrs, title, content, pathList)

    # 获取邮件的部分
    email='XXXXXXXXXXX@139.com' # 邮箱地址
    password='XXXXXXXXXXX' # 邮箱密码（如果是qq邮箱或者网易邮箱,这里填授权码）

    path=r'D:/DATA/Desktop/getAC/' # 附件保留的位置
    # em.receive_mail(email, password,path)






