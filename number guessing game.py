import random

guess_the_number = random.randint(1, 1000)

print("Welcome to the Number Guessing Game!")
while True:
 try:
   guess = int(input('Guess a number between 1 and 1000: '))
  
   if guess < guess_the_number:
    print('Too low!')
   elif guess > guess_the_number:
    print('Too high!')
   else: 
     print('Congratulations! You guessed the number!')
     break
 except ValueError:
    print("Please enter a valid integer.")
    
 