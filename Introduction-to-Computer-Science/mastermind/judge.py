def check(hidden: list[int], guess: list[int]) -> tuple[int, int]:
    """
    This function evaluates, how many colours from the query match the hidden sequence and which positions they match on.

    Args:
        hidden: first sequence to be compared
        guess: second sequence to be compared

    Returns:
        tuple[int, int]: tuple with feedback, with two values: correct colours, correct positions;
        correct colours, incorrect positions
    """
    correct_pos, incorrect_pos = 0, 0

    # Copies both lists in order to not change the initial data
    hidden_2 = hidden.copy()
    guess_2 = guess.copy()

    # This loop checks correct colours and correct positions
    for i in range(len(hidden)):
        if guess[i] == hidden[i]:
            correct_pos += 1
            # If a match is found, then both elements of copies are set to None
            hidden_2[i] = None
            guess_2[i] = None

    # This loop checks correct colours and incorrect positions
    for i in range(len(hidden)):
        if guess_2[i] is not None and guess_2[i] in hidden_2:
            incorrect_pos += 1
            # If the condition is fulfilled, element on the index of the element in guess_2 list is set to None on
            # hidden_2 list
            hidden_2[hidden_2.index(guess_2[i])] = None

    return (correct_pos, incorrect_pos)
