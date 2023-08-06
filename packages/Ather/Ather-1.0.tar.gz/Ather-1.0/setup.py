from setuptools import setup, find_packages


with open("README.md", "r") as fh:
    long_description = fh.read()


setup(name='Ather', # 패키지 명

version='1.0',

description='한국 초등 6학년이 만든 소형 모듈. 인터넷에서 만드는 방법 검색해서 만들어따!',

author='Aqouthe',

author_email='hoonie0929@gmail.com',

url='',

license='MIT', # MIT에서 정한 표준 라이센스 따른다

py_modules=['Aqouthe_', 'Aqouthe_module'], # 패키지에 포함되는 모듈

python_requires='>=3',

install_requires=[], # 패키지 사용을 위해 필요한 추가 설치 패키지

packages=['package_folder'] # 패키지가 들어있는 폴더들

)