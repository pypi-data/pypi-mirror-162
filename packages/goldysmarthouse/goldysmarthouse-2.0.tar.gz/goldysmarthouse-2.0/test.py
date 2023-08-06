import subprocess
from goldy_smart_house import events, Client, methods
import webview
import novauniverse
from wakeonlan import send_magic_packet

#client = Client(methods.Dropbox("https://www.dropbox.com/s/a6pobjyjutvz5do/commands_1.txt?dl=0"), google_nest_speaker_ip="192.168.1.75", enable_logs=True, read_back_volume=18)
client = Client(methods.Dropbox("https://www.dropbox.com/s/a6pobjyjutvz5do/commands_1.txt?dl=0"), enable_logs=True, read_back_volume=18)

@events.on_command()
async def open_notepad():
    subprocess.Popen(["C:/Windows/System32/notepad.exe"])
    #return "Notepad open"

@events.on_command(alias_names=["how many players are online on novauniverse"])
async def check_who_is_online_on_nova():
    online_players = []
    server = novauniverse.Server()
    
    for player in server.online_players:
        online_players.append(player.name)

    amount_of_online_players = len(online_players)
    
    if amount_of_online_players == 0:
        return "No one is online."

    if amount_of_online_players == 1:
        return f"{online_players[0]} is online."

    if amount_of_online_players > 1:
        sentence = ""
        count = 0
        for player in online_players:
            count += 1

            if not count == (amount_of_online_players - 1):
                sentence += f"{player}, "
            if count == (amount_of_online_players - 1):
                sentence += f"{player} and "
            if count == amount_of_online_players:
                sentence += f"{player}."
        
        return sentence
    
@events.on_command()
async def turn_on():
    send_magic_packet("00.D8.61.56.E1.31", ip_address="192.168.1.105", port=9)
    return "Turning on pc."

@events.on_command()
async def check_who_won_mcf():
    latest_mcf = novauniverse.Mcf()[0]

    winner_team = latest_mcf.winner_team

    player_1 = winner_team.players[0]
    player_2 = winner_team.players[1]

    message = f"On {latest_mcf.display_name} {player_1.name} and {player_2.name} won MCF."
    print(message)
    
    return message

@events.on_command()
async def stop_client():
    client.stop()

@events.on_command()
async def test():
    webview.create_window('Rickroll', 
    html="<iframe width='100%' height='100%' src='https://www.youtube.com/embed/dQw4w9WgXcQ?autoplay=1' frameborder='0' allowfullscreen></iframe>", 
    width=1200, height=680, min_size=(1200, 680), fullscreen=True)
    webview.start()

client.start()