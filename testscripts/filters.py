from better_profanity import profanity

profanity.load_censor_words_from_file('../profanity_wordlist.txt')

while True:
    c = input("Type something:")
    print(profanity.censor(c))
