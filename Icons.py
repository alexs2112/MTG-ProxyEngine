import pygame, Cards

class Icons:
  """
  An object that simply loads and stores images for every symbol
  Icons taken from MagicSetEditor
  """
  def __init__(self):
    """
    Loads a bunch of images from template-data/symbols and stores them in dictionaries
    To prevent slow initializing, start by storing paths in dictionaries. Whenever an
    icon is needed, load the icon image by path and store the image in a cache.

    self.title_cache: loaded icons to be used in the title box (mana costs for the card)
    self.text_cache: loaded icons to be used in the text box (tap symbols, smaller mana symbols, etc)
    self.title_path: icons by path, to be loaded from and stored in the cache when needed
    self.text_path: same thing
    """
    self.title_path = {}
    self.text_path = {}
    self.title_cache = {}
    self.text_cache = {}

    # Start with numbers
    for i in range(16):
      self.title_path[str(i)] = "template-data/symbols/title/" + str(i) + ".png"
    
    # Coloured mana symbols
    for c in ['W', 'U', 'B', 'R', 'G', 'C', 'S', 'X']:
      self.title_path[c] = "template-data/symbols/title/mana_" + c.lower() + ".png"

    # Dual costs of 2/C (mostly for reaper king)
    for c in ['2/B', '2/G', '2/R', '2/W', '2/U']:
      self.title_path[c] = "template-data/symbols/title/" + c + ".png"

    # Two colour costs, in the form of U/R, for stuff like Guttural Response
    for c in ['B/G', 'B/R', 'G/U', 'G/W', 'R/G', 'R/W', 'U/B', 'U/R', 'W/B', 'W/U']:
      self.title_path[c] = "template-data/symbols/title/mana_" + (c[0] + c[2]).lower() + ".png"
    
    # Phyraxian mana costs, in the form of R/P, for stuff like Gut Shot
    for c in ['W/P', 'U/P', 'B/P', 'R/P', 'G/P']:
      self.title_path[c] = "template-data/symbols/title/mana_phy" + c[0].lower() + ".png"

  def get_title(self, symbol):
    """
    If the image for the symbol is not already in cache, load it and store it in cache
    Title size, so used for the mana cost of the card in the top right corner
    
    PARAMETERS:
     - symbol: can be in format either "{W}" or "W"

    RETURNS:
     - The image as a pygame Surface
    """
    # If the symbol requested is formatted as {W}, cut off the head and end
    if symbol[0] == "{":
      symbol = symbol[1:-1]

    # Check if the symbol exists in the title cache, if it does not, try to load it
    if symbol in self.title_cache:
      return self.title_cache[symbol]
    
    if symbol in self.title_path:
      i = pygame.image.load(self.title_path[symbol])
      i = Cards.dynamically_scale_card(i,(150,150))
      self.title_cache[symbol] = i
      return i
    
    print('Cannot find symbol "' + symbol + '"')
    return
