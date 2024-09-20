'''
SMTP协议即简单邮件传输协议，允许用户按照标准发送/接收邮件。

在本文中，SMTP邮件客户端程序的基本流程如下：

1. 与163邮件服务器建立TCP连接，域名"smtp.126.com"，SMTP默认端口号25。建立连接后服务器将返回状态码220，代表服务就绪（类似HTTP，SMTP也使用状态码通知客户端状态信息）。
2. 发送"HELO"命令，开始与服务器的交互，服务器将返回状态码250（请求动作正确完成）。
3. 发送"AUTH LOGIN"命令，开始验证身份，服务器将返回状态码334（服务器等待用户输入验证信息）。
4. 发送**经过base64编码**的用户名（本例中是163邮箱的账号），服务器将返回状态码334（服务器等待用户输入验证信息）。
5. 发送**经过base64编码**的密码（本例中是163邮箱的密码），服务器将返回状态码235（用户验证成功）。
6. 发送"MAIL FROM"命令，并包含发件人邮箱地址，服务器将返回状态码250（请求动作正确完成）。
7. 发送"RCPT TO"命令，并包含收件人邮箱地址，服务器将返回状态码250（请求动作正确完成）。
8. 发送"DATA"命令，表示即将发送邮件内容，服务器将返回状态码354（开始邮件输入，以"."结束）。
9. 发送邮件内容，服务器将返回状态码250（请求动作正确完成）。
10. 发送"QUIT"命令，断开与邮件服务器的连接。
'''


#   使用封装好的smtp

import smtplib
from email.mime.text import MIMEText

mail_host = 'smtp.163.com'
mail_port = 465
mail_user = "wjj1796928652"
mail_pass = "DAMSOHUENVBCLNSV"
sender = "wjj1796928652@163.com"
receivers = ["3164351692@qq.com"]

content = '天天开心哦 哈哈哈'
title = 'happy everyday'


def sendmail():
    msg = MIMEText(content, 'plain', 'utf-8')
    msg['From'] = "{}".format(sender)
    msg['To'] = ",".join(receivers)
    msg['Subject'] = title

    try:
        smtpObj = smtplib.SMTP_SSL(mail_host, mail_port)
        smtpObj.login(mail_user, mail_pass)
        smtpObj.sendmail(sender, receivers, msg.as_string())
        print("mail has been send successfully.")
    except smtplib.SMTPException as e:
        print(e)












#   套接字版本
#   但是用户验证会出现问题？ 相信后人的智慧
'''
from socket import *

#   Mail content
subject = "I love computer networks!"
contenttype = "text/plain"
msg = "Hahaha"
endmsg = "\r\n.\r\n"

#   Choose a mail server () and call it mailserver
mailserver = "smtp.163.com"

#   Sender and receiver
fromaddress = "wjj1796928652@163.com"
toaddress = "1796928652@qq.com"

#   Author information(Encode with based 64)
username = "wjj1796928652"
password = "DAMSOHUENVBCLNSV"   #"WOPHTRORFBLSYNRO"   #   "1234567890Wjj."

# Create socket called clientSocket and establish a TCP connection with mailserver
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((mailserver, 25))

recv = clientSocket.recv(1024).decode()
print(recv)
if recv[:3] != '220':
    print('220 reply not received from server.')

# Send HELO command and print server response.
heloCommand = 'HELO Alice\r\n'
clientSocket.send(heloCommand.encode())
recv1 = clientSocket.recv(1024).decode()
print(recv1)
if recv1[:3] != '250':
    print('250 reply not received from server.')

# Auth
clientSocket.sendall('AUTH LOGIN\r\n'.encode())
recv = clientSocket.recv(1024).decode()
print(recv)
if recv[:3] != '334':
    print('334 reply not received from server')

clientSocket.sendall((username + '\r\n').encode())
recv = clientSocket.recv(1024).decode()
print(recv)
if recv[:3] != '334':
    print('334 reply not received from server')

clientSocket.sendall((password + '\r\n').encode())
recv = clientSocket.recv(1024).decode()
print(recv)
if recv[:3] != '235':
    print('235 reply not received from server')

# Send MAIL FROM command and print server response.
clientSocket.sendall(('MAIL FROM: <' + fromaddress + '>\r\n').encode())
recv = clientSocket.recv(1024).decode()
print(recv)
if recv[:3] != '250':
    print('250 reply not received from server')

# Send RCPT TO command and print server response.
clientSocket.sendall(('RCPT TO: <' + toaddress + '>\r\n').encode())
recv = clientSocket.recv(1024).decode()
print(recv)
if recv[:3] != '250':
    print('250 reply not received from server')

# Send DATA command and print server response.
clientSocket.send('DATA\r\n'.encode())
recv = clientSocket.recv(1024).decode()
print(recv)
if recv[:3] != '354':
    print('354 reply not received from server')

# Send message data.
message = 'from:' + fromaddress + '\r\n'
message += 'to:' + toaddress + '\r\n'
message += 'subject:' + subject + '\r\n'
message += 'Content-Type:' + contenttype + '\t\n'
message += '\r\n' + msg
clientSocket.sendall(message.encode())

# Message ends with a single period.
clientSocket.sendall(endmsg.encode())
recv = clientSocket.recv(1024).decode()
print(recv)
if recv[:3] != '250':
    print('250 reply not received from server')

# Send QUIT command and get server response.
clientSocket.sendall('QUIT\r\n'.encode())

# Close connection
clientSocket.close()

'''