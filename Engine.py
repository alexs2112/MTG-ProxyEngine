import json, sys, os
import Updater, Cards, Decklist, Template, Autofill


def print_cmd_arguments():
  print("""Help:
Functions:
  -help
  -update {all|bulk|cards|ser} (ex: -update all)
  -decklist Filepath
  -card [Card Name]
  -art [Card Name]              (just the card art)
  -artlist Filepath             (card art for the entire list)
  -autofill                     (clear autofill text from all files in autofill dir)
  -print_decklist Filepath true/false   (print condensed contents of a decklist in alphabetical order)
                                (true means each card is printed as a 1 of)

Flags:
  -noverbose                    (verbose is on by default)
  -basic                        (not formatted for MPC)
  -autoproxy                    (Set a flag to format art output 
                                 titles for the autoproxy tool)

Examples:
  python Engine.py -update all
  python Engine.py -decklist decklist.txt
  python Engine.py -card [Lightning Bolt]
  python Engine.py -autoproxy -artlist decklist.txt

If this is your first time running the engine,
you need to update all to build the necessary
local database

Art is saved to ProxyEngine/data/scryfall/card-art by default""")

def construct_card(name, database, template, basic=False):
  """
  A helper function to actually construct the card by name and template
  Will format the card and place it in output under its name

  If the card cannot be found in the local database, will print an error message

  PARAMETERS:
   - name: the card name as a string, this is case and punctuation sensitive
   - template: the template to use when formatting the card
   - basic: if the card should be formatted for MPC or not (default to MPC formatting)

  RETURNS:
   - True if the card could be constructed and placed in output, False if the card
     name could not be found in the local database
  """
  if name not in database:
    print("Cannot find " + name + " in local database")
    return False
  
  if basic:
    template.executeBasic(database[name])
  else:
    template.execute(database[name])
  return True

if __name__ == "__main__":
  def main():
    # Get cmd arguments
    args = sys.argv[1:]
    
    if len(args) == 0 or "-help" in args:
      print_cmd_arguments()
      return

    # Set a verbose tag to pass into other functions
    verbose = True
    if "-noverbose" in args:
      verbose = False

    # Set a tag to format for MPC or basic
    basic = False
    if "-basic" in args:
      basic = True

    # Set a tag to format art filenames as <CardName> (<ArtistName>).png
    autoproxy_format = False
    if "-autoproxy" in args:
      autoproxy_format = True

    # Handle updating
    if "-update" in args:
      i = args.index("-update")
      if len(args) <= i+1:
        print("Missing type of update")
        print("Correct Function: -update {all|bulk|cards|ser}")
        return
      if args[i+1] == "all":
        Updater.update(bulk=True,cards=True,cards_finalize=True, verbose=verbose)
      elif args[i+1] == "bulk":
        Updater.update(bulk=True,cards=False,cards_finalize=False, verbose=verbose)
      elif args[i+1] == "cards":
        Updater.update(bulk=False,cards=True,cards_finalize=False, verbose=verbose)
      elif args[i+1] == "ser":
        Updater.update(bulk=False,cards=False,cards_finalize=True, verbose=verbose)
      else:
        print("Incorrect type of update")
        print("Correct Function: -update {all|bulk|cards|ser}")
        return

    d = {}
    # Fix this ugly if condition later
    if "-decklist" in args or "-card" in args or "-art" in args or "-artlist" in args or "-autofill" in args:
      d = Cards.deserialize_all_cards()
      if d == {}:
        print("Cannot find all-cards.ser")
        return
      
      # Later allow the user to select a template
      t = Template.BasicModern(d)

    if "-decklist" in args:
      i = args.index("-decklist")
      if len(args) <= i+1:
        print("Missing filepath to decklist")
        print("Correct Function: -decklist filepath/filename.txt")
        return

      # Find that decklist, load it, and then execute on every card
      path = args[i+1]
      deck = Decklist.load_decklist_from_file(path)
      if deck == {}:
        # Could not find the decklist
        return
      for key in deck:
        construct_card(key, d, t, basic=basic)

    if "-card" in args:
      i = args.index("-card")
      if len(args) <= i+1:
        print("Missing card to generate")
        print("Correct Function: -card [Card Name]")
        return

      # Do some rudimentary handling of a card name, this probably sucks
      name = args[i+1][1:]
      if name[-1] == "]":
        # Account with names that only have 1 word
        name = name[:-1]
      else:
        for n in range(i+2, len(args)):
          if "]" in args[n]:
            name += " " + args[n][:-1]
            break
          name += " " + args[n]
      
      # Then construct the card given in the command line
      construct_card(name, d, t, basic=basic)
    
    if "-art" in args:
      i = args.index("-art")
      if len(args) <= i+1:
        print("Missing card art to fetch")
        print("Correct Function: -art [Card Name]")
        return

      # Do some rudimentary handling of a card name
      name = args[i+1][1:]
      if name[-1] == "]":
        # Account with names that only have 1 word
        name = name[:-1]
      else:
        for n in range(i+2, len(args)):
          if "]" in args[n]:
            name += " " + args[n][:-1]
            break
          name += " " + args[n]
      Cards.get_card_art_crop(d[name], autoproxy_format)

    if "-artlist" in args:
      i = args.index("-artlist")
      if len(args) <= i+1:
        print("Missing filepath to list")
        print("Correct Function: -artlist filepath/filename.txt")
        return

      # Find that decklist, load it, and then execute on every card
      path = args[i+1]
      deck = Decklist.load_decklist_from_file(path)
      if deck == {}:
        # Could not find the decklist
        return
      for key in deck:
        Cards.get_card_art_crop(d[key], autoproxy_format)

    if "-autofill" in args:
      # Go over every image in the autofill directory and remove the mpcautofill text
      Autofill.remove_autofill(d, verbose)

    if "-print_decklist" in args:
      i = args.index("-print_decklist")
      if len(args) <= i+1:
        print("Missing filepath to decklist")
        print("Correct Function: -print_decklist filepath/filename.txt [true/false]")
        return

      only_one_of_each = False
      if len(args) > i+2:
        if args[i+2] == "true":
          only_one_of_each = True

      # Find that decklist, load it, and then execute on every card
      path = args[i+1]
      deck = Decklist.load_decklist_from_file(path)
      if deck == {}:
        # Could not find the decklist
        return
      Decklist.print_decklist(deck, only_one_of_each)

    if "-compare_decklist" in args:
      i = args.index("-compare_decklist")
      if len(args) <= i+2:
        print("Missing filepath to decklists")
        print("Correct Function: -compare_decklist decklist.txt compare.txt")
        return

      deck1 = Decklist.load_decklist_from_file(args[i+1])
      deck2 = Decklist.load_decklist_from_file(args[i+2])
      Decklist.compare_decklist(deck1, deck2)
      

  main()
    