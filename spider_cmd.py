#!/usr/bin/env python
# -*- coding: utf-8 -*-
# FBSpider (https://www.github.com/R3nt0n/fbspider)
# R3nt0n (https://www.github.com/R3nt0n)

import ConfigParser
import argparse

from lib.spider import FacebookSpider
from lib.color import color


CFG_FILE = 'spider_cmd.cfg'  # Configuration file


# READING AUTH PARAMETERS FROM CONFIG FILE
###############################################################################
def read_conf():
    cfg = ConfigParser.ConfigParser()
    cfg.read([CFG_FILE])
    FIREFOX_PATH = cfg.get('PATH', 'firefox')
    USER = cfg.get('AUTH', 'user')
    PSWD = cfg.get('AUTH', 'pswd')
    return FIREFOX_PATH, USER, PSWD


# READING TARGET FROM ARGS
###############################################################################
def read_args():
    parser = argparse.ArgumentParser(description='Generate reports from Facebok profiles.')
    parser.add_argument('-t', '--target', action='store', metavar='', type=str, dest='target', required=True,
                        help='Specifies the profile\'s name of the target.')
    parser.add_argument('--html', action='store', metavar='', type=str, dest='extract_html', required=False,
                        help='Extract the data in html')
    args = parser.parse_args()
    return args.target, args.extract_html

# USAGE EXAMPLE
def main():
    FIREFOX_PATH, USER, PSWD = read_conf()
    TARGET, extract_html = read_args()

    fb = FacebookSpider(TARGET, FIREFOX_PATH)
    try:
        fb.login(USER, PSWD)

        report = {}
        report.update(fb.get_info("name"))
        # report.update(fb.get_info("basic"))
        # report.update(fb.get_info("contact"))
        # report.update(fb.get_info("relations"))
        # report.update(fb.get_info("bio"))
        # report.update(fb.get_info("quotes"))
        # report.update(fb.get_info("places"))
        # report.update(fb.get_info("edu_work"))
        # report.update(fb.get_info("life_events"))
        # report.update(fb.get_info("music"))
        # report.update(fb.get_info("movies"))
        # report.update(fb.get_info("books", 2))

        if extract_html:
            html = fb.report_as_html(report)
            with open('report.html', 'wb') as f:
                f.write(html)

        else:
            fb.print_info(report, 0)

    finally:
        try: fb.close()
        except AttributeError: pass


if __name__ == "__main__":
    import time
    start_time = time.time()

    main()

    elapsed_time = time.time() - start_time
    print '\n{}[*]{} Time elapsed: {}{}{}'.format(color.GREEN, color.END, color.BLUE, time.strftime("%H:%M:%S", time.gmtime(elapsed_time)), color.END)
