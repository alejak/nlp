import os
import argparse
import time
import string
import numpy as np
from halo import Halo
from sklearn.neighbors import NearestNeighbors
from collections import defaultdict


class RandomIndexing(object):
    # default self, filenames, dimension=2000, non_zero=100, non_zero_values=[-1, 1], left_window_size=3, right_window_size=3
    def __init__(self, filenames, dimension=30, non_zero=8, non_zero_values=[-1, 1], left_window_size=0, right_window_size=3):
        self.__sources = filenames
        self.__vocab = set()
        self.__dim = dimension
        self.__non_zero = non_zero
        self.__non_zero_values = non_zero_values
        self.__lws = left_window_size
        self.__rws = right_window_size
        self.__cv = None
        self.__rv = None


    def clean_line(self, line):
        # Remove punctuation and numerals, return cleaned line as list of words
        cleaned_line = line.translate(str.maketrans("", "", string.punctuation))
        cleaned_line = cleaned_line.translate(str.maketrans("", "", string.digits))
        return cleaned_line.strip().split()


    def text_gen(self):
        for fname in self.__sources:
            with open(fname, encoding='utf8', errors='ignore') as f:
                for line in f:
                    yield self.clean_line(line)


    def build_vocabulary(self):
        """
        Build vocabulary of words from the provided text files
        """
        # ✓
        for line in self.text_gen():
            for word in line:
                self.__vocab.add((word))

        self.write_vocabulary()


    @property
    def vocabulary_size(self):
        return len(self.__vocab)

    def generate_context(self, context):
        """
        Generate context vectors and shift context for next word
        """
        # ✓
        current = context.pop(self.__lws)

        for word in context:
            self.__cv[current] += self.__rv[word]
               
        if self.__lws >= 1:
            context.pop(0)
            context.insert(self.__lws-1, current)

        return context


    def create_word_vectors(self):
        """
        Create word embeddings using Random Indexing
        """
        self.__rv = defaultdict(lambda: 0)  # Random vectors {word: vector}
        self.__cv = defaultdict(int)  # Context vectors {word: vector}

        z_values = np.zeros(self.__dim - self.__non_zero)

        # Compute rv for each word with given amount of non-zero
        # and zero values. Randomise non-zero values for each word,
        # more computing but ensures random distribution.
        for word in self.__vocab:
            nz_values = np.random.choice(self.__non_zero_values, self.__non_zero)
            unique_rv = np.append(z_values, nz_values)
            np.random.shuffle(unique_rv)
            if word not in self.__rv:
                # while unique_rv in self.__rv.values():  # If rv not unique
                #     unique_rv = np.random.shuffle(unique_rv)

                self.__rv[word] = unique_rv
                self.__cv[word] = 0  # Initialise context vectors

        # Context for current word, accommodate for first left-empty context
        context = [None for i in range(self.__lws)]

        i = 0
        for line in self.text_gen():
            for next in line:
                if i < self.__rws:  # Fill context with first right window
                    context.append(next)
                    i += 1

                else:
                    context.append(next)
                    context = self.generate_context(context)

        for i in range(self.__rws):  # End of data, last contexts
            context = self.generate_context(context)

        pass


    def find_nearest(self, words, k=5, metric='cosine'):  # ‘cosine’, ‘euclidean’, ‘manhattan’,
        """
        Function returning k nearest neighbors for each word in `words`
        """
        # ✓
        res = [[] for word in words]  # Neighbours per given word
        sample = np.array(list(self.__cv.values()))  # Context vector dictionary to numpy array
        neigh = NearestNeighbors(n_neighbors=k, metric=metric).fit(sample)

        for j in range(len(words)):
            # Append each neighbour (word, distance) to res[j] for each given word
            distances, indices = neigh.kneighbors(np.reshape(self.__cv[words[j]], (1, -1)))
            for i in range(len(indices[0])):
                res[j].append((list(self.__cv.keys())[indices[0][i]], "{0:.2f}".format(distances[0][i])))

        return res


    def get_word_vector(self, word):
        """
        Returns a trained vector for the word
        """
        # ✓
        if self.__cv[word] == 0:
            return None
        else:
            return self.__cv[word]


    def vocab_exists(self):
        return os.path.exists('vocab.txt')


    def read_vocabulary(self):
        vocab_exists = self.vocab_exists()
        if vocab_exists:
            with open('vocab.txt') as f:
                for line in f:
                    self.__vocab.add(line.strip())
        self.__i2w = list(self.__vocab)
        return vocab_exists


    def write_vocabulary(self):
        with open('vocab.txt', 'w') as f:
            for w in self.__vocab:
                f.write('{}\n'.format(w))


    def train(self):
        """
        Main function call to train word embeddings
        """
        spinner = Halo(spinner='arrow3')

        if self.vocab_exists():
            spinner.start(text="Reading vocabulary...")
            start = time.time()
            ri.read_vocabulary()
            spinner.succeed(text="Read vocabulary in {}s. Size: {} words".format(round(time.time() - start, 2), ri.vocabulary_size))
        else:
            spinner.start(text="Building vocabulary...")
            start = time.time()
            ri.build_vocabulary()
            spinner.succeed(text="Built vocabulary in {}s. Size: {} words".format(round(time.time() - start, 2), ri.vocabulary_size))

        spinner.start(text="Creating vectors using random indexing...")
        start = time.time()
        ri.create_word_vectors()
        spinner.succeed("Created random indexing vectors in {}s.".format(round(time.time() - start, 2)))

        spinner.succeed(text="Execution is finished! Please enter words of interest (separated by space):")


    def train_and_persist(self):
        """
        Trains word embeddings and enters the interactive loop,
        where you can enter a word and get a list of k nearest neighours.
        """
        self.train()
        text = input('> ')
        while text != 'exit':
            text = text.split()
            neighbors = ri.find_nearest(text)

            for w, n in zip(text, neighbors):
                print("Neighbors for {}: {}".format(w, n))
            text = input('> ')



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Random Indexing word embeddings')
    parser.add_argument('-fv', '--force-vocabulary', action='store_true', help='regenerate vocabulary')
    parser.add_argument('-c', '--cleaning', action='store_true', default=False)
    parser.add_argument('-co', '--cleaned_output', default='cleaned_example.txt', help='Output file name for the cleaned text')
    args = parser.parse_args()

    if args.force_vocabulary:
        os.remove('vocab.txt')

    if args.cleaning:
        ri = RandomIndexing([os.path.join('data', 'example.txt')])
        with open(args.cleaned_output, 'w') as f:
            for part in ri.text_gen():
                f.write("{}\n".format(" ".join(part)))
    else:
        dir_name = "data"
        filenames = [os.path.join(dir_name, fn) for fn in os.listdir(dir_name)]

        ri = RandomIndexing(filenames)
        ri.train_and_persist()

    ''' dir_name = "data"
    filenames = [os.path.join(dir_name, fn) for fn in os.listdir(dir_name)]
    ri = RandomIndexing(filenames)

    text = str(input("For which word would you like the vector? "))
    print(type(text))
    vector = ri.get_word_vector(text)
    print(vector)
    '''