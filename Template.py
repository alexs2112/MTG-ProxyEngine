import os, pygame
import Cards

# Some constants regarding card dimensions
BLEED_WIDTH = 1632
BLEED_HEIGHT = 2220
CUT_WIDTH = 1488
CUT_HEIGHT = 2076
SAFE_WIDTH = 1344
SAFE_HEIGHT = 1932

# Here are where the rectangles should start on a card of those dimensions
# Start at this value, add the width or the height to be within the cut/safe area
CUT_START = 72
SAFE_START = 144

class Template:
  """
  The parent class that all other templates are derived from

  Most importantly has an execute(card) function, that will take a card:dictionary as input
  and save the processed card to the output folder
  """
  def __init__(self, all_cards):
    pygame.init()
    self.all_cards = all_cards

  def execute(self, card):
    """
    Actually perform the operations on the input card.
    Will save a processed version of the output file in output/[card-name]

    RETURNS:
     - A bool if the process could be completed or not
    """

    # Make sure the output file exists
    if not os.path.exists("output"):
      os.mkdir("output")

    # Then make sure the card name is actually a card in the dictionary
    if "name" not in card:
      print("Error: Cannot find 'name'")
      print(card)
      return False
    if card["name"] not in self.all_cards:
      print("Error: " + card["name"] + " not in all_cards")
      return False

    print("Processing " + card["name"])
    # Then be overridden by a subclass
  
class BlackBorderExtension(Template):
  """
  This template simply extends the black border of a scryfall card image
  to make it work with makeplayingcards

  It isn't very good, this was just a test
  """

  def execute(self, card):
    """
    This template simply loads the full card image in the cut zone, then
    places a black border on top of it

    This is mostly a testing class, the outcome is rather underwhelming

    Scryfall full cards are 745x1040
    """
    if super().execute(card) == False:
      return False
    
    # The first thing we need to do is download the full card image from scryfall
    path = Cards.get_full_card_image(card)
    if path == None:
      return False

    output = pygame.Surface((BLEED_WIDTH, BLEED_HEIGHT))
    card_image = pygame.image.load(path)
    border = pygame.image.load("template-data/black-border-extension.png")

    # First scale the card image by 2, to (1490, 2080)
    card_image = pygame.transform.scale(card_image, (1490, 2080))

    # Blit the image to the output, and then the border on top of it
    output.blit(card_image, (71, 70))
    output.blit(border, (0,0))

    # Then save the image
    pygame.image.save(output, "output/" + Cards.parse_card_name(card["name"]) + ".png")

    return True

class WhiteLined(Template):
  """
  A simple template, a white back with extended art and some coloured lines
  Unfinished, a future project
  """

  def execute(self, card):
    super().execute(card)
    linesize = 10
    canvas = pygame.Surface((BLEED_WIDTH, BLEED_HEIGHT))
    canvas.fill((255,255,255))  # Fill the canvas with white

    # Set up some text boxes for each area on the card
    # name_box = (144,144,1488,360)
    # oracle_box = (144,1330,1488,2076)
    # type_box = (144,1050,1488,280)
    # art_box = (60,370,1572,1050) 
    # mana_box = (0,0,0,0)
    # pt_box = (0,0,0,0)

    # Load the art
    card_art_path = Cards.get_card_art_crop(card)
    if card_art_path == None:
      return False
    card_art = pygame.image.load(card_art_path)

    # For now just scale the art to the art_box size
    # LATER DYNAMICALLY ADJUST THE SCALE SO IT DOESNT LOOK FUCKING UGLY
    # will need a mask I think
    card_art = pygame.transform.scale(card_art, (1532, 860))
    
    # Draw the art to the card
    canvas.blit(card_art, (50, 320))

    color = (255, 0, 0)

    # Then draw a bunch of random lines
    pygame.draw.lines(canvas, color, False, [(0,314), (BLEED_WIDTH, 314)], linesize)
    pygame.draw.lines(canvas, color, False, [(0,1184), (BLEED_WIDTH, 1184)], linesize)

    # Then save the image
    pygame.image.save(canvas, "output/" + Cards.parse_card_name(card["name"]) + ".png")

    return True

class BasicModern(Template):
  """
  Utilizes the old photoshop autoproxy tool template to generate them in this engine
  Images are extremely large to ensure crisp text. Around 5 MB each.

  Original Autoproxy Tool I had used to get the templates from located here:
  https://github.com/ndepaola/mtg-autoproxy

  Full Bleed: 2982x4044
  Cut: 2688x3744
  Base black border included in template files

  Loaded template should be placed at (150,150)
  """
  def execute(self, card):
    """
    Creates a full MPC ready proxy utilizing the template files and local database

    Use executeBasic(card) for generating a proxy formatted as a regular card
    """
    super().execute(card)
  
    # Where the x and y coordinates "start at" when placing to the full template
    base = 150

    card_type = card["type_line"]

    # A bunch of flags to be set when processing the card, before generating the image
    # Determines the borders and background
    land = False
    if "Land" in card_type:
      land = True

    # Determines the P/T box
    creature = False
    if "Creature" in card_type:
      creature = True
    
    # Determines if we need to overlay the Nyx enchantment border
    nyx = False
    if "Enchantment" in card_type:
      if "Creature" in card_type or "Artifact" in card_type:
        nyx = True
    
    # First get the main background, either land or nonland
    if land == True:
      background = None
      print("Tried to load a land?")
      return
    else:
      background = pygame.image.load("template-data/basic/white-nonland.png")
    
    # Load the card art
    card_art_path = Cards.get_card_art_crop(card)
    if card_art_path == None:
      return False
    card_art = pygame.image.load(card_art_path)

    # By the template, the image should be about 2294x1686 and be placed at (200,420) + base
    # For now, just directly resize it without worrying about scale
    card_art = Cards.dynamically_scale_card(card_art, (2294, 1686))

    # Now create an output canvas of the proper size, draw things to it
    canvas = pygame.Surface((2982,4044))
    canvas.blit(card_art, (200+base, 420+base))
    canvas.blit(background, (base, base))

    # Finally, add the MPC extended border and save the image
    border = pygame.image.load("template-data/basic/border-extend.png")
    canvas.blit(border, (0,0))
    pygame.image.save(canvas, "output/" + Cards.parse_card_name(card["name"]) + ".png")
    return True

  def executeBasic(self, card):
    print("ExecuteBasic(card) not yet implemented :(")




