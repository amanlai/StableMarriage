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
