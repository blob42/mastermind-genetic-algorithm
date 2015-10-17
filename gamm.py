#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import random
import sys

# COLORS = [1,2,3,4,5,6]
COLORS=[]
TOGUESS = [1,1,1,1]


MAX_POP_SIZE = 60
MAX_GENERATIONS = 100

CROSSOVER_PROBABILITY = 0.5
CROSSOVER_THEN_MUTATION_PROBABILITY = 0.03
PERMUTATION_PROBABILITY = 0.03
INVERSION_PROBABILITY = 0.02

ELITE_RATIO=0.4


WEIGHT_BLACK = 5 # weight of well placed colors we give them a slightly better weight
WEIGHT_WHITE = 3 # weight of bad placed colors

def check_play(ai_choice, right_choice):
    '''
    Returns number of good placements and bad placements from ai_choice
    compared to right_choice
    Assert ai_choice and right_choice with same length
    '''

    assert len(ai_choice) == len(right_choice)

    # local copy of color to guess as reference of already calculated colors

    copy_right_choice = []
    for code in right_choice:
        copy_right_choice.append(code)

    copy_ai_choice = []
    for code in ai_choice:
        copy_ai_choice.append(code)

    placeTrue = 0
    placeFalse = 0

    for i in range(len(right_choice)):
        if right_choice[i] == ai_choice[i]:
            placeTrue = placeTrue + 1
            copy_right_choice[i] = 42
            copy_ai_choice[i] = 4242

    for code in copy_ai_choice:
        if code in copy_right_choice:
            placeFalse = placeFalse + 1
            for i,c in enumerate(copy_right_choice):
                if c == code:
                    copy_right_choice[i] = 42


    return (placeTrue,placeFalse)



def fitness_score(trial, code, guesses, slots=4):
        '''
        fitness score function
        takes a `trial`(chromose) and compare it to a reference `code`
        it returns a score based on the quality of `trial` being a probable guess
        of `code`
        '''

        # Returns the difference between the trial color result and
        # the guess color result, assuming guess is the right choice
        def get_difference(trial, guess):

            # The result AI guess obtained
            guess_result = guess[1]

            # The ai guess code
            guess_code = guess[0]

            # We assume `guess` is the color to guess
            # we then establish the score our `trial` color would obtain

            trial_result = check_play(trial, guess_code)

            # We get the difference between the scores
            dif = [0,0]
            for i in range(2):
                dif[i] = abs(trial_result[i] - guess_result[i])

            return tuple(dif)


        # Given a list of guesses (picked from elite generations),
        # we build a list of difference score comparing our trial to
        # each guess
        differences = []
        for guess in guesses:
            differences.append(get_difference(trial, guess))

        # Sum of well placed colors
        sum_black_pin_differences = 0
        # Sum of wrong placed colors
        sum_white_pin_differences = 0

        for dif in differences:
            sum_black_pin_differences += dif[0]
            sum_white_pin_differences += dif[1]

        # Final score
        score = sum_black_pin_differences + sum_white_pin_differences
        return score

def genetic_evolution(popsize, generations, costfitness,
                            eliteratio=ELITE_RATIO, slots=4):
        '''
        Function implementing the genetic algorithm to guess the right color code
        for MasterMind game

        We generate several populations of guesses using natural selection strategies
        like crossover, mutation and permutation.

        In this function, we assume our color code to guess as a chromosome.
        The populations we generate are assimilated to sets of chromosomes for
        which the nitrogenous bases are our color code

        popsize: the maximum size of a population
        generations: maxumum number of population generations
        costfitness: function returning the fitness score of a chromosome (color code)
        '''

        def crossover(code1, code2):
            '''
            Cross Over function
            '''
            newcode = []
            for i in range(slots):
                if random.random() > CROSSOVER_PROBABILITY:
                    newcode.append(code1[i])
                else:
                    newcode.append(code2[i])
            return newcode

        def mutate(code):
            '''
            Mutation function
            '''
            i = random.randint(0, slots-1)
            v = random.randint(1, len(COLORS))
            code[i] = v
            return code

        def permute(code):
            '''
            Permutation function
            '''
            for i in range(slots):
                if random.random() <= PERMUTATION_PROBABILITY:
                    random_color_position_a = random.randint(0, slots-1)
                    random_color_position_b = random.randint(0, slots-1)

                    save_color_a = code[random_color_position_a]

                    code[random_color_position_a] = code[random_color_position_b]
                    code[random_color_position_b] = save_color_a
            return code


        # We generate the first population of chromosomes, in a randomized way
        # in order to reduce probability of duplicates

        population = [[random.randint(1, len(COLORS)) for i in range(slots)]\
                                   for j in range(popsize)]



        # Set of our favorite choices for the next play (Elite Group Ei)
        chosen_ones = []
        h = 1
        k = 0
        while len(chosen_ones) <= popsize and h <= generations:

                # Prepare the population of sons who will inherit from the parent
                # generation using a natural selection strategy
                sons = []

                for i in range(len(population)):

                        # If we find two parents for the son, we pick the son
                        if i == len(population) - 1:
                            sons.append(population[i])
                            break

                        # Apply corss over
                        son = crossover(population[i], population[i+1])


                        # Apply mutation after cross over
                        if random.random() <= CROSSOVER_THEN_MUTATION_PROBABILITY:
                                son = mutate(son)

                        # Apply mutation
                        son = permute(son)

                        # Add the son to the population
                        sons.append(son)



                # We link each son to a fitness score. The closest the score to
                # Zero, the better chance our code is the right guess
                pop_score = []
                for c in sons:
                    pop_score.append((costfitness(c), c))

                # We order our sons population based on fitness score (increasing)
                pop_score = sorted(pop_score, key=lambda x: x[0])




                # We use the eliteration parameter to choose an elite of chosen
                # codes among the choices, imitating natural selection process
                # NOTE: elite ratio is not currently used

                # First we pick an eligible elite (Score is Zero)
                eligibles = [(score, e) for (score, e) in pop_score if score == 0]

                if len(eligibles) == 0:
                    h = h + 1
                    continue


                # Pick out the code from our eligible elite (score, choice) tuples
                new_eligibles = []
                for (score, c) in eligibles:
                    new_eligibles.append(c)
                eligibles = new_eligibles



                # We remove the eligible codes already included in the elite choices (Ei)

                for code in eligibles:
                    if code in chosen_ones:
                        chosen_ones.remove(code)

                        # We replace the removed duplicate elite code with a random one
                        chosen_ones.append([random.randint(1, len(COLORS)) for i in range(slots)])


                # We add the eligible elite to the elite set (Ei)
                for eligible in eligibles:
                    # Make sure we don't overflow our elite size (Ei <= popsize)
                    if len(chosen_ones) == popsize:
                        break

                    # If the eligible elite code is not already chosen, promote it
                    # to the elite set (Ei)
                    if not eligible in chosen_ones:
                        chosen_ones.append(eligible)


                # Prepare the parent population for the next generation based
                # on the current generation
                population=[]
                population.extend(eligibles)


                # We fill the rest of the population with random codes up to popsize
                j = len(eligibles)
                while j < popsize:
                    population.append([random.randint(1, len(COLORS)) for i in range(slots)])
                    j = j + 1



                # For each generation, we become more aggressive in choosing
                # the best eligible codes. We become more selective
                #if not eliteratio < 0.01:
                    #eliteratio -= 0.01

                h = h + 1



        return chosen_ones

def play(trial, turn, toFind):

    # print('|||>>||||>>>>>>>>>>>>>>>>>> PLAYING: ', trial, ' Turn : ', turn)
    res =  check_play(trial, toFind)
    return res


def usage():
    """usage doc"""
    print('''
          Usage: ./gamastermind.py number_of_colors code_to_guess
          example: ./gamastermind.py 6 1234
          6 colors, and 4 digit code <1 2 3 4>
          ''')


def main():


        if len(sys.argv) != 3:
            usage()
            sys.exit(1)
        elif (sys.argv[1] == 'help'):
            usage()
            sys.exit(1)
        else:
            COLORS.extend(range(1, int(sys.argv[1]) + 1))
            TOGUESS = [int(c) for c in sys.argv[2]]

        print('Colors: %s' % COLORS )
        print('Code to guess: %s' % TOGUESS)

        random.seed(os.urandom(32))
        G1 = [1,1,2,2] #initial guess
        code = G1
        turn = 1


        # List of all tried guesses Gi
        guesses = []


        def scoref(trial):
                return fitness_score(trial, code, guesses, slots=4)

        result=play(code, turn, TOGUESS)
        guesses.append((code, result))

        last_eligibles = []
        while result != (4,0):
            eligibles = genetic_evolution(MAX_POP_SIZE, MAX_GENERATIONS, scoref, slots=4)
            print('Ei', len(eligibles))

            while len(eligibles) == 0:
                print('is 0')
                print(guesses)
                eligibles = genetic_evolution(MAX_POP_SIZE*2, MAX_GENERATIONS/2, scoref, slots=4)

            #### DO NOT USE RANDOM
            code = eligibles.pop()
            while code in [c for (c, r) in guesses]:
                # print('DUPLICAAAAAAAAAATE')
                code = eligibles.pop()


            #### DO NOT USE RANDOM
            turn += 1
            result = play(code, turn, TOGUESS)
            guesses.append((code, result))


            if result == (4,0):
                print('WIIIIIIN')
                print(code, result)



if __name__ == '__main__':
        main()
