import os
import re
import random
import argparse
import datetime
import networkx as nx
from urllib.request import urlopen
from urllib.parse import unquote
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup


class AdolfPathfinder:
    def __init__(self, training=False):
        random.seed(datetime.datetime.now())
        self.ADOLF_ARTICLE_URL = 'https://ru.wikipedia.org/wiki/%D0%93%D0%B8%D1%82%D0%BB%D0%B5%D1%80,_%D0%90%D0%B4%D0%BE%D0%BB%D1%8C%D1%84'
        self.training = training
        self.map_file = 'map.yaml'
        if os.path.exists(self.map_file):
            self.map = nx.read_yaml(self.map_file)
        else:
            self.map = nx.DiGraph()
        self.print_map()

    def print_map(self):
        print(self.map)

    def path_to_adolf(self, url, pr=False):
        # TODO:
        #   1. optimize code
        #   2. optimize training (now there adds only 1 article, however we can add all)
        path = []
        adolf = False
        path.append(url)
        self.map.add_node(url)
        if pr:
            print(unquote(str(url)))
        if self.training:
            while not adolf:
                # -1. store current url as previous
                prev_url = url
                # 0. making list of links, removing links met already
                links = Utils.get_wiki_hrefs(url)
                for l in links:
                    if Utils.full_wiki_href(l) in path:
                        links.remove(l)
                # 1. check if we have direct link to adolf
                for l in links:
                    if Utils.full_wiki_href(l) == self.ADOLF_ARTICLE_URL:
                        url = l
                        adolf = True
                # 2. if adolf still not met, then get random article
                if not adolf:
                    url = links[random.randint(0, len(links) - 1)] if len(links) > 1 else links[0]
                url = Utils.full_wiki_href(url)
                # 3. add current url to path and to graph
                path.append(url)
                self.map.add_node(url)
                self.map.add_edge(prev_url, url)
                if pr:
                    print(unquote(url))
            # update graph
            nx.write_yaml(self.map, self.map_file)
        else:
            while not adolf:
                # if we found url on map
                try:
                    # asking nx to build shortest path to target
                    self.map[url]
                    path.extend(nx.algorithms.shortest_paths.generic.shortest_path(self.map, source=url, target=self.ADOLF_ARTICLE_URL)[1:])
                    break
                # if no article found on map
                except (KeyError, nx.exception.NetworkXNoPath):
                    # using same algorithm as training mode
                    # -1. store current url as previous
                    prev_url = url
                    # 0. making list of links, removing links met already
                    links = Utils.get_wiki_hrefs(url)
                    for l in links:
                        if Utils.full_wiki_href(l) in path:
                            links.remove(l)
                    # 1. check if we have direct link to adolf
                    for l in links:
                        if Utils.full_wiki_href(l) == self.ADOLF_ARTICLE_URL:
                            url = l
                            adolf = True
                    # 2. if adolf still not met, then get random article
                    if not adolf:
                        url = links[random.randint(0, len(links) - 1)] if len(links) > 1 else links[0]
                    url = Utils.full_wiki_href(url)
                    # 3. add current url to path and to graph
                    path.append(url)
                    self.map.add_node(url)
                    self.map.add_edge(prev_url, url)
                    if pr:
                        print(unquote(url))
        return path


class Utils:
    @staticmethod
    def get_wiki_hrefs(url):
        # 1. make sure url is absolute
        url = Utils.full_wiki_href(url)
        # 2. get all links from article
        href_list = []
        try:
            html = urlopen(url)
        except HTTPError:
            print('Seems like 404')
            return None
        except URLError:
            print('Wrong URL')
            return None
        else:
            bsObj = BeautifulSoup(html.read(), features='html.parser')
            for link in bsObj.find('div', {'id': 'bodyContent'}).findAll('a', href=re.compile('^(/wiki/)((?!:).)*$')):
                if 'href' in link.attrs:
                    href_list.append(link.attrs['href'])
            return href_list

    @staticmethod
    def full_wiki_href(url):
        url = str(url)
        if not re.search('.*ru\.wikipedia\.org.*', url):
            url = 'https://ru.wikipedia.org' + url
        return url


ap = argparse.ArgumentParser(description='Searching path to Adolf Hitler page')
ap.add_argument('url', type=str, help='starting URL')
ap.add_argument('--training', dest='training', action='store_true', default=False, help='training mode')
args = ap.parse_args()

pathfinder = AdolfPathfinder(training=args.training)
path = pathfinder.path_to_adolf(args.url, pr=True)
for i, node in enumerate(path):
    print('{i}. {n}'.format(i=i, n=unquote(node)))
print('Done')
