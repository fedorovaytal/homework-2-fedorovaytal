import qrcode
import urllib.request
import re
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext


def hello(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(f'Hello {update.effective_user.first_name}')


def time(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(f'{update.message.date}')


def searchInDdg(update: Update, context: CallbackContext) -> None:
    url = 'http://html.duckduckgo.com/html/?q=' + update.message.text.replace('/s ', '', 1).strip()
    html = urllib.request.urlopen(url).read()

    soup = BeautifulSoup(html, 'html.parser')

    results_a = soup.find_all('a', class_='result__a')
    results_url = soup.find_all('a', class_='result__url')

    if len(results_a) == 0:
        text = 'not found'
    else:
        count = 3
        if len(results_a) < 3:
            count = len(results_a)
        for i in range(count):
            result_a = results_a[i]
            result_url = results_url[i]
            url = result_url.text.replace('\n                  ', '')
            update.message.reply_html(f'<a href="https://{url}">{result_a.text}</a>')


def searchInYt(update: Update, context: CallbackContext) -> None:
    url = 'https://www.youtube.com/results?search_query=' + update.message.text.replace('/v ', '', 1).strip()
    html = urllib.request.urlopen(url)

    video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())

    if len(video_ids) == 0:
        text = 'not found'
    else:
        count = 3
        if len(video_ids) < 3:
            count = len(video_ids)
        for i in range(count):
            update.message.reply_text(f'www.youtube.com/watch?v={video_ids[i]}\n')


def searchInYahooImages(update: Update, context: CallbackContext) -> None:
    yahoo_link1 = 'https://images.search.yahoo.com/search/images;_ylt=AwrE1xL0fa1h.8IApg1XNyoA;_ylu' \
                  '=Y29sbwNiZjEEcG9zAzEEdnRpZANGT05UVEVTVF8xBHNlYwNwaXZz?p= '
    yahoo_link2 = '&fr2=piv-web&fr=yfp-t'
    url = yahoo_link1.strip() + update.message.text.replace('/p ', '', 1).strip() + yahoo_link2.strip()
    html = urllib.request.urlopen(url).read()

    soup = BeautifulSoup(html, 'html.parser')

    imgs = soup.find_all('img', class_='')

    if len(imgs) == 0:
        text = 'not found'
    else:
        count = 3
        if len(imgs) < 3:
            count = len(imgs)
        for i in range(count):
            img = imgs[i]
            url = img['src']
            text = f'<a href="{url}">Result #{i + 1}</a>'
            update.message.reply_html(text)


def genQR(update: Update, context: CallbackContext) -> None:
    msg = update.message.text.replace('/q ', '', 1).strip()

    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(msg)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')
    img.save('qrcode.jpg')
    qrImg = open('qrcode.jpg', 'rb')
    update.message.reply_photo(qrImg)


with open('./token.txt') as f:
    token = f.readline()

updater = Updater(token.strip())

updater.dispatcher.add_handler(CommandHandler('hello', hello))
updater.dispatcher.add_handler(CommandHandler('time', time))
updater.dispatcher.add_handler(CommandHandler('s', searchInDdg))
updater.dispatcher.add_handler(CommandHandler('v', searchInYt))
updater.dispatcher.add_handler(CommandHandler('p', searchInYahooImages))
updater.dispatcher.add_handler(CommandHandler('q', genQR))

updater.start_polling()
updater.idle()