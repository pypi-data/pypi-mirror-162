from distutils.core import setup
setup(
  name = 'crossword_puzzle_generator',     
  packages = ['crossword_puzzle_generator'],   
  version = '0.4',   
  license='MIT',
  description = 'A library to generate crossword puzzles',
  author = 'Ahmad Issa Alaa Aldine',                  
  author_email = 'ahmad_alaa_eddein@hotmail.com',     
  url = 'https://github.com/AhmadIssaAlaa',
  download_url = 'https://github.com/AhmadIssaAlaa/crossword_puzzle_generator/archive/refs/tags/v0.4.tar.gz',
  keywords = ['SOME', 'MEANINGFULL', 'KEYWORDS'], 
  install_requires=[ 
          'numpy',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)