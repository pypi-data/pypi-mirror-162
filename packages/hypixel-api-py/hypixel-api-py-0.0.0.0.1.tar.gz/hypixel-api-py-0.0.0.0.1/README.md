# Hypixel API PY

Hypixel API PY is a Python Package used to interact with the Hypixel API

### Current Features:

###### General Features:

- ```Convert between UUID and Username```

###### Player Features:

- ```Get Player's First and Last Login Dates as well as their Last Logout Date```
- ```Get Player's Rank```
- ```Get Player's Friends```

###### Guild Features:
- ```Get Guild By ID, Player or Name```
- ```Get Guild Members```
- ```Get Guild Coins and EXP```
- ```Get Guild Members and Ranks```
- ```Get Guild Tag and preferred Games```

###### API Key Features:

- ```Get Username and UUID from API Key```
- ```Get API Key Information such as Request Limit, Total Requests and Requests in the last Minute```


### Usage:
First, go on Hypixel, run the command ```/api new``` and save the Key you get in chat.

After that, download the Package using:
```commandline
pip install hypixel-api-py
```

Then Import the Package:
```python
import hypixel_api
```

To connect to the Hypixel API you first need to create a Hypixel Object and initialize it with your API Key:
```python
connection = hypixel_api.Hypixel(your_api_key)
```

You can verify that your authentication has worked by using the created Player Object:
```python
owner = connection.owner
print(f"Authenticated as {owner.username} ({owner.UUID}) with the key {connection.key}")
```

To start accessing player data, create a Player Object by using a UUID:
```python
player = hypixel_api.Player(your_uuid)
```
You can also convert a Username to a UUID:
```python
from hypixel_api.utilities import UUID_from_username
player = hypixel_api.Player(hypixel_api.UUID_from_username(your_username))
```
After that, call the get_data() Method to obtain Player Data:
```python
player.get_data(connection)
```
Finally, print out your data:
```python
print(player.rank)
```
