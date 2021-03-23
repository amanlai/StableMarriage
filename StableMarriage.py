import numpy as np

class MarriageModel:
    
    def __init__(self, proposers, receivers):
        # initialize 
        self.proposers = proposers
        self.receivers = receivers
        
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% HELPER FUNCTIONS %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

        
    # checks if the algorithm should continue to run or not.
    # it returns False in two cases: (i) every proposer is matched to someone 
    #                                (ii) the remaining unmatched proposers have reached the end of their preference lists
    # in all other cases, it returns True and lets the algorithm continuel
    @staticmethod
    def __rejection_exists(PrefLists, mu, recent_proposals):
        # there is no rejection if every proposer is held by a receiver
        if set(PrefLists) == set(mu):
            return False
        # there is no rejection if every proposer is at the end of their list
        elif sum(0 if recent_proposals[p] == PrefLists[p][-1] else 1 for p in set(PrefLists).difference(set(mu))) is 0:
            return False
        # if there is rejection, iterate
        else:
            return True
    
    
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    
    
    # sorts the matching according to the given keys if any keys are passed
    # and returns a list of tuples
    # it returns None if the passed key is neither 'proposers' nor 'receivers'
    @staticmethod
    def sort_matching(mu, keys=None):
        
        # sort the matches either by receivers or proposers
        if isinstance(mu, dict):
            # separate the singles from the married couples 
            # they will be appended at the end of mu
            singles = sorted([(str(k), 'unmatched') for k,v in mu.items() if v is None])
            mu = {k: v for k,v in mu.items() if v is not None}
            if isinstance(keys, str):
            
                if keys == 'receivers':
                    return_mu = sorted(mu.items(), key=lambda el: el[1])
                elif keys is None or keys == 'proposers':
                    return_mu = sorted(mu.items())
                else:
                    raise ValueError('Not a valid argument was passed in sort_by.')
            
            # keys can also accept a dict_keys() or a list
            else:
            # if mu is a dict, compare the keys and sort
                if keys is not None and not set(mu).issubset(keys):
                    return_mu = sorted((v,k) for k,v in mu.items())
                else:
                    return_mu = sorted(mu.items())
                
        else:
            singles = sorted([(str(k), 'unmatched') for k,v in mu if v is None])
            mu = np.array([(k,v) for k,v in mu if v is not None])
            # if it's a numpy array, then compare the first element of each tuple with the keys and sort
            if keys is not None and set(mu[:,0]).issubset(keys):
                return_mu = sorted(mu[:,[1,0]], key=lambda x: x[0])
            else:
                return_mu = sorted(mu, key=lambda x: x[0])
        
        # append the singles to mu
        return_mu += singles
        
        return return_mu
    
            
    
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    
    
    # returns a blocking pair if one is found and returns None if none found
    # For a given person (denoted 'man'), it goes through a list of people on the other side (denoted 'women_list')
    # and checks if any married 'woman' on 'women_list' has 'man' higher on their preference list (w_Pref[woman]) 
    # than their current married partner (married[woman]); or
    # if any single 'woman' on 'women_list' has 'man' on their preference list (w_Pref[woman]).
    @staticmethod
    def __is_blocking_pair(man, women_list, w_Pref, married):

        for woman in women_list:
            # if man is on woman's preference list,
            if man in w_Pref[woman]:
                # if woman is married,    
                if woman in married:
                    # check if the man is more preferred by the woman than her husband
                    # (since Pref is a Python list, it is ordered; lower index is more preferred to higher index)
                    if w_Pref[woman].index(man) < w_Pref[woman].index(married[woman]):
                        # if yes, add them to blocking_pairs list
                        return (man, woman)
                # if woman is single (which implies that man and woman are both on each other's list but both are single),
                else:
                    # then add them to the list
                    return (man, woman)

        # if the for-loop did not return anything so far, then there is no blocking pair here
        return None
    

    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    
    # checks if a single person can form a blocking pair with anyone
    def __blocking_pair_among_singles(self, Preferences, singles, married, **kwargs):

        # only proceed if any singles were passed
        if singles != []:
            
            # if randomize=True, then shuffle the list of singles
            if kwargs.get('randomize') is True:
                np.random.shuffle(singles)
            
            # if Preferences are not passed, use the initialized preferences
            if Preferences is None:
                Preferences = [self.proposers, self.receivers]
            
            # reverse the order of keys and values for married couples 
            # (this will be useful later on to pass to is_blocking_pair)
            married_reverse = {r: p for p, r in married.items()} 
            
            for person in singles:
                # if the person is someone whose preferences are collected in Preferences[0], then
                if person in Preferences[0]:
                    # pass their entire preference list to is_blocking_pair to see 
                    # if they can form a blocking pair with anyone
                    would_rather_match = Preferences[0][person].copy()
                    pref_lists = Preferences[1]
                    # since married is a subset of Preferences[0], we need to pass its reverse 
                    # to check through the spouses of those in Preferences[1]
                    marriages = married_reverse 
                    
                # the exact opposite of the above case
                elif person in Preferences[1]:
                    would_rather_match = Preferences[1][person].copy()
                    pref_lists = Preferences[0]
                    marriages = married
                
                # if person is in neither of the preference profiles, then print an error message and escape
                else:
                    raise ValueError('{} in the matching is not present on any preference lists.'.format(person))
                
                # randomize the order of the list of preferred receivers if randomize is True
                if kwargs.get('randomize') is True:
                    np.random.shuffle(would_rather_match)

                # look for a blocking pair,
                blocking_pair = self.__is_blocking_pair(person, would_rather_match, pref_lists, marriages)
                # and if found, return it
                if blocking_pair is not None:
                    return blocking_pair
                
        # if not, return False (indicating no single can form a blocking pair with anyone)
        return False

    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    
    # checks if there is a blocking pair among married couples
    def __blocking_pair_among_married_couples(self, Preferences, married, **kwargs):
        
        # if Preferences are not passed, use the initialized preferences
        if Preferences is None:
            Preferences = [self.proposers, self.receivers]
        
        # reverse the order of keys and values for married couples 
        # (this will be useful later on to pass to is_blocking_pair)
        married_reverse = {r: p for p, r in married.items()}
        
        # for each married couples,
        for spouse1, spouse2 in married.items():

            # check if spouse1 is in Preferences[0] 
            # (if spouse1 is not there, then the passed matching does not match the passed preferences, an error)
            if spouse1 in Preferences[0]:

                # if spouse2 is in spouse1's preference list,
                if spouse2 in Preferences[0][spouse1]:
                    # then those with lower index than spouse2 on spouse1's list are more preferred for spouse1
                    better_than_partner = Preferences[0][spouse1][ : Preferences[0][spouse1].index(spouse2)].copy()

                # otherwise, the matching does not correspond to the passed preference lists
                else:
                    raise ValueError("Error: {}, who is matched to {} in the matching, is not on {}'s preference list."
                          .format(spouse2, spouse1, spouse1))

                # randomize the order of the list of preferred women if randomize is True
                if kwargs.get('randomize') is True:
                    np.random.shuffle(better_than_partner)

                # look for a blocking pair,
                blocking_pair = self.__is_blocking_pair(spouse1, better_than_partner, Preferences[1], married_reverse)
                # and if found, pass it along
                if blocking_pair is not None:
                    return blocking_pair


            # if spouse1 is neither proposer nor a receiver, print an error message and end the check
            else:
                raise ValueError('{} in the matching is on a preference lists of the proposing side when they should be on the receiving side.'.format(spouse1))
        
        # if no blocking pair is found (implied by the function reaching this point), 
        # return False to indicate that no married person can for a blocking pair with anyone
        return False

    
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% DEFERRED ACCEPTANCE %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    
    def Deferred_Acceptance(self, **kwargs):
        """
        A method that implements Gale and Shapley's Deferred Acceptance algorithm using the preference profiles 
        (Python dictionaries) passed into class instance initialization, where the first dictionary is the preference 
        profile of the proposing side and the second is that of the proposal receiving side. 
        Both preference profiles must be a Python dictionary where the keys denote the agents and the values denote 
        their preference order. Note that a preference order can only be of type list, int or str. If it is a list, then 
        lower index corresponds to higher preference.
        
        
        (Optional) key-word arguments: 
        print_rounds: If True, prints the number of steps it took to reach the final outcome.
        print_tentative_matchings: If True, prints all tentative matchings made after each step.
        
        Returns a dictionary where: 
        - For married couples: the keys correspond to the proposers and 
                               the values correspond to the receivers
        - For singles: the keys are the names of single people and the values are None
        """
        
        
        P_m = self.proposers.copy()
        P_w = self.receivers.copy()
        
        
        if P_m is None or P_w is None:
            print('No preferences are passed. Please create the MarriageModel instance with preferences.')
            return None
        
        
        # run through the passed dictionaries and see if it satisfies the required format.
        # if str or int is passed for value, change the type to list, if it's a list do nothing
        # and raise an error if any other type of data is passed as a value to a dictionary
        for k,v in P_m.items():
            # convert each proposer's preference list to a Python list if it is a singleton
            if isinstance(v, (str, int)):
                P_m.update({k:[v]})
            # if preference list is a Python list, no problem, continue
            elif isinstance(v, list):
                continue
            # in all other cases, stop the algorithm and raise an error message.
            else:
                raise ValueError("Proposer {}'s preference list is not a valid list.".format(k))
        
        # same job for the receivers
        for k,v in P_w.items():
            # convert each receiver's preference list to a Python list if it is a singleton
            if isinstance(v, (str, int)):
                P_w.update({k:[v]})
            # if preference list is a Python list, no problem, continue
            elif isinstance(v, list):
                continue
            # in all other cases, stop the algorithm and raise an error message.
            else:
                raise ValueError("Receiver {}'s preference list is not a valid list.".format(k))


        # counter for the number of rounds
        itr = 1
        
        
        # the first step of the algorithm
        # (i)   every proposer 'proposes' to their first choice; these proposals are collected (in dictionary mu)
        # (ii)  make a list of proposals for each receiver who received a proposal (in dictionary proposals).
        # (iii) each receiver holds onto the best among the received proposals (in dictionary mu_r)
        # (iv)  reverse mu_r so that the keys are the proposers and the values are the receivers (in dictionary mu);
        #       this will require updating the dictionary with the rejected proposers (who don't exist in mu_r)
        # this general framework is repeated in each step until convergence
        
        # (i)
        mu = {}
        for p,Pref_list in P_m.items():
            # every proposer proposes to their first choice
            pointed = Pref_list[0]
            # if the proposee is not present in the problem, we continue the problem with the next best option
            if pointed not in P_w:
                raise ValueError("Proposer {}'s preference list includes {}, who is not present in this problem."
                                 .format(p, pointed))
            elif isinstance(pointed, list):
                raise TypeError("Preference lists must be strict. {} in {}'s preference list implies that {} is indifferent between them.".format(pointed, p, p))
            # save each proposal here
            mu.update({p: pointed})
        
        # most recent proposal for every proposer (this will come in handy in the next step)
        recent_proposals = mu.copy()
        
        # (ii) make a proposal list for everyone who received a proposal
        proposals = {}
        for p, r in mu.items():
            proposals.setdefault(r, []).append(p)
        
        # (iii) every receiver keeps the best proposal according to their preferences and reject all others
        mu_r = {r: next((p for p in P_w[r] if p in proposers), None) for (r, proposers) in proposals.items()}
        
        # (iv) reverse the receiver-proposer mapping to fit it into the general framework
        mu = {}
        for r,p in mu_r.items():
            # if a receiver receives proposals only from unacceptable proposers, we leave it as is.
            if p is None:
                mu.update({r:p})
            # otherwise, we reverse the receiver-proposer mapping into a proposer-receiver dictionary
            else:
                mu.update({p:r})
        
        
        # iterate while there exist rejections
        rejections_exist = True
        while rejections_exist:
            
            # if print_tentative_matchings argument is passed, print the tentative matching so far.
            if rejections_exist and kwargs.get('print_tentative_matchings') is True:
                print('Tentative matching after Round {}:'.format(itr))
                print(mu)

            new_proposals = {}
            # iterate over every proposer who is rejected from their most recent proposal 
            for p in set(P_m).difference(set(mu)):
            
                # only consider those who are not at the end of their list
                if recent_proposals[p] != P_m[p][-1]:
                
                    # (i) each such proposer proposes to their next option on their preference list
                    pointed = P_m[p][P_m[p].index(recent_proposals[p])+1]
                    
                    # if that option is not someone who is present in this problem, raise an error and exit the algorithm
                    if pointed not in P_w:
                        raise ValueError("Proposer {}'s preference list includes {}, who is not present in this problem."
                                         .format(p, pointed))
                        
                    elif isinstance(pointed, list):
                        raise ValueError("The preference lists must be strict. {} in {}'s preference list implies {} is indifferent between them.".format(pointed, p, p))
                    
                    # add the proposal to the new set of proposals
                    new_proposals.update({p: pointed})
                        
            # update the most recent proposals list with the proposals of those who proposed above
            # (this way we can track where each proposer is on their preference list)
            recent_proposals.update(new_proposals)
            
            
            # (ii-a) make a proposal list for everyone who received a new proposal above
            proposals = {}
            for p, r in new_proposals.items():
                proposals.setdefault(r, []).append(p)
            
            
            # (ii-b) combine the new and holding proposals for each receiver
            tentative_mu = {}
            for d in (proposals, mu_r): # we iterate over the past and present proposals
                for r, p in d.items():
                    # if a receiver was holding an offer, extend the list
                    if isinstance(p, list):
                        tentative_mu.setdefault(r, []).extend(p)
                    # if a receiver wasn't holding any offers, open a new list
                    else:
                        tentative_mu.setdefault(r, []).append(p)
            
            
            # (iii) every receiver keeps the best proposal according to their preferences and reject all others
            mu_r = {r: next((p for p in P_w[r] if p in proposers), None) for (r, proposers) in tentative_mu.items()}
            
                        
            # (iv) reverse the receiver-proposer mapping to fit it into the general framework
            #      so that we don't lose unmatched receivers when updating mu
            mu = {}
            for r,p in mu_r.items():
                # if a receiver receives proposals only from unacceptable proposers, we leave it as is.
                if p is None:
                    mu.update({r:p})
                # otherwise, we reverse the receiver-proposer mapping into a proposer-receiver dictionary
                else:
                    mu.update({p:r})
                    
                    
            # check if there were any rejections in this round
            rejections_exist = self.__rejection_exists(P_m, mu, recent_proposals)

            itr +=1
        
        
        # denote the proposers who were left unmatched as being matched to None
        unmatched = {p: None for p in set(P_m).difference(set(mu))}
        mu.update(unmatched)
        # denote the receivers who were left unmatched as being matched to None
        unmatched = {r: None for r in set(P_w).difference(set(mu.values()))}
        mu.update(unmatched)
        
        # print rounds if print_rounds = True, else don't
        if kwargs.get('print_rounds') is True:
            print('Success. The Gale-Shapley algorithm ran {} rounds.'.format(itr))
        

        return mu
    
    
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    
    def is_stable(self, mu, preferences=None, married_and_singles_lists=None):
        
        """
        Evaluates whether a passed matching mu is stable with respect to the preference profile passed at class instantiation
        (unless another optional preferences are passed, in which case, it evaluates according to that.)
        
        Input:
        
        mu:  a matching; a Python dictionary in which keys correspond to proposers and values correspond to receivers
        
        Optional input:
        
        preferences: an optional 2-tuple of Python dictionaries denoting preference lists of each agent
        married_and_singles_lists: an optional 2-tuple where the first element is a Python dictionary of married couples 
                                   (in which the keys correspond to proposers and the values correspond to receivers) and
                                   the second element is a list of single agents
        
        Output: It returns either True, a blocking pair or an Error message.
        - True: if input mu has no blocking pair with respect to Preferences
        - A blocking pair if input mu has a blocking pair with respect to Preferences
        - Error message if the agents in mu are incompatible with the agents in Preferences 
          (e.g. the proposers in mu do not match the the proposers in Preferences, i.e. Preferences[0])
        """
        
        # if this argument is not passed, extract 'married' and 'singles' from the passed mu
        if married_and_singles_lists is None:
            # and do not randomize
            randomize = False
            married = {k:v for k,v in mu.items() if v is not None}
            singles = [person for person, match in mu.items() if match is None]

        else:
            # but if it's passed, since it's a tuple (married, singles), copy accordingly
            # (also prepare to randomize everything as usage of this tuple implies that this function is used 
            # in random_path_to_stability in its randomization process)
            randomize = True
            married = married_and_singles_lists[0]
            singles = married_and_singles_lists[1]



        # if mu is a matching, continue,
        if len(set(married.values())) is len(married.values()):
            
            # make a list of functions that will search whether couples or singles can form a blocking pair with anyone
            find_blocking_pair = [lambda: self.__blocking_pair_among_married_couples(preferences, married, 
                                                                                     randomize=randomize), 
                                  lambda: self.__blocking_pair_among_singles(preferences, singles, married, 
                                                                             randomize=randomize)]
            
            # if married_and_singles_lists != None, this means this function is being used to 
            # in random_path_to_stability, so we randomize whether to check through the singles or the couples first
            if randomize:
                np.random.shuffle(find_blocking_pair)
            
            # now, iterate over the functions,
            for func in find_blocking_pair:
                # and check if any blocking pair exists,
                blocking_pair = func()
                # if blocking pair is found or if there was an error, pass that along, otherwise just continue
                if blocking_pair is not False:
                    return blocking_pair

            # if the above loop did not find a blocking pair (implied by not stopping then), return True 
            # (meaning the passed matching mu is stable)
            return True


        # if mu is not a matching,
        else:
            # find someone who is matched to multiple partners
            polygamous = next(woman for woman in mu.values() if list(mu.values()).count(woman) > 1)
            # find at least two of their partners,
            husbands = [k for k,v in mu.items() if v is polygamous][:2]
            # and print an error message        
            raise ValueError('This is not a matching. {} is matched with both {} and {} at the same time.'
                  .format(polygamous, husbands[0], husbands[1]))

    
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    
    def random_path_to_stability(self, number_of_matchings=1, **kwargs):
        
        """
        A method that finds a stable matching with respect to the preference profile (passed at class instance 
        initialization) by randomly finding and matching blocking pairs with one another. 
        (It is guaranteed to converge due to a result in Roth and van de Vate (1990)).
        
        Input:
        
        number_of_matchings: Accepts a positive integer (otherwise raises an error). Default is 1.
                             The user can select the number of matchings the algorithm may find.
                             It may potentially find all stable matchings if run enough times.
        
        Optional input:
        
        print_rounds: If True, prints the number of rounds it took to reach a stable matching in each iteration.
        
        Output:
        
        Returns a lottery of stable matchings.
        """
        
        # will need to randomize the person doing the 'proposing'
        preferences = [self.proposers, self.receivers] # will use the preference lists passed at initialization
        output = [] # this list will collect all matchings
        
        # we need to find number_of_matchings number of matchings, 
        for i in range(number_of_matchings):
            
            # first let each person start out as single
            # the matches made (as well as those who remain unmatched) in each round of the while loop 
            # as well as the final matching will be saved in mu
            mu = {person: None for person in list(preferences[0])+list(preferences[1])}
            
            rounds = 0 # this counts the number of iterations it takes to reach a stable matching 
                       # (i.e. the number of iterations it takes to exit the while-loop below)
            
            while True:
                
                rounds += 1
                # randomly choose the side whose preferences will be the primary point of reference in each round,
                np.random.shuffle(preferences)
                # copy the married couples so far in mu into married
                married = {k:v for k,v in mu.items() if v is not None}
                # copy the singles so far in mu into singles
                singles = [k for k,v in mu.items() if v is None]
                # and check if the keys of the married couples match the keys of preferences[0]
                # (since is_stable loops through preferences[0] for married couples, 
                # it is essential that married is a subset of preferences[0]
                if married != {} and set(married).issubset(set(preferences[0])) is False:
                    # if they do not match, reverse keys and values 
                    # so that married is a subset of preferences[0]
                    married = {v:k for k,v in married.items()}
                    mu = married.copy()
                    # do not have to reverse single
                    mu.update({k:None for k in singles})
                
                # check if there is blocking pair in mu. is_stable can return a blocking pair or True
                # (note that is_stable will never return None since at each round, mu that is passed 
                # into it is guaranteed to be a matching)
                blocking_pair = self.is_stable(mu, preferences, (married, singles))
                
                
                # if blocking_pair returns True, it means mu is stable, so we exit the loop and mu is the final matching
                if blocking_pair is True:
                    # if print_rounds is True then print the number of rounds it took to reach a stable matching
                    if kwargs.get('print_rounds') is True:
                        print('The algorithm ran {} rounds to reach the following stable matching:'.format(rounds))
                        print(mu)
                    break
                # if it returns a blocking pair
                else:
                    # blocking_pair is a tuple and if its first element is not someone whose preferences  
                    # are represented in preferences[0], then it means that it was reversed during 
                    # randomization in is_stable, so we reverse it back
                    # (blocking_pair[0] must also be mu, but that follows if it is in preferences[0], so the
                    # reversal below is essential as it normalizes the way we keep track of each match made so far)
                    if blocking_pair[0] not in preferences[0]:
                        blocking_pair = (blocking_pair[1], blocking_pair[0])
                    
                    # if blocking_pair[0] had a partner in mu,
                    if mu[blocking_pair[0]] is not None:
                        # break them up and make blocking_pair[0]'s partner single
                        mu.update({mu[blocking_pair[0]]: None})
                    
                    # check if blocking_pair[1] had a partner in mu,
                    jilted_proposer = next((p for p, r in mu.items() if r is blocking_pair[1]), None)
                    # and if there was a partner under mu,
                    if jilted_proposer is not None:
                        # break them up and make blocking_pair[1]'s partner single
                        mu.update({jilted_proposer: None})
                    # if blocking_pair[1] did not have a partner, i.e. single, delete blocking_pair[1] from mu
                    # (note that singles are matched to None in mu)
                    else:
                        mu.pop(blocking_pair[1])
                    
                    # finally match the blocking_pair with one another
                    mu.update({blocking_pair[0]:blocking_pair[1]})
            
            # whenever the while loop breaks, it means that mu that was continuously updated in it is a stable matching,
            # so append it to output
            output.append(mu)   # output is a list of dictionaries
        
        
        # the proposers will serve as keys when sorting the matches
        keys = list(self.proposers)
        # and sort every matching in output in the alphabetical order of the saved keys
        # output is now a list of list of tuples (it was a list of dictionaries before)
        # note that there is no proposer-receiver here since the matches are made randomly; 
        # hence there is no need for a dictionary
        output = [self.sort_matching(mu, keys) for mu in output]
        # find the list of unique matchings (i.e. a list of tuples)
        # and count the number of times each unique matching is in output
        self.support, self.frequencies = np.unique(output, axis=0, return_counts=True)
        
        self.support = [{match[0]:match[1] for match in matching} for matching in self.support]
        
        
        # if there is only one matching, then return a list of tuples (i.e. a matching)
        if number_of_matchings is 1:
            return {match[0]:match[1] for match in output[0]}
        # but if there are multiple, return a list of list of tuples
        else:
            return self.support, self.frequencies
