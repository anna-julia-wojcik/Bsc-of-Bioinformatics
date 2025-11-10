import random

def import_data(source: str) -> list[str]:
    """
    This function reads the file line to line, and strips every line.

    Args:
        source (str): Path to the file containing the word list.

    Returns:
        list[str]: List of words that the file contains.

    """
    file = open(source, encoding="utf-8")
    data_set = [line.strip() for line in file]
    file.close()

    return data_set

def selection(data_set: list[str]) -> dict[str, list[str]]:
    """
    Returns words from the dataset that have at least two anagrams,
    mapping each word (uppercase) to its sorted letters.

    Args:
        data_set (list[str]): List of words to analyze.

    Returns:
        dict[str, list[str]]: Words with at least two anagrams and their sorted letters.
    """
    # Create a list of sorted letters for each word (uppercase)
    sorted_letters_list = [sorted(word.upper()) for word in data_set]

    dict_of_sorted = {}

    for i, letters in enumerate(sorted_letters_list):
        if sorted_letters_list.count(letters) >= 3:
            dict_of_sorted[data_set[i].upper()] = letters

    return dict_of_sorted

def get_valid_guess(word_letters: list[str], anagrams_list: list[str]) -> str:
    """
    Asks the player to enter a valid anagram and validates the input.

    The function keeps asking until the player enters a word that:
    - contains only letters,
    - uses exactly the letters of the target word,
    - exists in the anagrams list.

    Args:
        word_letters (list[str]): The letters of the target word (sorted).
        anagrams_list (list[str]): List of remaining valid anagrams.

    Returns:
        str: A valid guessed word in uppercase.
    """
    while True:
        try:
            guess = input("Please, enter an anagram: ").strip().upper()

            if not guess.isalpha():
                print("Your input is not a word. Try again!")
                continue

            if sorted(guess) != word_letters:
                print("Your word does not contain all of the required letters. Try again!")
                continue

            if guess not in anagrams_list:
                print("Your word is not on the anagrams list! Try again!")
                continue

            # If the guess is valid, return it
            return guess

        except EOFError:
            print(f"\nSuch a shame you gave up! Remaining anagrams were: {anagrams_list}")
            raise SystemExit

def start_game(data_source: str) -> None:
    """
    Starts the anagram guessing game using words from the given data source.

    A word is randomly selected from the data source and converted into a list of letters.
    All possible anagrams for this word are generated. The player is repeatedly prompted
    to guess anagrams until all are correctly found or exits the game.

    Args:
        data_source (str): Path to the file containing the word list.
    """
    # Load anagrams from the data source
    anagrams_dict = selection(import_data(data_source))

    # Randomly select a word and get its sorted letters
    word_letters = random.choice(list(anagrams_dict.values()))
    anagrams_list = [key for key, val in anagrams_dict.items() if val == word_letters]

    print(f"Make anagrams out of the given letters: {' '.join(word_letters)} \nPress Ctrl+D to give up.\n")

    while anagrams_list:
        guess = get_valid_guess(word_letters, anagrams_list)
        print("Correct anagram!")
        anagrams_list.remove(guess)

    print("\nCongrats! You guessed all the anagrams!")
