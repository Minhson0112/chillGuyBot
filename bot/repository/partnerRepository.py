from datetime import date

from bot.models.partner import Partner

class PartnerRepository:
    def __init__(self, session):
        self.session = session

    def findByGuildId(self, guildId):
        return self.session.query(Partner).filter(Partner.guild_id == guildId).first()

    def create(self, partnerData):
        partner = Partner(**partnerData)
        self.session.add(partner)
        self.session.flush()
        return partner