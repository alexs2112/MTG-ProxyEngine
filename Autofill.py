import os, pygame, math

"""
Simply remove the mpcautofill text from all files in the autofill directory
as it clashes with our previous proxies
"""
def remove_autofill(database, verbose=True):
  # First make sure the directory exists, create it if it does not
  if not os.path.exists("autofill"):
    os.mkdir("autofill")
    if verbose:
      print("Could not find autofill directory, creating and exiting")
      return False

  # Keep track of all the broken cards, print them at the end
  broken = []

  cards = os.listdir("autofill/")
  # if verbose:
  #   print("Working Directory:")
  #   print(cards)

  mask = pygame.Surface((610, 100))
  mask.fill((0,0,0))

  # for card in cards:
  for i in range(len(cards)):
    card = cards[i]
    cardname, ext = os.path.splitext(card)
    if ext not in ['.png', '.jpg']:
      continue

    if cardname not in database:
      if verbose:
        print("[****] Cannot find " + cardname + " in local database!")
        broken.append(cardname)
        continue
    
    if verbose:
      percentage = math.floor((i / len(cards)) * 100)
      prefix = '['
      if percentage < 100:
        prefix = prefix + ' '
      if percentage < 10:
        prefix = prefix + ' '
      prefix = prefix + str(percentage) + '%] '
      print(prefix + cardname)

    # Creatures, Planeswalkers, and Vehicles need the mask lowered to account for an extra p/t/loyalty box
    image = pygame.image.load('autofill/' + card)
    type_line = database[cardname]["type_line"]
    if "Creature" in type_line or "Vehicle" in type_line or "Planeswalker" in type_line:
      y = 4140
    else:
      y = 4064

    image.blit(mask, (2352, y))  # 4064 for non-creatures

    pygame.image.save(image, 'autofill/' + card)
  print("[100%] Complete!")
  if len(broken) > 0:
    print("\nMissing Cards:")
    for card in broken:
      print(card)
  
