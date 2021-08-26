import pickle, json, pygame
import os.path as path
import Updater
# https://scryfall.com/docs/api/cards

ALL_CARDS_SERIALIZED = "data/all-cards.ser"

def serialize_all_cards(verbose=True):
  """
  Loads data/all-cards.json in a more efficient format and then serializes it into
  a byte stream, writing the stream to data/all-cards.ser

  PARAMETERS:
   - verbose: If you would like to see all messages printed to the terminal
  """
  if verbose:
    print("Reading " + Updater.ALL_CARDS_FILE)
  if not path.exists(Updater.ALL_CARDS_FILE):
    # Always print these regardless of verbose
    print(Updater.ALL_CARDS_FILE + " does not exist!")
    print("Aborting!")
    return

  # If it does exist, read the file line by line, storing each card line in the dictionary
  f = open(Updater.ALL_CARDS_FILE, encoding='utf-8')
  
  # Set up a new dictionary
  d = {}
  
  if verbose:
    print("Parsing...")
  all_lines = f.readlines()
  
  # Read all lines in the scryfall file minus the first and last one
  for i in range(1, len(all_lines)-1): 
    line = all_lines[i]
    
    # The last line does not end with a , so we need to check the comma in every line
    if line[-2] == ',':
      line = line[:-2]
    
    card = json.loads(line)       # Need to cut off the extra scryfall data on the end
    d[card["name"]] = card        # Store in the database under its name
  
  if verbose:
    print("Done Reading!")

  # Then close the data/all-cards.ser file
  f.close()

  # Then serialize the dictionary via pythons Pickle
  if verbose:
    print("Serializing to " + ALL_CARDS_SERIALIZED + "...")
  pickle.dump(d, open(ALL_CARDS_SERIALIZED, 'wb'))
  if verbose:
    print("Done Serializing!")

def deserialize_all_cards(verbose=True):
  """
  Reads data/all-cards as a serialized dictionary and deserializes it

  PARAMETERS:
   - verbose: If you would like to see all messages printed to the terminal

  RETURNS:
   - The dictionary of all cards with names as keys and dictionaries of scryfall data as values
  """
  if not path.exists(ALL_CARDS_SERIALIZED):
    print("Cannot find " + ALL_CARDS_SERIALIZED)
    print("Local database may be corrupted, try updating")
    print("   python Engine.py -update all")
    return {}

  return pickle.load(open(ALL_CARDS_SERIALIZED, 'rb'))

def parse_card_name(name):
  """
  Translates the real name of the input card to a name to be used for the art file

  PARAMETERS:
   - name: The card name as shown on the card. Example: "Lightning Bolt"
  
  Returns:
   - The string conversion to be used for saving the file. Example: "lightning-bolt"
  """
  return name.lower().replace(", ", "-").replace(" ", "-")

def get_card_art_crop(card, autoproxy_format=False):
  """
  Searches scryfall for the specified card art and saves it to data/scryfall/card-art/[card-name]

  PARAMETERS:
   - card: the card dictionary from the main all-cards dictionary. Example: dictionary["Lightning Bolt"]
   - autoproxy_format: how the filename should be saved. Formats it to be <CardName> (<Artist>).png to comply
     with https://github.com/ndepaola/mtg-autoproxy

  RETURNS:
   - Returns the filepath to the image if available
  """
  assert type(card) == dict

  try:
    if autoproxy_format:
      name = card["name"] + " (" + card["artist"] + ")"
      extension = ".jpg"
    else:
      name = parse_card_name(card["name"])
      extension = ".png"
  except:
    print("Could not get the name from card " + card)
    return

  if path.exists("data/scryfall/card-art/" + name + extension):
    # If the art exists, just return with a message
    # We can fix this protocol later
    print("Card art already loaded for " + name)
    return "data/scryfall/card-art/" + name + extension
  
  # Otherwise, download the cropped art from scryfall
  try:
    uri = card["image_uris"]["art_crop"]
  except:
    print('Could not get ["image_uris"]["art_crop"] from card ' + name)
    return
  
  Updater.request_scryfall_data(uri, 'data/scryfall/card-art/' + name + extension, verbose=False)
  return "data/scryfall/card-art/" + name + extension

def get_full_card_image(card):
  """
  Searches scryfall for the specified card and saves it as a high res png image to data/scryfall/full-cards/[card-name]
  Nearly an identical function to get_card_art, can probably be condensed in the future

  PARAMETERS:
   - card: the card dictionary from the main all-cards dictionary. Example: dictionary["Lightning Bolt"]

  RETURNS:
   - Returns the filepath to the image if available
  """
  assert type(card) == dict

  try:
    name = parse_card_name(card["name"])
  except:
    print("Could not get the name from card " + card)
    return
  
  if path.exists("data/scryfall/full-cards/" + name + ".png"):
    # If the art exists, just return with a message
    # We can fix this protocol later
    return "data/scryfall/full-cards/" + name + ".png"
  
  # Otherwise, download the cropped art from scryfall
  try:
    uri = card["image_uris"]["png"]
  except:
    print('Could not get ["image_uris"]["png"] from card ' + name)
    return
  
  Updater.request_scryfall_data(uri, "data/scryfall/full-cards/" + name + ".png", verbose=False)
  return "data/scryfall/full-cards/" + name + ".png"

def dynamically_scale_card(image, newsize):
  """
  Scales the card to the specified size without warping it.
  Gets the max scaling to fit (newx, newy) and scales both x and y by that scale.

  PARAMETERS:
   - image: the image you want to resize
   - newx,newy: The minimum new width and height of the image, it can be bigger in one direction

  RETURNS:
   - The rescaled image, with size at least (newx, newy)
  """
  x,y = image.get_size()
  newx, newy = newsize
  scale = max(newx / x, newy / y)
  i = pygame.transform.scale(image, (int(x * scale), int(y * scale)))
  return i

def two_colour_background(card):
  """
  Checks if all mana symbols in a cards mana cost is either generic or two coloured (such as {R/W})
  If so, returns true, otherwise false

  RETURNS:
   - A boolean depending on if the card needs a two coloured background, rather than a gold background
  """
  if "mana_cost" not in card:
    return False
  
  # First get a list of the cost of the card
  cost = card["mana_cost"]
  l = cost[1:-1]
  l = l.split('}{')

  # Set up a couple other lists
  colours = ["W", "U", "B", "R", "G"]
  check = ['B/G', 'B/R', 'G/U', 'G/W', 'R/G', 'R/W', 'U/B', 'U/R', 'W/B', 'W/U']

  # Make sure there is only one dual colour cost
  current = ''
  
  # Iterate over every cost in the cards mana cost. If it is in colours, return False as the border cannot be
  # two coloured. If there is at least one cost in check that is not in colours, return True
  hasone = False
  for c in l:
    if c in colours:
      return False
    if c in check:
      if current != c and hasone == True:
        return False
      hasone = True
      current = c
  return hasone

  
