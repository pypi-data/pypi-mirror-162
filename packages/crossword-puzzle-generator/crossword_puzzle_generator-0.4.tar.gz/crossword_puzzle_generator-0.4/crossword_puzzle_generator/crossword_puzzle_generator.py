import numpy as np
import random
import re


class CrossWordPuzzleGenerator:
    def __init__(self, puzzle_questions, max_word_length=10, max_iter=10):
        self.max_word_length = max_word_length - max_word_length%2
        self.grid = np.chararray((self.max_word_length, self.max_word_length), unicode=True)
        self.grid[:] = '*'
        self.fit_words_count = 0
        self.rIndexes = []
        self.cIndexes = []
        r1 = random.randint(0, self.max_word_length) % 2
        r2 = random.randint(0, self.max_word_length) % 2 
        self.avialable_cols = [i*2+r1 for i in range(int(self.max_word_length/2))]
        self.avialable_rows = [i*2+r2 for i in range(int(self.max_word_length/2))]
        self.add_vertical = True
        self.max_iter = max_iter
        self.questions = puzzle_questions
        self.fitted_questions = []
        self.fitted_words = []
        self.fitted_ids = []
    
    def generate(self):
        self.questions = sorted(self.questions, key=lambda x: len(x.word_answer), reverse=True)
        done_flag = self.addFirstWord()

        if not done_flag:
            return False

        j = 0
        while self.fit_words_count < self.max_word_length:
            if self.fit_words_count == 2:
                random.shuffle(self.questions)

            flag, question_answer, mainIndex, secondaryIndex = self.fitNewWord()
            if not flag:
                j +=1
                if j == self.max_iter:
                    return False
                continue
            
            j = 0
            if self.add_vertical:
                self.addVerticalWord(mainIndex, secondaryIndex, question_answer)
            else:
                self.addHorizontalWord(secondaryIndex, mainIndex, question_answer)
        
        return True

    def fitNewWord(self):
        word = ""
        mainIndex = -1
        secondaryIndex = -1
        if self.add_vertical:
            mainIndex = self.avialable_cols[random.randint(0, len(self.avialable_cols)-1)]
            to_fit = "".join(self.grid[:,mainIndex])
        else:
            mainIndex = self.avialable_rows[random.randint(0, len(self.avialable_rows)-1)]
            to_fit = "".join(self.grid[mainIndex,:])
        
        find_word_flag, question_answer, secondaryIndex = self.searchWord(to_fit)
        if find_word_flag:
            return True, question_answer, mainIndex, secondaryIndex
        
        flag, result, indexes = self.handle_multiple_letters_to_fit(to_fit)
        
        if not flag:
            return False, word, mainIndex, secondaryIndex
        
        for i in range(len(result)):
            find_word_flag, question_answer, secondaryIndex = self.searchWord(result[i])
            if find_word_flag:
                secondaryIndex += indexes[i]
                return True, question_answer, mainIndex, secondaryIndex
        
        return False, word, mainIndex, secondaryIndex

    def handle_multiple_letters_to_fit(self, to_fit):
        all_letters_indexes = [occ.start() for occ in re.finditer("[A-Z]", to_fit)]

        if len(all_letters_indexes) < 2:
            return False, [], []
        indexes = []
        result = []
        for i in range(len(all_letters_indexes) - 1):
            for j in range(len(all_letters_indexes) - 1, i, -1):
                i1 = all_letters_indexes[i]
                i2 = all_letters_indexes[j]
                if i1 == all_letters_indexes[0] and i2 == all_letters_indexes[-1]:
                    result.append(to_fit[0:i2-1])
                    indexes.append(0)
                    result.append(to_fit[i1+2:])
                    indexes.append(i1+2)
                    result.append(to_fit[i1+2:i2-1])
                    indexes.append(i1+2)
                elif i1 == all_letters_indexes[0]:
                    result.append(to_fit[0:i2-1])
                    indexes.append(0)
                    result.append(to_fit[i1+2:i2-1])
                    indexes.append(i1+2)
                elif i2 == all_letters_indexes[-1]:
                    result.append(to_fit[i1+2:])
                    indexes.append(i1+2)
                    result.append(to_fit[i1+2:i2-1])
                    indexes.append(i1+2)
                else:
                    result.append(to_fit[i1+2:i2-1])
                    indexes.append(i1+2)
        
        return True, result, indexes

    def searchWord(self, to_fit):
        to_fit_list, starts = self.handleToFit(to_fit)
        for i in range(len(to_fit_list)):
            to_fit = to_fit_list[i]
            start = starts[i]
            if len(to_fit) < 2:
                continue
            pattern = self.createRegexPattern(to_fit)
            for question_answer in self.questions:
                if len(question_answer.word_answer) < 2 or question_answer.word_answer in self.fitted_words:
                    continue
                res = re.search(pattern, question_answer.word_answer)
                if res:
                    secondaryIndex = self.getIndex(question_answer.word_answer, to_fit) + start
                    return True, question_answer, secondaryIndex
        return False, "", -1

    def handleToFit(self, to_fit):
        to_fit_list = to_fit.split(',')
        indexes = [0]
        for i in range(len(to_fit_list)-1):
            indexes.append(len(to_fit_list[i]) + indexes[i] + 1)

        # sort the list (put ones with letters first)
        result = []
        new_indexes = []
        for i in range(len(to_fit_list)):
            patt = "[A-Z]"
            if re.search(patt, to_fit_list[i]):
                result.append(to_fit_list[i])
                new_indexes.append(indexes[i])
        
        for i in range(len(to_fit_list)):
            if to_fit_list[i] not in result:
                result.append(to_fit_list[i])
                new_indexes.append(indexes[i])
        
        return result, new_indexes

    def getIndex(self, word, to_fit):
        for i in range(len(to_fit)):
            ch = to_fit[i]
            if ch.isalpha():
                result = [occ.start() for occ in re.finditer(ch, word)]
                for j in result:
                    if i - j + len(word) <= len(to_fit):
                        return i - j
        
        return random.randint(0, len(to_fit) - len(word))
    
    def createRegexPattern(self, to_fit):
        patt = "[A-Z]"
        
        all_letters_indexes = [occ.start() for occ in re.finditer(patt, to_fit)]
        if len(all_letters_indexes) <= 1:
            return "^" + to_fit.replace("*", patt + "?") + "$"
        else:
            regex = "^"
            start = all_letters_indexes[0]
            end = all_letters_indexes[-1]
            for i in range(len(to_fit)):
                if i < start or i > end:
                    regex += (patt + "?")
                elif i in all_letters_indexes:
                    regex += to_fit[i]
                else:
                    regex += patt
            return regex + "$"

    def addHorizontalWord(self, cIndex, rIndex, question_answer):
        word = question_answer.word_answer
        temp_cIndex = cIndex
        if cIndex > 0:
            word = "," + word
            cIndex -= 1
        if cIndex + len(word) - 1 < 9:
            word = word + ","
        self.grid[rIndex, cIndex:cIndex+len(word)] = list(word)
        self.fit_words_count += 1
        self.fitted_words.append(question_answer.word_answer)
        self.fitted_ids.append(question_answer.id)
        self.fitted_questions.append(question_answer)
        
        self.avialable_rows.remove(rIndex)
        if (rIndex -1) in self.avialable_rows:
            self.avialable_rows.remove(rIndex-1)
        if (rIndex + 1) in self.avialable_rows:
            self.avialable_rows.remove(rIndex+1)
        
        self.add_vertical = not self.add_vertical
        self.rIndexes.append(rIndex)
        self.cIndexes.append(temp_cIndex)
    
    def addVerticalWord(self, cIndex, rIndex, question_answer):
        temp_rIndex = rIndex
        word = question_answer.word_answer
        
        if rIndex > 0:
            word = "," + word
            rIndex -= 1
        if rIndex + len(word) - 1 < 9:
            word = word + ","
        
        self.grid[rIndex:rIndex+len(word), cIndex] = list(word)
        self.fit_words_count += 1
        self.fitted_words.append(question_answer.word_answer)
        self.fitted_ids.append(question_answer.id)
        self.fitted_questions.append(question_answer)
        
        self.avialable_cols.remove(cIndex)
        if (cIndex -1) in self.avialable_cols:
            self.avialable_cols.remove(cIndex-1)
        if (cIndex + 1) in self.avialable_cols:
            self.avialable_cols.remove(cIndex+1)
        
        self.add_vertical = not self.add_vertical
        self.rIndexes.append(temp_rIndex)
        self.cIndexes.append(cIndex)

    def addFirstWord(self):
        question_answer = self.questions[0]
        word = question_answer.word_answer
        if len(word) < 3:
            return False
        
        cIndex = self.avialable_cols[random.randint(0, len(self.avialable_cols)-1)]
        rIndex = random.randint(0, self.max_word_length - len(word))
        self.addVerticalWord(cIndex, rIndex, question_answer)
        return True