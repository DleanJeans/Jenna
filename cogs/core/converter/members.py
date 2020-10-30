from discord.ext import commands
import difflib
import typing
import discord

DEFAULT_MATCHING = .35

class FuzzyMemberConverter(commands.MemberConverter):
    def __init__(self, *, matching=DEFAULT_MATCHING):
        self.matching = matching
    
    async def convert(self, ctx, argument):
        try:
            member = await super().convert(ctx, argument)
        except:
            member = find_member(ctx, argument, self.matching)
            if member:
                return member
            raise

FuzzyMember = typing.Union[discord.Member, FuzzyMemberConverter]

ROLE_SCORE_WEIGHT = 0.05
MATCH_RETURNS = 10

def find_member(context, input_name, matching=DEFAULT_MATCHING, contains_all_only=True):
    members = context.guild.members
    members = [m for m in members if contains_the_other(input_name, m.name) or contains_the_other(input_name, m.display_name)]
    members_by_name = {}
    for m in members:
        members_by_name[m.name] = m
        members_by_name[m.name.lower()] = m
        if m.name != m.display_name:
            members_by_name[m.display_name] = m
            members_by_name[m.display_name.lower()] = m
    close_matches = difflib.get_close_matches(input_name, members_by_name, MATCH_RETURNS, matching)
    
    def score_member(member_name):
        similarity = match_ratio(input_name, member_name)
        similarity += match_ratio(input_name.lower(), member_name.lower()) / 2

        member = members_by_name[member_name]
        role_score = score_member_role(context.guild, member)
        weighted_role_score = role_score * ROLE_SCORE_WEIGHT
        total_score = similarity + weighted_role_score

        return total_score

    close_matches.sort(key=lambda name: score_member(name), reverse=True)

    member = None
    if close_matches:
        name = close_matches[0]
        member = members_by_name[name]
    
    return member

def contains_the_other(a, b):
    a = a.lower()
    b = b.lower()
    return contains_all(a, b) or contains_all(b, a)

def contains_all(a, b):
    return all(char in b for char in a)

def match_ratio(a, b):
    return difflib.SequenceMatcher(None, a, b).ratio()

def score_member_role(guild, member):
    role_count = len(guild.roles)
    role_score = [role.position / role_count for role in member.roles]
    return sum(role_score)