from setuptools import setup, find_packages

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    # pip install nnn
    name="WeReadScan",
    version="0.8.5",
    keywords=["weread", "scan", "pdf", "convert", "selenium"],
    description="WeRead PDF Scanner",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # 协议
    license="GPL Licence",

    url="https://github.com/Algebra-FUN/WeReadScan",
    author="Algebra-FUN",
    author_email="g.creator.fan@gmail.com",

    # 自动查询所有"__init__.py"
    packages=find_packages(),
    include_package_data=True,
    platforms="window",
    # 提示前置包
    install_requires=['pillow', 'numpy',
                      'matplotlib', 'opencv-python', 'selenium'],
    python_requires='>=3.6'
)
