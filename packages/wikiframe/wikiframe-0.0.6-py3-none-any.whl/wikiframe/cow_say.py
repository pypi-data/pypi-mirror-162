from random import choice

class Say:
    '''
    A cow helper function to say something

    Parameters:
    -----------
    something:  A string to say in console
    '''
    
    def cow_says_good(self,something) -> str:
        """
        A method to say something good/positive in console
        """
        emoji_list = ['😉','🛐','🙈','🐶','🥇','🤖']
        """

        """
        lenght = len(something)
        print(" _" + lenght * "_" + "_ ")
        print("< " + something + " > ")
        print(" -" + lenght * "-" + "- ")
        print("        \   ^__^ ")
        print("         \  (oo)\_______ ")
        print(f"            (__)\ good{choice(emoji_list)} )\/\ ")
        print("                ||----w | ")
        print("                ||     || ")

    def cow_says_error(self, something) -> str:
        '''
        A method to say something error/negative in console
        '''
        emoji_list = ['😭','❌','😬','🌑','💔','🙈']
        lenght = len(something)
        print(" _" + lenght * "_" + "_ ")
        print("< " + something + " > ")
        print(" -" + lenght * "-" + "- ")
        print("        \   ^__^ ")
        print("         \  (oo)\_______ ")
        print(f"            (__)\ error{choice(emoji_list)} )\/\ ")
        print("                ||----w | ")
        print("                ||     || ")