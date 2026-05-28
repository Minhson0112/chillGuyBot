import random
from datetime import datetime, timedelta, timezone

import discord

from bot.config.database import getDbSession
from bot.repository.giveawayParticipantRepository import GiveawayParticipantRepository
from bot.repository.giveawayRepository import GiveawayRepository
from bot.repository.giveawayWinnerRepository import GiveawayWinnerRepository
from bot.services.giveaway.giveawayMessageService import GiveawayMessageService


class GiveawayDrawService:
    GMT7 = timezone(timedelta(hours=7))

    def __init__(self):
        self.giveawayMessageService = GiveawayMessageService()

    def drawGiveaway(self, giveawayId: int):
        endedAt = datetime.now(self.GMT7).replace(tzinfo=None)

        with getDbSession() as session:
            giveawayRepository = GiveawayRepository(session)
            participantRepository = GiveawayParticipantRepository(session)
            winnerRepository = GiveawayWinnerRepository(session)
            giveaway = giveawayRepository.findById(giveawayId)

            if giveaway is None:
                return {
                    "success": False,
                    "message": "Giveaway không tồn tại.",
                }

            currentWinners = winnerRepository.findCurrentWinnersByGiveawayId(giveawayId)

            if len(currentWinners) > 0:
                giveawayRepository.markEnded(
                    giveaway=giveaway,
                    endedAt=endedAt,
                )
                session.commit()

                return {
                    "success": True,
                    "giveaway": giveaway,
                    "winners": currentWinners,
                    "message": self.buildGiveawayResultMessage(giveaway, currentWinners),
                }

            participants = participantRepository.findActiveParticipantsByGiveawayId(giveawayId)
            winnerCount = min(giveaway.winner_count, len(participants))
            selectedParticipants = []

            if winnerCount > 0:
                selectedParticipants = random.sample(participants, winnerCount)

            winners = []

            for index, participant in enumerate(selectedParticipants):
                winners.append(
                    winnerRepository.create(
                        giveawayId=giveaway.id,
                        userId=participant.user_id,
                        slotNumber=index + 1,
                    )
                )

            giveawayRepository.markEnded(
                giveaway=giveaway,
                endedAt=endedAt,
            )

            session.commit()

            return {
                "success": True,
                "giveaway": giveaway,
                "winners": winners,
                "message": self.buildGiveawayResultMessage(giveaway, winners),
            }

    def rerollWinner(
        self,
        giveawayId: int,
        winnerId: int,
        requestedByUserId: int,
    ):
        with getDbSession() as session:
            giveawayRepository = GiveawayRepository(session)
            participantRepository = GiveawayParticipantRepository(session)
            winnerRepository = GiveawayWinnerRepository(session)
            giveaway = giveawayRepository.findById(giveawayId)
            oldWinner = winnerRepository.findById(winnerId)

            if giveaway is None:
                return {
                    "success": False,
                    "message": "Giveaway không tồn tại.",
                }

            if giveaway.created_by_user_id != requestedByUserId:
                return {
                    "success": False,
                    "message": "Chỉ người tạo giveaway mới có quyền reroll.",
                }

            if oldWinner is None or oldWinner.giveaway_id != giveawayId:
                return {
                    "success": False,
                    "message": "Winner cần reroll không tồn tại.",
                }

            if oldWinner.current_slot_number is None:
                return {
                    "success": False,
                    "message": "Winner này đã được reroll trước đó.",
                }

            participants = participantRepository.findActiveParticipantsByGiveawayId(giveawayId)
            existingWinnerUserIds = winnerRepository.findWinnerUserIdsByGiveawayId(giveawayId)
            eligibleParticipants = [
                participant
                for participant in participants
                if participant.user_id not in existingWinnerUserIds
            ]

            if len(eligibleParticipants) == 0:
                return {
                    "success": False,
                    "message": "Không còn người tham gia hợp lệ để reroll.",
                }

            selectedParticipant = random.choice(eligibleParticipants)
            winnerRepository.markRerolled(oldWinner)
            newWinner = winnerRepository.create(
                giveawayId=giveawayId,
                userId=selectedParticipant.user_id,
                slotNumber=oldWinner.slot_number,
                drawRound=oldWinner.draw_round + 1,
                rerolledFromWinnerId=oldWinner.id,
            )

            session.commit()

            currentWinners = winnerRepository.findCurrentWinnersByGiveawayId(giveawayId)

            return {
                "success": True,
                "giveaway": giveaway,
                "winner": newWinner,
                "winners": currentWinners,
                "message": self.buildGiveawayRerollMessage(giveaway, currentWinners),
            }

    def buildGiveawayResultMessage(self, giveaway, winners):
        winnerText = self.buildWinnerText(winners)
        rewardText = self.giveawayMessageService.buildRewardText(giveaway)

        if len(winners) == 0:
            winnerText = "- Không có người tham gia hợp lệ"

        return (
            f"Giveaway **{giveaway.title}** do <@{giveaway.created_by_user_id}> tổ chức đã kết thúc\n"
            "người chiến thắng\n"
            f"{winnerText}\n"
            f"phần thưởng : {rewardText}"
        )

    def buildGiveawayRerollMessage(self, giveaway, winners):
        return (
            f"Đã reroll giveaway **{giveaway.title}**\n"
            "người chiến thắng\n"
            f"{self.buildWinnerText(winners)}\n"
            f"phần thưởng : {self.giveawayMessageService.buildRewardText(giveaway)}"
        )

    def buildWinnerText(self, winners):
        if len(winners) == 0:
            return "- Không có người chiến thắng"

        return "\n".join([f"- <@{winner.user_id}>" for winner in winners])

    async def sendGiveawayResult(self, bot, giveawayId: int):
        result = self.drawGiveaway(giveawayId)

        if not result["success"]:
            print(f"Giveaway draw failed: {result['message']}")
            return

        giveaway = result["giveaway"]

        if giveaway.channel_id is None or giveaway.message_id is None:
            print(f"Giveaway draw skipped message reply: giveawayId={giveaway.id}")
            return

        channel = await self.resolveTextChannel(bot, giveaway.channel_id)

        if channel is None:
            print(f"Giveaway draw skipped missing channel: giveawayId={giveaway.id}")
            return

        try:
            giveawayMessage = await channel.fetch_message(giveaway.message_id)
        except discord.NotFound:
            print(f"Giveaway draw skipped missing message: giveawayId={giveaway.id}")
            return
        except discord.Forbidden:
            print(f"Giveaway draw skipped forbidden message: giveawayId={giveaway.id}")
            return
        except discord.HTTPException as error:
            print(f"Giveaway draw skipped http error: giveawayId={giveaway.id}, error={error}")
            return

        from bot.views.giveawayRerollView import GiveawayRerollView

        rerollView = None

        if len(result["winners"]) > 0:
            rerollView = GiveawayRerollView(
                giveawayId=giveaway.id,
                winners=result["winners"],
            )

        await giveawayMessage.reply(
            content=result["message"],
            view=rerollView,
            allowed_mentions=discord.AllowedMentions(
                users=True,
                roles=False,
                everyone=False,
            ),
        )

    async def resolveTextChannel(self, bot, channelId: int):
        channel = bot.get_channel(channelId)

        if channel is None:
            try:
                channel = await bot.fetch_channel(channelId)
            except discord.NotFound:
                return None
            except discord.Forbidden:
                return None
            except discord.HTTPException:
                return None

        if not isinstance(channel, discord.TextChannel):
            return None

        return channel
