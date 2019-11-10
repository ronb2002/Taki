from socket import *
import re
import sys
import json

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
    if taki_active:
        additional_cards = []
        for crd in info_recv['hand']:
            if crd['color'] == info_recv['pile_color'] and crd != card:
                additional_cards.append(crd)
        if card == '' or len(additional_cards) == 0 or card['value'] == 'STOP' or card['value'] == 'CHDIR':
            taki_active = False
            return {'card': card, 'order': 'close_taki'}

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
    pile = info_recv['pile']
    # Pile Color is needed because sometimes the color is unknown just looking at the top card
    pile_color = info_recv['pile_color']
    direction = info_recv['turn_dir']
    other_hands = info_recv['others']
    # This block of code checks if a +2 needs to be added
    if prev_info_recv:
        other_hands_prev = prev_info_recv['others']
        if len(other_hands) == len(other_hands_prev):
            need_to_plus2 = True
            for i in range(len(other_hands)):
                if other_hands_prev[i] + 2 <= other_hands[i]:
                    need_to_plus2 = False
            if need_to_plus2 and pile['value'] == '+2':
                for c in hand:
                    if c['value'] == '+2' and c['color'] == pile_color:
                        return try_to_place(info_recv, c)
                return try_to_place(info_recv, "", 'draw card')

    for c in hand:
        if c['value'] == 'TAKI' and (c['color'] == pile_color or c['color'] == 'ALL'):
            taki_active = True
            return try_to_place(info_recv, c)
    for c in hand:
        if c['value'] == '+' and c['color'] == pile_color:
            return try_to_place(info_recv, c)
    if taki_active:
        for c in hand:
            if (9 <= c['value'] >= 0) and c['color'] == pile_color:
                return try_to_place(info_recv, c)
    for c in hand:
        if (c['value'] == 'STOP' or c['value'] == 'CHDIR') and c['color'] == pile_color:
            return try_to_place(info_recv, c)
    for c in hand:
        if (9 <= c['value'] >= 0) and c['color'] == pile_color:
            return try_to_place(info_recv, c)
    for c in hand:
        if c['value'] == pile['value']:
            return try_to_place(info_recv, c)
    for c in hand:
        if c['value'] == '+2' and c['color'] == pile_color:
            return try_to_place(info_recv, c)
    for c in hand:
        if c['value'] == 'CHCOL':
            colors = {'red': 0, 'yellow': 0, 'green': 0, 'blue': 0}
            for crd in hand:
                    if crd['color'] != 'ALL':
                        colors[crd['color']] += 1
            return try_to_place(info_recv, c, order=max(colors, key=colors.get))
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
open('info.json', 'w').close() # Erases file contents
with(open('info.json', 'a')) as f:
    if our_id == 1:  # NEEDS TO BE DELETED BEFORE TURN IN!
        f.write(json.dumps({'our_id': our_id}) + '\n')
    while True:
        info_recv = tcpCliSock.recv(BUFSIZ)[4:]
        try:
            info_recv = json.loads(info_recv)
        except:
            print("JSON NOT RECIEVED:")
            print(info_recv)
            sys.exit()
        turn = info_recv['turn']
        if turn == our_id:
            print(info_recv)
            command = choose_card(info_recv, prev_info_recv)  # Choose which card to play
            print(command)
            command = json.dumps(command, **json_kwargs)
            tcpCliSock.send(command)
        prev_info_recv = info_recv
        if our_id == 1:  # NEEDS TO BE DELETED BEFORE TURN IN!
            f.write(json.dumps(info_recv) + '\n')
