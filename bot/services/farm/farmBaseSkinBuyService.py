from bot.config.database import getDbSession
from bot.config.emoji import FARM_GAME_EMOJI
from bot.helper.numberFormatHelper import formatNumber
from bot.repository.baseSkinMasterRepository import BaseSkinMasterRepository
from bot.repository.farmRepository import FarmRepository
from bot.repository.memberBaseSkinInventoryRepository import MemberBaseSkinInventoryRepository
from bot.repository.memberRepository import MemberRepository


class FarmBaseSkinBuyService:
    def buyBaseSkin(self, userId: int, baseSkinId: int):
        with getDbSession() as session:
            memberRepository = MemberRepository(session)
            farmRepository = FarmRepository(session)
            baseSkinMasterRepository = BaseSkinMasterRepository(session)
            memberBaseSkinInventoryRepository = MemberBaseSkinInventoryRepository(session)

            member = memberRepository.findByUserIdForUpdate(userId)

            if member is None:
                return {
                    "success": False,
                    "message": "Không tìm thấy dữ liệu member của bạn.",
                }

            farm = farmRepository.findByUserId(userId)

            if farm is None:
                return {
                    "success": False,
                    "message": "Bạn chưa có nông trại.",
                }

            baseSkin = baseSkinMasterRepository.findById(baseSkinId)

            if baseSkin is None:
                return {
                    "success": False,
                    "message": f"Không tìm thấy base skin với ID **{baseSkinId}**.",
                }

            if not baseSkin.is_active:
                return {
                    "success": False,
                    "message": (
                        "Skin chưa mở bán vào thời điểm hiện tại, vui lòng quay lại sau "
                        "hoặc chờ thông báo mới."
                    ),
                }

            ownedBaseSkin = memberBaseSkinInventoryRepository.findByUserIdAndBaseSkinId(
                userId=userId,
                baseSkinId=baseSkin.id,
            )

            if ownedBaseSkin is not None:
                return {
                    "success": False,
                    "message": f"Bạn đã sở hữu base skin **{baseSkin.name}** rồi.",
                }

            if farm.farm_level < baseSkin.required_farm_level:
                return {
                    "success": False,
                    "message": (
                        f"Base skin **{baseSkin.name}** yêu cầu farm level "
                        f"**{baseSkin.required_farm_level}**, farm của bạn hiện level "
                        f"**{farm.farm_level}**."
                    ),
                }

            chillCoinEmoji = FARM_GAME_EMOJI["chill_coin"]

            if member.chill_coin < baseSkin.buy_price:
                return {
                    "success": False,
                    "message": (
                        f"Mua base skin **{baseSkin.name}** cần "
                        f"**{formatNumber(baseSkin.buy_price)}** {chillCoinEmoji}, "
                        f"bạn chỉ có **{formatNumber(member.chill_coin)}** {chillCoinEmoji}."
                    ),
                }

            member.chill_coin -= baseSkin.buy_price

            inventory = memberBaseSkinInventoryRepository.create(
                userId=userId,
                baseSkinId=baseSkin.id,
                isUsing=False,
            )

            session.commit()

            return {
                "success": True,
                "message": (
                    f"Bạn đã mua base skin **{baseSkin.name}** với "
                    f"**{formatNumber(baseSkin.buy_price)}** {chillCoinEmoji}. "
                    f"ID kho: **{inventory.id}**"
                ),
            }
