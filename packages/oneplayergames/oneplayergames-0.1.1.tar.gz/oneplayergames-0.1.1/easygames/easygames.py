import os
import random
import argparse

'''
Function for one game of Rock-Paper-Scissors - user vs computer.
This gets the input from the user, randomly generates one for the computer, and works out the winner.

Return values:
0 if draw
1 if player wins
2 if computer wins
'''

def rock_paper_scissors():
    options = ['R', 'P', 'S']
    computer_choice = random.choice(options)
    while True:
        user_choice = input('Choose Rock (R), Paper (P), or Scissors (S): ').upper()
        if user_choice:
            if user_choice[0] in options:
                break
        print('Invalid choice')
    print('Computer chose:', computer_choice)
    diff = options.index(user_choice[0]) - options.index(computer_choice)
    if diff < 0:
        diff += 3
    if diff == 0:
        print('Draw!')
    elif diff == 1:
        print('You win!')
    else:
        print('Computer wins!')
    return diff

'''
Function for one game of Guess the Number (user guesses computer's number)
This gets the input from the user until the number is guessed correctly.

Parameters:
n: int (optional, default: 100) - maximum number which can be the computer's number. In other words, the computer generates a random number from 1 to n.

Return value:
Number of guesses it took for the user to guess the number correctly
'''

def guess_the_number(n=100):
    num = random.randint(1, n)
    count = 1
    while True:
        while True:
            user_input = input(f'Guess {count} | Guess a number: ')
            if user_input.isdigit():
                guessed = int(user_input)
                break
            print('Invalid: not a number')
        if guessed > num:
            print('The number is lower than', guessed)
        elif guessed < num:
            print('The number is higher than', guessed)
        else:
            print('Correct! The number is', num)
            break
        print('')
        count += 1
    return count

'''
NOT A GAME: This function is just for getting inputs from the terminal
'''

def from_terminal():
    parser = argparse.ArgumentParser(prog ='play',
                                     description ='easygames play')
    parser.add_argument('game', metavar ='game', type=str, nargs=1, help= 'game')

    args = parser.parse_args()
    
    if parser.game[0] == 'rps':
        return rock_paper_scissors()
    elif parser.game[0] == 'gtn':
        return guess_the_number()

