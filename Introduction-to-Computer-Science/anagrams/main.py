import anagram_game
import os

if __name__ == "__main__":
    # Find the directory where main.py is located
    current_dir = os.path.dirname(__file__)

    # Create a path to a directory, where file with data is in
    data_file = os.path.join(current_dir, "data", "slownik.txt")

    anagram_game.start_game(data_file)