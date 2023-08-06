
from setuptools import setup, find_packages
import chariotCore

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()



setup(
    # 应用名
    name = "chariot-sdk",

    # 作者
    author = "chariot",

    # 作者邮箱
    author_email = "chariot@example.com",

    # 描述
    description = "Chariot plugin maker",

    # 版本号
    version = chariotCore.VERSION,

    # 安装 当前目录下有哪些包
    packages = find_packages(),

    # 配合 MANIFEST.ni文件上传静态资源
    include_package_data = True,

    # 碳泽社区
    url = "https://pypi.org/",

    # py版本
    python_requires = '>=3',

    # 依赖
    install_requires = [
        "argparse",
        "jinja2",
        "pyyaml",
        "fastapi",
        "uvicorn",
        "requests",
    ],

    # 入口
    entry_points={
        "console_scripts": [
            "chariot-plugin = chariotCore.main:cmdline"
        ]
    },

    # 项目的详细描述
    long_description = long_description,
    long_description_content_type = "text/markdown",

    # 许可证
    license = 'MIT',
)



