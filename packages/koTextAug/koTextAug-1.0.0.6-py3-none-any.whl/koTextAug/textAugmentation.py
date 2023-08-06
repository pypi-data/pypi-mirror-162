import random
from koTextAug.utils import *

class Augmentation:
    def __init__(self, mode='whole', tokenizer='okt'):
        assert mode in ['whole','trans','token','no-package'], "mode must be one of 'whole' or 'trans' or 'token' or 'no-package'"
        if mode == 'trans' or mode == 'whole':
            import googletrans
            self.translator = googletrans.Translator()
            self.origin = 'ko'
        if mode == 'token' or mode == 'whole':
            from koTextAug.tokenizer import Tokenizer
            self.tokenizer = Tokenizer(tokenizer)
            self.stopwords = ['이', '가', '께서', '에서', '이다', '을', '를', '이', '의', '에', '에서', '에게', '께', '에게서', '한테', '으로', '로', '로써', '로서', '과', 
                              '와', '아', '야', '은', '는', '에선', '라고', '이라고' '다', '냐', '까', '까지', '부터' , '이여', '야', '여', '랑','이며','도', '부터', '뿐', '만']
            self.special = ['.', ',', '!', ';', ':', '\'', '"', '?', '/', '>', '<', '@', '#', '$', '%', '^', '&', '*', '(', ')', '_', '-', '+', '=']
            self.stopwords.extend(self.special)
        
    def backTranslation(self, sentence, lang='en'): # 언어별 약어 참고해서 lang 변경
        trans = self.translator.translate(sentence, dest=lang)
        result = self.translator.translate(trans.text, dest=self.origin)
        return result.text

    def backTranslation_list(self, input_list, lang='en'):
        trans = self.translator.translate(input_list, dest=lang)
        trans = [i.text for i in trans]
        result = self.translator.translate(trans, dest=self.origin)
        result = [i.text for i in result]
        return result
    
    def randomSwap(self, sentence, n=1):
        tokens = self.tokenizer.tokenize(sentence)
        for _ in range(n):
            i1,i2 = random.sample(range(len(tokens)), 2)
            while (tokens[i1]=='SEP' or tokens[i2]=='SEP' or tokens[i1] in self.stopwords or tokens[i2] in self.stopwords):
                i1,i2 = random.sample(range(len(tokens)), 2)
            tokens[i1], tokens[i2] = tokens[i2], tokens[i1]
        result = self.tokenizer.back_to_sentence(tokens)
        if result==sentence: #swap 후에 변경된 게 없는 경우
            return
        else:
            return result
        
    def randomDeletion(self, sentence, p=0.2):
        tokens = self.tokenizer.tokenize(sentence)
        delete = []
        for c in tokens:
            if(c!='SEP' and random.random()<p):  # and c not in self.special):
                delete.append(c)
        if delete==[] or len(delete) == len(tokens)-tokens.count('SEP'): #단어가 모두 삭제되었거나, 삭제할 게 없는 경우 
            return
        for i in delete:
            tokens.remove(i)
        return self.tokenizer.back_to_sentence(tokens)

    def synonymReplacement(self, sentence, n=1):
        tokens = self.tokenizer.tokenize(sentence)
        for _ in range (n):
            synonym = []
            cnt = 0
            r = random.choice(tokens)
            while(r == 'SEP' or r in self.stopwords or synonym==[]):
                if(cnt==5): # 유의어가 있는 단어가 없을 경우
                    return 
                cnt+=1
                r = random.choice(tokens)
                synonym = crawlSynonyms(r)

            idx = tokens.index(r)
            tokens[idx] = synonym
        return self.tokenizer.back_to_sentence(tokens)
    
    def randomInsertion(self, sentence, n=1):
        tokens = self.tokenizer.tokenize(sentence)
        synonym = []
        for _ in range (n):
            cnt = 0
            r = random.choice(tokens)
            while(r == 'SEP' or r in self.stopwords or synonym==[]):
                if(cnt==5): # 유의어가 있는 단어가 없을 경우
                    return 
                cnt+=1
                r = random.choice(tokens)
                synonym = crawlSynonyms(r)
            tmp = random.randint(0,len(tokens)-1)
            tokens.insert(tmp, 'SEP' + synonym + 'SEP')
        return self.tokenizer.back_to_sentence(tokens)

    def question(self, info, sent=['긍정','부정'], domain='댓글'):
        comment = info[0]
        label = info[1]
        aug_list = []
        for i,s in enumerate(sent):
            new_label = 1 if i==label else 0
            aug_list.append([comment, '해당 '+domain+'은 '+s+" "+domain+"입니까?", new_label])
        return aug_list 