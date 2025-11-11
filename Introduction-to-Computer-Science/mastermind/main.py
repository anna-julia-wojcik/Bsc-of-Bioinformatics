import player_gameplay
import automatic_gameplay


def main():
    """
    This function allows the player to select the game module they want to run and checks the correctness of
    the entered data. If it's incorrect, it prints a message informing what is wrong.
    """
    print("Welcome to Mastermind - a game of logic and deduction!")
    print("\nChoose your gameplay type:")
    print("1. Automatic gameplay")
    print("2. Player gameplay")

    while True:
        choice_input = input("\nYour choice: ")

        try:
            choice = int(choice_input)
        except ValueError:
            print("Invalid input. You must enter a number. Try again.")
            continue

        if choice == 1:
            automatic_gameplay.start_automatic_gameplay()
            break
        elif choice == 2:
            player_gameplay.start_player_gameplay()
            break
        else:
            print("Incorrect number. Please enter 1 or 2.")

if __name__ == "__main__":

    main()
