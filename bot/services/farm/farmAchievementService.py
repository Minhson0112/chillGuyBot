from datetime import datetime

from bot.config.database import getDbSession
from bot.helper.numberFormatHelper import formatNumber
from bot.repository.farmAchievementCategoryRepository import FarmAchievementCategoryRepository
from bot.repository.farmCookingHistoryRepository import FarmCookingHistoryRepository
from bot.repository.farmEggHarvestHistoryRepository import FarmEggHarvestHistoryRepository
from bot.repository.farmHarvestHistoryRepository import FarmHarvestHistoryRepository
from bot.repository.farmMarketListingRepository import FarmMarketListingRepository
from bot.repository.farmMilkHarvestHistoryRepository import FarmMilkHarvestHistoryRepository
from bot.repository.farmRepository import FarmRepository
from bot.repository.farmTrainEventHistoryRepository import FarmTrainEventHistoryRepository
from bot.repository.fishingHistoryRepository import FishingHistoryRepository
from bot.repository.memberRepository import MemberRepository
from bot.repository.userFarmAchievementRepository import UserFarmAchievementRepository


class FarmAchievementService:
    REWARD_TYPE_CHILL_COIN = "chill_coin"
    REWARD_TYPE_FARM_EXP = "farm_exp"
    REWARD_TYPE_DISCORD_ROLE = "discord_role"

    def getAchievementPage(
        self,
        userId: int,
        page: int = 1,
    ):
        with getDbSession() as session:
            categoryRepository = FarmAchievementCategoryRepository(session)
            userFarmAchievementRepository = UserFarmAchievementRepository(session)

            categories = categoryRepository.findActiveCategoriesWithAchievements()

            if not categories:
                return {
                    "success": False,
                    "message": "Hiện chưa có thành tựu farm nào.",
                }

            totalPage = len(categories)
            currentPage = min(max(page, 1), totalPage)
            category = categories[currentPage - 1]
            now = datetime.now()
            achievements = []

            for achievement in self.getActiveAchievements(category):
                progress = self.calculateProgress(
                    session=session,
                    userId=userId,
                    achievement=achievement,
                )
                isCompleted = self.isProgressCompleted(progress)
                userAchievement = userFarmAchievementRepository.upsertProgress(
                    userId=userId,
                    achievementId=achievement.id,
                    progressValue=progress["progressValue"],
                    isCompleted=isCompleted,
                    now=now,
                )

                achievements.append(
                    self.buildAchievementData(
                        achievement=achievement,
                        progress=progress,
                        userAchievement=userAchievement,
                    )
                )

            session.commit()

            return {
                "success": True,
                "categoryName": category.name,
                "categoryDescription": category.description,
                "currentPage": currentPage,
                "totalPage": totalPage,
                "achievements": achievements,
            }

    def previewClaimPage(
        self,
        userId: int,
        page: int,
    ):
        with getDbSession() as session:
            categoryRepository = FarmAchievementCategoryRepository(session)
            userFarmAchievementRepository = UserFarmAchievementRepository(session)

            categories = categoryRepository.findActiveCategoriesWithAchievements()

            if not categories:
                return {
                    "success": False,
                    "message": "Hiện chưa có thành tựu farm nào.",
                }

            currentPage = min(max(page, 1), len(categories))
            category = categories[currentPage - 1]
            now = datetime.now()
            claimableAchievements = []
            roleIds = []
            missingRoleAchievements = []

            for achievement in self.getActiveAchievements(category):
                progress = self.calculateProgress(
                    session=session,
                    userId=userId,
                    achievement=achievement,
                )
                isCompleted = self.isProgressCompleted(progress)
                userAchievement = userFarmAchievementRepository.upsertProgress(
                    userId=userId,
                    achievementId=achievement.id,
                    progressValue=progress["progressValue"],
                    isCompleted=isCompleted,
                    now=now,
                )

                if not isCompleted or userAchievement.is_reward_claimed:
                    continue

                missingRoleReward = next(
                    (
                        reward
                        for reward in achievement.rewards
                        if reward.reward_type == self.REWARD_TYPE_DISCORD_ROLE
                        and reward.discord_role_id is None
                    ),
                    None,
                )

                if missingRoleReward is not None:
                    missingRoleAchievements.append(achievement.name)
                    continue

                claimableAchievements.append(achievement)

                for reward in achievement.rewards:
                    if (
                        reward.reward_type == self.REWARD_TYPE_DISCORD_ROLE
                        and reward.discord_role_id is not None
                    ):
                        roleIds.append(reward.discord_role_id)

            session.commit()

            if missingRoleAchievements:
                return {
                    "success": False,
                    "message": (
                        "Một số thành tựu đã hoàn thành nhưng reward role chưa được cấu hình: "
                        + ", ".join(missingRoleAchievements)
                    ),
                }

            if not claimableAchievements:
                return {
                    "success": False,
                    "message": "Trang này không có thành tựu nào có thể nhận thưởng.",
                }

            return {
                "success": True,
                "roleIds": list(dict.fromkeys(roleIds)),
            }

    def claimPage(
        self,
        userId: int,
        page: int,
    ):
        with getDbSession() as session:
            categoryRepository = FarmAchievementCategoryRepository(session)
            userFarmAchievementRepository = UserFarmAchievementRepository(session)
            memberRepository = MemberRepository(session)
            farmRepository = FarmRepository(session)

            categories = categoryRepository.findActiveCategoriesWithAchievements()

            if not categories:
                return {
                    "success": False,
                    "message": "Hiện chưa có thành tựu farm nào.",
                }

            member = memberRepository.findByUserIdForUpdate(userId)
            farm = farmRepository.findByUserIdForUpdate(userId)

            if member is None:
                return {
                    "success": False,
                    "message": "Không tìm thấy dữ liệu member của bạn.",
                }

            if farm is None:
                return {
                    "success": False,
                    "message": "Bạn chưa có nông trại.",
                }

            currentPage = min(max(page, 1), len(categories))
            category = categories[currentPage - 1]
            now = datetime.now()
            claimedAchievementNames = []
            totalChillCoin = 0
            totalFarmExp = 0

            for achievement in self.getActiveAchievements(category):
                progress = self.calculateProgress(
                    session=session,
                    userId=userId,
                    achievement=achievement,
                )
                isCompleted = self.isProgressCompleted(progress)
                userAchievement = userFarmAchievementRepository.upsertProgress(
                    userId=userId,
                    achievementId=achievement.id,
                    progressValue=progress["progressValue"],
                    isCompleted=isCompleted,
                    now=now,
                )

                userAchievement = userFarmAchievementRepository.findByUserIdAndAchievementIdForUpdate(
                    userId=userId,
                    achievementId=achievement.id,
                )

                if not isCompleted or userAchievement.is_reward_claimed:
                    continue

                missingRoleReward = next(
                    (
                        reward
                        for reward in achievement.rewards
                        if reward.reward_type == self.REWARD_TYPE_DISCORD_ROLE
                        and reward.discord_role_id is None
                    ),
                    None,
                )

                if missingRoleReward is not None:
                    session.rollback()
                    return {
                        "success": False,
                        "message": f"Thành tựu **{achievement.name}** có reward role chưa được cấu hình.",
                    }

                for reward in achievement.rewards:
                    if reward.reward_type == self.REWARD_TYPE_CHILL_COIN:
                        totalChillCoin += reward.reward_amount or 0
                    elif reward.reward_type == self.REWARD_TYPE_FARM_EXP:
                        totalFarmExp += reward.reward_amount or 0

                userFarmAchievementRepository.markRewardClaimed(
                    userFarmAchievement=userAchievement,
                    now=now,
                )
                claimedAchievementNames.append(achievement.name)

            if not claimedAchievementNames:
                return {
                    "success": False,
                    "message": "Trang này không có thành tựu nào có thể nhận thưởng.",
                }

            if totalChillCoin > 0:
                member.chill_coin += totalChillCoin

            if totalFarmExp > 0:
                farmRepository.increaseFarmExp(
                    farm=farm,
                    exp=totalFarmExp,
                )

            session.commit()

            rewardParts = []

            if totalChillCoin > 0:
                rewardParts.append(f"**{formatNumber(totalChillCoin)}** chill coin")

            if totalFarmExp > 0:
                rewardParts.append(f"**{formatNumber(totalFarmExp)}** exp")

            rewardText = ", ".join(rewardParts) if rewardParts else "role"

            return {
                "success": True,
                "message": (
                    "Đã nhận thưởng cho: "
                    + ", ".join(f"**{name}**" for name in claimedAchievementNames)
                    + f"\nPhần thưởng: {rewardText}."
                ),
            }

    def calculateProgress(
        self,
        session,
        userId: int,
        achievement,
    ):
        conditionType = achievement.condition_type

        if conditionType == "collect_item_quantity":
            return self.calculateCollectItemQuantityProgress(
                session=session,
                userId=userId,
                achievement=achievement,
            )

        if conditionType == "catch_all_item_type":
            return self.calculateCatchAllItemTypeProgress(
                session=session,
                userId=userId,
                achievement=achievement,
            )

        if conditionType == "catch_all_item_type_with_min_weight":
            return self.calculateCatchAllItemTypeProgress(
                session=session,
                userId=userId,
                achievement=achievement,
                minWeightKg=achievement.required_weight_kg,
            )

        if conditionType == "harvest_all_crops_by_level":
            return self.calculateHarvestAllCropsByLevelProgress(
                session=session,
                userId=userId,
                achievement=achievement,
            )

        if conditionType == "cook_all_recipes_by_level":
            return self.calculateCookAllRecipesByLevelProgress(
                session=session,
                userId=userId,
                achievement=achievement,
            )

        if conditionType == "complete_train_order_count":
            farmTrainEventHistoryRepository = FarmTrainEventHistoryRepository(session)
            progressValue = farmTrainEventHistoryRepository.countByUserId(userId)

            return self.buildCountProgress(
                progressValue=progressValue,
                requiredValue=achievement.required_value,
            )

        if conditionType == "earn_market_chill_coin":
            farmMarketListingRepository = FarmMarketListingRepository(session)
            progressValue = farmMarketListingRepository.sumSoldPriceBySellerUserId(userId)

            return self.buildCountProgress(
                progressValue=progressValue,
                requiredValue=achievement.required_value,
            )

        return self.buildCountProgress(
            progressValue=0,
            requiredValue=achievement.required_value or 1,
        )

    def getActiveAchievements(self, category):
        return sorted(
            [
                achievement
                for achievement in category.achievements
                if achievement.is_active
            ],
            key=lambda achievement: (achievement.sort_order, achievement.id),
        )

    def calculateCollectItemQuantityProgress(
        self,
        session,
        userId: int,
        achievement,
    ):
        targetItem = achievement.targetItem

        if targetItem is None:
            return self.buildCountProgress(
                progressValue=0,
                requiredValue=achievement.required_value,
            )

        progressValue = 0

        if targetItem.code == "egg":
            farmEggHarvestHistoryRepository = FarmEggHarvestHistoryRepository(session)
            progressValue = farmEggHarvestHistoryRepository.sumQuantityByUserIdAndItemId(
                userId=userId,
                itemId=targetItem.id,
            )
        elif targetItem.code == "milk":
            farmMilkHarvestHistoryRepository = FarmMilkHarvestHistoryRepository(session)
            progressValue = farmMilkHarvestHistoryRepository.sumQuantityByUserIdAndItemId(
                userId=userId,
                itemId=targetItem.id,
            )

        return self.buildCountProgress(
            progressValue=progressValue,
            requiredValue=achievement.required_value,
        )

    def calculateCatchAllItemTypeProgress(
        self,
        session,
        userId: int,
        achievement,
        minWeightKg=None,
    ):
        fishingHistoryRepository = FishingHistoryRepository(session)
        requiredValue = fishingHistoryRepository.countActiveItemsByTypeCode(
            achievement.target_item_type_code,
        )
        progressValue = fishingHistoryRepository.countDistinctCaughtItemsByUserIdAndTypeCode(
            userId=userId,
            typeCode=achievement.target_item_type_code,
            minWeightKg=minWeightKg,
        )

        return self.buildCountProgress(
            progressValue=progressValue,
            requiredValue=requiredValue,
        )

    def calculateHarvestAllCropsByLevelProgress(
        self,
        session,
        userId: int,
        achievement,
    ):
        farmHarvestHistoryRepository = FarmHarvestHistoryRepository(session)
        requiredValue = farmHarvestHistoryRepository.countRequiredCropsBySeedLevel(
            achievement.target_level,
        )
        progressValue = farmHarvestHistoryRepository.countDistinctHarvestedCropsByUserIdAndSeedLevel(
            userId=userId,
            level=achievement.target_level,
        )

        return self.buildCountProgress(
            progressValue=progressValue,
            requiredValue=requiredValue,
        )

    def calculateCookAllRecipesByLevelProgress(
        self,
        session,
        userId: int,
        achievement,
    ):
        farmCookingHistoryRepository = FarmCookingHistoryRepository(session)
        requiredValue = farmCookingHistoryRepository.countRequiredRecipesByLevel(
            achievement.target_level,
        )
        progressValue = farmCookingHistoryRepository.countDistinctCookedRecipesByUserIdAndLevel(
            userId=userId,
            level=achievement.target_level,
        )

        return self.buildCountProgress(
            progressValue=progressValue,
            requiredValue=requiredValue,
        )

    def buildCountProgress(
        self,
        progressValue,
        requiredValue,
    ):
        requiredValue = requiredValue or 0

        return {
            "progressValue": int(progressValue or 0),
            "requiredValue": int(requiredValue),
            "progressText": f"{formatNumber(int(progressValue or 0))}/{formatNumber(int(requiredValue))}",
        }

    def isProgressCompleted(self, progress):
        requiredValue = progress["requiredValue"]

        if requiredValue <= 0:
            return False

        return progress["progressValue"] >= requiredValue

    def buildAchievementData(
        self,
        achievement,
        progress,
        userAchievement,
    ):
        return {
            "name": achievement.name,
            "description": achievement.description,
            "progressText": progress["progressText"],
            "isCompleted": userAchievement.is_completed,
            "isRewardClaimed": userAchievement.is_reward_claimed,
            "rewardText": self.buildRewardText(achievement.rewards),
        }

    def buildRewardText(self, rewards):
        rewardParts = []

        for reward in sorted(rewards, key=lambda item: item.id):
            if reward.reward_type == self.REWARD_TYPE_CHILL_COIN:
                rewardParts.append(f"{formatNumber(reward.reward_amount)} coin")
            elif reward.reward_type == self.REWARD_TYPE_FARM_EXP:
                rewardParts.append(f"{formatNumber(reward.reward_amount)} exp")
            elif reward.reward_type == self.REWARD_TYPE_DISCORD_ROLE:
                if reward.discord_role_id is None:
                    rewardParts.append("role")
                else:
                    rewardParts.append(f"<@&{reward.discord_role_id}>")

        return ", ".join(rewardParts) if rewardParts else "-"
