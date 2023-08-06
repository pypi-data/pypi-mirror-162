import __init__ as turkish-lemma
#It is 'import turkish-lemma' in regular case (if pulled from pip)

def example(lemmatizedWords=[]):
    return lemmatizedWords
turkish-lemma.tryLemmatizers(wordList="Merhaba, bu bir test cümlesidir.".split(' '), func=example)


"""
OUTPUT:
              --------------------
              Lemmatizer: akoksal_Turkish_Lemmatizer
              Return From Function: ['merhaba', 'bu', 'bir', 'test', 'cümle']
              --------------------


              --------------------
              Lemmatizer: obulat_zeyrek
              Return From Function: ['merhaba', 'bu', 'bir', 'test', 'cümlesi']
              --------------------


              --------------------
              Lemmatizer: otuncelli_turkish_stemmer_python
              Return From Function: ['Merhaba,', 'bu', 'bir', 'test', 'cümlesidir.']
              --------------------


              --------------------
              Lemmatizer: deeplearningturkiye_kelime_kok_ayirici
              Return From Function: ['merhaba', 'bu', 'bir', 'test', 'cümles']
              --------------------


              --------------------
              Lemmatizer: snowballstem_snowball
              Return From Function: ['Merhaba,', 'bu', 'bir', 'test', 'cümlesidir.']
              --------------------
"""