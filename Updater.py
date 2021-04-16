import requests, json, time, os
import os.path as path
import Cards

# Some Static Strings
BULK_DATA_FILE = "data/bulk-data.json"
BULK_DATA_PATH = "https://api.scryfall.com/bulk-data"
ALL_CARDS_FILE = "data/all-cards.json"

def request_scryfall_data(url, filename, verbose=True):
  """
  A basic way to request data from scryfall and store it in file in data

  PARAMETERS:
   - url: The full https path to the file you wish to access (such as https://api.scryfall.com/bulk-data)
   - filename: The name of the resulting file
   - verbose: How much info you want to print to the terminal
  """

  # Wait 0.1 seconds every request as to not flood scryfall and get IP banned. This is per their request
  time.sleep(0.1)

  r = requests.get(url)
  if verbose:
    print(" - Connecting to " + url)

  f = open(filename, 'wb')
  f.write(r.content)
  if verbose:
    print(" - Writing Data...")

  f.close()
  if verbose:
    print(" - Closing Connection")

def get_all_cards_json(cards=0, verbose=True):
  """
  Reads the bulk-data.json file to determine the url to get the json file

  PARAMETERS:
   - Cards: An index of data in bulk-data, by scryfall:
   - 0: A JSON file containing one Scryfall card object for each Oracle ID on Scryfall. The chosen sets for the cards are an attempt to return the most up-to-date recognizable version of the card.
   - 1: A JSON file of Scryfall card objects that together contain all unique artworks. The chosen cards promote the best image scans.
   - 2: A JSON file containing every card object on Scryfall in English or the printed language if the card is only available in one language.
   - 3: A JSON file containing every card object on Scryfall in every language.
   - 4: A JSON file containing all Rulings on Scryfall. Each ruling refers to cards via an `oracle_id`.
  """

  if verbose:
    print("Reading " + BULK_DATA_FILE)
  if not path.exists(BULK_DATA_FILE):
    # Always print these regardless of verbose
    print(BULK_DATA_FILE + " does not exist!")
    print("Aborting!")
    return

  # Otherwise open and read the file
  f = open(BULK_DATA_FILE)
  bulk_data_string = f.read()
  f.close()

  # Load the file into a dictionary
  if verbose:
    print("Loading JSON...")
  bulk_data = json.loads(bulk_data_string)

  # Then we want to determine the proper download_uri from the bulk data
  # Currently the only field we care about is the download_uri, we can update this later
  all_cards_uri = bulk_data["data"][cards]["download_uri"]

  # Then request that scryfall data and save it as all-cards.json
  if verbose:
    print("Fetching Scryfall Card Database...")
  request_scryfall_data(all_cards_uri, ALL_CARDS_FILE, verbose=verbose)

def check_directories(verbose=True):
  """
  Make sure that all the proper directories exist to store data. 
  I feel like there has to be an easier way to do this

  PARAMETERS
   - verbose: If you would like to see all messages printed to the terminal
  """
  mkc = False   # Keep track of changes made to inform the user
  if not path.exists("data"):
    mkc = True
    os.mkdir("data")
  if not path.exists("data/scryfall"):
    mkc = True
    os.mkdir("data/scryfall")
  if not path.exists("data/scryfall/card-art"):
    mkc = True
    os.mkdir("data/scryfall/card-art")
  if not path.exists("data/scryfall/full-cards"):
    mkc = True
    os.mkdir("data/scryfall/full-cards")

  if verbose and mkc:
    print("Some folders were missing! They have been created!")

def update(bulk=True,cards=True,cards_finalize=True,verbose=True):
  """
  Update the local database by pulling info from scryfall.

  I would recommend leaving all parameters as their default of True, the option to set
  them to False is for debugging purposes.

  PARAMETERS:
   - bulk: Download Scryfall's bulk data, which gives a temporary link to download all cards
   - cards: Use data/bulk-data.json to update data/all-cards.json.
   - cards_finalize: Load and serialize data/all-cards.json to data/all-cards.ser, for quicker access between sessions
   - verbose: If you would like to see all messages printed to the terminal
  """

  if verbose:
    print("Updating Local Database")

  # First we need to make sure that all folders are properly arranged
  check_directories(verbose=verbose)

  # Fetch scryfall bulk data and store it in data
  if bulk:
    if verbose:
      print("Fetching Bulk Data...")
    request_scryfall_data(BULK_DATA_PATH, BULK_DATA_FILE, verbose=verbose)
  
  # Read from bulk data, get the URI to download all cards as a JSON file
  if cards:
    get_all_cards_json(0, verbose=verbose)
  
  # Serialize all scryfall data into an easier to parse format
  if cards_finalize:
    Cards.serialize_all_cards(verbose=verbose)
  
    
    


  
  