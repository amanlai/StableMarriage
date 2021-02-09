import numpy as np

class MarriageModel:
    
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
    
    
    # prints out the matching in two rows where each column corresponds to a match
    # the first row prints out the proposers and the second row prints out the receivers
    # the end result should look like an Excel table
    def __print_matching(self, mu, **kwargs):
        
        # sort the matching using sort_matching method 
        # (the input mu is a dictionary and the output mu is a list of tuples)
        mu = self.sort_matching(mu, kwargs.get('sort_by'))
        
        # if a value was passed to sort_by and it is neither 'proposers' nor 'receivers' then return None
        if mu is None:
            raise ValueError('There is no matching to print.')
        
        else:
        
            proposers = ''
            matches = ''
            for k, v in mu:
                # each column is separated by |
                proposers += '| '
                matches += '| '
                # measure the width of each column
                max_len = max(len(str(k)), len(str(v)) if v else 1)
                # and center the proposers and receivers in each column
                proposers += str(k).center(max_len) + ' '
                matches += (str(v).center(max_len) if v else ' '*max_len) + ' '

            # final | to serve as a border for the table
            proposers += '|'
            matches += '|'

            # reserve the option of not printing the proposers, in case there may be a need to print multiple matchings
            if kwargs.get('no_proposers') is None or kwargs.get('no_proposers') is not True:
                print('-'*len(matches))
                print(proposers)
            # if end kwarg is passed, separate the proposers row with the receivers row by --- and use the ender 
            if kwargs.get('end') is not None:
                print('-'*len(matches))
                print(matches, end=kwargs.get('end'))
            # if no end kwarg is passed, then print the 'matches' row and print a separator from a new row
            else:
                print(matches)
                print('-'*len(matches))
            
    
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
    
    def Deferred_Acceptance(self, proposers, receivers, **kwargs):
        """
        A method that implements Gale and Shapley's Deferred Acceptance algorithm using the preference profiles 
        (Python dictionaries) passed into class instance initialization, where the first dictionary is the preference 
        profile of the proposing side and the second is that of the proposal receiving side. 
        Both preference profiles must be a Python dictionary where the keys denote the agents and the values denote 
        their preference order. Note that a preference order can only be of type list, int or str. If it is a list, then 
        lower index corresponds to higher preference.
        
        Input:
        Preference_profile: Can be either a 2-tuple of Python dictionaries (indicating preference lists) or None.
                            If passed, it override the preference profile passed at initialization.
        
        
        (Optional) key-word arguments: 
        print_rounds: If True, prints the number of steps it took to reach the final outcome.
        print_tentative_matchings: If True, prints all tentative matchings made after each step.
        sort_by: 'proposers' or 'receivers'. Sorts the final outcome according to either the proposers or the receivers.
                 Maybe useful when printing a matching.
        print_matching: If True, prints the final matching.
        
        Returns a dictionary where: 
        - For married couples: the keys correspond to the proposers and 
                               the values correspond to the receivers
        - For singles: the keys are the names of single people and the values are None
        """
        
        # initialize 
        self.proposers = proposers
        self.receivers = receivers
        
        P_m = proposers.copy()
        P_w = receivers.copy()
        
        
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
                # sort_by either header or match
                sorting = kwargs.get('sort_by')
                self.__print_matching(mu, sort_by=sorting)

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
        
        # print the final matching if print_matching = True, else don't
        if kwargs.get('print_matching') is True:
            sorting = kwargs.get('sort_by')
            self.__print_matching(mu, sort_by=sorting)

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
        (It is guarenteed to converge due to a result in Roth and van de Vate (1990)).
        
        Input:
        
        number_of_matchings: Accepts a positive integer (otherwise raises an error). Default is 1.
                             The user can select the number of matchings the algorithm may find.
                             It may potentially find all stable matchings if run enough times.

        Optional input:
        
        print_rounds: If True, prints the number of rounds it took to reach a stable matching in each iteration.
        print_unique_matchings: If True, prints the unique stable matchings among number_of_matchings number of matchings,
                                along with the number of times each unique matching appeared in the entire set.
                                
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
                        print('The algorithm ran {} rounds.'.format(rounds))
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
        
        
        if kwargs.get('print_unique_matchings') is True:
            # if there are multiple matchings, then print the first element of each tuple in the first matching
            # and skip it for all matchings after that 
            # (because of the sorting done above, in each matching (i.e. list), the first element of the tuples match, 
            #  thus, it would be redundant to print it again after the first one)
            for idx, matching in enumerate(self.support):
                if idx is not 0:
                    need_to_print_proposers = True
                else:
                    need_to_print_proposers = False
                # print each 
                self.__print_matching(matching, no_proposers=need_to_print_proposers, sort_by = keys, end = ' ')
                print('({})'.format(idx+1))
            
            # print the number of times each matching appears as well
            for idx in range(len(self.support)):
                print('({}) appeared {},'.format(idx+1, self.frequencies[idx]), end=' ')
            print('times each.')
        
        
        # if there is only one matching, then return a list of tuples (i.e. a matching)
        if number_of_matchings is 1:
            return output[0]
        # but if there are multiple, return a list of list of tuples
        else:
            return (self.support, self.frequencies)
    
    
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    
    # derives a random matching from a given array of matchings
    # (i)   initialize a matrix of zeros (which will be filled up with probabilities)
    # (ii)  count the frequency of each match
    # (iii) assign the frequency of a given match to a cell in random_matching that corresponds to it
    def lottery_to_random_matching(self, lottery=None):
        
        """
        Input:
        
        (support, frequencies): a tuple of a numpy array and a list. The first dimension of the numpy array and the length 
                                of the list should match
        
        Returns:
        a random matching: a Python dictionary of rows, columns and random_matching where:
                           rows / columns: Python dictionaries assigns a row / column number to proposers / receivers, 
                                           respectively
                           random_matching: A 2D numpy array of probability matrix
        """
        
        if lottery is None:
            frequencies = self.frequencies
            matches = self.support.copy()
            
        else:
            frequencies = lottery[1]
            matches = lottery[0]
        
        # find the number of passed matchings
        # since the idea is to divide the number of matches by the number of matchings 
        # to find the probability that a pair is matched, it will be useful later on
        size = np.sum(frequencies)
        
        # create a dictionary where the keys are the names of the agents and the values are the row/column indices 
        # on random_matching that correspond to that agent 
        rows = dict(zip(self.proposers, range(len(self.proposers))))
        columns = dict(zip(self.receivers, range(len(self.receivers))))
        
        # if anyone is unmatched in at all, 
        num_unmatched = len(matches[matches=='unmatched'])
        if num_unmatched > 0:
            # add one more row and one more column to collect the probability of being unmatched
            rows.update({'unmatched':len(self.proposers)})
            columns.update({'unmatched':len(self.receivers)})
        
        # initialize an empty random matching
        # this object will be iteratively filled, first for unmatched people and then for married people
        random_matching = np.zeros((len(rows), len(columns)))
        
        # separate unmatched agents from matched agents, so that it becomes possible to iterate over them separately
        if num_unmatched > 0:
            # select those who got matched to None as a proposer 
            # and select those who got matched to None as a receiver (this is only possible at random_path_to_stability)
            # and concatenate the two arrays
            # since everyone in 'unmatched' is matched to None, there is no need to keep None in there,
            # so only the agents names are selected
            # it only suffices to look through the first matching, as anyone who is unmatched in one stable matching is 
            # always unmatched in any other stable matching
            unmatched = np.concatenate((matches[0][matches[0,:,1]=='unmatched'][:,0], 
                                        matches[0][matches[0,:,0]=='unmatched'][:,1]))
            
            for person in unmatched:
                # if an agent is a proposer, then add their probability 
                # (calculated by dividing its number of matches with the number of matchings)
                # to a cell where the row corresponds to the agent and the column corresponds to 'unmatched'
                if person in self.proposers:
                    random_matching[rows[person], columns['unmatched']] = 1
                
                # if an agent is a receiver, then add their probability to a cell where column that corresponds 
                # to the agent and the row corresponds to 'unmatched'
                elif person in self.receivers:
                    random_matching[rows['unmatched'], columns[person]] = 1
                
                # if the agent is neither proposer nor a receiver, then print an error message and exit
                else:
                    raise ValueError('Agents in the matching and preference lists do not match.')
            
            
            # finally, reassign the matches with no 'None' in them back to 'matches'
            # and keep the initial 3D nature of matches
            matches = matches[(matches[:,:,0]!='unmatched')&(matches[:,:,1]!='unmatched')].reshape(3,-1,2)
            
                
        for idx, matching in enumerate(matches):
            # for each matching, assign its probability
            # to a cell in random_matching where the row corresponds to the first agent (i.e. proposer) and 
            # the column corresponds to the second agent (i.e. receiver)
            for match in matching:
                try:
                    random_matching[rows[match[0]],
                                    columns[match[1]]] += frequencies[idx] / size
                # this exception is raised if 'None' is in the iteration 
                # (who is not an agent but just a filler to make the numpy arrays match) so we skip them
                except KeyError:
                    continue
        
        # collect row names, column names and the numpy 2D array of probabilities into a dictionary
        random_matching_dict = {'rows': rows, 'columns': columns, 'random_matching': random_matching}
                    
        return random_matching_dict
    




###################################################################################################################
###################################################################################################################
###################################################################################################################
###################################################################################################################

class MarriageModelWithIndifferences(MarriageModel):
    
    # class initialization
    def __init__(self, proposers=None, receivers=None):
        # 'proposers' and 'receivers' must be Python dictionaries
        self.proposers = proposers
        self.receivers = receivers
        
    
    # a function that creates a single iterable from an iterable that includes other iterables in it
    # e.g. a list that includes other lists in it may be "flattened" to a list of non-iterable elements
    # for every element in a given list, if it's an iterable (and not a string), call flatten on it to dig deeper 
    # if not, yield it to a generator
    from collections.abc import Iterable
    def __flatten(self, lst):
        
        for el in lst:
            if isinstance(el, self.Iterable) and not isinstance(el, (str, bytes)):
                yield from self.__flatten(el)
            else:
                yield el
                
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    
    # given a non-strict preference list, 
    def __strict_preference_list(self, preferences, priority_order):
                       # re-order inside each indifference tiers (which is indicated by a list inside the preference list)
        strict_list = [priority_order[np.isin(priority_order, pref_tier)] if isinstance(pref_tier, list) 
                       else pref_tier 
                       for pref_tier in preferences]
        # and finally create a single strict preference list
        return list(self.__flatten(strict_list))
    
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    
    # a function that derives a random matching from a given array of matchings
    # (i)   initialize a matrix of zeros (which will be filled up with probabilities)
    # (ii)  count the frequency of each match
    # (iii) assign the frequency of a given match to a cell in random_matching that corresponds to it
    def to_random_matching(self, matchings):
        
        """
        Input:
        
        matchings: a numpy array of size number_of_matchings x number of matches_per_matching x 2
        
        Returns:
        2-tuple: a dictionary of rows, columns and random_matching where:
                 rows / columns: Python dictionaries assigns a row / column number to proposers / receivers, respectively
                 random_matching: A 2D numpy array of probability matrix
        """
        
        # find the number of passed matchings
        # since the idea is to divide the number of matches by the number of matchings 
        # to find the probability that a pair is matched, it will be useful later on
        size = len(matchings)
        
        # create a dictionary where the keys are the names of the agents and the values are the row/column indices 
        # on random_matching that correspond to that agent 
        rows = dict(zip(self.proposers, range(len(self.proposers))))
        columns = dict(zip(self.receivers, range(len(self.receivers))))
        
        # if anyone is unmatched in at all, 
        num_unmatched = len(matchings[matchings=='unmatched'])
        if num_unmatched > 0:
            # add one more row and one more column to collect the probability of being unmatched
            rows.update({'unmatched':len(self.proposers)})
            columns.update({'unmatched':len(self.receivers)})
        
        # initialize an empty random matching
        random_matching = np.zeros((len(rows), len(columns)))
        # to construct a random matching, only the matches are needed, 
        # so reshape 'matchings' (it was of dimensions len(matchings) x len(matching[0]) x 2) 
        # to a 2D matrix where each row is a match that occurs in matchings
        matches = matchings.reshape(-1,2)
        
        # separate unmatched agents from matched agents, so that it becomes possible to iterate over them separately
        if num_unmatched > 0:
            # select those who got matched to None as a proposer 
            # and select those who got matched to None as a receiver (this is only possible at random_path_to_stability)
            # and concatenate the two arrays
            # since everyone in 'unmatched' is matched to None, there is no need to keep None in there,
            # so only the agents names are selected
            unmatched = np.concatenate((matches[matches[:,1]=='unmatched'][:,0], 
                                        matches[matches[:,0]=='unmatched'][:,1]))
            # now count the number of times each agent appears in unmatched
            unmatched_and_counts = np.unique(unmatched, return_counts=True)
            # zip the two so that we can access it easily in a loop
            unmatched_and_counts = zip(unmatched_and_counts[0], unmatched_and_counts[1])
            
            for um_and_count in unmatched_and_counts:
                # if an agent is a proposer, then add their probability 
                # (calculated by dividing its number of matches with the number of matchings)
                # to a cell where the row corresponds to the agent and the column corresponds to 'unmatched'
                if um_and_count[0] in self.proposers:
                    random_matching[rows[um_and_count[0]], columns['unmatched']] += um_and_count[1] / size
                
                # if an agent is a receiver, then add their probability to a cell where column that corresponds 
                # to the agent and the row corresponds to 'unmatched'
                elif um_and_count[0] in self.receivers:
                    random_matching[rows['unmatched'], columns[um_and_count[0]]] += um_and_count[1] / size
                # if the agent is neither proposer nor a receiver, then print an error message and exit
                else:
                    raise ValueError('Agents in the matching and preference lists do not match.')
            
            
            # finally, reassign the matches with no 'None' in them back to 'matches'
            matches = matches[(matches[:,0]!='unmatched')&(matches[:,1]!='unmatched')]
            
        
        # count the frequency of each unique match that happened throughout 'matchings'
        matches_and_counts = np.unique(matches, axis=0, return_counts=True)
        # zip each match with its frequency, so that we can access it easily in the loop below
        matches_and_counts = zip(matches_and_counts[0], matches_and_counts[1])
        
        for match_and_count in matches_and_counts:
            # for each match, assign its probability (calculated by dividing its count by the number of matchings, 'size')
            # to a cell in random_matching where the row corresponds to the first agent (i.e. proposer) and 
            # the column corresponds to the second agent (i.e. receiver)
            try:
                random_matching[rows[match_and_count[0][0]],
                               columns[match_and_count[0][1]]] += match_and_count[1] / size
            # this exception is raised if 'None' is in the iteration 
            # (who is not an agent but just a filler to match the numpy array sizes)
            # so we skip them
            except KeyError:
                continue
            
        
        # collect row names, column names and the numpy 2D array of probabilities into a dictionary
        random_matching_dict = {'rows': rows, 'columns': columns, 'random_matching': random_matching}
                    
        return random_matching_dict
    
    
    
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% RANDOM DEFERRED ACCEPTANCE %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    
    
    def random_Deferred_Acceptance(self, proposers, receivers, num_iter=1, **kwargs):
        """
        Given a weak preference profile, breaks ties using a single random tiebreaker and applies 
        the Deferred Acceptance algorithm to the pseudo-strict preference profile.
        
        Input: 
        
        proposers: Python dictionary of receiver preferences
        receivers: Python dictionary of receiver preferences
        num_iter: a positive integer. This indicates the number of times the DA algorithm is to be repeated.
        epe: (Optional) if True, finds the constrained ex post efficient stable matching for every iteration.
        
        Returns:
        
        A lottery and its corresponding random matching.
        
        The lottery is a list of tuples where each tuple consists of a matching and its count.
        The random matching is a dictionary where 
            - 'rows': the proposers' names and their corresponding position in the row of the random matching
            - 'columns': the receivers' names and their corresponding position in the column of the random matching
            - 'random_matching': a numpy 2D array where the rows are the proposers and the columns are the receivers
                                 and each cell is the probability they are matched with each other
        """
        
        MM = MarriageModel()
        
        output = []
        
        self.proposers = proposers
        self.receivers = receivers
        
        for i in range(num_iter):
        # for each iteration,
            # copy the raw preference profiles 
            P_m = self.proposers.copy()
            P_w = self.receivers.copy()
            # and create a numpy array out of the agents' names
            # since __strict_preference_list uses numpy.isin on priority order to efficiently reorder 
            # an indifference list, convert the priority order to a numpy array
            priority_order_m = np.array(list(P_m))
            priority_order_w = np.array(list(P_w))
            # and randomly shuffle each array
            np.random.shuffle(priority_order_m)
            np.random.shuffle(priority_order_w)
            
            try:
                # for each proposer, make their preference list strict 
                for man, preferences in P_m.items():
                    P_m.update({man: self.__strict_preference_list(preferences, priority_order_w)})
                    
                # for each receiver, make their prefence list strict
                for woman, preferences in P_w.items():
                    P_w.update({woman: self.__strict_preference_list(preferences, priority_order_m)})

            except AttributeError:
                raise AttributeError('The passed preferences are not dictionaries.')
            
            # using the (now strict) preference lists, compute the Deferred Acceptance algorithm outcome
            mu = MM.Deferred_Acceptance(P_m, P_w)
            
            
            if kwargs.get('epe') is True:
                mu = self.stable_improvement_cycle(mu)
                
                
            # and add it to list 'output'
            output.append(mu)
        
        # sort the matchings in output
        output = np.array([MM.sort_matching(mu) for mu in output])
        
        
        exception_activated = False
        # change dtype to unicode in case there was an unmatched agent in any matching 
        # (in which case the numpy array would be dtype object, which is not accepted by np.unique)
        try:
            output = output.astype('<U'+str(max(len(el) if isinstance(el, str) else 1 
                                                for el in list(P_m)+list(P_w)+['unmatched'])))
        except ValueError:
            # the exception is raised if 'output' has matchings of different length 
            # (could happen if some matchings have more unmatched agents than others)
            # in that case, append (None, None) to the 'short' matchings until the lengths match
            max_len = max(len(matches) for matches in output)            
            for matches in output:
                while len(matches) < max_len:
                    matches.append((None, None))
            # and stack the new 'output' and change its dtype to Unicode
            output = np.stack(output, axis=0).astype('<U'+str(max(len(el) if isinstance(el, str) else 1 
                                                                  for el in list(P_m)+list(P_w)+['unmatched'])))
            exception_activated = True
        
        
        # extract the unique matchings and count the frequency of each unique matching in output
        unique_matchings, matching_counts = np.unique(output, axis=0, return_counts=True)
        
        # if the above exception was raised, that means the matchings included some filler rows to make 
        # the numpy array dimensions match (to use np.unique())
        # here, these fillers are deleted
        if exception_activated is True:
            # the matchings were filled with None, but the dtype of the entire array was changed to Unicode
            # which changed None -> 'None', so here these rows are excluded
            unique_matchings = [arr[arr[:,0]!='None'] for arr in unique_matchings]
        
        # create a random matching
        # rows / columns are dictionaries that are the index and column names, respectively of random_matching
        random_matching_dict = self.to_random_matching(output)
        
        return (unique_matchings, matching_counts), random_matching_dict
    
    
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% CONSTRAINED EX-POST EFFICIENT STABILITY %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    
    # a private method that checks if some 'proposer' is among the most preferred set of proposers 
    # that points to a given 'receiver'
    def __dominant_set(self, receiver, proposer):
        
        # starting from the proposers who are in the most preferred tier for 'receiver'
        for tier in self.receivers[receiver]:
            # if that tier is a list,
            if isinstance(tier, list):
                # check if 'proposer' is in that tier,
                if proposer in tier:
                    # and if yes, then see if the proposers collected so far in R_upper[receiver] are in this tier 
                    # if yes, add 'proposer' to the existing list, 
                    if self.R_upper[receiver][0] in tier:
                        # so that 'proposer' is in the same tier as everyone in R_upper[receiver]
                        self.R_upper[receiver].append(proposer)
                        return
                    else:
                        # otherwise, update the list by 'proposer' and return; 
                        # since the iteration always starts from the top, if 'proposer' appears before anyone in 
                        # R_upper[receiver] then he is more preferred than anyone is the existing list by receiver
                        self.R_upper.update({receiver: [proposer]})
                        return
                # if however, 'proposer' is not in that tier, but
                else:
                    # the already existing R_upper[receiver] is, then simply return 
                    # (as this means R_upper[receiver] is more preferred than 'proposer')
                    if self.R_upper[receiver][0] in tier:
                        return
            # if the tier is a singleton,
            else:
                # see if this sole proposer in this tier is the the one already in the list,
                if tier == self.R_upper[receiver][0]:
                    # if yes, do nothing 
                    # as it means 'proposer' is not more preferred than the person already in R_upper[receiver]
                    return
                # otherwise, check if tier is the same person as 'proposer',
                elif tier == proposer:
                    # if yes, update the list by 'proposer' as it means whoever was already in the list, they are 
                    # not more preferred than 'proposer' since the checking starts from the top
                    self.R_upper.update({receiver: [proposer]})
                    return
                # if neither, move on
                else:
                    continue
    
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    
    # a private method that searches for cycles and if found assigns every proposer in a cycle the receiver they point to
    def __cycles(self, matching, reverse_matching):
        
        # copy the Preferences to P; we will be working directly on P from here on
        P = self.P_better.copy()
        
        mu = {} # a dictionary to collect all matches
        pointers = [] # the list that lets proposers point to their 1st choice until a cycle forms
        
        # while there are unmatched proposers who still have not exhausted their preference list, continue
        while True:
            
            if pointers == []:
                try:
                    # pick a proposer still in the algorithm, if there is any left
                    pointer = next(proposer for proposer in P)
                    # each proposer participates with their partner
                    # the proposer is looking to improve on their current partner by exchanging them with someone 
                    # they prefer more
                    pointers = [matching[pointer], pointer]
                # if there is no one left, stop the algorithm
                except StopIteration:
                    break
            
            # iterate until a cycle is encountered or until every proposer checked so far have no one to point to:
            # a cycle forms if a proposer who was already in the list 'pointers' appears again
            # if a cycle forms, break loop to extract the cycle from pointers
            while (len(set(pointers[1::2])) is len(pointers[1::2])) and pointers != []:
                
                try:
                    # the last proposer in 'pointers' points to their best remaining choice for whom he is 
                    # among the most preferred (highest priority) proposers
                    nextReceiver = next(r for r in P[pointers[-1]] if pointers[-1] in self.R_upper[r] 
                                        and r not in mu.values())
                    # if any such receiver exists, then add them along with their current partner / a proposer
                    pointers += [nextReceiver, reverse_matching[nextReceiver]]
                
                except (StopIteration, KeyError):
                    # if the last proposer does not have anyone on their list left, 
                    # take that him out of 'pointers' along with his match
                    del P[pointers[-1]]
                    del pointers[-2:]
            
            # if the above while-loop was stopped because there is a cycle,
            if pointers != []:
            
                # find the index of the proposer who is the head of a cycle in 'pointers'
                idx = next(ind for ind, proposer in enumerate(pointers) if proposer==pointers[-1])
                # and slice the list to extract the cycle that formed in pointers
                cycle = pointers[idx:]
                # every proposer in the cycle is matched to the receiver they are pointing to
                mu.update({cycle[i]: cycle[i+1] for i in range(0,len(cycle)-1,2)})
                
                # if there are proposers left in 'pointers', continue that list
                # pointers[idx]'s match in 'pointers' is not taken in cycle, so that receiver must be excluded
                pointers = pointers[:idx-1]

                # remove proposers who are already matched from the dictionary of proposers in the problem
                for matched in cycle:
                    P.pop(matched, None)
        
        return mu
    
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    # a method that runs a stable improvement cycle on a given matching
    # it uses the preferences input in random_Deferred_Acceptance
    # and looks for cycles and improves the assignment of every proposer who are in a cycle
    def stable_improvement_cycle(self, matching):
        
        while True:
        
            # only married couples can participate in SIC because singles don't have anything to exchange
            mu = {p:r for p,r in matching.items() if r is not None}
            # every married proposer points to receivers who are more preferred than their current partner if there is one
            self.P_better = {p: pref[: pref.index(mu[p])] for p, pref in mu.items() if pref[0] != mu[p]}
            # reverse the proposer-receiver mapping
            reverse_mu = {v:k for k,v in mu.items()}

            # R_upper will collect the most preferred list of proposers for each receiver who are pointed by a proposer
            self.R_upper = {}
            # for each proposer, 
            for p, receivers in self.P_better.items():
                # check through all receivers he is pointing to,
                for r in receivers:
                    # since a receiver can be in a cycle only with their accompanying proposer, 
                    # only the receivers whose proposer is pointing to someone is considered,
                    if reverse_mu[r] in self.P_better:
                        # if the receiver r already has an existing list, check if proposer p is 
                        # among the most preferred among the proposers who are pointing to receiver r
                        if r in self.R_upper:
                            self.__dominant_set(r, p)
                        # if not, start a new list for receiver r with proposer p
                        else:
                            self.R_upper.update({r: [p]})

            # search for cycles among married couples and if any is found, 
            # update 'matching' by matching each proposer in a cycle to the receiver they point to
            old_matching = matching.copy()
            matching.update(self.__cycles(mu, reverse_mu))
            
            # if there are no cycles found, stop the algorithm
            if old_matching == matching:
                break        
        
        # return the updated matching
        return matching
    
    
    
    
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    
    
    
    def rDA_raw_data(self, proposers, receivers, **kwargs):
        
        """
        Finds 
        
        """
        
        MM = MarriageModel()
        
        from itertools import permutations
        
        output = []
        
        self.proposers = proposers
        self.receivers = receivers
        
        tiebreakers = []
        
        # copy the raw preference profiles 
        P_m = self.proposers.copy()
        # and create a numpy array out of the agents' names
        # since __strict_preference_list uses numpy.isin on priority order to efficiently reorder 
        # an indifference list, convert the priority order to a numpy array
        priority_order_w = np.array(list(self.receivers))
        
        all_permutations = permutations(list(P_m), len(P_m))
        
        for perm in all_permutations:
        # for each iteration,
            
            priority_order_m = np.array(perm)
            P_w = self.receivers.copy()
            
            try:
                # for each receiver, make their prefence list strict
                for woman, preferences in P_w.items():
                    P_w.update({woman: self.__strict_preference_list(preferences, priority_order_m)})

            except AttributeError:
                raise AttributeError('The passed preferences are not dictionaries.')
            
            # using the (now strict) preference lists, compute the Deferred Acceptance algorithm outcome
            mu = MM.Deferred_Acceptance(P_m, P_w)
            
            
            if kwargs.get('epe') is True:
                mu = self.stable_improvement_cycle(mu)
                tiebreakers.append(priority_order_m)
                
                
            # and add it to list 'output'
            output.append(mu)
        
        # sort the matchings in output
        output = [np.array(MM.sort_matching(mu)) for mu in output]
        
        return output, tiebreakers
    
    
    
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    
    def pi_ordinally_dominates_rho(self, pi_lottery, rho_lottery):
        
        """
        Finds whether the random matching induced by pi_lottery FOSDs the random matching induced by rho_lottery 
        with respect to the proposer preferences passed at class instantiation.
        Returns True if it does, False otherwise.
        
        Input:
        
        - pi_lottery: a tuple of 3D numpy array of size number_of_matchings x pairs x 2 (i.e. matchings) and 
                      a list of length number_of_matchings (i.e. frequencies)
        - rho_lottery: a tuple of 3D numpy array and a list (dimensions must match that of pi_array)
        
        N.B. To indicate 'frequencies', if None is passed instead of a list, then every matching in the corresponding 
             numpy array will be treated as having an equal probability.
        """
        
        # if no frequencies were passed for some reason, create a pseudo frequency list
        if pi_lottery[1] is None:
            # since pi_lottery is a tuple, which is immutable, it must be converted to a list first
            pi_lottery = list(pi_lottery)
            # create an array of 1s to be used as a frequency list to induce a random matching from the matchings in pi_lottery[0]
            pi_lottery[1] = np.array([1]*len(pi_lottery[0]))
            
        # if no frequencies were passed for some reason, create a pseudo frequency list
        if rho_lottery[1] is None:
            # since pi_lottery is a tuple, which is immutable, it must be converted to a list first
            rho_lottery = list(rho_lottery)
            # create an array of 1s to be used as a frequency list to induce a random matching from that matchings in rho_lottery[0]
            rho_lottery[1] = np.array([1]*len(rho_lottery[0]))
            
        # convert to a random_matching
        rho_dict = self.lottery_to_random_matching(rho_lottery)
        pi_dict  = self.lottery_to_random_matching(pi_lottery)
        
        # save the number of receivers to be used for numpy.concatenate later
        rho_width = rho_dict['random_matching'].shape[1]
        pi_width = pi_dict['random_matching'].shape[1]
        
        # create a numpy array where rows correspond to proposers and columns correspond to receivers.
        # for each proposer, their probabilities of being matched to receivers are re-arranged such that
        # lower the column index, higher the preference for the corresponding receiver
        ranked_rho = []
        # for each proposer, 
        for row in rho_dict['rows']:
            # a row that corresponds to the current proposer in the random matching induced by rho
            current_proposer = rho_dict['random_matching'][rho_dict['rows'][row]]
            # re-arrange the probabilities of the current_proposer according to their preference list
            arranged_array = current_proposer[[rho_dict['columns'][col] for col in self.proposers[row]]]
            # since proposers may be matched to fewer receivers than the total number of receivers, 
            # the columns (corresponding to receivers who are unmatched to the current proposer) 
            # must be filled with zeros to keep using a float numpy array later
            arranged_array = np.concatenate((arranged_array, [0]*(rho_width-len(arranged_array))))
            ranked_rho.append(arranged_array)
        
        
        ranked_pi = []
        for row in pi_dict['rows']:
            # a row that corresponds to the current proposer in the random matching induced by pi
            current_proposer = pi_dict['random_matching'][pi_dict['rows'][row]]
            # re-arrange the probabilities of the current_proposer according to their preference list
            arranged_array = current_proposer[[pi_dict['columns'][col] for col in self.proposers[row]]]
            # since proposers may be matched to fewer receivers than the total number of receivers, 
            # the columns (corresponding to receivers who are unmatched to the current proposer) 
            # must be filled with zeros to keep using a float numpy array later
            arranged_array = np.concatenate((arranged_array, [0]*(pi_width-len(arranged_array))))
            ranked_pi.append(arranged_array)
        
        # find the cumulative sum for each column to be used for FOSD comparison
        ranked_rho = np.cumsum(np.array(ranked_rho), axis=1)
        ranked_pi = np.cumsum(np.array(ranked_pi), axis=1)
        # calculate the difference
        diff = ranked_pi - ranked_rho
        
        # since each proposer's probabilities are sorted according to their preference list, it suffices to check if 
        # the cumulative sum of probabilities at any receiver on their preference list is negative
        # if for any proposer, the difference in cumulative sum is negative at any preference rank, then pi does not
        # first-order stochastically dominate rho
        if len(diff[diff<0]) > 0:
            return False
        else:
            return True