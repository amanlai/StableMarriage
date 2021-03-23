# StableMarriage

Suppose there were boys and girls in a room and they wanted to dance with each other. Each boy has a list of girls that he wants to dance with and each girl has a list of boys that she wants to dance with. Is there a way to match them in such a way that no boy-girl pair who are not dance partners would want to become dance partners instead of their current arrangements? This was answered in the affirmative by Gale and Shapley in the seminal 1962 paper: *College Admissions and the Stability of Marriage.*

Gale and Shapley proved that if preferences are strict and no one has a person of the same sex on their preference list, then there exists a matching such that no boy-girl pair would ever want to break off from their respective matched dance partners in favor of each other. They proved this statement constructively using an algorithm later known as the Gale-Shapley algorithm.


### The Problem

* There are a certain number of boys and girls in a room.
* Everyone has strict preferences over people from the opposite sex. So boys have a list of girls whom he wants to dance with, ranking them from most desirable to least desirable, and girls have a list of boys whom she wants to dance with, ranking them from most desirable to least desirable. A girl is acceptable for a boy if she is on his preference list; similarly, a boy is acceptable for a girl if he is on her preference list.
* Everyone's preferences depend only on their own opinions; there is no jealousy (in economic terms, there are no *externalities*).
* No one is forced to dance with anyone who is not on their preference list.
* **A matching:** An outcome which tells everyone in the room who their dance partners are. Formally, a matching is a function that maps the set of boys and girls onto itself.
* **Stability:** Suppose a matching has been made but there is a boy and a girl who want to dance with each other rather than dance with the person the matching matched them up with. Then they are said to form a *blocking pair.* A stable matching happens if there are no *blocking pairs.*

### Gale-Shapley algorithm

Gale-Shapley algorithm is a constructive way to find a stable matching. It works as follows:

* **Step 1.** Each boy proposes to his first acceptable choice (if he has any names on his preference list). Each girl who receives an offer rejects all offers except the best acceptable proposal (according to her preference list), which she *holds* on to.

* **Step *k*.** Any boy who was rejected at step *k − 1* makes a new proposal to his most preferred girl on his list who has not yet rejected him. (If he ran through the names on his list, he makes no more proposals.) Each girl *holds* her most preferred acceptable proposal to date, and rejects the rest.

Algorithm terminates when there are no more rejections and each girl is matched with the boy she has been holding in the
last step. Any girl who has not been holding an offer or any boy who was rejected by all acceptable girls remains single.

*Note:* In the explanation above, we had boys propose for demonstration purposes, but of course, girls can propose too, and in that case, we would reach a stable matching as well.


### Interesting properties of the Gale-Shapley algorithm

* It finds the best outcome for the people on the proposing side and the worst outcome for the people on the receiving side.

* It is strategy-proof for the proposers, i.e. no proposer benefits by unilaterally submitting a false preference list. It is always in the best interest of the proposer to submit their true preference list.


## Random paths to stability

Gale-Shapley algorithm implies a centralized authority who can match men and women by collecting their preference lists and using them to output a stable matching. 

**Question:** Can a group of men and women reach a stable outcome if they match up in a decentralized way? In other words, if men and women date each other, break up, date another, break up, etc. out on their own, can they reach a stable matching eventually?

Roth and van de Vate (1990) answered this question in the affirmative. They proved that starting from any unstable matching, there exists a path to *a* stable matching. This result suggests that stable matchings are a natural converging point for two-sided matching problems. Note that we are not sure which stable matching will be reached in this decentralized setting, whereas in the Gale-Shapley algorithm, we are very certain which stable matching will be reached.


{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 1,
   "metadata": {},
   "outputs": [],
   "source": [
    "from StableMarriage import MarriageModel"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### Example 1:\n",
    "\n",
    "Let's first initialize a sample preference profile.\n",
    "\n",
    "`guyprefers` is the preference profile of boys and `galprefers` is the preference profile of girls. In each dictionary, the keys denote the person and the values denote the strict preference list of the person the key corresponds to.\n",
    "\n",
    "*N.B.* This preference profile was pulled from [Rosetta Code](http://rosettacode.org/wiki/Stable_marriage_problem#Python)."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "metadata": {},
   "outputs": [],
   "source": [
    "guyprefers = {\n",
    "    'abe':  ['abi', 'eve', 'cath', 'ivy', 'jan', 'dee', 'fay', 'bea', 'hope', 'gay'],\n",
    "    'bob':  ['cath', 'hope', 'abi', 'dee', 'eve', 'fay', 'bea', 'jan', 'ivy', 'gay'],\n",
    "    'col':  ['hope', 'eve', 'abi', 'dee', 'bea', 'fay', 'ivy', 'gay', 'cath', 'jan'],\n",
    "    'dan':  ['ivy', 'fay', 'dee', 'gay', 'hope', 'eve', 'jan', 'bea', 'cath', 'abi'],\n",
    "    'ed':   ['jan', 'dee', 'bea', 'cath', 'fay', 'eve', 'abi', 'ivy', 'hope', 'gay'],\n",
    "    'fred': ['bea', 'abi', 'dee', 'gay', 'eve', 'ivy', 'cath', 'jan', 'hope', 'fay'],\n",
    "    'gav':  ['gay', 'eve', 'ivy', 'bea', 'cath', 'abi', 'dee', 'hope', 'jan', 'fay'],\n",
    "    'hal':  ['abi', 'eve', 'hope', 'fay', 'ivy', 'cath', 'jan', 'bea', 'gay', 'dee'],\n",
    "    'ian':  ['hope', 'cath', 'dee', 'gay', 'bea', 'abi', 'fay', 'ivy', 'jan', 'eve'],\n",
    "    'jon':  ['abi', 'fay', 'jan', 'gay', 'eve', 'bea', 'dee', 'cath', 'ivy', 'hope']\n",
    "}\n",
    "\n",
    "galprefers = {\n",
    "    'abi':  ['bob', 'fred', 'jon', 'gav', 'ian', 'abe', 'dan', 'ed', 'col', 'hal'],\n",
    "    'bea':  ['bob', 'abe', 'col', 'fred', 'gav', 'dan', 'ian', 'ed', 'jon', 'hal'],\n",
    "    'cath': ['fred', 'bob', 'ed', 'gav', 'hal', 'col', 'ian', 'abe', 'dan', 'jon'],\n",
    "    'dee':  ['fred', 'jon', 'col', 'abe', 'ian', 'hal', 'gav', 'dan', 'bob', 'ed'],\n",
    "    'eve':  ['jon', 'hal', 'fred', 'dan', 'abe', 'gav', 'col', 'ed', 'ian', 'bob'],\n",
    "    'fay':  ['bob', 'abe', 'ed', 'ian', 'jon', 'dan', 'fred', 'gav', 'col', 'hal'],\n",
    "    'gay':  ['jon', 'gav', 'hal', 'fred', 'bob', 'abe', 'col', 'ed', 'dan', 'ian'],\n",
    "    'hope': ['gav', 'jon', 'bob', 'abe', 'ian', 'dan', 'hal', 'ed', 'col', 'fred'],\n",
    "    'ivy':  ['ian', 'col', 'hal', 'gav', 'fred', 'bob', 'abe', 'ed', 'jon', 'dan'],\n",
    "    'jan':  ['ed', 'hal', 'gav', 'abe', 'bob', 'jon', 'col', 'ian', 'fred', 'dan']\n",
    "}"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "metadata": {
    "scrolled": true
   },
   "outputs": [
    {
     "data": {
      "text/plain": [
       "{'dan': 'fay',\n",
       " 'col': 'dee',\n",
       " 'abe': 'ivy',\n",
       " 'jon': 'abi',\n",
       " 'bob': 'cath',\n",
       " 'hal': 'eve',\n",
       " 'ian': 'hope',\n",
       " 'ed': 'jan',\n",
       " 'fred': 'bea',\n",
       " 'gav': 'gay'}"
      ]
     },
     "execution_count": 3,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "model = MarriageModel(guyprefers, galprefers)\n",
    "mu = model.Deferred_Acceptance()\n",
    "mu"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "We can also print the number of steps it took to reach a final stable matching by setting `print_rounds=True`."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 4,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Success. The Gale-Shapley algorithm ran 5 rounds.\n"
     ]
    }
   ],
   "source": [
    "model.Deferred_Acceptance(print_rounds=True);"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "We can also print the tentative matchings of each step by setting `print_tentative_matchings=True`."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 5,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Tentative matching after Round 1:\n",
      "{'jon': 'abi', 'bob': 'cath', 'ian': 'hope', 'dan': 'ivy', 'ed': 'jan', 'fred': 'bea', 'gav': 'gay'}\n",
      "Tentative matching after Round 2:\n",
      "{'hal': 'eve', 'jon': 'abi', 'bob': 'cath', 'ian': 'hope', 'dan': 'ivy', 'ed': 'jan', 'fred': 'bea', 'gav': 'gay'}\n",
      "Tentative matching after Round 3:\n",
      "{'jon': 'abi', 'bob': 'cath', 'hal': 'eve', 'ian': 'hope', 'dan': 'ivy', 'ed': 'jan', 'fred': 'bea', 'gav': 'gay'}\n",
      "Tentative matching after Round 4:\n",
      "{'col': 'dee', 'abe': 'ivy', 'jon': 'abi', 'bob': 'cath', 'hal': 'eve', 'ian': 'hope', 'ed': 'jan', 'fred': 'bea', 'gav': 'gay'}\n"
     ]
    }
   ],
   "source": [
    "model.Deferred_Acceptance(print_tentative_matchings=True);"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "The algorithm can handle unmatched matches too, i.e. it can handle examples where someone will have to end up unmatched in a stable matching."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 6,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "{'abi': None,\n",
       " 'bob': 'cath',\n",
       " 'fred': 'bea',\n",
       " 'ed': 'jan',\n",
       " 'hal': 'eve',\n",
       " 'ian': 'hope',\n",
       " 'gav': 'gay',\n",
       " 'col': 'dee',\n",
       " 'jon': 'fay',\n",
       " 'abe': 'ivy',\n",
       " 'dan': None}"
      ]
     },
     "execution_count": 6,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "galprefers['abi'] = ['bob', 'fred']\n",
    "\n",
    "model = MarriageModel(guyprefers, galprefers)\n",
    "mu_2 = model.Deferred_Acceptance()\n",
    "mu_2"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "In the above example, Abi was matched to her 3rd best choice, Jon in the stable matching `mu` but if she somehow decides that she only want either Bob or Fred (her top 2 choices), she will end up unmatched."
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### Example 2:\n",
    "\n",
    "*N.B.* This example is adapted from Example 2.17 in the seminal book on stable matching theory: *Two-sided matching: A study in game-theoretic modeling and analysis* (Roth and Sotomayor, 1990).\n",
    "\n",
    "Similar to Example 1, `guyprefers` is the preference profile of guys and `galprefers` is the preference profile of gals. Each key denotes a person and each value denotes the preference profile of the person corresponding to its key."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 7,
   "metadata": {},
   "outputs": [],
   "source": [
    "guyprefers = {\n",
    "    'abe': ['abi', 'bea', 'cat', 'dee'],\n",
    "    'bob': ['bea', 'abi', 'dee', 'cat'],\n",
    "    'col': ['cat', 'dee', 'abi', 'bea'],\n",
    "    'dan': ['dee', 'cat', 'bea', 'abi']\n",
    "}\n",
    "\n",
    "galprefers = {\n",
    "    'abi': ['dan', 'col', 'bob', 'abe'],\n",
    "    'bea': ['col', 'dan', 'abe', 'bob'],\n",
    "    'cat': ['bob', 'abe', 'dan', 'col'],\n",
    "    'dee': ['abe', 'bob', 'col', 'dan']\n",
    "}"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "`MarriageModel()` is a class that has three main methods: `Deferred_Acceptance()`, `is_stable()` and `random_path_to_stability()`.\n",
    "\n",
    "An instance of `MarriageModel()` must be initialized with preference profiles. `Deferred_Acceptance()` treats the first preference profile as that of the proposing side and the second as that of the receiving side.\n",
    "\n",
    "For preference profiles `(galprefers, guyprefers)` (where gals propose and guys hold on to proposals), the outcome of the Gale-Shapley algorithm is `mu`:"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 8,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "{'abi': 'dan', 'bea': 'col', 'cat': 'bob', 'dee': 'abe'}"
      ]
     },
     "execution_count": 8,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "model2 = MarriageModel(galprefers, guyprefers)\n",
    "mu = model2.Deferred_Acceptance()\n",
    "mu"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "We can check if `mu` is stable or not with respect to the preference profiles at initialization."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 9,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "True"
      ]
     },
     "execution_count": 9,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "model2.is_stable(mu)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "However, if a matching is not stable, `is_stable()` throws out a blocking pair as follows:"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 10,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "('bea', 'dan')"
      ]
     },
     "execution_count": 10,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "unstable_matching = {'abi':'dan', 'bea':'bob', 'cat':'abe', 'dee':'col'}\n",
    "\n",
    "blocking_pair = model2.is_stable(unstable_matching)\n",
    "blocking_pair"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "We can use `random_path_to_stability()` to find a random stable matching (stable with respect to the preference profiles at initialization)."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 11,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "{'abi': 'dan', 'bea': 'col', 'cat': 'bob', 'dee': 'abe'}"
      ]
     },
     "execution_count": 11,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "some_stable_matching = model2.random_path_to_stability()\n",
    "some_stable_matching"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "We can also print out the number of iterations it took to reach a stable outcome."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 12,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "The algorithm ran 48 rounds to reach the following stable matching:\n",
      "{'abi': 'abe', 'dee': 'dan', 'bea': 'bob', 'cat': 'col'}\n"
     ]
    },
    {
     "data": {
      "text/plain": [
       "{'abi': 'abe', 'bea': 'bob', 'cat': 'col', 'dee': 'dan'}"
      ]
     },
     "execution_count": 12,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "another_stable_matching = model2.random_path_to_stability(print_rounds=True)\n",
    "another_stable_matching"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "We can also specify the number of paths to stability. For example, if `number_of_matchings=100`, 100 stable matchings will be found. The outcome will be a 2-tuple where the first element is a list of unique stable matchings and the second element is a list of frequencies where the *i*th frequency corresponds to the *i*th unique stable matching."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 13,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "([{'abi': 'abe', 'bea': 'bob', 'cat': 'col', 'dee': 'dan'},\n",
       "  {'abi': 'abe', 'bea': 'bob', 'cat': 'dan', 'dee': 'col'},\n",
       "  {'abi': 'bob', 'bea': 'abe', 'cat': 'col', 'dee': 'dan'},\n",
       "  {'abi': 'bob', 'bea': 'abe', 'cat': 'dan', 'dee': 'col'},\n",
       "  {'abi': 'bob', 'bea': 'dan', 'cat': 'abe', 'dee': 'col'},\n",
       "  {'abi': 'col', 'bea': 'abe', 'cat': 'dan', 'dee': 'bob'},\n",
       "  {'abi': 'col', 'bea': 'dan', 'cat': 'abe', 'dee': 'bob'},\n",
       "  {'abi': 'col', 'bea': 'dan', 'cat': 'bob', 'dee': 'abe'},\n",
       "  {'abi': 'dan', 'bea': 'col', 'cat': 'abe', 'dee': 'bob'},\n",
       "  {'abi': 'dan', 'bea': 'col', 'cat': 'bob', 'dee': 'abe'}],\n",
       " array([13, 10, 12,  5, 10,  3,  8, 10, 12, 17], dtype=int64))"
      ]
     },
     "execution_count": 13,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "lottery = model2.random_path_to_stability(number_of_matchings=100)\n",
    "lottery"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.7.7"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}
