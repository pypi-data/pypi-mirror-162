from setuptools import setup, find_packages

setup(
    name='myweixin',
    version='0.0.2',
    keywords='get_friend_list',
    description='a library for weixin robot',
    license='MIT License',
    url='https://pypi.org/project/myweixin/#description',
    author='pythonnic',
    author_email='2696047693@qq.com',
    packages=find_packages(),
    include_package_data=True,
    platforms='any',
    install_requires=["requests"],
)
