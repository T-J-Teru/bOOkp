#!/usr/bin/env python3

import getpass
import json
import logging
import os
import re
import requests
import sys
import urllib.parse
import time

from argparse import ArgumentParser
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

user_agent = {'User-Agent': 'krumpli'}
logger = logging.getLogger(__name__)

def create_session(email, password, browser_visible=False, proxy=None):
    if not browser_visible:
        display = Display(visible=0)
        display.start()

    logger.info("Starting browser")
    options = webdriver.ChromeOptions()
    if proxy:
        options.add_argument('--proxy-server='+proxy)
    browser = webdriver.Chrome(chrome_options=options)

    logger.info("Loading www.amazon.co.uk")
    browser.get('https://www.amazon.co.uk')

    logger.info("Logging in")
    hover = browser.find_element_by_css_selector('#nav-link-accountList > div')
    ActionChains(browser).move_to_element(hover)
    button = browser.find_element_by_css_selector('#nav-flyout-ya-signin > a')
    browser.get(button.get_attribute('href'))
    browser.find_element_by_id("ap_email").clear()
    browser.find_element_by_id("ap_email").send_keys(email)
    browser.find_element_by_css_selector("#continue").click()
    browser.implicitly_wait(10)
    browser.find_element_by_id("ap_password").clear()
    browser.find_element_by_id("ap_password").send_keys(password)
    browser.find_element_by_id("signInSubmit").click()
    try:
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[contains(text(),'For your security, approve the notification sent to')]")
            )
        )
        logger.info('Triggered an SMS check, waiting here...')
        input("Press Enter to continue...")
    except TimeoutException:
        pass

    logger.info("Switching to books page")
    browser.get('https://www.amazon.co.uk/hz/mycd/myx#/home/content/booksAll')
    browser.implicitly_wait(4)

    return browser

def reconnect_session(url, session_id):
    logger.info("Reconnecting to browser")
    browser = webdriver.Remote(command_executor=url, desired_capabilities={})
    browser.close()   # this prevents the dummy browser
    browser.session_id = session_id

    return browser

def find_confirm_element(browser):
    for confirm in browser.find_elements_by_xpath("//*[starts-with(@id,'DOWNLOAD_AND_TRANSFER_ACTION_') and contains(@id,'_CONFIRM')]/span"):
        if confirm.is_displayed():
            return confirm

    raise Exception("Failed to find Confirm button")

def find_notification_close_element(browser):
    for e in browser.find_elements_by_id('notification-close'):
        if e.is_displayed():
            return e

    raise Exception("Failed to find notification close button")

def click_download(browser):
    confirm = find_confirm_element(browser)
    webdriver.ActionChains(browser).move_to_element(confirm).click().perform()
    browser.implicitly_wait(3)

    logger.info("clicking the notification close button")
    n_close = find_notification_close_element(browser)
    webdriver.ActionChains(browser).move_to_element(n_close).click().perform()
    browser.implicitly_wait(1)

    logger.info("ready to download the next book")

def find_download_element(browser):
    for span in browser.find_elements_by_xpath("//span[contains(text(),'Download & transfer via USB')]"):
        if span.is_displayed():
            return span

    raise Exception("Download & transfer element not found")

def find_device_radio_element(browser):
    for list in browser.find_elements_by_xpath("//*[contains(@id, 'download_and_transfer_list_')]"):
        if list.is_displayed():
            return list.find_element_by_xpath("li[2]/div[1]/label/input")

    return None

def download_books(browser):
    logger.info("Downloading all books on page")
    skip_count = 0
    for element in browser.find_elements_by_class_name("dropdown_title"):
        element.click()
        browser.implicitly_wait(1)

        logger.info("Finding Download & transfer button")
        btn = find_download_element(browser)
        logger.info("Clicking Download & transfer button")
        btn.click()
        browser.implicitly_wait(1)

        logger.info("Select device radio button")
        radio = find_device_radio_element(browser)
        if radio is None:
            print("!! Skipping book, no device radio button found")
            skip_count += 1
            continue
        radio.click()

        logger.info("Downloading book")
        click_download(browser)

    if skip_count > 0:
        print(f"Skipped {skip_count} books due to missing device support")

def shutdown_session(browser, browser_visible=False):
    browser.quit()
    if not browser_visible:
        display.stop();

def main():
    parser = ArgumentParser(description="Amazon e-book downloader.")
    parser.add_argument("--verbose", help="show info messages", action="store_true")
    parser.add_argument("--showbrowser", help="display browser while creating session.", action="store_true")
    parser.add_argument("--email", help="Amazon account e-mail address", required=True)
    parser.add_argument("--password", help="Amazon account password", default=None)
    parser.add_argument("--proxy", help="HTTP proxy server", default=None)
    parser.add_argument("--url", help="URL for existing browser session", default=None)
    parser.add_argument("--sessionid", help="Session ID for existing browser session", default=None)
    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.WARNING)

    formatter = logging.Formatter('[%(levelname)s]\t%(asctime)s %(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    if not args.url:
        password = args.password
        if not password:
            password = getpass.getpass("Your Amazon password: ")

        browser = create_session(args.email, password,
                                 browser_visible=args.showbrowser,
                                 proxy=args.proxy)

        url = browser.command_executor._url
        session_id = browser.session_id

        print(f"url: {url}")
        print(f"session-id: {session_id}")
    else:
        if not args.sessionid:
            print("missing --sessionid argument")
            exit(1)

        browser = reconnect_session(args.url, args.sessionid)

    download_books(browser)

if __name__ == '__main__':
    try:
    	sys.exit(main())
    except KeyboardInterrupt:
        logger.info("Exiting...")
