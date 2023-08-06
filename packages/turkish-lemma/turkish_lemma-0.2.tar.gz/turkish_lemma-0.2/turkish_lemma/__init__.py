import subprocess
import os
import shutil
import stat
import sys
import urllib.request
import pathlib
import json
import numpy as np
import keras.models
from typing import Callable, Optional

class LemmatizationModule:
    def __init__(self):
        self.setup()
        
    def __call__(self, wordList: list):
        return self.lemmatize(wordList)
        
######################################################
# Custom package classes
class akoksal_Turkish_Lemmatizer(LemmatizationModule):
    MODULE_URL = r"https://github.com/sfurkan20/Turkish-Lemmatizer"
    
    def __init__(self):
        super().__init__()
            
    def setup(self):
        # Remove target directory if exists
        className = type(self).__name__
        
        pathToFiles = os.path.join(pathlib.Path().resolve(), className)
        if os.path.isdir(pathToFiles):
            shutil.rmtree(pathToFiles, onerror=lambda func, path, execinfo: (os.chmod(path, stat.S_IWRITE), func(path)))
        
        # Fetch from source
        subprocess.check_output(['git', 'clone', type(self).MODULE_URL, pathToFiles])

        # Build lexicon
        __import__(f"{className}.trainLexicon").trainLexicon
        
    def lemmatize(self, wordList: list) -> list:        
        lemmatizer = __import__(f"{type(self).__name__}.lemmatizer").lemmatizer
        
        lemmaList = []
        for word in wordList:
            lemma = lemmatizer.main(word)
            lemmaList.append(lemma)
        
        return lemmaList

class obulat_zeyrek(LemmatizationModule):
    MODULE_URL = r"https://github.com/obulat/zeyrek.git"
    
    def __init__(self):
        super().__init__()
            
    def setup(self):        
        try:
            import zeyrek
        except ModuleNotFoundError:
            subprocess.check_output([sys.executable, '-m', "pip", "install", f"git+{type(self).MODULE_URL}"])
            import zeyrek
        
        self.analyzer = zeyrek.MorphAnalyzer()
        
    def lemmatize(self, wordList: list) -> list:
        lemmaList = []
        for word in wordList:
            if len(word) == 0:
                lemmaList.append('')
                continue
            
            lemma = self.analyzer.lemmatize(word)[0][1][0]
            lemmaList.append(lemma)
        
        return lemmaList
    
class otuncelli_turkish_stemmer_python(LemmatizationModule):
    MODULE_URL = r"https://github.com/otuncelli/turkish-stemmer-python.git"
    
    def __init__(self):
        super().__init__()
            
    def setup(self):
        try:
            from TurkishStemmer import TurkishStemmer
        except ModuleNotFoundError:
            subprocess.check_output([sys.executable, '-m', "pip", "install", f"git+{type(self).MODULE_URL}"])
            from TurkishStemmer import TurkishStemmer       
            
        self.stemmer = TurkishStemmer()
        
    def lemmatize(self, wordList: list) -> list:        
        lemmaList = []
        for word in wordList:
            if len(word) == 0:
                lemmaList.append('')
                continue
            
            lemma = self.stemmer.stem(word)
            lemmaList.append(lemma)
        
        return lemmaList
    
class deeplearningturkiye_kelime_kok_ayirici(LemmatizationModule):
    MODULE_URL = r"https://github.com/sfurkan20/kelime_kok_ayirici/raw/master"
    
    def __init__(self):
        super().__init__()
            
    def setup(self):        
        className = type(self).__name__
        
        pathToFiles = os.path.join(pathlib.Path().resolve(), className)
        if os.path.isdir(pathToFiles):
            shutil.rmtree(pathToFiles, onerror=lambda func, path, execinfo: (os.chmod(path, stat.S_IWRITE), func(path)))
        os.mkdir(pathToFiles)
                
        # Source name - Target name tuples
        filesToDownload = [("kokbul-18-0.98.hdf5", "weights.hdf5"),
                          ("kokbul.json", "model.json"),
                          ("utilities.py", "utilities.py"),
                          ("datafile.pkl", "datafile.pkl")]        
        for source, target in filesToDownload:
            urllib.request.urlretrieve(f"{type(self).MODULE_URL}/{source}", os.path.join(pathToFiles, target))
        
        modelJS = json.loads(open(os.path.join(pathToFiles, "model.json")).read())
        model = keras.models.model_from_json(modelJS)
        model.load_weights(os.path.join(pathToFiles, "weights.hdf5"))
        
        self.model = model
        self.utilities = __import__(f"{className}.utilities").utilities
        
    def lemmatize(self, wordList: list) -> list:
        lemmaList = []
        for word in wordList:
            if len(word) == 0:
                lemmaList.append('')
                continue
            
            encodedInput = np.array([self.utilities.encode(word)])
            encodedOutput = self.model.predict(encodedInput, verbose=0)
            
            decodedOutput = self.utilities.decode(encodedOutput[0])
            
            lemmaList.append(decodedOutput)
        
        return lemmaList

class snowballstem_snowball(LemmatizationModule):
    MODULE_URL = r"https://github.com/snowballstem/snowball"
    
    def __init__(self):
        super().__init__()
            
    def setup(self):
        try:
            from snowballstemmer import TurkishStemmer
        except ModuleNotFoundError:
            subprocess.check_output([sys.executable, '-m', "pip", "install", "snowballstemmer"])
            from snowballstemmer import TurkishStemmer
        
        self.stemmer = TurkishStemmer()
        
    def lemmatize(self, wordList: list) -> list:
        lemmaList = []
        for word in wordList:
            if len(word) == 0:
                lemmaList.append('')
                continue
            
            lemmaList.append(self.stemmer.stemWord(word))
        
        return lemmaList
######################################################

LEMMATIZERS = [akoksal_Turkish_Lemmatizer(), obulat_zeyrek(), otuncelli_turkish_stemmer_python(), deeplearningturkiye_kelime_kok_ayirici(), snowballstem_snowball()]  # Also includes stemmers, is named 'lemmatizers' for consistency
def tryLemmatizers(wordList: list, func: Callable, funcArgs: Optional[tuple]=(), funcKwargs: Optional[dict]={}, includeNone=False):
    """
    :param list wordList: List of words that will be lemmatized.
    :param Callable func: Function to operate upon.
    :param tuple funcArgs: Arguments supplied to 'func'.
    :param dict funcKwargs: Key-value arguments supplied to 'func'.
    :param bool includeNone: Specifies whether the case that does not use lemmatizer will be taken into consideration.
    This function enhances the NLP pipeline by trying each of the elements of 'LEMMATIZERS' and printing corresponding outputs associated with each lemmatizer.
    """
    
    global LEMMATIZERS
        
    iteratedLemmatizers = [*LEMMATIZERS, None] if includeNone else LEMMATIZERS
    for lemmatizer in iteratedLemmatizers:
        lemmatizedWords = lemmatizer(wordList) if lemmatizer else wordList
        funcOutput = func(lemmatizedWords=lemmatizedWords)
        print(f"""
              {'-' * 20}
              Lemmatizer: {type(lemmatizer).__name__}
              Return From Function: {funcOutput}
              {'-' * 20}
              """)