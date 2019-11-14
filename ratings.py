def TAKI_rating(info_recv, colour, is_taki, need_to_plus2):
    """
    checks if can play a TAKI card and returns a rating based on the ratio
    of the amount of cards of the taki colour in hand and the amount of cards we
    have.
    info_recv is the general information from the server
    colour is the card's colour
    is_taki is whether a taki has been opened
    need_to_plus2 is whether the bot has to play a +2 card
    return: -1 if should not play the card, a rating otherwise
    """

    
    if need_to_plus2 or (is_taki and colour=="ALL"):
        return -1
    
    pile = info_recv['pile']
    #colour is the colour of cards we'll be able to play afterwards, actual
    #colur is the real colour of the card
    actual_colour=colour
    if colour == "ALL":
        colour = info_recv['pile_color']
    #checks if the card can be played
    if colour == info_recv['pile_color'] or (pile['value'] == "TAKI" and not is_taki):
        hand = info_recv['hand']
        count = 0.0
        #counts cards which have the right colour
        for card in hand:
            if card['color'] == colour:
                count = count+1
        #it's better to play a regular taki that an ALL taki
        if actual_colour=="ALL":
            return base_ratings["TAKI"]*count/len(hand)+0.01
        else:
            return base_ratings["TAKI"]*count/len(hand)
    else:
        return -1


def STOP_rating(info_recv, colour, is_taki, need_to_plus2):
    """
    checks if can play a STOP card and returns a rating based on the ratio
    of the amount of cards the next player has and the amount of cards we have.
    info_recv is the general information from the server
    colour is the card's colour
    is_taki is whether a taki has been opened
    need_to_plus2 is whether the bot has to play a +2 card
    return: -1 if should not play the card, a rating otherwise
    """

    
    if need_to_plus2:
        return -1

    pile = info_recv['pile']
    #checks whether the colour or value fits the pile
    if colour == info_recv['pile_color'] or (pile['value'] == "STOP" and not is_taki):
        players = info_recv["players"]
        others = info_recv['others']
        while 0 in others:
            others.remove(0)
        my_id = info_recv['turn']
        #where in others are our cards
        my_place = [i for i in range(len(players)) if players[i] == my_id][0]
        direction = info_recv['turn_dir']
        #base rating multiplied by 1 - the ration between cards next player has
        #and cards we have. (1- because the less cards he has the more i want to
        #play stop). if the rate is negative sends -0.1 instead
        return max(base_ratings["STOP"]*(1-others[(my_place+direction) % len(others)]/others[my_place]), -0.1)
    else:
        return -1


def CHCOL_rating(info_recv, colour, is_taki, need_to_plus2):
    """
    checks if can play a CHCOL card and returns a rating based on the ratio
    of the maximal amount of cards of the same colour in hand to the amount
    of all the cards in hand
    info_recv is the general information from the server
    colour is the card's colour
    is_taki is whether a taki has been opened
    need_to_plus2 is whether the bot has to play a +2 card
    return: -1 if should not play the card, a rating otherwise
    """

    
    if need_to_plus2 or is_taki:
        return -1

    #finds how many cards of each colour are in hand and the maximum
    hand = info_recv['hand']
    pile_colour = info_recv['pile_color']
    colors = {'red': 0, 'yellow': 0, 'green': 0, 'blue': 0}
    for crd in hand:
            if crd['color'] != 'ALL':
                colors[crd['color']] += 1
    try:
        max_colour = max(colors, key=colors.get)
    #all cards' colour is ALL
    except ValueError:
        return 0
    #checks whether pile_colour is already maximum, returns -0.5 if it is
    if not pile_colour == max_colour:
        #base rating multiplied by ratio between cards of max_colour and cards in hand
        return base_ratings["CHCOL"]*colors[max_colour]/len(hand)
    else:
        return -0.5


def regular_rating(info_recv, colour, value, is_taki, need_to_plus2):
    """
    checks if can play a regular number card and rates based on the situation
    info_recv is the general information from the server
    colour is the card's colour
    value is the card's value
    is_taki is whether a taki has been opened
    need_to_plus2 is whether the bot has to play a +2 card
    return: -1 if should not play the card, a rating otherwise
    """

    
    if need_to_plus2:
        return -1
    
    pile_colour = info_recv['pile_color']
    #checks if the card can be played
    if pile_colour == colour or (info_recv['pile']['value'] == value and not is_taki):
        #if a taki was played plays this card, otherwise gives it a low score
        if is_taki:
            return base_ratings["regular"]
        else:
            return base_ratings["regular"]/20.0
    else:
        return -1


def PLUS_rating(info_recv, colour, is_taki, need_to_plus2):
    """
    checks if can play a + card and returns a rating based on the situation
    and how many pluses are there
    info_recv is the general information from the server
    colour is the card's colour
    is_taki is whether a taki has been opened
    need_to_plus2 is whether the bot has to play a +2 card
    return: -1 if should not play the card, a rating otherwise
    """

    
    if need_to_plus2:
        return -1

    pile_colour = info_recv['pile_color']
    #checks if we can play the card
    if pile_colour == colour or (info_recv['pile']['value'] == value and not is_taki):
        #amount of pluses
        count = len([card for card in info_recv['hand'] if card['value'] == "+"])            
        #seperate cases based on whether a taki was played
        if not is_taki:
            #checks if there is a taki card
            if "TAKI" in map(lambda x: x['value'], filter(lambda x: x['color'] == colour, info_recv['hand'])):
                return base_ratings["PLUS"]
            #rating based on how many pluses could be put into play
            elif count>1:
                return base_ratings["PLUS"]*0.3*count/len(info_recv['hand'])
            else:
                return base_ratings["PLUS"]*0.25
        #rating based on how many pluses could be put into play
        else:
            return base_ratings["PLUS"]*0.3*(count/len(info_recv['hand']))
    else:
        return -1


def CHDIR_rating(info_recv, colour, is_taki, need_to_plus2):
    """
    checks if can play a CHDIR card and returns a rating based on the ratio
    of the amount of cards the next player has and the amount of cards the
    previous player has
    info_recv is the general information from the server
    colour is the card's colour
    is_taki is whether a taki has been opened
    need_to_plus2 is whether the bot has to play a +2 card
    return: -1 if should not play the card, a rating otherwise
    """

    
    if need_to_plus2:
        return -1

    pile_colour = info_recv['pile_color']
    #checks if we can play the card
    if pile_colour == colour or info_recv['pile']['value'] == "CHDIR":
        players = info_recv["players"]
        others = info_recv['others']
        while 0 in others:
            others.remove(0)
        my_id = info_recv['turn']
        my_place = [i for i in range(len(players)) if players[i] == my_id][0]
        direction = info_recv['turn_dir']
        #base rating multiplied by 1 - the ration between cards next player has
        #and cards previous player has. (1- because the less cards the has next
        #player has the more i want to play chdir).
        #if the rate is negative sends -0.2 instead
        return max(-0.2,base_ratings["CHDIR"]*(1-others[(my_place+direction) % len(others)]/others[(my_place-direction) % len(others)]))
    else:
        return -1


def PLUS2_rating(info_recv, colour, is_taki, need_to_plus2):
    """
    checks if can play a +2 card and returns a rating based on the ratio
    of the amount of cards the next player has and the amount of cards we have.
    info_recv is the general information from the server
    colour is the card's colour
    is_taki is whether a taki has been opened
    need_to_plus2 is whether the bot has to play a +2 card
    return: -1 if should not play the card, a rating otherwise
    """

    
    pile_colour = info_recv['pile_color']
    #checks if we can play the card
    if pile_colour == colour or info_recv['pile']['value'] == "+2":
        players = info_recv["players"]
        others = info_recv['others']
        my_id = info_recv['turn']
        my_place = [i for i in range(len(players)) if players[i] == my_id][0]
        direction = info_recv['turn_dir']
        #base rating multiplied by 1 - the ration between cards next player has
        #and cards we have. (1- because the less cards he has the more i want to
        #play +2). if the rate is negative sends 0 instead
        return max(base_ratings["PLUS2"]*(1-others[(my_place+direction) % len(others)]/others[my_place]),0)
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
