from socket import *
import re
import sys
import json


TAKI_ACTIVE = False
prev_card = None
json_kwargs = {'default': lambda o: o.__dict__, 'sort_keys': True, 'indent': 4}
HOST = 'localhost'
PORT = 50000
BUFSIZ = 4096
ADDR = (HOST, PORT)


def choose_card(info_recv):
    global TAKI_ACTIVE
    global prev_card
    hand = info_recv['hand']
    pile = info_recv['pile']
    pile_color = info_recv['pile_color']
    card_options = []
    for c in hand:
        if pile['value'] != '+2' or prev_card['value'] != '+2':
            if c['color'] == pile_color or c['value'] == pile['value'] or c['color'] == 'ALL':
                card_options.append(c)
        else:
            if c['value'] == pile['value']:
                card_options.append(c)
    if len(card_options) == 0:
        return {'card': {"color": "", "value": ""}, 'order': 'draw card'}
    else:
        card_being_played = card_options[0]
        if card_being_played['value'] == 'CHCOL':
            return {'card': card_being_played, 'order': 'red'}
        if card_being_played['value'] == 'TAKI':
            TAKI_ACTIVE = True
        if TAKI_ACTIVE and len(card_options) == 1:
            TAKI_ACTIVE = False
            return {'card': card_being_played, 'order': 'close taki'}
        return {'card': card_being_played, 'order': ''}


tcpCliSock = socket(AF_INET, SOCK_STREAM)
tcpCliSock.connect(ADDR)
tcpCliSock.send('1234')
info_recv = tcpCliSock.recv(BUFSIZ)
print('connected')
info_recv = tcpCliSock.recv(BUFSIZ)
our_id = int(re.findall('[0-9]+', info_recv[4:])[0])
print(our_id)
if our_id > 5:
    our_id = 3
while True:
    info_recv =tcpCliSock.recv(BUFSIZ)[4:]
    if 'Over' in info_recv:
        sys.exit()
    try:
        info_recv = json.loads(info_recv)
    except:
        print(info_recv)
        print(info_recv)
        sys.exit()
    turn = info_recv['turn']
    if turn == our_id:
        print(info_recv)
        command = choose_card(info_recv)
        print(command)
        command = json.dumps(command, **json_kwargs)
        tcpCliSock.send(command)
    prev_amount = info_recv['pile']
