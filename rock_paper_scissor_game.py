import random

emojis  = {'r': '🪨', 'p': '📄', 's': '✂️'}
choices = ('r', 'p', 's')

#---------------------------------------------------------------------------------
def get_the_user_choice():
    while True:
        user_choice = input("Enter your choice Rock, Paper, Scissors? (r/p/s): ").lower()
        if user_choice in choices:
            return user_choice
        else:
            print("Invalid choice! Please choose 'r', 'p', or 's'.")

#---------------------------------------------------------------------------------
def both_choices(user_choice, computer_choice):
    print(f"You chose:      {emojis[user_choice]}")
    print(f"Computer chose: {emojis[computer_choice]}")

#---------------------------------------------------------------------------------
def determine_winner(user_choice, computer_choice):
    if user_choice == computer_choice:
        print("It's a tie! Both chose the same.")
    elif (user_choice == 'r' and computer_choice == 's') or \
         (user_choice == 'p' and computer_choice == 'r') or \
         (user_choice == 's' and computer_choice == 'p'):
        print("😎 You win! Congratulations! 🥳")
        print("🎉 !HOORAY! 🎉")
    else:
        print("🤖 Computer wins! Better luck next time! 💻")

#---------------------------------------------------------------------------------
def while_playing():                      # ✅ only ONE definition
    while True:
        user_choice     = get_the_user_choice()
        computer_choice = random.choice(choices)

        both_choices(user_choice, computer_choice)
        determine_winner(user_choice, computer_choice)

        while True:
            should_continue = input("Let's play again! 🎮 (y/n): ").lower()
            if should_continue == 'y':
                print("Starting a new game... 🎉\n")
                break
            elif should_continue == 'n':
                print("Thanks for playing! 👋")
                print("Goodbye! 👋")
                return
            else:
                print("Please choose 'y' or 'n'!")

#---------------------------------------------------------------------------------
while_playing()                           # ✅ actually calls the function