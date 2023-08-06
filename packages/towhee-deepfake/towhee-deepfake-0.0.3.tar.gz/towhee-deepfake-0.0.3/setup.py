import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="towhee-deepfake",
    version="0.0.3",
    author="Zhuoran Yu",
    author_email="zhuoran.yu@zilliz.com",
    install_requires=[
	'cmake',
	'dlib',
	'facenet-pytorch',
	'albumentations',
	'timm',
	'pytorch_toolbelt',
	'tensorboardx',
	'matplotlib',
	'tqdm',
	'pandas',
    ],
    description="Deepfake",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://towhee.io/towhee/deepfake",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
