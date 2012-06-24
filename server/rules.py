import random

def spies_for_team(usernames):
  n = len(usernames)
  spies = [2, 2, 3, 3, 3, 4][n - 5]
  return set(random.sample(usernames, spies))

def mission_size(users, mission):
  return mission_sizes(users)[mission]

def mission_sizes(users):
  return {
      5:  [2, 3, 2, 3, 3],
      6:  [2, 3, 4, 3, 4],
      7:  [2, 3, 3, 4, 4],
      8:  [3, 4, 4, 5, 5],
      9:  [3, 4, 4, 5, 5],
      10: [3, 4, 4, 5, 5],
      }[users]
