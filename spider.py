import os
import requests
import aiohttp, asyncio
from pyquery import PyQuery as pq


class Model():
    """
    基类, 用来显示类的信息
    """
    def __repr__(self):
        name = self.__class__.__name__
        properties = ('{}=({})'.format(k, v) for k, v in self.__dict__.items())
        s = '\n<{} \n  {}>'.format(name, '\n  '.join(properties))
        return s


class Comic(Model):
    def __init__(self):
        self.name = ''
        self.srcUrl = ''

def cached_url(url,filename):
    folder = 'cached'
    path = os.path.join(folder,filename)
    if os.path.exists(path):
        with open(path, 'rb') as f:
            s = f.read()
            return s
    else:
        # 建立 cached 文件夹
        if not os.path.exists(folder):
            os.makedirs(folder)
        # 发送网络请求, 把结果写入到文件夹中
        r = requests.get(url)
        print(path)
        with open(path, 'wb') as f:
            f.write(r.content)
        return r.content


def comics_from_url(url):
    filename = url.split('=')[1] + '.html'
    page = cached_url(url,filename)

    e = pq(page)
    items = e('.gallery')
    #从gallery中解析出
    comics = [detail_from_div(i) for i in items]
    return comics

def detail_from_div(div):
    e = pq(div)
    baseUrl = 'https://nhentai.net'
    # 从div中获取需要的信息
    c = Comic()
    c.name = e('.caption').text()
    c.srcUrl = baseUrl + e('a').attr('href')
    return c


def comic_list_from_url(page_number):
    p = page_number
    page_list = []
    for i in range(2,p):
        url = 'https://nhentai.net/?page={}'.format(i)
        comics = comics_from_url(url)
        page_list.append(comics)

    comic_list = []
    for p in page_list:
        for c in p:
            comic_list.append(c)
    return comic_list


def src_from_container(container):
    e = pq(container)
    src = e('img').attr('data-src')
    i = 'https://i' + src[9:]
    url = i[:-5] + '.jpg'
    return url


async def down_img(src, folder, img_name):
    img = 'img'
    path = os.path.join(img, folder, img_name)
    if not os.path.exists(img):
        os.mkdir(img)

    p = os.path.join(img, folder)
    if not os.path.exists(p):
        os.mkdir(p)
    if os.path.exists(path):
        return

    async with aiohttp.ClientSession() as session:
        print('开始请求')
        response = await session.get(src)
        content = await response.read()
        with open(path, 'wb') as f:
            f.write(content)
            print('保存成功')


def get_comic_html(comic):
    serial_num = comic.srcUrl.split('/')[-2]
    fn = serial_num + '.html'
    page = cached_url(comic.srcUrl,fn)
    e = pq(page)
    container = e('.thumb-container')
    img_srcs = [src_from_container(c) for c in container]
    # print(img_srcs)
    tasks = []
    for index, src in enumerate(img_srcs):
        img_name = str(index + 1) + '.jpg'
        folder = comic.name.replace('/', '').replace('|', '').replace('?', '')
        tasks.append(asyncio.ensure_future(down_img(src, folder, img_name)))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(tasks))


def main():
    cl = comic_list_from_url(30)
    for c in cl:
        get_comic_html(c)

if __name__ == '__main__':
    main()