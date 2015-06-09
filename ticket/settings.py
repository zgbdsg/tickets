# -*- coding: utf-8 -*-

# Scrapy settings for ticket project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'ticket'

SPIDER_MODULES = ['ticket.spiders']
NEWSPIDER_MODULE = 'ticket.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'ticket (+http://www.yourdomain.com)'

AUTOTHROTTLE_ENABLED = True
COOKIES_ENABLED = False
CONCURRENT_REQUESTS = 100
LOG_LEVEL = 'INFO'
RETRY_ENABLED = False
DOWNLOAD_TIMEOUT = 5
REDIRECT_ENABLED = False