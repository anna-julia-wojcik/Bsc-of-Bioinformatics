import judge
import itertools
from typing import Generator

def making_first_guess(n: int) -> list[int]:
    """
    This function creates the first, most optimal guess for the game in order to provide inital data for minimax alogirthm.
    The most optimal guess is to double every number starting from 1, depending on how many numbers are in the sequence.

    Args:
        n: length of the hidden sequence

    Returns:
        list[int]: generated guess
    """
    guess = []
    # Pivot says, how many 'doubled' numbers should be in the guess
    pivot = n // 2

    for i in range(1, pivot + 1):
        guess.extend([i, i])

    # Case, where n length is odd; we add one non-doubled number, in order to match the length of the hidden sequence
    if n % 2 != 0:
        guess.append(pivot + 1)

    return guess

def is_new_guess_valid(new_guess: list[int], previous_guesses: list[list[int]], feedbacks: list[tuple[int, int]]) -> bool:
    """
    This function checks, if the new guess feedback is consistent to previous feedbacks

    Args:
        new_guess: new guess, which computer made
        previous_guesses: list of previous guesses used in game
        feedbacks: list of feedbacks to previous_guesses (checked by judge.check(...))

    Returns:
        False - if guess is not valid, so if its feedback doesn't match previous feedbacks
        True - if guess is valid, so if its feedback does match previous feedbacks
    """
    for old_guess, feedback in zip(previous_guesses, feedbacks):
        if judge.check(old_guess, new_guess) != feedback:
            return False
    return True

def generate_valid_guesses(possible_values: list[int], length: int, previous_guesses: list[list[int]],
                              feedbacks: list[tuple[int, int]], limit: int = None) -> Generator[list[int], None, None]:
    """
    Generator of possible sequences. It is based on all possible combinations, but only chooses those considered valid

    Args:
        possible_values: list of every colour used in the hidden sequence
        length: length of the hidden sequence
        previous_guesses: list of previous guesses used in game
        feedbacks: list of feedbacks to previous_guesses (checked by judge.check(...))
        limit: optional parameter that limits the number of candidates generated.

    Yields:
        A valid guess as a list of integers.
    """
    # Counter of already generated guesses
    count = 0

    # Function generates all possible combinations of possible values with the specified length
    for guess in itertools.product(possible_values, repeat=length):
        guess = list(map(int, guess))

        if is_new_guess_valid(guess, previous_guesses, feedbacks):
            # If guess feedback is consistent to previous feedbacks, it yields a candidate and generator pauses
            yield guess
            count += 1
            # If limits exists and counter gets bigger than the limit, the generator stops
            if limit and count >= limit:
                break

def minimax_guess(k: int, n: int, previous_guesses: list[list[int]], feedbacks: list[tuple[int, int]]) -> list[int]:
    """
    This function calculates the best guess using the minimax algorithm. The minimax algorithm aims to choose a guess
    that minimizes the worst-case number of possible solutions (feedback responses) remaining after the guess is made.

    The "worst-case" scenario for each guess is determined by the number of remaining candidate solutions that are
    consistent with previous guesses and feedbacks after the guess is evaluated. The guess that results in the least
    number of possible solutions in the worst case is chosen as the next guess.

    Args:
        k: biggest colour in the hidden sequence
        n: length of the hidden sequence
        previous_guesses: list of previous guesses used in game
        feedbacks: list of feedbacks to previous_guesses (checked by judge.check(...))

    Returns:
        list[int]: guess, which minimizes the worst-case number of possible solutions remaining
    """
    best_guess = None
    # Minimal maximum number of possible guesses after each step (first set to infinity, so the worst case)
    min_max_remaining = float('inf')
    limit = 1000

    # Loop that goes through all the generator's guesses
    for guess in generate_valid_guesses([i for i in range(1, k + 1)], n, previous_guesses, feedbacks, limit = limit):
        feedback_counts = {}
        # Loop that updates feedback counts for every candidate in the generator
        for candidate in generate_valid_guesses([i for i in range(1, k + 1)], n, previous_guesses, feedbacks, limit = limit):
            feedback = judge.check(guess, candidate)
            # If feedback doesn't exist in the dict, a definition is created
            if feedback not in feedback_counts:
                feedback_counts[feedback] = 0
            # If feedback exists, one is added to the counter of all possible candidates that match this feedback
            feedback_counts[feedback] += 1

        # Worst case (biggest number of possible candidates) is taken as the max_remaining variable
        max_remaining = max(feedback_counts.values())

        # Update of the best guess and minimal maximum of possible guesses
        if max_remaining < min_max_remaining:
            min_max_remaining = max_remaining
            best_guess = guess

    return best_guess

def players_hidden_sequence() -> list[int]:
    """
    This function requests hidden sequence from the player and checks if it's correct. If it's incorrect, it prints
    a message informing what is wrong.

    Returns:
        list[int]: as a list of integers instead of a string
    """
    while True:
        sequence_input = input("Pass the hidden sequence (separate colours by space): ")
        hidden_sequence = sequence_input.split()
        valid_sequence = True

        # Check each character
        for char in hidden_sequence:
            if char != " " and char.isdigit() == False:
                print("Incorrect sequence. You can only use numbers in the sequence. Try once more.")
                valid_sequence = False
                break
            if int(char) <= 0:
                print("Incorrect sequence. Your colour can't be zero. (Only: 1, 2, ..., k). Try once more.")
                valid_sequence = False
                break

        if valid_sequence:
            return list(map(int, hidden_sequence))

def start_automatic_gameplay():
    """
    This function is the main game module that uses the previous functions. The game loop continues until the
    sequence is guessed.
    """
    print("\nPass the hidden sequence and let the computer guess your sequence.\n")

    hidden_sequence = players_hidden_sequence()
    k = max(hidden_sequence) # biggest colour in the passed sequence
    n = len(hidden_sequence) # the length of the passed sequence

    previous_guesses = []
    feedbacks = []

    guess = making_first_guess(n)
    previous_guesses.append(guess)
    print(f"\nLet's start the game!! My initial guess is: {guess}")

    # Counter of already made guesses
    moves = 1
    running = True

    while running:
        # Evaluation of the previous guess
        checked = judge.check(hidden_sequence, guess)
        feedbacks.append(checked)

        # Game is finished when the judge evaluation says, that there are only correct colours on correct positions
        if checked == (n, 0):
            print(f"\nCongrats to me!! I won the game in {moves} moves!")
            running = False

        # Otherwise, the program creates new guess and goes back to the beginning of the loop
        else:
            print(f"Correct colours, correct positions: {checked[0]}; correct colours, incorrect positions: {checked[1]}")

            guess = minimax_guess(k, n, previous_guesses, feedbacks)
            previous_guesses.append(guess)
            moves += 1

            print(f"\nMy {moves} guess is: {guess}")