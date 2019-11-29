from typing import List, Dict
import copy
import pandas as pd
import stats    

class WordFactory: 
    @classmethod
    def getWord(cls, wordText):
        startContent = wordText.find(',')
        endContent = wordText.rfind('",') 

        content = wordText[startContent + 2: endContent]
        end = wordText[endContent + 2:].split(",")
        return Word(content, *end)

class Word:
    def __init__(self, word, female, i_pronoun,
        exclude, coef="0", ME="0", nFemale="0", nMale="0", coef_pronoun="0",
        ME_pronoun="0", nFemale_pronoun="0", nMale_pronoun="0", linear_coef="0"):
        '''
            female: 1 if female classifier (refering to a female)
                    0 if a male classifier
                    NA otherwise
            
            i_pronoun: 1 iff a gender classifier is a female or male pronoun
                       (e.g."he"/"she")
            
            exclude: 1 iff a word is NOT used as a predictor in the Lasso models.
                     This list includes all gender classifiers, plus names of
                     celebrities who are not economists.	
        '''
        self.word = word
        self.female = female
        self.i_pronoun = i_pronoun
        self.exclude = exclude
        self.coef = coef
        self.ME = ME
        self.nFemale = nFemale
        self.nMale = nMale
        self.coef_pronoun = coef_pronoun
        self.ME_pronoun = ME_pronoun
        self.nFemale_pronoun = nFemale_pronoun
        self.nMale_pronoun = nMale_pronoun
        self.linear_coef = linear_coef
    
    def __str__(self):
        return ",".join([
            '"{}"'.format(self.word), self.female,
            self.i_pronoun, self.exclude, self.coef, self.ME,
            self.nFemale, self.nMale, self.coef_pronoun, self.ME_pronoun,
            self.nFemale_pronoun, self.nMale_pronoun, self.linear_coef
            ])
        

def getWuWordsFromFile(genderedWordsPath)-> List[Word]:
    '''
        genderedWordsPath should be the path to Wu's vocab10K.csv file.
        
        returns a list of words with fields corresponding to
        the field's used by Wu in vocab10K.csv. See We_README.pdf for more
        information on the fields.
    '''
    words = []
    with open(genderedWordsPath, "r") as f:
        # Reading past header of .csv file
        f.readline()
        for line in f:
            word = WordFactory.getWord(line)
            words.append(word)
    return words

def getGenderedWordsMap(genderedWordsPath) -> Dict[str, Word]:
    '''
        genderedWordsPath should be the path to Wu's vocab10K.csv file.

        returns a map from the words coded by Wu in vocab10K.csv to a Word
        object containing Wu's metadata for the word, such as if the word is
        female.
    '''
    words = {}
    genderedWords = getWuWordsFromFile(genderedWordsPath)
    for w in genderedWords:
        words[w.word] = w    
    return words


def genderCodeWords(genderedWordsMap: Dict[str, Word], wordsToCode: List[str]) -> List[Word]:
    '''
        genderedWordsMap should be a map from strings to gender coded Word objects.
            genderCodeWords assumes none of the words in genderedWordsMap have "TODO"
            in any field.

        returns a list of Word objects from wordsToCode which are coded with the
            same female, i_pronoun, and exclude fields as Wu's words. If a word in
            wordsToCode isn't coded by Wu the aforementioned fields will all be "TODO".
    '''

    codedWords = []
    for w in wordsToCode:
        word = None
        if w in genderedWordsMap:
            wuWord = genderedWordsMap[w]
            word = Word(wuWord.word, wuWord.female, wuWord.i_pronoun, wuWord.exclude)
        else:
            word = Word(w, "TODO", "TODO", "TODO")
        codedWords.append(word)
    
    return codedWords


    