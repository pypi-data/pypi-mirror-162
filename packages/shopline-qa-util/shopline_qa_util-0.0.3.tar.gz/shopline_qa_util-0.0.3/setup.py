import setuptools

setuptools.setup(
    name='shopline_qa_util',
    version='0.0.3',
    description='shopline qa util',
    author='zhouibhui',
    author_email='zhoubihui@shoplineapp.com',
    url='https://shoplineapp.cn',
    install_requires=[
        "requests>=2.24.0"
    ],
    license='MIT',
    packages=setuptools.find_packages(),
    platforms=["all"],
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        "License :: OSI Approved :: MIT License"
    ],
)
