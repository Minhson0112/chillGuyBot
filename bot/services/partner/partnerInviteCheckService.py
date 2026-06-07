from bot.config.database import getDbSession
from bot.repository.partnerRepository import PartnerRepository


class PartnerInviteCheckService:
    async def findInvalidActivePartnerInvites(self, bot):
        invalidPartners = []

        activePartners = self.findActivePartnerInviteData()

        for partner in activePartners:
            if not partner["inviteLink"]:
                invalidPartners.append(partner)
                continue

            try:
                await bot.fetch_invite(partner["inviteLink"], with_counts=True)
            except Exception:
                invalidPartners.append(partner)

        return invalidPartners

    def findActivePartnerInviteData(self):
        with getDbSession() as session:
            partnerRepository = PartnerRepository(session)
            activePartners = partnerRepository.findActivePartnersWithInviteLink()

            return [
                self.buildInvalidPartnerData(partner)
                for partner in activePartners
            ]

    def buildInvalidPartnerData(self, partner):
        return {
            "id": partner.id,
            "guildName": partner.guild_name,
            "representativeUserId": partner.representative_user_id,
            "inviteLink": partner.invite_link,
        }
