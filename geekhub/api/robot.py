import requests
from geekhub.common import user_agent_random
import copy
from bs4 import BeautifulSoup
from collections import namedtuple
import re
from pathlib import Path

Article = namedtuple('Article', ['id', 'is_new'])


class Robot:
    def __init__(self, cookies):
        self.user_agent = user_agent_random()
        self.session = requests.Session()
        requests.utils.add_dict_to_cookiejar(
            self.session.cookies, {"_session_id": cookies})
        self.domain = 'https://geekhub.com'
        self.comment_url = 'https://geekhub.com/comments'
        self.headers = {"Host": "www.geekhub.com", "User-Agent": self.user_agent}
        self.check_in_url = 'https://geekhub.com/checkins/start'
        self.molecules_list = self.load_molecules()

    def get_authenticity_token(self, url):
        headers = copy.deepcopy(self.headers)
        headers['Refer'] = url
        resp = self.session.get(url, headers=headers)

        soup = BeautifulSoup(resp.content, 'html.parser')

        if resp.text.find("今日已签到") != -1:
            return self.check_if_check_in_success(resp.content)
        meta = soup.find("meta", attrs={"name": "csrf-token"})
        return meta['content']

    def check_in(self):
        """
            post https://geekhub.com/checkins/start 302
            get https://geekhub.com/checkins
        """
        headers = copy.deepcopy(self.headers)
        headers['Refer'] = self.check_in_url
        payload = {'_method': "POST"}
        authenticity_token = self.get_authenticity_token(
            'https://geekhub.com/checkins')
        if isinstance(authenticity_token, int):
            return authenticity_token
        payload['authenticity_token'] = authenticity_token
        resp = self.session.post(
            self.check_in_url, headers=headers, data=payload)
        if resp.status_code == 200:
            return self.check_if_check_in_success(resp.content)
        return False

    def check_if_check_in_success(self, resp):
        try:
            soup = BeautifulSoup(resp, 'html.parser')
            div_list = soup.find_all(class_='w-3/12')
            g_bit = div_list[1].find('div').string
            return int(g_bit)
        except:
            return False

    def get_user_info(self):
        headers = copy.deepcopy(self.headers)
        headers['Refer'] = 'https://geekhub.com/checkins'
        resp = self.session.get('https://geekhub.com/checkins', headers=headers)
        if resp.status_code != 200:
            return None
        user_name_groups = re.search(r'<a href="/u/(.+)">', resp.text)
        if user_name_groups:
            return user_name_groups.group(1)
        return None

    def get_msg(self):
        headers = copy.deepcopy(self.headers)
        headers['Refer'] = 'https://geekhub.com/molecules'
        resp = self.session.get('https://geekhub.com/molecules', headers=headers)
        if resp.status_code != 200:
            return None
        soup = BeautifulSoup(resp.content, 'html.parser')
        msg_a = soup.find('a', href='/activities')
        if msg_a:
            has_new_molecules = self.get_molecules(soup)
            return msg_a.text.strip(), has_new_molecules
        return None, None

    def get_molecules(self, soup):
        feed_list = self._feed_list_mode(soup)
        media_list = self._media_list_mode(soup)
        new_molecules_id_list = feed_list if len(media_list) == 0 else media_list
        self.save_molecules(new_molecules_id_list)
        return len(new_molecules_id_list)

    def _feed_list_mode(self, soup):
        """
        列表模式
        :param soup:
        :return:
        """
        new_molecules_id_list = []
        article_list = soup.find_all('feed')
        for article in article_list:
            if article.select('div:nth-child(2) > div:nth-child(1)>div:nth-child(2) > div:nth-child(2)'):
                div = article.select('div:nth-child(2) > div:nth-child(1)>div:nth-child(2) > div:nth-child(2)')[0]
                end = div.text.strip()
                is_new = False if end == "已结束" else True
                if is_new:
                    a = article.select('div:nth-child(2) > div:nth-child(2) > a')[0]
                    id = a['href'].split("/")[-1]
                    if id not in self.molecules_list:
                        new_molecules_id_list.append(id)

        return new_molecules_id_list

    def _media_list_mode(self, soup):
        """
        图片模式
        :param soup:
        :return:
        """
        new_molecules_id_list = []
        article_list = soup.find_all('article')
        for article in article_list:
            span_list = article.select('div:nth-child(3) > span:nth-child(1)')
            if span_list:
                end = span_list[0].text.strip()
                is_new = False if end == "已结束" else True
                if is_new:
                    a = article.find("h3").find("a")
                    id = a['href'].split("/")[-1]
                    if id not in self.molecules_list:
                        new_molecules_id_list.append(id)

        return new_molecules_id_list

    def load_molecules(self):
        if not Path('molecules.txt').exists():
            return []
        with open('molecules.txt', 'r', encoding='utf-8') as f:
            molecules = "".join(f.readlines())
            return molecules.strip().split(",")

    def save_molecules(self, molecules_list):
        self.molecules_list += molecules_list
        if self.molecules_list:
            with open('molecules.txt', 'w', encoding='utf-8') as f:
                f.write(",".join(self.molecules_list))


if __name__ == '__main__':
    robot = Robot(
        'jghjutCIQ%2BVjsnvnN1TsXBAQCVAAGZ8vkZU7QDf50wKUMkAiBV9hJWaA67l%2FrLsBUoQOPh5R1IpzLOrhZI2faIum%2Ba6ZmF%2FiKajdU2fxROfZ7UoRT9Dyoj9OzZfxHbsLhZh189MKc8gSQ9h78puruHnvPOVmWItfo5Bw%2B2Xuljxjeu39Ur1tSRaUdEarZJjCe%2BCf3uc4YSPZ8IZlp%2FUpNrOnBULM7LL8pjshpYunVnQ%2FZyM%2FvkuAYr1RTPGbzr6aXEe%2FhaxGa1PVrAQHMqObOR21lMn94v4SzMvg4LPt1Ku9Hl0%2BxpzDH0LnSY%2FjZg8bC5kMu1%2BvYQV2aH%2BjdxeJ3iTc08VsA0X0WwUPmeZRxc47yMXlvR4k0alyXI3Im75U1JurUCze%2F%2BCMzXug1lSbsyoDqbmSjztlnD4OhfcfM%2FKuA2fsC5dk1A242h0RRtb57hYlWXc%2Fh7FFnS1yApkP%2FS6ZaxxEMnaNyJuwzcpDuSmY--wMaDRw5y88obIX%2BL--%2FnTiLRJ5lr%2FHgDGqWGq0SQ%3D%3D')
    # print(robot.check_in())
    print(robot.check_in())
