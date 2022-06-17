# bOOkp

## Background

Originally forked from: https://github.com/moyix/bOOkp/fork

The original script tried to download the books directly.  But by the
time I started looking at the script this wasn't working any more.

So, I hacked up the script to scrape the Amazon website and download
the books as a user would, this worked fine at the time I initially
wrote this script, but it probably going to break as the site changes
over time.

## Original Description

Quick'n'dirty script to download all you Kindle ebooks.

I needed to backup all my Kindle e-books, so put together this script. It does
work for now, but a change in the download process will probably break it, and I
may not have the time to fix it right away.

You can download all your e-books (that are eligible for download), or you can
specify multiple ASINs to download. By default the script will only display
warnings, errors, and a finish message. If you want to see progress, you have to
use the `--verbose` flag. Selenium with ChromeDriver is used to handle login,
and you can display the browser with `--showbrowser` - this may come handy if
something goes wrong.

The only mandatory command line parameter is the e-mail address associated with
your Amazon account, but of course the script will need your password too - it
will ask for it if not given as parameter. Keep in mind that passwords given as
parameters will probably be stored in you history!

The script will also ask which of your devices you want to download your books
to. This is important, because the downloaded books will be DRMd to that
particular device. The serial number (which is required to remove DRM) will be
printed when the books are downloaded.

### Usage

```
usage: bookp.py [-h] [--verbose] [--showbrowser] --email EMAIL
                [--password PASSWORD] [--outputdir OUTPUTDIR] [--proxy PROXY]
                [--asin [ASIN [ASIN ...]]]

Amazon e-book downloader.

optional arguments:
  -h, --help            show this help message and exit
  --verbose             show info messages
  --showbrowser         display browser while creating session.
  --email EMAIL         Amazon account e-mail address
  --password PASSWORD   Amazon account password
  --outputdir OUTPUTDIR
                        download directory (default: books)
  --proxy PROXY         HTTP proxy server
  --asin [ASIN [ASIN ...]]
                        list of ASINs to download
```

## New Description

The script is now works in a multi-stage process.  First usage will be
something like this:

  `bookp.py --email=EMAIL --showbrowser --verbose`

This will start up a browser window, sign in to your Amazon account,
and switch to the books page.

Then the script will start downloading all the books on the first page.

Once the first page is complete the script will exit.

At this point you should manually select the second page of books, and rerun the script like this:

  `bookp.py --email=EMAIL --url=URL --sessionid=ID --showbrowser --verbose`

The URL and ID will hav been printed the first time the script ran.
This second invocation of the script will reconnect to the existing
browser session and download all the books on the second page.

After which the script exits again.

Select the third page of books, and repeat, etc.

## NOTES

The function `find_device_radio_element` is written to suite my needs.
I have two devices, and I want to download the books for the second
device.

You will likely need to update this function to suite the number of
devices that you have.

## Requirements

* [Python 3.x](https://www.python.org)
* [ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver/downloads)
* the following Python modules:
  * [requests](https://pypi.org/project/requests/)
  * [PyVirtualDisplay](https://pypi.org/project/PyVirtualDisplay/)
  * [selenium](https://pypi.org/project/selenium/)
