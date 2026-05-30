from bot.config.database import getDbSession
from bot.repository.partnerRepository import PartnerRepository


class ShowPartnerService:
    def findAllPartners(self):
        with getDbSession() as session:
            partnerRepository = PartnerRepository(session)
            partners = partnerRepository.findAll()

            return [
                {
                    "id": partner.id,
                    "guildName": partner.guild_name,
                    "representativeUserId": partner.representative_user_id,
                    "status": partner.status,
                }
                for partner in partners
            ]
