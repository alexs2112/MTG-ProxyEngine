import os.path as path

def load_decklist_from_file(filepath):
  """
  Load a decklist from a text file. The decklist has to be in format:
    4 name
    9 name
    1 name
    name
  
  PARAMETERS:
   - filepath: the filepath to the requested file

  RETURNS:
   - a dictionary of { "cardname" : quantity }
     The name of the card is just an unedited string, it can be passed into a
     card dictionary in the future.
     No error handling of card names are done here, this simply counts

  CURRENT RESTRICTIONS:
   - The decklist can only be of the formats above
   - You cannot have more than 9 of a card on one line. Simply make two lines like so
        9 Shadowborn Apostle
        8 Shadowborn Apostle
  """

  # First make sure the file even exists
  if not path.exists(filepath):
    print("Cannot find " + filepath)
    return {}

  # Open and read all lines of the decklist
  f = open(filepath, 'r', encoding='utf-8')
  dat = f.readlines()
  f.close()

  # Set up the dictionary to be returned
  d = {}

  # Iterate over every line in the decklist
  for line in dat:
    if line[0] == '\n' or line[0] == '#':
      continue

    # Base amount of a card is 1
    n = 1

    # If the first char of the line is a digit, set the amount of that card to be the digit and cut it off
    if line[0].isdigit():
      n = int(line[0])
      line = line[1:]

    # Then strip all the extra whitespace from the line
    line = line.strip()

    # Now we check, if it is already in the dictionary, add n to its amount, otherwise add it to the dictionary
    if line in d:
      d[line] += n
    else:
      d[line] = n

  return d

def print_decklist(decklist, only_one_of_each=False):
  total = 0
  cards = []
  for key in decklist:
    cards.append(key)
  
  cards.sort()

  for card in cards:
    if only_one_of_each:
      print("1 " + card)
      total += 1
    else:
      print(str(decklist[card]) + " " + card)
      total += decklist[card]

  print("\nTotal Cards: " + str(total))
  
def compare_decklist(deck1, deck2):
  missing = []

  for card in deck2:
    if card not in deck1:
      missing.append(card)
  
  if len(missing) == 0:
    print("All cards already in decklist!")
    return
  else:
    print("Missing " + str(len(missing)) + " cards")
    for card in missing:
      print(card)

  