from sqlalchemy import asc

from bot.models.partner import Partner

class PartnerRepository:
    def __init__(self, session):
        self.session = session

    def findByGuildId(self, guildId):
        return self.session.query(Partner).filter(Partner.guild_id == guildId).first()

    def findById(self, partnerId):
        return self.session.query(Partner).filter(Partner.id == partnerId).first()

    def findAll(self):
        return (
            self.session.query(Partner)
            .order_by(asc(Partner.id))
            .all()
        )

    def create(self, partnerData):
        partner = Partner(**partnerData)
        self.session.add(partner)
        self.session.flush()
        return partner

    def findByRepresentativeUserId(self, representativeUserId):
        return (
            self.session.query(Partner)
            .filter(Partner.representative_user_id == representativeUserId)
            .first()
        )

    def updateStatus(self, partner, status):
        partner.status = status
        self.session.flush()
        return partner

    def updateGuildName(self, partner, guildName):
        partner.guild_name = guildName
        self.session.flush()
        return partner
