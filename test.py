import os

def down_img(folder, img_name):
    img = 'test111'
    if not os.path.exists(img):
        os.mkdir(img)
    path = os.path.join(img, folder,img_name)
    print(path)
    p = os.path.join(img, folder)
    if not os.path.exists(p):
        os.mkdir(p)
    if os.path.exists(path):
        return

    with open(path, 'wb') as f:
        f.write(b'111')
        print('下载成功')

down_img('[榎維]Antholo Kikou (Fate/stay night)[Digital]', '[榎維].html')
