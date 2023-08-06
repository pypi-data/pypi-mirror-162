from Exceptions import Exceptions
import requests, json
class Games:
  def get_universe_id(gameID):
    API_URL = f"https://api.roblox.com/universes/get-universe-containing-place?placeid={gameID}"
    API_CONTENT = requests.get(API_URL).text
    API_JSON = json.loads(API_CONTENT)
    if "error" in API_JSON:
      raise Exceptions.Exceptions.InvalidGameError(game=gameID)
    else:
      return API_JSON['UniverseId']
  def get_place_id_by_universe_id(universeID):
    """
    This function will convert the PlaceID to the UniverseID. 
    """
    API_URL = f"https://games.roblox.com/v1/games?universeIds={universeID}"
    API_CONTENT = requests.get(API_URL).text
    API_JSON = json.loads(API_CONTENT)
    return API_JSON['data'][0]['id']
  def get_game_description_by_id(gameID):
    try:
      API_URL = f"https://games.roblox.com/v1/games?universeIds={Games.get_universe_id(gameID)}"
      API_CONTENT = requests.get(API_URL).text
      API_JSON = json.loads(API_CONTENT)
      return API_JSON['data'][0]["description"]
    except KeyError:
      raise Exceptions.InvalidGameError(game=gameID)
  def get_game_name_by_id(gameID):
    try:
      API_URL = f"https://games.roblox.com/v1/games?universeIds={Games.get_universe_id(gameID)}"
      API_CONTENT = requests.get(API_URL).text
      API_JSON = json.loads(API_CONTENT)
      return API_JSON['data'][0]["name"]
    except KeyError:
      raise Exceptions.InvalidUniverseIDError(id=Games.get_universe_id(gameID))
  def get_owner_of_game_by_id(gameID):
    try:
      API_URL = f"https://games.roblox.com/v1/games?universeIds={Games.get_universe_id(gameID)}"
      API_CONTENT = requests.get(API_URL).text
      API_JSON = json.loads(API_CONTENT)
      return API_JSON['data'][0]['creator']["name"]
    except KeyError:
      raise Exceptions.InvalidGameError(gameID)
  def get_playing_count_by_id(gameID):
    try:
      API_URL = f"https://games.roblox.com/v1/games?universeIds={Games.get_universe_id(gameID)}"
      API_CONTENT = requests.get(API_URL).text
      API_JSON = json.loads(API_CONTENT)
      return API_JSON['data'][0]["playing"]
    except KeyError:
      raise Exceptions.InvalidUniverseIDError(id=Games.get_universe_id(gameID))
  def get_visits_by_id(gameID):
    try:
      API_URL = f"https://games.roblox.com/v1/games?universeIds={Games.get_universe_id(gameID)}"
      API_CONTENT = requests.get(API_URL).text
      API_JSON = json.loads(API_CONTENT)
      return API_JSON['data'][0]['visits']
    except KeyError:
      raise Exceptions.InvalidGameError(game=gameID)
  def get_placeid_by_universeid(universeID):
    try:
      API_URL = f"https://games.roblox.com/v1/games?universeIds={universeID}"
      API_CONTENT = requests.get(API_URL).text
      API_JSON = json.loads(API_CONTENT)
      return API_JSON["data"][0]["rootPlaceId"]
    except KeyError:
      raise Exceptions.InvalidUniverseIDError(id=universeID)

def get_game_owner_type_by_id(gameID):
  """
  This function will get the owner of the game's type, it can be a Group or a User.
  """
  try:
    API_URL = f"https://games.roblox.com/v1/games?universeIds={Games.get_universe_id(gameID)}"
    API_CONTENT = requests.get(API_URL).text
    API_JSON = json.loads(API_CONTENT)
    return API_JSON['data'][0]['creator']['type']
  except KeyError:
    raise Exceptions.InvalidGameError(game=gameID)