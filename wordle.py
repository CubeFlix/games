import random, copy

WORDLE_WORDS = []
WORDLE_ANSWERS = []

# Wordle guess status values.
STATUS_LETTER_CORRECT = 2
STATUS_LETTER_INCORRECT_POSITION = 1
STATUS_LETTER_INCORRECT = 0

# Load the words.
def load_words(words_path='wordle_words', answers_path='wordle_answers'):
    def rstrip(s):
        return s.rstrip()

    with open(words_path) as f:
        global WORDLE_WORDS
        WORDLE_WORDS = list(map(rstrip, f.readlines()))

    with open(answers_path) as f:
        global WORDLE_ANSWERS
        WORDLE_ANSWERS = list(map(rstrip, f.readlines()))

# Generate a Wordle word.
def generate_word():
    return random.choice(WORDLE_ANSWERS)

class Game:

    """The Wordle game."""

    def __init__(self, word=None):

        """Create the game."""

        if word:
            self.word = word.lower()
        else:
            self.word = generate_word()

    def guess(self, guess):

        """Take a guess at the word and return the status as a list of status values."""

        values = []
        guess = guess.lower()
        for i in range(5):
            if guess[i] == self.word[i]:
                values.append(STATUS_LETTER_CORRECT)
            elif guess[i] in self.word:
                values.append(STATUS_LETTER_INCORRECT_POSITION)
            else:
                values.append(STATUS_LETTER_INCORRECT)

        return values

    def play(self):

        """Play the game in the console."""

        print('WORDLE')
        print()
        won = False
        for i in range(6):
            # Continue prompting until we get a valid guess.
            while True:
                guess = input('Guess: ')
                if not guess.lower() in WORDLE_ANSWERS:
                    print('Invalid guess.')
                    continue

                # Make the guess.
                status = self.guess(guess)

                # Print the status of the guess.
                for i in range(5):
                    if status[i] == STATUS_LETTER_CORRECT:
                        print(f'\033[0;32m{guess[i].upper()}\033[m', end='')
                    elif status[i] == STATUS_LETTER_INCORRECT_POSITION:
                        print(f'\033[1;33m{guess[i].upper()}\033[m', end='')
                    else:
                        print(f'{guess[i].upper()}', end='')

                # If the guess is correct, exit.
                if status == [STATUS_LETTER_CORRECT] * 5:
                    won = True
                
                break

            print()
            print()

            if won:
                print('You got the word!')
                break

        if not won:
            print(f'The word was: {self.word}')

class Constraint:

    """A constraint for a single character (used by Solver)."""

    def __init__(self):

        """Create a new constraint."""

        self.solved_answer = None
        self.acceptable_chars = []
        self.incorrect_chars = []

    def dup(self):
        
        """Duplicate the constraint."""

        c = Constraint()
        c.solved_answer = self.solved_answer
        c.acceptable_chars = self.acceptable_chars[:]
        c.incorrect_chars = self.incorrect_chars[:]
        return c

class Solver:

    """The Wordle solver."""

    def __init__(self, starting_word='reais', next_word='blahs'):

        """Create the Wordle solver object."""

        self.starting_word = starting_word
        self.next_word = next_word
        self.my_words = WORDLE_WORDS[:10]

        self.num_guesses = 0
        self.guesses = []
        self.constraints = [Constraint() for _ in range(5)]
        self.must_contain_somewhere = []
        self.possible_words = WORDLE_ANSWERS

    def calculate_guess(self):

        """Calculate the next guess."""

        if self.num_guesses == 0:
            self.num_guesses += 1
            self.guesses.append(self.starting_word)
            return self.starting_word

        if self.num_guesses == 1:
            self.calculate_possible_words()
            self.num_guesses += 1
            self.guesses.append(self.next_word)
            return self.next_word

        self.num_guesses += 1

        # Calculate the possible words.
        self.calculate_possible_words()

        if len(self.possible_words) == 1:
            return self.possible_words[0]

        if len(self.possible_words) == 2:
            for guess in self.possible_words:
                if guess in self.guesses:
                    continue
                return guess

        # Pick the guess that gives us the lowest number of possible words
        # in the worst-case scenario, after running the guess after all 
        # possible solutions.
        best_guess = None
        best_worst_case_len = len(self.possible_words) + 1
        for guess in self.my_words:
            if guess in self.guesses:
                continue

            # print(guess)
            worst_case = 1
            for answer in WORDLE_ANSWERS:
                # Test the guess on this answer.
                values = [0, 0, 0, 0, 0]
                for i in range(5):
                    if guess[i] == answer[i]:
                        values[i] = STATUS_LETTER_CORRECT
                    elif guess[i] in answer:
                        values[i] = STATUS_LETTER_INCORRECT_POSITION
                    else:
                        values[i] = STATUS_LETTER_INCORRECT

                # Create a copy of our solver state, and recalculate words.
                new_solver = copy.deepcopy(self)
                new_solver.calculate_constraints(guess, values)
                new_solver.calculate_possible_words()

                if len(new_solver.possible_words) > worst_case:
                    worst_case = len(new_solver.possible_words)

            # print(worst_case)

            if worst_case == 1:
                self.guesses.append(guess)
                return guess

            if worst_case < best_worst_case_len:
                best_guess = guess
                best_worst_case_len = worst_case

            # print(best_guess, best_worst_case_len)
        
        self.guesses.append(best_guess)
        return best_guess

    def calculate_constraints(self, guess, status):

        """Calculate constraints based on status."""

        for i in range(5):
            letter = guess[i]
            if status[i] == STATUS_LETTER_CORRECT:
                # This letter was correct!
                self.constraints[i].solved_answer = letter
            elif status[i] == STATUS_LETTER_INCORRECT_POSITION:
                # This letter exists somewhere in the word, but not here.
                if letter in self.constraints[i].acceptable_chars:
                    # We originally thought the letter could have been here, 
                    # but now we know it cannot.
                    self.constraints[i].acceptable_chars.remove(letter)
                
                self.constraints[i].incorrect_chars.append(letter)

                for j in range(5):
                    if j == i:
                        continue

                    # If this letter already has the original latter marked as
                    # invalid, we don't want to mark it.
                    if letter in self.constraints[j].incorrect_chars:
                        continue

                    # If this letter already has the original letter marked as
                    # acceptable, we don't want to re-mark it.
                    if not letter in self.constraints[j].acceptable_chars:
                        self.constraints[j].acceptable_chars.append(letter)

                if letter not in self.must_contain_somewhere:
                    self.must_contain_somewhere.append(letter)
            else:
                # This letter cannot exist here.
                for j in range(5):
                    if letter in self.constraints[i].acceptable_chars:
                        # We originally thought the letter could have been here, 
                        # but now we know it cannot.
                        self.constraints[i].acceptable_chars.remove(letter)
                
                    self.constraints[i].incorrect_chars.append(letter)

    def check_guess_valid_constraints(self, guess):
        for c, g in zip(self.constraints, guess):
            # If we know the correct letter, check that this letter is correct.
            if c.solved_answer:
                if g != c.solved_answer:
                    # Remove this guess.
                    return False

            # If this letter cannot exist here, remove the guess.
            if g in c.incorrect_chars:
                return False

        return True

    def check_guess_valid(self, guess):
        # Check if the guess is valid, given our constraints.
        if not self.check_guess_valid_constraints(guess):
            return False

        for char in self.must_contain_somewhere:
            # Make sure the guess contains this char somewhere.
            if not char in guess:
                return False

        return True

    def calculate_possible_words(self):

        """Filter the current possible words using the constraints."""

        new_possible_words = []
        for guess in self.possible_words:
            if self.check_guess_valid(guess):
                new_possible_words.append(guess)

        self.possible_words = new_possible_words

    def __deepcopy__(self, memodict={}):

        """Speed improvement for deepcopy."""

        s = Solver()
        s.constraints = [self.constraints[i].dup() for i in range(5)]
        s.must_contain_somewhere = self.must_contain_somewhere[:]
        s.possible_words = self.possible_words[:]
        return s

# Load words.
load_words()

def play():
    g = Game()
    try:
        g.play()
    except KeyboardInterrupt:
        pass

def solver_play():
    s = Solver()
    g = Game()
    
    for i in range(7):
        guess = s.calculate_guess()
        print(s.must_contain_somewhere)
        print(f'Guess: {guess} ({len(s.possible_words)})')
        status = g.guess(guess)

        for i in range(5):
            if status[i] == STATUS_LETTER_CORRECT:
                print(f'\033[0;32m{guess[i].upper()}\033[m', end='')
            elif status[i] == STATUS_LETTER_INCORRECT_POSITION:
                print(f'\033[1;33m{guess[i].upper()}\033[m', end='')
            else:
                print(f'{guess[i].upper()}', end='')
        print()
        
        if status == [STATUS_LETTER_CORRECT] * 5:
            break

        s.calculate_constraints(guess, status)
        print()
    
    print(f'Correct Answer: {g.word}')

def solver_test():
    num_solved = 0
    total = len(WORDLE_ANSWERS)
    for word in WORDLE_ANSWERS:
        s = Solver()
        g = Game(word)

        solved = False
        for i in range(6):
            guess = s.calculate_guess()
            status = g.guess(guess)

            if status == [STATUS_LETTER_CORRECT] * 5:
                solved = True
                break

            s.calculate_constraints(guess, status)

        if solved:
            num_solved += 1

    print(f'Solved {num_solved}/{total}')
    
if __name__ == '__main__':
    # import cProfile
    # cProfile.run('solver_play()')
    solver_play()