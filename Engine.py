import json, sys, os
import Updater, Cards, Decklist, Template


def print_cmd_arguments():
  print("""Arguments:
  -help
  -update {all|bulk|cards|ser} (ex: -update all)
  -decklist Filepath
  -card [Card Name]
  -noverbose                   (verbose is on by default)
  -basic                       (not formatted for MPC)

Examples:
  python Engine.py -update all
  python Engine.py -decklist decklist.txt
  python Engine.py -card [Lightning Bolt]

If this is your first time running the engine,
you need to update all to build the necessary
local database""")

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
    #print(args)
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
    if "-decklist" in args or "-card" in args:
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
        print("Correct Function: -decklist [Card Name]")
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
  main()
    
    
    
    




  


  
  