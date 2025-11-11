import judge
import random


def sequence_randomizer(k: int, n: int) -> list[int]:
    """
    This function randomizes a list of integers in range between 1 and the biggest colour (given by the player)

    Args:
        k: the biggest colours in the hidden sequence
        n: the length of the hidden sequence

    Returns:
        list[int]: list of randomized colours, that need to be guessed
    """
    hidden_sequence = []
    for i in range(n):
        hidden_sequence.append(random.randint(1, k))

    return hidden_sequence


def player_guess(k: int, n: int) -> list[int]:
    """
    This function requests a guess from the player, checks if it's correct and returns it. If it's incorrect, it prints
    a message informing what is wrong and asks again for a guess.

    Args:
        k: the biggest colours in the hidden sequence
        n: the length of the hidden sequence

    Returns:
        list[int]: as a list of integers instead of a string
    """
    while True:
        guess_input = input("\nTell me your guess (separate colours by space): ")
        guess = guess_input.split()

        if len(guess) != n:
            print("Incorrect guess. The length of your sequence doesn't match the hidden sequence. Try again.")
            continue

        # Check each character
        valid_guess = True
        for char in guess:
            if char != " " and not char.isdigit():
                print("Incorrect guess. You can only use numbers to guess the sequence. Try again.")
                valid_guess = False
                break

            num = int(char)
            if num <= 0 or num > k:
                print(f"Incorrect guess. Your colour must be between 1 and {k}. Try again.")
                valid_guess = False
                break

        if valid_guess:
            return list(map(int, guess))


def start_player_gameplay():
    """
    This function is the main game module that uses the previous functions. The game loop continues until the
    sequence is guessed, or player gives up.
    """
    print("Your goal is to guess the secret code.\nYou can give up by pressing Ctrl + D.\n\nLet the game begin!\n")

    k = int(input("Tell me the number of 'the biggest' colour: "))
    n = int(input("Tell me the length of the hidden sequence: "))
    hidden_sequence = sequence_randomizer(k, n)

    # Counter of already made guesses
    moves = 0
    running = True

    try:
        while running:
            # Request for a guess and evaluation of this guess
            current_guess = player_guess(k, n)
            checked = judge.check(hidden_sequence, current_guess)
            moves += 1

            # Game is finished when the judge evaluation says, that there are only correct colours on correct positions
            if checked == (n, 0):
                print("\nCongrats!! You won the game in ", moves, " moves!")
                running = False
            # Otherwise, the program prints the evaluation and goes back to the beginning of the loop
            else:
                print("Correct colours, correct positions:", checked[0], "; correct colours, incorrect positions:", checked[1])

    # Ctrl + D was pressed, player gave up
    except EOFError:
        print("\nWow. Really? Giving up already? Mastermind might be a game of logic, but clearly, perseverance isn’t one "
              "of your strong suits.\nDid the challenge get too overwhelming? Or were you just hoping for a participation "
              "trophy? This isn’t the playground.\nReal problem solvers don’t throw in the towel when it gets tough, "
              "they recover and try again.\nBut hey, if you’re content with being outsmarted by a set of colored pegs, who "
              "am I to stop you?\nQuitters don’t win, and winners don’t quit. Unfortunately, now I know which camp you "
              "belong to.\nGo ahead, hit that quit button, but don’t forget to tell yourself, ‘I gave up.’, unless you "
              "wanna try again.")

        print("\nThe sequence you were supposed to guess was:", " ".join(map(str, hidden_sequence)))

