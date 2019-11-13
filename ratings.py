def TAKI_rating(info_recv, colour, is_taki, need_to_plus2):
    if need_to_plus2:
        return -1
    pile = info_recv['pile']
    if colour == "ALL":
        colour = info_recv['pile_color']
    if colour == info_recv['pile_color'] or (pile['value'] == "TAKI" and not is_taki):
        hand = info_recv['hand']
        count = 0.0
        for card in hand:
            if card['color'] == colour:
                count = count+1
        return base_ratings["TAKI"]*count/len(hand)
    else:
        return -1


def STOP_rating(info_recv, colour, is_taki, need_to_plus2):
    if need_to_plus2:
        return -1
    pile = info_recv['pile']
    if colour == "ALL":
        colour = info_recv['pile_color']
    if colour == info_recv['pile_color'] or (pile['value'] == "STOP" and not is_taki):
        players = info_recv["players"]
        others = info_recv['others']
        my_id = info_recv['turn']
        my_place = [i for i in range(len(players)) if players[i] == my_id][0]
        direction = info_recv['turn_dir']
        return max(base_ratings["STOP"]*(1-others[(my_place+direction) % len(others)]/others[my_place]), 0)
    else:
        return -1


def CHCOL_rating(info_recv, colour, is_taki, need_to_plus2):
    if need_to_plus2:
        return -1
    hand = info_recv['hand']
    pile_colour = info_recv['pile_color']
    colors = {'red': 0, 'yellow': 0, 'green': 0, 'blue': 0}
    for crd in hand:
            if crd['color'] != 'ALL':
                colors[crd['color']] += 1
    max_colour = max(colors, key=colors.get)
    if not pile_colour == max_colour:
        return base_ratings["CHCOL"]*colors[max_colour]/len(hand)
    else:
        return -1


def regular_rating(info_recv, colour, value, is_taki, need_to_plus2):
    if need_to_plus2:
        return -1
    pile_colour = info_recv['pile_color']
    if pile_colour == colour or info_recv['pile']['value'] == value:
        if is_taki and pile_colour == colour:
            return base_ratings["regular"]
        else:
            return base_ratings["regular"]/20.0
    else:
        return -1


def PLUS_rating(info_recv, colour, is_taki, need_to_plus2):
    if need_to_plus2:
        return -1
    pile_colour = info_recv['pile_color']
    if pile_colour == colour or info_recv['pile']['value'] == "+":
        count = len([card for card in info_recv['hand'] if card['value'] == "+" and card['color'] == colour])
        if not is_taki:
            if info_recv['pile_color'] == colour:
                if count > 0:
                    return base_ratings["PLUS"]*0.2
                elif "TAKI" in map(lambda x: x['value'], filter(lambda x: x['color'] == colour, info_recv['hand'])):
                    return base_ratings["PLUS"]
                else:
                    return base_ratings["PLUS"]*0.25
        elif pile_colour == colour:
            return base_ratings["PLUS"]*0.3*(count/len(info_recv['hand']))
    else:
        return -1


def CHDIR_rating(info_recv, colour, is_taki, need_to_plus2):
    if need_to_plus2:
        return -1
    pile_colour = info_recv['pile_color']
    if pile_colour == colour or info_recv['pile']['value'] == "CHDIR":
        players = info_recv["players"]
        others = info_recv['others']
        my_id = info_recv['turn']
        my_place = [i for i in range(len(players)) if players[i] == my_id][0]
        direction = info_recv['turn_dir']
        return base_ratings["CHDIR"]*(others[(my_place-direction) % len(others)]/others[(my_place+direction) % len(others)])
    else:
        return -1


def PLUS2_rating(info_recv, colour, is_taki, need_to_plus2):
    pile_colour = info_recv['pile_color']
    if pile_colour == colour or info_recv['pile']['value'] == "+2":
        players = info_recv["players"]
        others = info_recv['others']
        my_id = info_recv['turn']
        my_place = [i for i in range(len(players)) if players[i] == my_id][0]
        direction = info_recv['turn_dir']
        return base_ratings["PLUS2"]*(1-others[(my_place+direction) % len(others)]/others[my_place])
    else:
        return -1


base_ratings = {
    "TAKI": 3.0,
    "STOP": 2.0,
    "CHCOL": 2.5,
    "regular": 10.0,
    "PLUS": 10.0,
    "CHDIR": 2.0,
    "PLUS2": 4.0
    }