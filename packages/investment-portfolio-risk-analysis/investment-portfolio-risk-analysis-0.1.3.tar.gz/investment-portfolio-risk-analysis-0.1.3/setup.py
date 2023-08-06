from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path (__file__).parent
long_description = (this_directory / "README.md").read_text ()

setup (name = 'investment-portfolio-risk-analysis', version = '0.1.003', license = 'MIT',
       author = "Khoi Nguyen NGUYEN, Ecole Polytechnique, France,Ingénieur Polytechnicien Program,  Promotion 2011",
       author_email = 'khoi-nguyen.nguyen@polytechnique.org', packages = find_packages ('src'),
       package_dir = { '' : 'src' }, url = 'https://github.com/feilongbk/portfolio-risk-analysis-001.git',
       keywords = 'Investment Portfolio Risk Analysis',
       install_requires = ['yfinance', 'quantstats', 'numpy', 'pandas', 'scikit-learn'],
       long_description = long_description, long_description_content_type = 'text/markdown'

       )
