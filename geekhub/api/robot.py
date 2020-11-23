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
        self.headers = {"Origin": "https://geekhub.com",
                        "Host": "geekhub.com", "User-Agent": self.user_agent}
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
        'mkaduq5yv7tlse%2BGdUB5vq3Ev7V%2BJBM8dUjYy117ReOGXBp1PyGZHbLXfWUHcGjx7ENb3ONFew%2BwMZVV6%2BzRxX5hbndbiyaAx8ScPWN52Dso9mpn18AaxB%2B085981Y2w9%2FR5LI6%2BD7JB0a%2BH5b%2BiON8xyw6ndjfJkq7T0mhH1GiUVK%2FuvH99U7mIKcw%2B1Qytjv3NF4bJlowgoyfYpL9yG%2FY9JWvyBoO6LTwWTaisNpqL0iRP1DpiF7TzKYmlmYN%2B0g6nwW5EtJaSsn4YFx3xudxEJmX8%2FRr58l6%2F6Q9M6PQL3CdQEdVpKWDov%2ByILaXanif58gLsq9oMmR72IXl7mMs2K4dbijcVL%2B602oQPtaExHjPMVPgq2%2FgT9E%2BLOqg1mX%2Fe7AQQp4A9WXla%2F8RL7o3ri430H80Ut07hmrDIFoduVpUFz5W5cj%2BulIgGE3PZwR4Jqasj%2F%2F%2Bk76RtJ64pnbyUPK8f--xXynCRm9q0xv7Ngg--VeEZ%2FKzVuK8%2BwrOOOuJ%2FTQ%3D%3D')
    # print(robot.check_in())
    print(robot.get_msg())
