#coding=utf-8

from __future__ import print_function
import argparse
import codecs
import numpy as np
import json
import requests


"""
Lab by Alexander Jakobsen KTH
"""


"""
This file is part of the computer assignments for the course DD1418/DD2418 Language engineering at KTH.
Created 2017 by Johan Boye and Patrik Jonell.
"""


"""
This module computes the minimum-cost alignment of two strings.
"""


"""
When printing the results, only print BREAKOFF characters per line.
"""
BREAKOFF = 60


def compute_backpointers(s0, s1, distance):
    """
    <p>Computes and returns the backpointer array (see Jurafsky and Martin, Fig 3.27)
    arising from the calculation of the minimal edit distance of two strings
    <code>s0</code> and <code>s1</code>.</p>

    <p>The backpointer array has three dimensions. The first two are the row and
    column indices of the table in Fig 3.27. The third dimension either has
    the value 0 (in which case the value is the row index of the cell the backpointer
    is pointing to), or the value 1 (the value is the column index). For example, if
    the backpointer from cell (5,5) is to cell (5,4), then
    <code>backptr[5][5][0]=5</code> and <code>backptr[5][5][1]=4</code>.</p>

    :param s0: The first string.
    :param s1: The second string.
    :return: The backpointer array.
    """
    if s0 == None or s1 == None:
        raise Exception('Both s0 and s1 have to be set')

    backptr = [[[0, 0] for y in range(len(s1)+1)] for x in range(len(s0)+1)]
    #backptr = np.zeros((2, len(s0)+1, len(s1)+1))
    # MY CODE  STARTS HERE

    i = len(s0)
    k = len(s1)
    curr = distance[i][k]
    #Nedan tar vi in distansmatrisen och räknar ut den optimala vägen mha backpointers
    #hur gör en detta mer elegant, select cases?
    while int(curr) != 0 and i != 0 and k != 0:
        diagonal = distance[i-1][k-1]
        up = distance[i-1][k]
        left = distance[i][k-1]
        #print(curr, left, diagonal, up, "curr_coordinates = ",backptr)
        if min(diagonal, up, left) == diagonal:
            print("moved diagonally")
            backptr[i][k][0] = i-1
            backptr[i][k][1] = k-1
            curr = diagonal
            i -= 1
            k -= 1
        elif min(diagonal, up, left) == up:
            print("moved up")
            backptr[i][k][0] = i
            backptr[i][k][1] = k-1
            curr = up
            i -= 1
        elif min(diagonal, up, left) == left:
            print("moved left")
            backptr[i][k][0] = i-1
            backptr[i][k][1] = k
            curr = left
            k -= 1
    for line in distance:
        print(line)
    for line in backptr:
        print(line)
    return backptr


"""
    #Here follows a failed attempt at solving the problem recusievely

    s = list(s1)
    t = list(s0)
    i = 0
    k = 0

    # here we have implemented a recursive method based on the recursive definition of the levenshtein distance

    for i in s:
        i = s.index(i)
        for k in t:
            k = t.index(k)
            if s[i] == t[k]:
                backptr[i][k][0] = i
                backptr[i][k][1] = k
            elif i == 0:
                i += 1
                backptr[i][k][0] = i
            elif k == 0:
                k += 1
                backptr[k][i][0] = k
            else :
                #backptr[i,k] = compute_backpointers[s[i-1],t[k-1]]
                #print(np.shape(backptr))
                #print(backptr[i-1][k])
                ipdb.set_trace()
                backptr[i-1][k] = compute_backpointers(s[i-1],t[k])
                backptr[i][k-1] = compute_backpointers(s[i],t[k-1])
"""
# MY CODE  ENDS HERE


# here follows an adaptation of the min edit distance algorithm from Jurafsky and Martin p33


def min_edit_distance(s0, s1):
    n = len(s0)
    m = len(s1)
    s0 = list(s0)
    s1 = list(s1)
    distance = np.zeros((n+1, m+1))

    distance[0:, 0] = range(0, n+1)
    distance[0, 0:] = range(0, m+1)

    for i in distance[1:, 0]:
        i = int(i)
        # print(i,distance)
        distance[i, 0] = distance[i-1, 0] + 1
    for j in distance[0, 1:]:
        j = int(j)
        # print(j,distance)
        distance[0, j] = distance[0, j-1] + 1
    for i in distance[1:, 0]:
        for j in distance[0, 1:]:
            i = int(i)
            j = int(j)
            distance[i, j] = min(
                distance[i-1, j]+1, distance[i-1, j-1]+subst_cost(s0[i-1], s1[j-1]), distance[i, j-1]+1)

    return distance


def subst_cost(c0, c1):
    """
    The cost of a substitution is 2 if the characters are different
    or 0 otherwise (when, in fact, there is no substitution).
    """
    return 0 if c0 == c1 else 2

    # MY CODE  STARTS HERE
# here we reapply the resursive method in order to caluclate the cost of the changes as seen by the backpointers


"""
def compute_levendist(s0, s1):

    s0 = np.array(list(s0))
    s1 = np.array(list(s1))

    # hur definierar jag denna array på en rad istället för 5?
    leven_dist = np.zeros((len(s0)+1, len(s1)+1))
    print(leven_dist)
    leven_dist[0][1:] = s0
    leven_dist[1:][0] = s1
    print(column_index)

    print(leven_dist)

"""


# MY CODE  ENDS HERE


def align(s0, s1, backptr):
    """
    <p>Finds the best alignment of two different strings <code>s0</code>
    and <code>s1</code>, given an array of backpointers.</p>

    <p>The alignment is made by padding the input strings with spaces. If, for
    instance, the strings are <code>around</code> and <code>rounded</code>,
    then the padded strings should be <code>around  </code> and
    <code> rounded</code>.</p>

    :param s0: The first string.
    :param s1: The second string.
    :param backptr: A three-dimensional matrix of backpointers, as returned by
    the <code>diff</code> method above.
    :return: An array containing exactly two strings. The first string (index 0
    in the array) contains the string <code>s0</code> padded with spaces
    as described above, the second string (index 1 in the array) contains
    the string <code>s1</code>ß padded with spaces.
    """

    """
    result = ['', '']
    i,j = len(s1), len(s0)
    while i > 0 or j > 0:
        if backptr[j][i][0] == i-1 and backptr[j][i][1] == j-1: # Substitution, step diagonal
            result[0] += s0[j-1]
            result[1] += s1[i-1]
            i,j = i-1, j-1
        if backptr[j][i][0] == i-1 and backptr[j][i][1] == j: # Deletion, step down
            result[0] += " "
            result[1] += s1[i-1]
            i -= 1
        if backptr[j][i][1] == j-1 and backptr[j][i][0] == i: # Insertion, step right
            result[0] += s0[j-1]
            result[1] += " "
            j -= 1

    return result
    """
    #this is the truth
    result = ['', '']
    i,j = len(s1), len(s0)
    while i > 0 or j > 0:
        print(i,j,backptr[j][i][:])
        if backptr[j][i][0] == j-1 and backptr[j][i][1] == i-1: # Substitution, step diagonal          
            result[1] += s0[i-1]
            result[0] += s1[j-1]
            i,j = i-1, j-1
            print("substitute",i,j,backptr[j][i][:])
        elif backptr[j][i][0] == j and backptr[j][i][1] == i-1 : # Deletion, step up
            result[1] += " "
            result[0] += s1[j-1]
            j -= 1
            print("delete",i,j,backptr[j][i][:])

        elif backptr[j][i][0] == j-1 and backptr[j][i][1] == i: # Insertion, step left
            result[1] += s0[i-1]
            result[0] += " "
            i -= 1
            print("insert",i,j,backptr[j][i][:])
        
        else:
            break

    for word in result:
        word = "".join(reversed(word))
        print(word)
    result = "".join(reversed(result))
    
    return result[::-1][::-1]
    
def print_alignment(s):
    """
    <p>Prints two aligned strings (= strings padded with spaces).
    Note that this printing method assumes that the padded strings
    are in the reverse order, compared to the original strings
    (because we are following backpointers from the end of the
    original strings).</p>

    :param s: An array of two equally long strings, representing
    the alignment of the two original strings.
    """
    if s[0] == None or s[1] == None:
        return None
    start_index = len(s[0]) - 1
    while start_index > 0:
        end_index = max(0, start_index - BREAKOFF + 1)
        print_list = ['', '', '']
        for i in range(start_index, end_index-1, -1):
            print_list[0] += s[0][i]
            print_list[1] += '|' if s[0][i] == s[1][i] else ' '
            print_list[2] += s[1][i]

        for x in print_list:
            print(x)
        start_index -= BREAKOFF


def main():
    """
    Parse command line arguments
    """
    parser = argparse.ArgumentParser(description='Aligner')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--file', '-f', type=str,
                       nargs=2, help='align two strings')
    group.add_argument('--string', '-s', type=str, nargs=2,
                       help='align the contents of two files')

    parser.add_argument('--check', action='store_true',
                        help='check if your alignment is correct')

    arguments = parser.parse_args()

    if arguments.file:
        f1, f2 = arguments.file
        with codecs.open(f1, 'r', 'utf-8') as f:
            s1 = f.read().replace('\n', '')
        with codecs.open(f2, 'r', 'utf-8') as f:
            s2 = f.read().replace('\n', '')

    elif arguments.string:
        s1, s2 = arguments.string

    if arguments.check:
        payload = json.dumps({
            's1': s1,
            's2': s2,
            'result': align(s1, s2, compute_backpointers(s1, s2))
        })
        response = requests.post(
            'https://language-engineering.herokuapp.com/correct',
            data=payload,
            headers={'content-type': 'application/json'}
        )
        response_data = response.json()
        if response_data['correct']:
            print_alignment(align(s1, s2, compute_backpointers(s1, s2)))
            print('Success! Your results are correct')
        else:
            print('Your results:\n')
            print_alignment(align(s1, s2, compute_backpointers(s1, s2)))
            print("The server's results\n")
            print_alignment(response_data['result'])
            print("Your results differ from the server's results")
    else:
        print_alignment(align(s1, s2, compute_backpointers(s1, s2)))


if __name__ == "__main__":
    #main()
    s0 = "is"
    s1 = "has"
    align(s0, s1, (compute_backpointers(s0, s1, min_edit_distance(s0, s1))))
