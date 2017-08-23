import discord
import random
import json

## Formatting embeds from data.

random_colors = [0xff6600, 0xff0000, 
                 0xff3399, 0x9966ff, 
                 0x00ffff, 0x3366ff, 
                 0x00ff00, 0xffff00, 
                 0x990099, 0x009933, 
                 0x00cc66, 0x0000ff, 
                 0xff66cc]

default = 'https://statsroyale.com/images/leagues/league-0.png'

with open('data/emojis.json') as f:
    conversions = json.load(f)

def parse_stats(data):
    em = discord.Embed(color=random.choice(random_colors))
    em.set_thumbnail(url=data.get('arena_url'))
    em.set_author(name='{} (#{})'.format(data.get('username'), data['tag']),
                  icon_url=data['clan'].get('badge_url') or default)
    em.add_field(name='Trophies',value=data['trophies'].get('current'))
    em.add_field(name='Personal Best', value=data['trophies'].get('highest'))
    if data['trophies'].get('legend'):
        em.add_field(name='Legend Trophies', value=data['trophies']['legend'])
    if data['rank']:
        em.add_field(name='League Rank', value=data['rank'])
    em.add_field(name='Challenge Cards Won', value=data.get('challenge_cards_won'))
    em.add_field(name='Tourney Cards Won', value=data.get('tourney_cards_won'))
    em.add_field(name='Total Donations', value=data.get('total_donations'))
    em.add_field(name='Wins', value=data.get('wins'))
    em.add_field(name='Losses', value=data.get('losses'))
    em.add_field(name='Draws', value=data.get('draws'))
    em.add_field(name='Three Crowns', value=data.get('three_crown_wins'))
    try:
        ratio = data.get('wins')/data.get('losses')
        ratio = "{0:.2f}".format(ratio)
    except:
        ratio = 'N/A'
    em.add_field(name='Win Ratio', value=ratio)
    em.set_footer(text='Stats v3')
    return em

def to_emoji(card):
    return card.replace(' ', '').replace('.','').lower()

def to_chest(chest):
    return chest.lower().replace('_', '') + 'chest'

def parse_deck(data):
    fmt = ''
    for card in data.get('deck'):
        fmt += '{}{} '.format(conversions[to_emoji(card['name'])], card['level'])
    return fmt

def parse_chests_until(data):
    special_chests = ['legendary', 'super_magical', 'epic']
    fmt = ''
    for chest, days in data.get('chests').items():
        if chest in special_chests:
            fmt += '{}{} '.format(conversions.get(to_chest(chest)), days)

    return fmt if fmt else 'Not available.'

def parse_cycle(data):
    chests = data.get('chests')
    special_chests = ['legendary', 'super_magical', 'epic']
    fmt = ''
    for i, c in enumerate(chests.get('cycle')):
        if i == 7:
            break
        for key, val in chests.items():
            if key in special_chests:
                if val == i:
                    c = key
        if i < 1:
            fmt += '| {} | '.format(conversions.get(to_chest(c)))
        else:
            fmt += conversions[to_chest(c)]

    return fmt

def parse_chests_command(data):
    em = discord.Embed(color=random.choice(random_colors))
    em.set_thumbnail(url=data.get('arena_url'))
    em.set_author(name='{} (#{})'.format(data.get('username'), data['tag']),
                  icon_url=data['clan'].get('badge_url') or default)
    em.add_field(name='Chests Until', value=parse_chests_until(data))
    em.add_field(name='Upcoming Chests', value=parse_cycle(data), inline=False)
    em.set_footer(text='Stats v3')
    return em

def parse_deck_command(data):
    em = discord.Embed(color=random.choice(random_colors))
    em.set_thumbnail(url=data.get('arena_url'))
    em.set_author(name='{} (#{})'.format(data.get('username'), data['tag']),
                  icon_url=data['clan'].get('badge_url') or default)
    em.add_field(name='Battle Deck',value=parse_deck(data))
    em.set_footer(text='Stats v3')
    return em

def parse_offers_command(data):
    em = discord.Embed(color=random.choice(random_colors))
    em.set_thumbnail(url=data.get('arena_url'))
    em.set_author(name='{} (#{})'.format(data.get('username'), data['tag']),
                  icon_url=data['clan'].get('badge_url') or default)
    em.add_field(name='Shop Offers',value=parse_offers(data))
    em.set_footer(text='Stats v3')
    return em

def parse_offers(data):
    s2l = {
        'epic':'epicchestoffer',
        'legendary':'legendarychestoffer',
        'arena':'arenapackoffer'
        }
    if not data.get('shop_offers'):
        return 'Not available.'
    fmt = ''
    for offer, days in data.get('shop_offers').items():
        if days == 1:
            fmt += '{}{} day '.format(conversions.get(s2l.get(offer)), days)
        else:
            fmt += '{}{} days '.format(conversions.get(s2l.get(offer)), days)

    return fmt

def parse_profile(data):
    em = discord.Embed(color=random.choice(random_colors))
    em.set_thumbnail(url=data.get('arena_url'))
    em.set_author(name='{} (#{})'.format(data.get('username'), data['tag']),
                  icon_url=data['clan'].get('badge_url') or default)
    em.add_field(name='Level', value=data.get('level'))
    em.add_field(name='Experience', value=data.get('experience'))
    em.add_field(name='Clan Name',value=data.get('clan').get('name'))
    em.add_field(name='Clan Tag',value='#'+data.get('clan').get('tag') if data['clan'].get('tag') else 'None')
    em.add_field(name='Clan Role',value=data.get('clan').get('role'))
    em.add_field(name='Cards Found',value=data.get('cards_found'))
    em.add_field(name='Favorite Card',value=data.get('favorite_card'))
    em.add_field(name='Account Age',value='{} days'.format(data.get('account_age_in_days')) if data.get('account_age_in_days') else 'Not available.')
    em.add_field(name='Trophies',value=data['trophies'].get('current'))
    em.add_field(name='Personal Best', value=data['trophies'].get('highest'))
    if data['trophies'].get('legend'):
        em.add_field(name='Legend Trophies', value=data['trophies']['legend'])
    if data['rank']:
        em.add_field(name='League Rank', value=data['rank'])
    em.add_field(name='Challenge Cards Won', value=data.get('challenge_cards_won'))
    em.add_field(name='Tourney Cards Won', value=data.get('tourney_cards_won'))
    em.add_field(name='Total Donations', value=data.get('total_donations'))
    em.add_field(name='Wins', value=data.get('wins'))
    em.add_field(name='Losses', value=data.get('losses'))
    em.add_field(name='Draws', value=data.get('draws'))
    em.add_field(name='Three Crowns', value=data.get('three_crown_wins'))
    try:
        ratio = data.get('wins')/data.get('losses')
        ratio = "{0:.2f}".format(ratio)
    except:
        ratio = 'N/A'
    em.add_field(name='Win Ratio', value=ratio)
    em.add_field(name='Battle Deck',value=parse_deck(data), inline=False)
    em.add_field(name='Upcoming Chests', value=parse_cycle(data))
    em.add_field(name='Chests Until', value=parse_chests_until(data))
    em.add_field(name='Shop Offers',value=parse_offers(data))
    em.set_footer(text='Stats v3')
    return em

def parse_clan(data):
    em = discord.Embed(color=random.choice(random_colors), description=data.get('description'))
    em.set_author(name='{}'.format(data.get('name')), icon_url=data.get('badge_url'))
    em.add_field(name='Score', value=data.get('score'))
    em.add_field(name='Donation/Week', value=data.get('donations'))
    em.add_field(name='Required Trophies',value=data.get('requiredScore'))
    em.add_field(name='Members',value='{}/50'.format(data.get('numberOfMembers')))
    em.add_field(name='Status', value=data.get('type'))
    em.add_field(name='Clan Tag', value='#'+data.get('tag'))
    em.set_thumbnail(url=data.get('badge_url'))
    em.set_footer(text='Stats v3')
    return em
