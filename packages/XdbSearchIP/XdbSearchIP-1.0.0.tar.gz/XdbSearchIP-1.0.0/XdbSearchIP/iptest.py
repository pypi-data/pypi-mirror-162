# Copyright 2022 The Ip2Region Authors. All rights reserved.
# Use of this source code is governed by a Apache2.0-style
# license that can be found in the LICENSE file.
#

from .xdbSearcher import XdbSearcher, dbPath


def searchWithFile(ip="1.2.3.4"):
    # 1. 创建查询对象
    searcher = XdbSearcher(dbfile=dbPath)

    # 2. 执行查询
    region_str = searcher.searchByIPStr(ip)

    # 3. 关闭searcher
    searcher.close()
    return region_str


def searchWithVectorIndex(ip="1.2.3.4"):
    # 1. 预先加载整个 xdb
    vi = XdbSearcher.loadVectorIndexFromFile(dbfile=dbPath)

    # 2. 使用上面的缓存创建查询对象, 同时也要加载 xdb 文件
    searcher = XdbSearcher(dbfile=dbPath, vectorIndex=vi)

    # 3. 执行查询
    region_str = searcher.search(ip)

    # 4. 关闭searcher
    searcher.close()
    return region_str


def searchWithContent(ip='1.2.3.4'):
    # 1. 预先加载整个 xdb
    cb = XdbSearcher.loadContentFromFile(dbfile=dbPath)

    # 2. 仅需要使用上面的全文件缓存创建查询对象, 不需要传源 xdb 文件
    searcher = XdbSearcher(contentBuff=cb)

    # 3. 执行查询
    region_str = searcher.search(ip)

    # 4. 关闭searcher
    searcher.close()
    return region_str


if __name__ == "__main__":
    searchWithContent()
