from datetime import datetime, timedelta
from math import ceil

from bot.config.database import getDbSession
from bot.helper.farmItemHelper import buildItemText
from bot.helper.timeFormatHelper import formatHoursMinutesSeconds
from bot.repository.farmRepository import FarmRepository
from bot.repository.farmTheftHistoryRepository import FarmTheftHistoryRepository
from bot.repository.memberRepository import MemberRepository
from bot.repository.userInventoryRepository import UserInventoryRepository


class FarmTheftService:
    THEFT_COOLDOWN_HOURS = 2
    THEFT_PERCENT = 20

    def stealCrop(self, thiefUserId: int, victimUserId: int):
        if thiefUserId == victimUserId:
            return {
                "success": False,
                "message": "Bạn không thể ăn trộm nông sản của chính mình.",
            }

        with getDbSession() as session:
            memberRepository = MemberRepository(session)
            farmRepository = FarmRepository(session)
            farmTheftHistoryRepository = FarmTheftHistoryRepository(session)
            userInventoryRepository = UserInventoryRepository(session)

            thiefMember = memberRepository.findByUserIdForUpdate(thiefUserId)

            if thiefMember is None:
                return {
                    "success": False,
                    "message": "Không tìm thấy dữ liệu thành viên của bạn.",
                }

            victimFarm = farmRepository.findByUserIdForUpdate(victimUserId)

            if victimFarm is None:
                return {
                    "success": False,
                    "message": "Không tìm thấy nông trại này.",
                }

            now = datetime.now()
            cooldown = timedelta(hours=self.THEFT_COOLDOWN_HOURS)

            victimCooldownResult = self.validateVictimCooldown(
                victimFarm=victimFarm,
                now=now,
                cooldown=cooldown,
            )

            if victimCooldownResult is not None:
                return victimCooldownResult

            latestTheftHistory = farmTheftHistoryRepository.findLatestByThiefUserId(
                thiefUserId,
            )
            thiefCooldownResult = self.validateThiefCooldown(
                latestTheftHistory=latestTheftHistory,
                now=now,
                cooldown=cooldown,
            )

            if thiefCooldownResult is not None:
                return thiefCooldownResult

            cropResult = self.validateHarvestableCrop(victimFarm, now)

            if not cropResult["success"]:
                return cropResult

            cropItem = cropResult["cropItem"]
            stolenQuantity = self.calculateStolenQuantity(victimFarm.cropArea)

            userInventoryRepository.addOrCreate(
                userId=thiefUserId,
                itemId=cropItem.id,
                quantity=stolenQuantity,
            )
            farmTheftHistoryRepository.create(
                thiefUserId=thiefUserId,
                victimUserId=victimUserId,
                itemId=cropItem.id,
                stolenAt=now,
            )
            farmRepository.markRobbed(
                farm=victimFarm,
                robbedAt=now,
                stolenQuantity=stolenQuantity,
            )

            session.commit()

            return {
                "success": True,
                "message": (
                    f"Bạn đã ăn trộm được **{stolenQuantity}** "
                    f"{buildItemText(cropItem)}."
                ),
            }

    def calculateStolenQuantity(self, farmCropArea):
        crop = farmCropArea.crop
        maxHarvestQuantity = (
            farmCropArea.unlocked_plot_count * crop.harvest_quantity_per_plot
        )

        return max(maxHarvestQuantity * self.THEFT_PERCENT // 100, 1)

    def validateVictimCooldown(self, victimFarm, now: datetime, cooldown: timedelta):
        if victimFarm.last_robbed_at is None:
            return None

        nextRobberyAt = victimFarm.last_robbed_at + cooldown

        if now >= nextRobberyAt:
            return None

        return {
            "success": False,
            "message": (
                "Farm này vừa bị ăn trộm. Có thể trộm lại sau "
                f"**{self.formatRemainingTime(nextRobberyAt, now)}**."
            ),
        }

    def validateThiefCooldown(self, latestTheftHistory, now: datetime, cooldown: timedelta):
        if latestTheftHistory is None:
            return None

        nextTheftAt = latestTheftHistory.stolen_at + cooldown

        if now >= nextTheftAt:
            return None

        return {
            "success": False,
            "message": (
                "Bạn vừa ăn trộm gần đây. Có thể tiếp tục sau "
                f"**{self.formatRemainingTime(nextTheftAt, now)}**."
            ),
        }

    def validateHarvestableCrop(self, victimFarm, now: datetime):
        farmCropArea = victimFarm.cropArea

        if farmCropArea is None:
            return {
                "success": False,
                "message": "Nông trại này chưa có khu đất trồng.",
            }

        if farmCropArea.crop_id is None or farmCropArea.crop is None:
            return {
                "success": False,
                "message": "Nông trại này hiện không trồng cây nào.",
            }

        if farmCropArea.harvestable_at is None or now < farmCropArea.harvestable_at:
            return {
                "success": False,
                "message": "Cây của nông trại này chưa thể thu hoạch.",
            }

        cropItem = farmCropArea.crop.cropItem

        if cropItem is None:
            return {
                "success": False,
                "message": "Không tìm thấy item nông sản của cây này.",
            }

        return {
            "success": True,
            "cropItem": cropItem,
        }

    def formatRemainingTime(self, availableAt: datetime, now: datetime):
        remainingSeconds = max(ceil((availableAt - now).total_seconds()), 1)
        return formatHoursMinutesSeconds(remainingSeconds)
