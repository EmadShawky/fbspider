#!/usr/bin/env python
# -*- coding: utf-8 -*-
# FBSpider (https://www.github.com/R3nt0n/fbspider)
# R3nt0n (https://www.github.com/R3nt0n)
#
# Tested with:
# - Firefox 46.0
# - Selenium 2.53.0

import time
import sys

import requests
from bs4 import BeautifulSoup
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from lib.color import color


class FacebookSpider:
    def __init__(self, target, firefox_path):
        self.target = target

        # Setting up a virtual display to hide Firefox window
        self.display = Display(visible=0, size=(800, 600))
        self.display.start()

        self.driver = webdriver.Firefox(executable_path=firefox_path)
        self.driver.delete_all_cookies()
        self.db = {}

    def login(self, user, pswd):
        self.driver.get("https://www.facebook.com/login")
        assert "Facebook" in self.driver.title
        elem = self.driver.find_element_by_id("email")
        elem.send_keys(user)
        elem = self.driver.find_element_by_id("pass")
        elem.send_keys(pswd)
        elem.send_keys(Keys.RETURN)
        time.sleep(3)
        if (u"The password you’ve entered is incorrect.".encode('utf8') in (self.driver.page_source).encode('utf8')) \
                or (u"Sorry, something went wrong.".encode('utf8') in (self.driver.page_source).encode('utf8')):
            print("\n{}[!]{} Error while trying to authenticate".format(color.RED,color.END))
            self.close()
            return False
        else:
            return True

    def scroll_to_end(self, mult_time=1):
        delay = 3 * mult_time
        # Get scroll height
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            # Scroll down to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # Wait to load page
            time.sleep(delay)
            # Calculate new scroll height and compare with last scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height: break
            last_height = new_height

    def wait_until_load(self, elem_id, mult_time=1):
        timeout = 10 * mult_time
        element_present = EC.presence_of_element_located((By.ID, elem_id))
        try:
            WebDriverWait(self.driver, timeout).until(element_present)
        except TimeoutException:
            print "{}[!]{} Error while loading {} element".format(color.RED,color.END,elem_id)

    def print_info(self, report, n_tabs=0):
        tab = "\t"
        for k, v in report.iteritems():
            if n_tabs == 0:
                line_break = "\n"
            else:
                line_break = ""
            print "{}{}[*] {}".format(line_break, tab * n_tabs, k.upper())
            if isinstance(v, dict):
                self.print_info(v, n_tabs + 1)
            elif isinstance(v, list):
                for i in v:
                    print "{}[+] {}".format(tab * (n_tabs + 1), i)
            else:
                print "{}[+] {}".format(tab * (n_tabs + 1), v)

    def report_as_html(self, report):
        body = ''
        for k, v in report.iteritems():
            class_name = (k.lower()).replace(' ', '_')
            body += '<dl id="{}"><dt>{}</dt>'.format(class_name, k.upper())
            if isinstance(v, dict):
                body += self.report_as_html(v)
            elif isinstance(v, list):
                body += '<dd><ul>'
                for i in v:
                    body += '<li>{}</li>'.format(i)
                body += '</ul></dd>'
            else:
                body += '<dd>{}</dd>'.format(v)
            body += '</dl>'

        css_filename = 'styles.css'
        head = '<head><meta charset="UTF-8"><link rel="stylesheet" type="text/css" href="' + css_filename + '"></head>'
        body = '<body><div id="report">' + body + '</div></body>'
        html = '<html>' + head + body + '</html>'

        return html

    def get_info(self, info_type, timeout=1):
        base_url = "https://www.facebook.com/" + self.target + "/"
        query = False
        results = {}
        hobbies_info = ("music", "movies", "books", "sports")

        if info_type == "name":
            # REQUESTS
            request = requests.get("https://m.facebook.com/" + self.target + "/")
            html = request.text
            elem_id = "cover-name-root"
            html_proc = BeautifulSoup(html, "lxml")
            elem = html_proc.find(id=elem_id)
            elem_proc = BeautifulSoup(str(elem), "lxml")
            results[info_type] = elem_proc.text
            # SELENIUM
            # self.driver.get(base_url)
            # elem_id = "fb-timeline-cover-name"
            # self.wait_until_load(elem_id)
            # name = (self.driver.find_element_by_id(elem_id)).text
            # results[info_type] = (name).encode('utf8')

        elif info_type in hobbies_info:
            self.driver.get(base_url + info_type)
            self.scroll_to_end(timeout)

            elem_id = "pagelet_timeline_medley_" + info_type
            self.wait_until_load(elem_id, timeout)
            elems = self.driver.find_element_by_id(elem_id)
            elems = elems.find_elements_by_class_name("_gx7")
            info_list = []
            for elem in elems:
                elem = (elem.get_attribute("title")).encode('utf8')
                info_list.append(elem)
            results[info_type] = info_list

        elif info_type == "life_events":
            self.driver.get(base_url + "about?section=year-overviews")
            elem_id = "u_0_24"
            self.wait_until_load(elem_id, timeout)
            elems = self.driver.find_element_by_id(elem_id)

            elems = elems.find_elements_by_class_name("_2pi4")  # One li for each year containing events
            events_dict = {}
            for li in elems:
                events_list = []
                year = (li.find_element_by_class_name("_2iem")).text
                events = li.find_elements_by_tag_name("li")
                for event in events:
                    event = ((event.text).encode('utf8')).replace("\n", "; ")
                    if len(event) > 0: events_list.append(event)
                events_dict[year] = events_list

            results[info_type] = events_dict

        elif info_type == "basic":     query = "about?section=contact-info"; card_name = "pagelet_basic"
        elif info_type == "contact":   query = "about?section=contact-info"; card_name = "pagelet_contact"
        elif info_type == "edu_work":  query = "about?section=education";    card_name = "pagelet_eduwork"
        elif info_type == "places":    query = "about?section=living";       card_name = "pagelet_hometown"
        elif info_type == "relations": query = "about?section=relationship"; card_name = "pagelet_relationships"
        elif info_type == "bio":       query = "about?section=bio";          card_name = "pagelet_bio"
        elif info_type == "quotes":    query = "about?section=bio";          card_name = "pagelet_quotes"
        elif info_type == "pronounce": query = "about?section=bio";          card_name = "pagelet_pronounce"
        elif info_type == "nicknames": query = "about?section=bio";          card_name = "pagelet_nicknames"

        if query:
            self.driver.get(base_url + query)
            elem_id = card_name
            self.wait_until_load(elem_id, timeout)
            base_div = self.driver.find_element_by_id(elem_id)
            categories = base_div.find_elements_by_class_name("_4qm1")
            cat_dict = {}

            for cat in categories:
                title_cat = ((cat.find_element_by_class_name("_h71")).text).lower()
                items_list = []
                base_elems = cat.find_elements_by_class_name("fbProfileEditExperiences")
                for elems in base_elems:
                    elems = elems.find_elements_by_tag_name("li")
                    for elem in elems:
                        if info_type == "quotes":
                            quotes = ((elem.text).encode('utf8')).split("\n\n")
                            for e in quotes:
                                if len(quotes) > 0: items_list.append(e.replace("\n", " "))
                        else:
                            elem = ((elem.text).encode('utf8')).replace("\n", ": ")
                            if len(elem) > 0: items_list.append(elem)
                cat_dict[title_cat] = items_list

            results = cat_dict

        self.db.update(results)
        return results

    def close(self):
        self.driver.close()
        self.display.stop()


################################################################################
# USAGE EXAMPLE
################################################################################
if __name__ == "__main__":
    USER = "example.user@gmail.com"
    PSWD = "123456seven"
    TARGET = "zuck"
    FIREFOX_PATH = '/home/my/folder/to/firefox_46/firefox'

    fb = FacebookSpider(TARGET, FIREFOX_PATH)
    try:
        fb.login(USER, PSWD)

        name = fb.get_info("name")            # Returns a dict
        basic = fb.get_info("basic")          # Returns a dict
        music = fb.get_info("music")          # Returns a list

        print "\n[*] {}: {}".format(name, name["name"])

        for categ in basic:
            print '\n[*] {} [{}]'.format(categ, len(basic[categ]))
            for info in basic[categ]:
                print '\t [+] ' + info

        print "\n[*] MUSIC [{}]".format(len(music))
        for info in music: print '\t[+] ' + info

    finally:
        try: fb.close()
        except AttributeError: pass
