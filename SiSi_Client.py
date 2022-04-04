try:
    import os
    import tkinter as tk
    import requests as rq
    import logging as lg
    import urllib3
    from threading import Thread
    from time import sleep

    os.makedirs('log', exist_ok=True)
    lg.basicConfig(filename='./log/LOG.log', filemode='w', format='(%(levelname)s)%(asctime)s - %(message)s',
                   level=lg.INFO)


    def data_update() -> None:
        """Gets live game data from the API"""
        global response

        while True:
            try:
                response = dict(rq.get('https://127.0.0.1:2999/liveclientdata/allgamedata', verify=False).json())
            except:
                response = {}


    def get_id_and_role(name: str) -> tuple:
        """Returns ID and Role of the player by player name"""
        for pid in range(len(response['allPlayers'])):
            if response['allPlayers'][pid]['summonerName'] == name:
                prole = response['allPlayers'][pid]['position']
                return pid, prole


    def get_enemy_id(pid: int) -> int:
        """Returns the enemy ID by the player's ID"""
        prole = response['allPlayers'][pid]['position']
        pteam = response['allPlayers'][pid]['team']
        # Checks for an ID that has the same role as the player and is in the opposite team
        return [eid for eid in range(len(response['allPlayers']))
                if response['allPlayers'][eid]['team'] != pteam
                and response['allPlayers'][eid]['position'] == prole][0]


    def get_score(pid: int) -> int:
        """Returns either VS or CS depending on the player role"""
        prole = response['allPlayers'][pid]['position']
        if prole.lower() == 'utility':
            return int(response['allPlayers'][pid]['scores']['wardScore'])
        else:
            return response['allPlayers'][pid]['scores']['creepScore']


    def get_level(pid: int) -> int:
        """Returns the level of a player"""
        return response['allPlayers'][pid]['level']


    def start_check() -> bool:
        """Checks if the game has been loaded completely"""
        if 'allPlayers' in response:
            for player in response['allPlayers']:
                print(player['items'])
                if player['items']:
                    return True
                else:
                    return False
        else:
            return False


    class MainWindow(tk.Tk):
        def __init__(self):
            super(MainWindow, self).__init__()
            self.withdraw()
            self.attributes('-topmost', True)
            self.overrideredirect(True)
            lg.info('Window initiation is finished.')

        def update(self) -> None:
            """Updates the Overlay"""
            global response
            global label

            while True:
                if start_check():
                    lg.info('Game is now loaded.')
                    break
                sleep(1)

            player_name = response['activePlayer']['summonerName']
            player_id, role = get_id_and_role(player_name)
            enemy_id = get_enemy_id(player_id)
            enemy_name = response['allPlayers'][enemy_id]['summonerName']

            if not role or response['gameData']['gameMode'] != "CLASSIC":
                lg.error('Game does not support role mode.')
                sleep(20)
                self.update()
            else:
                lg.info(f'{player_name} vs {enemy_name}, Role: {role}')

            self.deiconify()

            if role.lower() == 'utility':
                while 'gameData' in response:
                    tformat = f'You vs {enemy_name}\n' \
                              f'VS: {get_score(player_id)} vs {get_score(enemy_id)}\n' \
                              f'Level: {get_level(player_id)} vs {get_level(enemy_id)}'
                    label['text'] = tformat
                    self.geometry(
                        f'+{self.winfo_vrootwidth() - label.winfo_reqwidth()}+{int(self.winfo_vrootheight() / 5)}')
            else:
                while 'gameData' in response:
                    tformat = f'You vs {enemy_name}\n' \
                              f'CS: {get_score(player_id)} vs {get_score(enemy_id)}\n' \
                              f'Level: {get_level(player_id)} vs {get_level(enemy_id)}'
                    label['text'] = tformat
                    self.geometry(
                        f'+{self.winfo_vrootwidth() - label.winfo_reqwidth()}+{int(self.winfo_vrootheight() / 5)}')

            self.withdraw()
            self.update()


    response = {}
    root = MainWindow()
    label = tk.Label(
        font=('Arial', 15),
        foreground='grey80',
        background='grey23',
    )
    label.pack()

    up_thread = Thread(target=root.update)
    up_thread.start()
    data_thread = Thread(target=data_update)
    data_thread.start()

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    lg.info('Update is now enabled, Waiting for a match to be loaded...')
    root.mainloop()

except Exception as err:
    import logging as lg

    lg.basicConfig(filename='./log/LOG.log', filemode='w', format='(%(levelname)s)%(asctime)s - %(message)s',
                   level=lg.INFO)
    lg.error(err)
