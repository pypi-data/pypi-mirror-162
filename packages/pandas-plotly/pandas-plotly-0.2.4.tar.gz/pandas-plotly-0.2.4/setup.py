from distutils.core import setup
setup(
    name = 'pandas-plotly',
    packages = ['pp',],
    version = '0.2.4',
    long_description = 'A simple, unified interface for pandas & plotly for data wrangling, vizualization & report generating',
    long_description_content_type = 'text/markdown',
    install_requires=[
        'numpy>=1.21.2',
        'pandas>=1.3.47',
        'plotly>=5.1.0',
    ]
)