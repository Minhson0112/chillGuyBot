from bot.helper.numberFormatHelper import formatNumber
from bot.config.database import getDbSession
from bot.config.emoji import FARM_GAME_EMOJI
from bot.config.farmPlot import (
    FARM_MAX_PLOT_COUNT,
    FARM_LEVEL_MAX_PLOT_COUNT,
    FARM_PLOT_UNLOCK_PRICE,
)
from bot.repository.farmCropAreaRepository import FarmCropAreaRepository
from bot.repository.farmRepository import FarmRepository
from bot.repository.memberRepository import MemberRepository


class FarmPlotUnlockService:
    def unlockPlot(self, userId: int):
        with getDbSession() as session:
            memberRepository = MemberRepository(session)
            farmRepository = FarmRepository(session)
            farmCropAreaRepository = FarmCropAreaRepository(session)

            member = memberRepository.findByUserId(userId)

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

            farmCropArea = farmCropAreaRepository.findByFarmId(farm.id)

            if farmCropArea is None:
                return {
                    "success": False,
                    "message": "Nông trại của bạn chưa có khu đất trồng.",
                }

            if farmCropArea.unlocked_plot_count >= FARM_MAX_PLOT_COUNT:
                return {
                    "success": False,
                    "message": f"Bạn đã mở tối đa **{FARM_MAX_PLOT_COUNT}** ô đất.",
                }

            if not self.isCropAreaIdle(farmCropArea):
                return {
                    "success": False,
                    "message": "Chỉ có thể mở thêm ô đất khi khu đất đang trống, chưa trồng cây.",
                }

            nextPlotCount = farmCropArea.unlocked_plot_count + 1
            maxPlotCountByLevel = FARM_LEVEL_MAX_PLOT_COUNT.get(farm.farm_level, 1)

            if nextPlotCount > maxPlotCountByLevel:
                return {
                    "success": False,
                    "message": (
                        f"Farm level **{farm.farm_level}** chỉ mở được tối đa "
                        f"**{maxPlotCountByLevel}** ô đất. Hãy tăng level farm trước."
                    ),
                }

            unlockPrice = FARM_PLOT_UNLOCK_PRICE.get(nextPlotCount)

            if unlockPrice is None:
                return {
                    "success": False,
                    "message": "Không tìm thấy giá mở ô đất này trong config.",
                }

            chillCoinEmoji = FARM_GAME_EMOJI["chill_coin"]

            if member.chill_coin < unlockPrice:
                return {
                    "success": False,
                    "message": (
                        f"Mở ô đất thứ **{nextPlotCount}** cần "
                        f"**{formatNumber(unlockPrice)}** {chillCoinEmoji}, "
                        f"bạn chỉ có **{formatNumber(member.chill_coin)}** {chillCoinEmoji}."
                    ),
                }

            member.chill_coin -= unlockPrice
            farmCropAreaRepository.increaseUnlockedPlotCount(farmCropArea)

            session.commit()

            return {
                "success": True,
                "message": (
                    f"Bạn đã mở ô đất thứ **{nextPlotCount}** với "
                    f"**{formatNumber(unlockPrice)}** {chillCoinEmoji}."
                ),
            }

    def isCropAreaIdle(self, farmCropArea):
        if farmCropArea.crop_id is not None:
            return False

        if farmCropArea.planted_at is not None:
            return False

        if farmCropArea.status != "idle":
            return False

        return True
