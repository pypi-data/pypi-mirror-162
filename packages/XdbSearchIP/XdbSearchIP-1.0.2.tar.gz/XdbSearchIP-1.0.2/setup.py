"""
@FileName：setup.py
@Description：
@Author：道长
@Time：2022/8/11 17:05
@Department：产品
@Website：www.geekaso.com
@Copyright：©2019-2022 GeekASO
"""

import setuptools

# with open("README.md", "r") as fh:
#     long_description = fh.read()

setuptools.setup(
    name="XdbSearchIP",
    version="1.0.2",
    author="@道长",
    author_email="ctrlf4@yeah.net",
    license='Apache License 2.0',
    description="ip2region查询Python版，数据来源https://github.com/lionsoul2014/ip2region，代码来源https://github.com/luckydog6132，本作者仅做封装使用。",
    long_description="IP查询Python版，数据来源https://github.com/lionsoul2014/ip2region，代码来源https://github.com/luckydog6132，本作者仅做封装使用。",
    long_description_content_type="text/markdown",
    url="https://github.com/lionsoul2014/ip2region",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5'
)