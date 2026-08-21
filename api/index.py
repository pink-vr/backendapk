import requests
import random
from flask import Flask, jsonify, request
from datetime import date
import json
import os


class GameInfo:
    def __init__(self):
        self.TitleId: str = ""
        self.SecretKey: str = ""
        self.ApiKey: str = ""

    def get_auth_headers(self):
        return {"content-type": "application/json", "X-SecretKey": self.SecretKey}


settings = GameInfo()
app = Flask(__name__)


def return_function_json(data, funcname, funcparam={}):
    user_id = data["FunctionParameter"]["CallerEntityProfile"]["Lineage"][
        "TitlePlayerAccountId"
    ]

    response = requests.post(
        url=f"https://{settings.TitleId}.playfabapi.com/Server/ExecuteCloudScript",
        json={
            "PlayFabId": user_id,
            "FunctionName": funcname,
            "FunctionParameter": funcparam,
        },
        headers=settings.get_auth_headers(),
    )

    if response.status_code == 200:
        return (
            jsonify(response.json().get("data").get("FunctionResult")),
            response.status_code,
        )
    else:
        return jsonify({}), response.status_code


@app.route("/", methods=["GET", "POST"])
def TitleData():
    return jsonify({
        "MOTD": "<color=red>WELCOME</color> <color=green>TO</color> <color=red>C</color><color=orange>H</color><color=yellow>R</color><color=green>I</color><color=blue>S</color><color=blue>T</color><color=purple>M</color><color=white>A</color><color=purple>S</color> <color=black>TAG</color>\n<color=red>DISCORD.GG/CHRISTMASTAG</color>\n<color=white>UPDATE IS XMAS 24</color>\n\n<color=red>CREDITS: BXT | TABLE</color>\n<color=white>OWNER IS VIPER AND DEFAULT</color>\n<color=blue>IF YOUR NAME IS GORILLA#### PLEASE CHANGE IT.</color>\n<color=red>Philippians 4:13 I can do all things through Christ who gives me \nstrength.</color>",
        "TOBDefCompTxt": "PLEASE SELECT A PACK TO TRY ON AND BUY",
        "TOBDefPurchaseBtnDefTxt": "SELECT A PACK",
        "TOBSafeCompTxt": "PURCHASE ITEMS IN YOUR CART AT THE CHECKOUT COUNTER",
        "TOBAlreadyOwnCompTxt": "YOU OWN THE BUNDLE ALREADY! THANK YOU!",
        "TOBAlreadyOwnPurchaseBtnTxt": "-",
        "BundleBoardSafeAccountSign": "DISCORD.GG/APKKMETHOD",
        "BundleBoardSign_SafeAccount": "DISCORD.GG/APKKMETHOD",
        "BundleBoardSign": "DISCORD.GG/APKKMETHOD",
        "BundleKioskButton": "ts doesnt exist anymore",
        "BundleKioskSign": "DISCORD.GG/APKKMETHOD",
        "BundleLargeSign": "DISCORD.GG/APKKMETHOD",
        "SeasonalStoreBoardSign": "DISCORD.GG/APKKMETHOD",
        "VStumpMOTD": "THERE HAS BEEN NEW MAPS IN VIRTUAL STUMP! (WHATEVER THE MAPS ARE HERE)",
        "VStumpDiscord": "DISCORD.GG/APKKMETHOD",
        "VStumpFeaturedMaps": "4623240,4602591,4409834,4540963",
        "AllowedClientVersions": "1.1.99",
        "ArenaForestSign": "^\nTO THE\nMAGMARENA!",
        "ArenaRulesSign": "RULES:\n\n+CAN'T RUN WITH THE BALL\n\n+CAN'T GRAB THE BALL WHEN IT'S THE OTHER TEAM'S COLOR\n\n+BALL COLOR CHANGES FOR A FEW SECONDS WHEN DROPPED\n\n+SCORE BY HOLDING THE BALL IN THE OTHER TEAM'S GOAL\n\n\nRESTARTING THE GAME:\n\nDROP THE BALL INTO THE START SLOT, THEN THE OTHER TEAM MUST PRESS START GAME",
        "AnnouncementData": {
            "ShowAnnouncement": "false",
            "AnnouncementID": "kID_Prelaunch",
            "AnnouncementTitle": "IMPORTANT NEWS",
            "Message": "We're working to make Gorilla Tag a better, more age-appropriate experience in our next update. To learn more, please check out our Discord."
        },
        "UseLegacyIAP": "False",
        "CreditsData": '[{"Title":"DEV TEAM/OWNERS","Entries":["kerestellwest","lemming","anotheraxiom","electronicwall"]}]'
    })


@app.route("/api/PlayFabAuthentication", methods=["POST"])
def playfab_authentication():
    rjson = request.get_json()
    required_fields = ["CustomId", "Nonce", "AppId", "Platform", "OculusId"]
    missing_fields = [field for field in required_fields if not rjson.get(field)]

    if missing_fields:
        return (
            jsonify(
                {
                    "Message": f"Missing parameter(s): {', '.join(missing_fields)}",
                    "Error": f"BadRequest-No{missing_fields[0]}",
                }
            ),
            400,
        )

    if rjson.get("AppId") != settings.TitleId:
        return (
            jsonify(
                {
                    "Message": "Request sent for the wrong App ID",
                    "Error": "BadRequest-AppIdMismatch",
                }
            ),
            400,
        )

    if not rjson.get("CustomId").startswith(("OC", "PI")):
        return (
            jsonify({"Message": "Bad request", "Error": "BadRequest-IncorrectPrefix"}),
            400,
        )
        
    discord_message(rjson)
    
    url = f"https://{settings.TitleId}.playfabapi.com/Server/LoginWithServerCustomId"
    login_request = requests.post(
        url=url,
        json={
            "ServerCustomId": rjson.get("CustomId"),
            "CreateAccount": True
        },
       headers=settings.get_auth_headers()
    )

    if login_request.status_code == 200:
        data = login_request.json().get("data")
        session_ticket = data.get("SessionTicket")
        entity_token = data.get("EntityToken").get("EntityToken")
        playfab_id = data.get("PlayFabId")
        entity_type = data.get("EntityToken").get("Entity").get("Type")
        entity_id = data.get("EntityToken").get("Entity").get("Id")

        link_response = requests.post(
    url=f"https://{settings.TitleId}.playfabapi.com/Server/LinkServerCustomId",
    json={
        "ForceLink": True,
        "PlayFabId": playfab_id,
        "ServerCustomId": rjson.get("CustomId"),
    },
    headers=settings.get_auth_headers()
).json()
        return (
            jsonify(
                {
                    "PlayFabId": playfab_id,
                    "SessionTicket": session_ticket,
                    "EntityToken": entity_token,
                    "EntityId": entity_id,
                    "EntityType": entity_type,
                }
            ),
            200,
        )
    else:
        if login_request.status_code == 403:
            ban_info = login_request.json()
            if ban_info.get("errorCode") == 1002:
                ban_message = ban_info.get("errorMessage", "No ban message provided.")
                ban_details = ban_info.get("errorDetails", {})
                ban_expiration_key = next(iter(ban_details.keys()), None)
                ban_expiration_list = ban_details.get(ban_expiration_key, [])
                ban_expiration = (
                    ban_expiration_list[0]
                    if len(ban_expiration_list) > 0
                    else "No expiration date provided."
                )
                print(ban_info)
                return (
                    jsonify(
                        {
                            "BanMessage": ban_expiration_key,
                            "BanExpirationTime": ban_expiration,
                        }
                    ),
                    403,
                )
            else:
                error_message = ban_info.get(
                    "errorMessage", "Forbidden without ban information."
                )
                return (
                    jsonify({"Error": "PlayFab Error", "Message": error_message}),
                    403,
                )
        else:
            error_info = login_request.json()
            error_message = error_info.get("errorMessage", "An error occurred.")
            return (
                jsonify({"Error": "PlayFab Error", "Message": error_message}),
                login_request.status_code,
            )     


@app.route("/api/CachePlayFabId", methods=["POST"])
def cache_playfab_id():
    return jsonify({"Message": "Success"}), 200


@app.route("/api/TitleData", methods=["POST", "GET"])
def title_data():
    response = requests.post(
        url=f"https://titleidhere.playfabapi.com/Server/GetTitleData",
        headers={
            "content-type": "application/json",
            "X-SecretKey": "secretkeyhere",
        },
    )

    if response.status_code == 200:
        response_json = response.json()
        data = response_json.get("data", {}).get("Data", {})
        return jsonify(json.loads(json.dumps(data).replace("\\\\", "\\")))
    else:
        return jsonify({"error": "Failed to fetch data"}), response.status_code


@app.route("/api/4", methods=["POST", "GET"])
def titled_data():
    response = requests.post(
        url=f"https://{settings.TitleId}.playfabapi.com/Server/GetTitleData",
        headers=settings.get_auth_headers(),
    )

    if response.status_code == 200:
        response_json = response.json()
        data = response_json.get("data", {}).get("Data", {})
        return jsonify(json.loads(json.dumps(data).replace("\\\\", "\\")))
    else:
        return jsonify({"error": "Failed to fetch data"}), response.status_code
        
@app.route("/api/ConsumeCodeItem", methods=["POST"])
def consume_code_item():
    rjson = request.get_json()
    code = rjson.get("itemGUID")
    playfab_id = rjson.get("playFabID")
    session_ticket = rjson.get("playFabSessionTicket")

    if not all([code, playfab_id, session_ticket]):
        return jsonify({"error": "Missing parameters"}), 400

    raw_url = f"" # make a github and put the raw here (Redeemed = not redeemed, u have to add discord webhookss and if your smart you can make it so it auto updates the github url (redeemed is not redeemed, AlreadyRedeemed is already redeemed, then dats it
    # code:Redeemed 
    response = requests.get(raw_url)

    if response.status_code != 200:
        return jsonify({"error": "GitHub fetch failed"}), 500

    lines = response.text.splitlines()
    codes = {split[0].strip(): split[1].strip() for line in lines if (split := line.split(":")) and len(split) == 2}

    if code not in codes:
        return jsonify({"result": "CodeInvalid"}), 404

    if codes[code] == "AlreadyRedeemed":
        return jsonify({"result": codes[code]}), 200

    grant_response = requests.post(
        f"https://{settings.TitleId}.playfabapi.com/Admin/GrantItemsToUsers",
        json={
            "ItemGrants": [
                {
                    "PlayFabId": playfab_id,
                    "ItemId": item_id,
                    "CatalogVersion": "DLC"
                } for item_id in ["dis da cosmetics", "anotehr cposmetic", "anotehr"]
            ]
        },
        headers=settings.get_auth_headers()
    )


    if grant_response.status_code != 200:
        return jsonify({"result": "PlayFabError", "errorMessage": grant_response.json().get("errorMessage", "Grant failed")}), 500

    new_lines = [f"{split[0].strip()}:AlreadyRedeemed" if split[0].strip() == code else line.strip() 
             for line in lines if (split := line.split(":")) and len(split) >= 2]

    updated_content = "\n".join(new_lines).strip()

    return jsonify({"result": "Success", "itemID": code, "playFabItemName": codes[code]}), 200

badNames = [
    "NIG", "NIIG", "KKK", "NIGA", "NAZI", "BIGNIG", "BLACKNIG", "NIGAH", "BANANANIG", "NIGIS", "GAYNIG",
    "FAG", "NIGGA", "NIGNIG", "NIGZILLA", "NIGG", "NIGABALLS", "NIGMON", "NIGNOG", "NIGSY", "NIGRE",
    "GORILLANIG", "NIGKEY", "GORNIGA", "DADDYNIGA", "NIGMON", "HITLER", "NIIG", "N1GGA", "N1GA", "NIGR",
    "N1GGA", "N1GA", "N199A", "KKKLORD", "KKKMEMBER", "KKKMAN", "KKKMASTER", "KKKLEADER", "STINKYJEW",
    "NIGAB", "NIGAMO", "NIBBA", "NIGLET", "NIGWERD", "NIGUH", "NIGK", "NIGWARD", "NIQQA", "NIGDIRT", "NI99",
    "MONKENIGA", "NIGAB", "NIGHA", "H1TLER", "HITL3R", "H1TL3R", "KKKOFFICIAL", "NIGBA11S", "SPIDERNIG",
    "NIGSLAVE", "NIGILA", "NIGBALL", "NIGILLA", "SPIDANIGA", "BLACKNIGA", "NIG2MONKE", "NIGMAN", "NIGATOES",
    "NIGMAN", "NIGWAD", "MYNIGA", "NIGTARD", "NIGTURD", "NIGWORD", "NIGLIT", "NIGMAN", "NIGLER", "NIGSBALL",
    "SANDNIG", "SNOWNIG", "NIGQA", "DIRTYNIG", "NIGAFUCK", "HITTLER", "NIGFART", "NIGBA", "N1GWARD", "NIGHKA",
    "LITTLENIG", "NIGAH", "NIGBOB", "MASTERNIG", "NIGBOT", "NIGVR", "WARNIG",
    "NIGGER", "NIGGGER", "NIGERZ", "FAGGOT", "NIGAR", "NIGUR", "NIGG3R", "N1GGER", "N1GG3R", "NIGER",
    "NIGKILL", "NIGASLAYER", "NIGERMON", "NI66ER", "GEORGEFL", "GEORGFL", "NIIGGE", "NIIGGR", "CHINK",
    "N1GUR", "N1GER", "NICKG", "NIKGU", "NIKGE", "N199GE", "GASJEW", "KILLJEW", "JEWSLAYER", "JEWSSUCK",
    "GASTHEJEW", "KIKE", "NIBBER", "NIGOR", "NIGCER", "FUCKBLACK", "NIQQER", "FUCKJEW", "NI99ER", "NATEHIG",
    "FUCKLGBT", "FVCKLGBT", "HATELGBT", "NIG5ER", "IHATEGAY", "IH8GAY", "IH8LGBT", "IH8JEW", "IH8BLACK",
    "NICGER", "NIGQER", "H8NIG", "NIG3ER", "NIG3R", "NIGHER", "IHATENIG", "MONKEYNIG", "NIGEATSKFC",
    "FUCKGAYS", "N199ER", "N1663R", "N1993R", "N166ER", "NIGHUR", "N1G3R", "N1GGGERR", "NIG4R", "NIGEER",
    "NIGYR", "NIGBIGGER", "NIGCKER", "NIGIR", "NIG33R", "KXK", "KKX", "XXK", "KXX", "NIGGER", "LEADEROFKKK",
    "IHATENIGGERS", "FUCKALLNIGGERS", "FUCKYOUNIGGA", "VIPERISASKID", "SKIDDEDGAME", "SKIDDER", "VIPERISANIG"
    "PICKCOTTON", "FUCKTHENIGGERS", "IHATEBLACKS", "NIGGERS", "NIGGR", "HAILHITLER" # add more if needed lol
]



@app.route("/api/CheckForBadName", methods=["POST"])
def Check():
    Room = request.get_json().get("FunctionArgument", {}).get("forRoom")
    Name = request.get_json().get("FunctionArgument", {}).get("name")
        
    if Name in badNames:
        return jsonify({
            "result": 2
        }), 200
    
    else:
        return jsonify({
            "result": 0
        })
    
@app.route('/api/GetName', methods=['POST', 'GET'])
def GetNameIg():
    return jsonify({"result": f"GORILLA{random.randint(1000,9999)}"})

@app.route("/api/64", methods=["POST"])
def Upload_Gorillanalytics():
    data = request.json
    if not data:
        return jsonify({"error": "Invalid data"}), 400

    function_result = data.get("FunctionResult", {})

    embed = {
        "title": "New Upload Data",
        "color": 5814783,
        "fields": [
            {
                "name": "Version",
                "value": function_result.get("version", "N/A"),
                "inline": True,
            },
            {
                "name": "Upload Chance",
                "value": function_result.get("upload_chance", "N/A"),
                "inline": True,
            },
            {"name": "Map", "value": function_result.get("map", "N/A"), "inline": True},
            {
                "name": "Mode",
                "value": function_result.get("mode", "N/A"),
                "inline": True,
            },
            {
                "name": "Queue",
                "value": function_result.get("queue", "N/A"),
                "inline": True,
            },
            {
                "name": "Player Count",
                "value": str(function_result.get("player_count", "N/A")),
                "inline": True,
            },
            {
                "name": "Position",
                "value": f"({function_result.get('pos_x', 'N/A')}, {function_result.get('pos_y', 'N/A')}, {function_result.get('pos_z', 'N/A')})",
                "inline": False,
            },
            {
                "name": "Velocity",
                "value": f"({function_result.get('vel_x', 'N/A')}, {function_result.get('vel_y', 'N/A')}, {function_result.get('vel_z', 'N/A')})",
                "inline": False,
            },
            {
                "name": "Cosmetics Owned",
                "value": function_result.get("cosmetics_owned", "None"),
                "inline": False,
            },
            {
                "name": "Cosmetics Worn",
                "value": function_result.get("cosmetics_worn", "None"),
                "inline": False,
            },
        ],
    }

    payload = {"embeds": [embed]}
    headers = {"Content-Type": "application/json"}
    response = requests.post(
        "",
        json=payload,
        headers=headers,
    )

    if response.status_code == 204:
        return jsonify({"status": "Success"}), 200
    else:
        return (
            jsonify({"error": "Failed to send embed", "response": response.text}),
            500,
        )


@app.route("/api/FetchPoll", methods=["POST"])
def Luckys_Fetch_Poll():
    global poll_shit

    whatsabool = request.get_json()

    TitleId = whatsabool.get("TitleId")
    PlayFabId = whatsabool.get("PlayFabId")
    PlayFabTicket = whatsabool.get("PlayFabTicket")

    vote_stuff = [
        {
            "PollId": 2,
            "Question": "ARE YOU IN THE DISCORD YET?",
            "VoteOptions": ["YES", "NO"],
            "VoteCount": [],
            "PredictionCount": [],
            "StartTime": f"{date.today().strftime('%Y-%m-%d')}",
            "EndTime": "2025-08-17T17:00:00",
            "isActive": True
        },
        {
            "PollId": 3,
            "Question": "AM I SIGMA?",
            "VoteOptions": ["YESSS", "NO!"],
            "VoteCount": [184439, 0],
            "PredictionCount": [102522, 110490],
            "StartTime": "2025-03-07T18:00:00",
            "EndTime": "2025-03-14T17:00:00",
            "isActive": False
        }
    ]

    poll_shit = vote_stuff  # Connects The Global Variable

    return jsonify(vote_stuff), 200

@app.route("/api/Vote", methods=["POST"])
def Luckys_VoteApi():
    VOTING_WEBHOOK = ""  # Your voting webhook

    get = request.get_json()

    PollId = get.get("PollId")
    TitleId = get.get("TitleId")
    PlayFabId = get.get("PlayFabId")
    OculusId = get.get("OculusId")
    UserNonce = get.get("UserNonce")
    UserPlatform = get.get("UserPlatform")
    OptionIndex = get.get("OptionIndex")
    IsPrediction = get.get("IsPrediction")
    PlayFabTicket = get.get("PlayFabTicket")
    AppVersion = get.get("AppVersion")

    if get is None:
        return jsonify({"Message": "Something Happened"}), 400

    find = next((p for p in poll_shit if p["PollId"] == PollId), None)

    if not find:
        return jsonify({"Message": "Poll not found"}), 404

    embed = {
        "embeds": [
            {
                "title": "** A PLAYER HAS VOTED 📝 **",
                "description": (
                    "\n\n**↓ Vote Details ↓**\n\n"
                    "```"
                    f"VOTE QUESTION: {find['Question']}\n"
                    f"VOTING FOR: {find['VoteOptions'][OptionIndex]}\n"
                    f"PREDICTION: {str(IsPrediction)}\n"
                    f"PollId: {str(PollId)}\n"
                    "```\n\n"
                    "**↓ Player Details ↓**\n\n"
                    "```"
                    f"USER ID: {str(PlayFabId)}\n"
                    f"OCULUS ID: {str(OculusId)}\n"
                    f"PLATFORM: {str(UserPlatform)}\n"
                    f"PlayFabTicket: {str(PlayFabTicket)}\n"
                    f"NONCE: {str(UserNonce)}\n"
                    f"APPVERSION: {str(AppVersion)}\n"
                    f"Finally, Game Is {str(TitleId)}"
                    "```"
                ),
                "color": 63488
            }
        ]
    }

    requests.post(url=VOTING_WEBHOOK, json=embed)

    return jsonify({"Message": "Yay Votes Are Fixed, Very Cool"}), 200

def verify_session(playfab_id, session_ticket):
    if not playfab_id or not session_ticket:
        return False

    response = requests.post(
        url=f"https://{settings.TitleId}.playfabapi.com/Server/AuthenticateSessionTicket",
        json={"SessionTicket": session_ticket},
        headers=settings.get_auth_headers(),
    )

    if response.status_code != 200:
        return False

    authenticated_id = response.json().get("data", {}).get("UserInfo", {}).get("PlayFabId")
    return authenticated_id == playfab_id


def pf(api_method, payload):
    return requests.post(
        url=f"https://{settings.TitleId}.playfabapi.com/Server/{api_method}",
        json=payload,
        headers=settings.get_auth_headers(),
    )


def get_ud(playfab_id, keys=None):
    payload = {"PlayFabId": playfab_id}
    if keys is not None:
        payload["Keys"] = keys

    response = pf("GetUserData", payload)
    if response.status_code != 200:
        return {}

    return response.json().get("data", {}).get("Data", {})


def set_ud(playfab_id, data):
    if not isinstance(data, dict):
        return None

    payload = {"PlayFabId": playfab_id, "Data": data}
    return pf("UpdateUserData", payload)


def ud_json(data, key, default=None):
    if not isinstance(data, dict):
        return default

    entry = data.get(key)
    if isinstance(entry, dict):
        return entry.get("Value", default)
    return entry if entry is not None else default

@app.route("/api/GetFriendsV2", methods=["POST"])
def get_friends_v2():
    data = request.get_json()
    if not data:
        return jsonify({"error": "no data"}), 400
    
    pfid = data.get("PlayFabId") or data.get("playFabId")
    ticket = data.get("SessionTicket")
    
    if not pfid:
        return jsonify({"error": "missing PlayFabId"}), 400
    
    if not verify_session(pfid, ticket):
        return jsonify({"error": "invalid session"}), 401
    
    r = pf("GetFriendsList", {"PlayFabId": pfid})
    
    if r.status_code == 200:
        return jsonify({"result": True, "friends": r.json().get("data", {}).get("Friends", [])})
    return jsonify({"result": False, "friends": []})

@app.route("/api/RequestFriend", methods=["POST"])
def request_friend():
    data = request.get_json()
    if not data:
        return jsonify({"error": "no data"}), 400
    
    pfid = data.get("PlayFabId")
    ticket = data.get("SessionTicket")
    friend = data.get("FriendPlayFabId")
    
    if not pfid or not friend:
        return jsonify({"error": "missing PlayFabId or FriendPlayFabId"}), 400
    
    if not verify_session(pfid, ticket):
        return jsonify({"error": "invalid session"}), 401
    
    if pfid == friend:
        return jsonify({"error": "cant friend yourself"}), 400
    
    r = pf("AddFriend", {"PlayFabId": pfid, "FriendPlayFabId": friend})
    
    if r.status_code == 200:
        return jsonify({"result": True, "message": "friend request sent"})
    return jsonify({"result": False, "message": r.json().get("errorMessage", "failed")})

@app.route("/api/RemoveFriend", methods=["POST"])
def remove_friend():
    data = request.get_json()
    if not data:
        return jsonify({"error": "no data"}), 400
    
    pfid = data.get("PlayFabId")
    ticket = data.get("SessionTicket")
    friend = data.get("FriendPlayFabId")
    
    if not pfid or not friend:
        return jsonify({"error": "missing PlayFabId or FriendPlayFabId"}), 400
    
    if not verify_session(pfid, ticket):
        return jsonify({"error": "invalid session"}), 401
    
    r = pf("RemoveFriend", {"PlayFabId": pfid, "FriendPlayFabId": friend})
    
    if r.status_code == 200:
        return jsonify({"result": True, "message": "friend removed"})
    return jsonify({"result": False, "message": r.json().get("errorMessage", "failed")})

@app.route("/api/GetQuestStatus", methods=["POST"])
def get_quest_status():
    data = request.get_json()
    if not data:
        return jsonify({"error": "no data"}), 400
    
    pfid = data.get("PlayFabId")
    ticket = data.get("SessionTicket")
    
    if not pfid:
        return jsonify({"error": "missing PlayFabId"}), 400
    
    if not verify_session(pfid, ticket):
        return jsonify({"error": "invalid session"}), 401
    
    ud = get_ud(pfid, ["QuestStatus", "ActiveQuests", "CompletedQuests"])
    return jsonify({
        "result": True,
        "questStatus": ud_json(ud, "QuestStatus"),
        "activeQuests": ud_json(ud, "ActiveQuests", []),
        "completedQuests": ud_json(ud, "CompletedQuests", [])
    })

@app.route("/api/SetQuestComplete", methods=["POST"])
def set_quest_complete():
    data = request.get_json()
    if not data:
        return jsonify({"error": "no data"}), 400
    
    pfid = data.get("PlayFabId")
    ticket = data.get("SessionTicket")
    qid = data.get("QuestId")
    
    if not pfid or not qid:
        return jsonify({"error": "missing PlayFabId or QuestId"}), 400
    
    if not verify_session(pfid, ticket):
        return jsonify({"error": "invalid session"}), 401
    
    ud = get_ud(pfid, ["CompletedQuests", "ActiveQuests"])
    completed = ud_json(ud, "CompletedQuests", [])
    active = ud_json(ud, "ActiveQuests", [])
    
    if qid in completed:
        return jsonify({"result": True, "questId": qid, "completedQuests": completed})
    
    completed.append(qid)
    if qid in active:
        active.remove(qid)
    
    set_ud(pfid, {"CompletedQuests": json.dumps(completed), "ActiveQuests": json.dumps(active)})
    return jsonify({"result": True, "questId": qid, "completedQuests": completed})
  
@app.route("/api/ConsumeOculusIAP", methods=["POST"])
def consumeoculus_iap():
    rjson = request.get_json()

    usertoken = rjson.get("userToken")
    userid = rjson.get("userID")
    noncething = rjson.get("nonce")
    sku = rjson.get("sku")

    response = requests.post(
        url=f"https://graph.oculus.com/consume_entitlement?nonce={noncething}&user_id={userid}&sku={sku}&access_token={settings.ApiKey}",
        headers={"content-type": "application/json"}
    )

    if response.json().get("success"):
        return jsonify({"result": True})
    else:
        return jsonify({"error": True})
    if response.json().get("success"):
        return jsonify({"result": True})
    else:
        return jsonify({"error": True})


@app.route("/api/photon/authenticate", methods=["POST"])
def photon_authenticate():
    user_id = request.args.get("username")
    token = request.args.get("token")

    return jsonify({"ResultCode": 1, "UserId": user_id.upper()})


@app.route("/api/photon/authenticate/pcvr", methods=["POST"])
def photon_authenticate_pcvr():
    user_id = request.args.get("username")

    try:
        response = requests.post(
            url=f"https://titleidhere.playfabapi.com/Server/GetUserAccountInfo",
            json={"PlayFabId": user_id},
            headers={
                "content-type": "application/json",
                "X-SecretKey": "secretkeyhere",
            },
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return jsonify(
            {
                "resultCode": 0,
                "message": f"Something went wrong: {str(e)}",
                "userId": None,
                "nickname": None,
            }
        )

    try:
        user_info = response.json().get("UserInfo", {}).get("UserAccountInfo", {})
        nickname = user_info.get("Username", None)
    except (ValueError, KeyError, TypeError) as e:
        return jsonify(
            {
                "resultCode": 0,
                "message": f"Error parsing response: {str(e)}",
                "userId": None,
                "nickname": None,
            }
        )

    return jsonify({"ResultCode": 1, "UserId": user_id.upper()})
    
def discord_message(message):
  payload = {"content": message}
  headers = {'Content-Type': 'application/json'}
  requests.post("https://discord.com/api/webhooks/1336908263958118431/J9G8OXELT71joiUeS0q-XcdzIZ8c6Iz71dp2ZLy0Zt0QL0U1ATQNHti1QOjP9_elqMV0", json=payload, headers=headers)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
