from distutils.core import setup
setup(
  name = 'turkish_lemma',        
  packages = ['turkish_lemma'], 
  version = '0.3',      
  license='MIT',      
  description = 'Lemmatization abstraction library for Turkish language.', 
  author = 'Furkan Salık',                  
  author_email = 'fsalik25@outlook.com',
  url = 'https://github.com/sfurkan20', 
  download_url = 'https://github.com/sfurkan20/Turkish-Lemmatization-Abstraction/archive/refs/tags/v_02.tar.gz',
  keywords = ['NLP', 'Turkish', 'Lemmatization', 'Abstraction'], 
  install_requires=[           
          'keras',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      
    'Intended Audience :: Developers',      
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   
    'Programming Language :: Python :: 3',      
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
  ],
)
