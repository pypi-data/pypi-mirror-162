"""
module created by aryo
a module to count letter dots in a persian text
"""
class Text:
    def __init__(self,text):
        self.text = text

    def __str__(self):
        return self.text
    
    def count_dot(self):
        """returns amount of dots in persian text"""
        alphabet = {
        "single_dot" : ['خ','ب','ج','ذ','ز','ض','ظ','غ','ف','ن'],
        "double_dot" : ['ت','ق','ی'],
        "triple_dot" : ['پ','ش','ژ','چ','ث']
        }
        counter = 0
        for word in self.text.split():
            if word[-1] == "ی":
                counter -=2
            for letter in word:
                if letter in alphabet["single_dot"]:
                    counter +=1
                elif letter in alphabet["double_dot"]:
                    counter +=2
                elif letter in alphabet["triple_dot"]:
                    counter +=3
        return counter

    def __eq__(self, other):
        return self.text == other.text

if __name__ == "__main__":
    sentence = Text("طهران دریا یی")
    print(sentence.count_dot())