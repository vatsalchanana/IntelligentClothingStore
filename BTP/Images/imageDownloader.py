import urllib
iter = 0
not_downloaded = []
with open("/Users/shivamahajan/Desktop/meta_file_truncated.txt") as f:
    for line in f:
        meta_list = line.split(',')
        title_index = 0
        if title_index != -1:
            title = meta_list[0][title_index + 10:-1]
        for item in meta_list:
            url_index = item.find("'imUrl':")
            if url_index != -1:
                url = item[url_index + 10:-1]
        try:
            urllib.urlretrieve(url, title+".jpg")
        except IOError:
            not_downloaded.append((iter, title))
            print iter
        iter += 1
for i in not_downloaded:
    print i