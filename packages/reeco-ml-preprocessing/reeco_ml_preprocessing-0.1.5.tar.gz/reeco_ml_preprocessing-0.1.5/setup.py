import os
from setuptools import find_packages
from distutils.core import setup

current_directory = os.path.dirname(os.path.abspath(__file__))
try:
    with open(os.path.join(current_directory, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()
except Exception:
    long_description = ''

setup(
	name='reeco_ml_preprocessing',
	packages=find_packages('.'),
	version='0.1.5',
	description='Package for ML preprocessing',
	long_description=long_description,
	long_description_content_type='text/markdown',
	author='ARI Technology',
	author_email='dung.ut@ari.com.vn',
	url='https://gitlab.com/vn-reecotech/Ari/reeco-data-platform/preprocessor',
	download_url='https://gitlab.com/vn-reecotech/Ari/reeco-data-platform/preprocessor',
	install_requires=[
        "joblib==1.0.1",
        "LunarCalendar==0.0.9",
        "numpy",
        "pandas"
    ]
)