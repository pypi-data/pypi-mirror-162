
class PuzzleQuestion:
    def __init__(self, id, question, word_answer):
        self.id = id
        self.question = question
        self.word_answer = word_answer

    def __str__(self):
        return "question: " + self.question + ";; answer: " + self.word_answer
    
    def __repr__(self):
        return str(self)