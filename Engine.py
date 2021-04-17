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
    if "-decklist" in args:
      i = args.index("-decklist")
      if len(args) <= i+1:
        print("Missing filepath to decklist")
        print("Correct Function: -decklist filepath/filename.txt")
        return
      
      d = Cards.deserialize_all_cards()
      if d == {}:
        # Cannot find the serialized file
        return

      # Later allow the user to select a template
      t = Template.BasicModern(d)

      # Find that decklist, load it, and then execute on every card
      path = args[i+1]
      deck = Decklist.load_decklist_from_file(path)
      if deck == {}:
        # Could not find the decklist
        return
      for key in deck:
        if key in d:
          if basic:
            t.executeBasic(d[key])
          else:
            t.execute(d[key])
        else:
          print("Could not find " + key)

    if "-card" in args:
      i = args.index("-card")
      if len(args) <= i+1:
        print("Missing card to generate")
        print("Correct Function: -decklist [Card Name]")
        return

      # Try to open the full database
      if d == {}:
        d = Cards.deserialize_all_cards()
        if d == {}:
          # Cannot find the serialized file
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
      
      # Later allow the user to select a template
      t = Template.BasicModern(d)
      if basic:
        t.executeBasic(d[name])
      else:
        t.execute(d[name])
  main()
    
    
    
    




  


  
  