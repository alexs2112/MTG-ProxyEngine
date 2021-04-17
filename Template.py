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

# A few dictionaries of fonts, with keys as sizes and values as the font object
pygame.init()
FONTS_BOLD = {
  140:pygame.font.Font('template-data/fonts/JaceBeleren-Bold.ttf', 140),
  120:pygame.font.Font('template-data/fonts/JaceBeleren-Bold.ttf', 120)
}
FONTS_BASIC = {
  140:pygame.font.Font('template-data/fonts/MPlantin.ttf', 140),
  130:pygame.font.Font('template-data/fonts/MPlantin.ttf', 130),
  120:pygame.font.Font('template-data/fonts/MPlantin.ttf', 120)
}
FONTS_ITAL = {
  120:pygame.font.Font('template-data/fonts/MPlantin-Italic.ttf', 120)
}

def write(surface, text, x, y, size, bold=False, ital=False):
  """
  A basic helper function to write to the surface

  PARAMETERS:
   - surface: The pygame Surface object we want to write to
   - text: The text to write
   - x,y: The starting x,y coordinates of the text
   - size: The font size in { 72, 100, 150 }
   - bold: If the text is to be bolded
   - ital: If the text is to be italicized. Cannot be both bolded and italicized
  """
  if bold:
    font = FONTS_BOLD[size]
  elif ital:
    font = FONTS_ITAL[size]
  else:
    font = FONTS_BASIC[size]
  label = font.render(text, 1, (0,0,0))
  surface.blit(label, (x,y))

def write_wrapped(surface, text, rect, font, color=(0,0,0)):
  """
  A basic function to write wrapped text in a block
  Pygame doesnt come with this functionality
  Copied from https://www.pygame.org/wiki/TextWrap
  although I might need to make changes in the future as this is probably really slow

  PARAMETERS: 
   - surface: The card to draw on
   - text: The text to write
   - rect: The rectangle the text will be written in
   - font: The font to use
   - color: Colour of the text, defaults to black

  RETURNS:
   - Any text that will not fit in the box
  """
  rect = pygame.Rect(rect)
  y = rect.top
  lineSpacing = -2

  # get the height of the font
  fontHeight = font.size("Tg")[1]
  print(text)

  while text:
    i = 1

    # determine if the row of text will be outside our area
    if y + fontHeight > rect.bottom:
      break

    # determine maximum width of line
    while font.size(text[:i])[0] < rect.width and i < len(text):
      i += 1

    # if we've wrapped the text, then adjust the wrap to the last word      
    if i < len(text): 
      i = text.rfind(" ", 0, i) + 1

    # render the line and blit it to the surface
    image = font.render(text[:i], False, color)

    surface.blit(image, (rect.left, y))
    y += fontHeight + lineSpacing

    # remove the text we just blitted
    text = text[i:]

  return text

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
  
    canvas = self.format_card(card)

    # Finally, add the MPC extended border and save the image
    border = pygame.image.load("template-data/basic/border-extend.png")
    canvas.blit(border, (0,0))
    self.add_text(canvas, card)
    pygame.image.save(canvas, "output/" + Cards.parse_card_name(card["name"]) + ".png")
    return True

  def executeBasic(self, card):
    super().execute(card)
    pygame.image.save(self.format_card(card, base=0), "output/" + Cards.parse_card_name(card["name"]) + ".png")

  def format_card(self, card, base=150):
    """
    Format the entire card, does not add text. Just the template and the card art and returns it

    PARAMETERS:
     - card: The card to be formatted and returned
     - base: Where the card should be placed on the returned canvas. Do either 150 (for MPC) or 0 (for regular)

    RETURNS
     - A pygame Surface of the card, centered if set for MPC
    """
    card_type = card["type_line"]
    colours = card["colors"]

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
      background = pygame.image.load("template-data/basic/background/land.png")
      title_box = pygame.image.load("template-data/basic/title-boxes/land.png")

      # Determine land text colours by the mana they produce, or if they are an artifact
      if "Artifact" in card_type:
        text_t = "artifact"
      elif "produced_mana" in card:
        temp = card["produced_mana"] # Store temporary list, to handle fetchlands and stuff
        text_t = self.get_file_name_colour(temp, 3)
      # Default to land
      else:
        text_t = "land"
      text_box = pygame.image.load("template-data/basic/land-textboxes/" + text_t + ".png")

    else:
      # Determine the background, text-boxes, and title-boxes from the colours and types
      if "Artifact" in card_type:
        back_t = "artifact"
      else:
        back_t = self.get_file_name_colour(colours, 2)
      text_t = self.get_file_name_colour(colours, 3)
      title_t = self.get_file_name_colour(colours, 2) # The title does not care about artifact
      background = pygame.image.load("template-data/basic/background/" + back_t + ".png")
      title_box = pygame.image.load("template-data/basic/title-boxes/" + title_t + ".png")
      text_box = pygame.image.load("template-data/basic/nonland-textboxes/" + text_t + ".png")

    # Load the card art
    card_art_path = Cards.get_card_art_crop(card)
    if card_art_path == None:
      return False
    card_art = pygame.image.load(card_art_path)

    # By the template, the image should be about 2294x1686 and be placed at (200,420) + base
    # For now, just directly resize it without worrying about scale
    card_art = Cards.dynamically_scale_card(card_art, (2294, 1686))

    # Now create an output canvas of the proper size, draw things to it
    canvas = pygame.Surface((2682+2*base,3744+2*base))
    canvas.fill((255,255,255))  # Fill the canvas with white, before drawing to it
    canvas.blit(card_art, (200+base, 420+base))
    canvas.blit(background, (base, base))
    if nyx:
      canvas.blit(pygame.image.load("template-data/basic/nyx-border.png"), (base, base))
    canvas.blit(text_box, (base, base))
    canvas.blit(title_box, (base, base))

    return self.add_text(canvas, card, base=base)

  def add_text(self, canvas, card, base=150, flavour_text=True):
    """
    Finishes up card creation by adding all the relevant text to the card.

    PARAMETERS:
     - canvas: The current card, formatted with the image already loaded
     - card: The card object
     - base: An offset for all the text. Do 150 for MPC format and 0 for regular format
     - flavour_text: If you want flavour text or not

    RETURNS:
     - The completed canvas, to be saved as a png file to output
    """

    # For now, write a bunch of tests to make sure it actually works
    write(canvas, card["name"], 220+base, 230+base, 140, bold=True)
    write(canvas, card["type_line"], 220+base, 2170+base, 120, bold=True)
    #write(canvas, card["oracle_text"], 230+base, 2374+base, 120)
    # Some additional height of the text box for noncreatures
    nc = 0
    if "Creature" not in card["type_line"]:
      nc = 220
    write_wrapped(canvas, card["oracle_text"], (230+base, 2464+base, 2200+base, 3200+nc+base), FONTS_BASIC[130])
    return canvas

  def get_file_name_colour(self, l, gold=2):
    """
    Return the colour by the list of colours (by dictionary["CardName"]["colors"])
    in a format that can be directly used to find a file

    PARAMETERS:
     - l: the list of colours of the card object
     - gold: When the length of the list just returns "gold", either 2 or 3

    RETURNS:
     - The word representing the colour (Of the set {white,blue,black,red,green,gold})
    """
    if len(l) >= gold:
      return "gold"
    
    if len(l) == 1:
      mono = {
        "W":"white",
        "U":"blue",
        "B":"black",
        "R":"red",
        "G":"green",
        "C":"land" # A special check for colourless lands
      }
      if l[0] in mono:
        return mono[l[0]]
      else:
        # Default to artifacts for now
        return "artifact" 

    # Handle two colours, for text boxes, I feel like there are way better ways to do this with list comprehension
    if "W" in l:
      if "U" in l:
        return "wu"
      if "B" in l:
        return "wb"
      if "R" in l:
        return "rw"
      if "G" in l:
        return "gw"
    if "U" in l:
      if "B" in l:
        return "ub"
      if "R" in l:
        return "ur"
      if "G" in l:
        return "gu"
    if "B" in l:
      if "R" in l:
        return "br"
      if "G" in l:
        return "bg"
    if "R" and "G" in l:
      return "rg"
    return "artifact"   # Default to artifact for now, dont have colourless yet




