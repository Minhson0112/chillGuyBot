from datetime import datetime

from bot.config.database import getDbSession
from bot.repository.farmChickenCoopRepository import FarmChickenCoopRepository
from bot.repository.farmCowShedRepository import FarmCowShedRepository


class FarmAnimalStarvationService:
    STARVATION_HOURS = 23

    ANIMAL_TYPE_CHICKEN = "chicken"
    ANIMAL_TYPE_COW = "cow"

    def removeStarvedAnimals(self):
        now = datetime.now()

        with getDbSession() as session:
            farmChickenCoopRepository = FarmChickenCoopRepository(session)
            farmCowShedRepository = FarmCowShedRepository(session)

            starvedChickenCoops = farmChickenCoopRepository.findStarvedChickenCoops(
                now=now,
                starvationHours=self.STARVATION_HOURS,
            )
            starvedCowSheds = farmCowShedRepository.findStarvedCowSheds(
                now=now,
                starvationHours=self.STARVATION_HOURS,
            )

            notificationSummaries = {}
            deadChickenCount = 0
            deadCowCount = 0

            for chickenCoop in starvedChickenCoops:
                chickenCount = chickenCoop.chicken_count
                deadChickenCount += chickenCount
                self.addNotificationSummary(
                    notificationSummaries=notificationSummaries,
                    farm=chickenCoop.farm,
                    animalType=self.ANIMAL_TYPE_CHICKEN,
                    quantity=chickenCount,
                )
                farmChickenCoopRepository.clearChickens(chickenCoop)

            for cowShed in starvedCowSheds:
                cowCount = cowShed.cow_count
                deadCowCount += cowCount
                self.addNotificationSummary(
                    notificationSummaries=notificationSummaries,
                    farm=cowShed.farm,
                    animalType=self.ANIMAL_TYPE_COW,
                    quantity=cowCount,
                )
                farmCowShedRepository.clearCows(cowShed)

            session.commit()

            return {
                "success": True,
                "deadChickenCount": deadChickenCount,
                "deadCowCount": deadCowCount,
                "notificationSummaries": list(notificationSummaries.values()),
            }

    def addNotificationSummary(
        self,
        notificationSummaries,
        farm,
        animalType: str,
        quantity: int,
    ):
        if farm is None or farm.member is None:
            return

        member = farm.member

        if not member.is_allow_notifications:
            return

        if member.user_id not in notificationSummaries:
            notificationSummaries[member.user_id] = {
                "userId": member.user_id,
                "deadChickenCount": 0,
                "deadCowCount": 0,
            }

        if animalType == self.ANIMAL_TYPE_CHICKEN:
            notificationSummaries[member.user_id]["deadChickenCount"] += quantity
            return

        if animalType == self.ANIMAL_TYPE_COW:
            notificationSummaries[member.user_id]["deadCowCount"] += quantity
