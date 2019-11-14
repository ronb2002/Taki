from socket import *
import re
import json
from ratings import *

# --- CONSTANTS ---
json_kwargs = {'default': lambda o: o.__dict__, 'sort_keys': True, 'indent': 4}
HOST = 'localhost'
PORT = 50000
BUFSIZ = 4096
ADDR = (HOST, PORT)
# ----------------
prev_info_recv = None  # Previous information taken from server (for comp. with new info)
taki_active = False  # If Taki has been played but not yet closed


def try_to_place(info_recv, card, order=""):
    """
    This function recieves the card that needs to be sent and creates a message that needs to be sent to the server
    :param info_recv: Information recieved from the server (json)
    :param card: Card that needs to be played (json)
    :param order: Order that needs to be given to the server (string; '' is default)
    :return: command that needs to be sent to the server (json)
    """
    global taki_active
    # This block of code decides whether to close the taki

    if card != '':
        return {'card': card, 'order': order}
    else:
        return {'card': {'value': '', 'color': ''}, 'order': order}


def choose_card(info_recv, prev_info_recv):
    """
    This function chooses which card to play
    :param info_recv: information received from the server (json)
    :param prev_info_recv: information that was received last turn from the server (json)
    :return: The command that needs to be sent to the server (json)
    """
    global taki_active
    hand = info_recv['hand']
    pile_colour = info_recv['pile_color']

    need_to_plus2 = False
    pile = info_recv['pile']
    # Pile Color is needed because sometimes the color is unknown just looking at the top card
    other_hands = info_recv['others']
    # This block of code checks if a +2 needs to be added
    if prev_info_recv and info_recv['pile']['value'] == "+2":
        other_hands_prev = prev_info_recv['others']
        if len(other_hands) == len(other_hands_prev):
            need_to_plus2 = True
            for i in range(len(other_hands)):
                if other_hands_prev[i] < other_hands[i]:
                    need_to_plus2 = False

    rates = []
    for card in hand:
        val = card['value']
        if val.isdigit():
            rates.append([card, eval("regular_rating(info_recv,card['color'],val,taki_active,need_to_plus2)")])
        else:
            val = val.replace("+", "PLUS")
            rates.append([card, eval(val + "_rating(info_recv,card['color'],taki_active,need_to_plus2)")])
    rates = filter(lambda x: x[1] != -1, rates)
    try:
        card_to_play = max(rates, key=lambda x: x[1])[0]
        val_to_play = card_to_play['value']
        if val_to_play == "TAKI":
            taki_active = True
            return try_to_place(info_recv, card_to_play)
        if taki_active:
            if val_to_play in ("+", "+2", "STOP", "CHDIR", "CHCOL") or len(
                    filter(lambda x: x['color'] == pile_colour or x['value'] == "CHCOL", hand)) == 0:
                taki_finished = True
            else:
                taki_finished = False
            if not val_to_play == "CHCOL":
                if taki_finished:
                    return try_to_place(info_recv, card_to_play, "close taki")
                else:
                    return try_to_place(info_recv, card_to_play)
            else:
                colors = {'red': 0, 'yellow': 0, 'green': 0, 'blue': 0}
                for crd in hand:
                    if crd['color'] != 'ALL':
                        colors[crd['color']] += 1
                return try_to_place(info_recv, card_to_play, order=max(colors, key=colors.get))
        elif not val_to_play == "CHCOL":
            return try_to_place(info_recv, card_to_play)
        else:
            colors = {'red': 0, 'yellow': 0, 'green': 0, 'blue': 0}
            for crd in hand:
                if crd['color'] != 'ALL':
                    colors[crd['color']] += 1
            return try_to_place(info_recv, card_to_play, order=max(colors, key=colors.get))
    except ValueError:
        return try_to_place(info_recv, "", 'draw card')


tcpCliSock = socket(AF_INET, SOCK_STREAM)  # Initial connection to server
tcpCliSock.connect(ADDR)
tcpCliSock.send('1234')  # Server Password

info_recv = tcpCliSock.recv(BUFSIZ)
print('connected')

info_recv = tcpCliSock.recv(BUFSIZ)[4:]
our_id = int(re.findall('[0-9]+', info_recv)[0])  # Retrieval of our ID from the server
print(our_id)

if our_id > 5:
    our_id = 3

open('info.json', 'w').close()  # Erases file contents
with(open('info.json', 'a')) as f:
    if our_id == 1:  # NEEDS TO BE CHANGED LATER
        f.write(json.dumps({'our_id': our_id}) + '\n')
    while True:
        info_recv = tcpCliSock.recv(BUFSIZ)[4:]
        try:
            info_recv = json.loads(info_recv)
        except:
            print("JSON NOT RECIEVED:")
            print(info_recv)
            command = json.dumps({'card': {'value': '', 'color': ''}, 'order': 'draw card'}, **json_kwargs)
            tcpCliSock.send(command)
            continue
        if 'error' in info_recv:
            print('Error')
            print(info_recv)
            command = json.dumps({'card': {'value': '', 'color': ''}, 'order': 'draw card'}, **json_kwargs)
            tcpCliSock.send(command)
            continue
        if 'command' in info_recv:
            print('Game ended')
            print(info_recv)
            break
        turn = info_recv['turn']
        try:
            if not turn == prev_info_recv['turn']:
                taki_active = False
        except TypeError:
            taki_active = False
        if turn == our_id:
            print(info_recv)
            command = choose_card(info_recv, prev_info_recv)  # Choose which card to play
            print(command)
            command = json.dumps(command, **json_kwargs)
            tcpCliSock.send(command)
        prev_info_recv = info_recv
        if our_id == 1:  # NEEDS TO BE CHANGED LATER
            f.write(json.dumps(info_recv) + '\n')