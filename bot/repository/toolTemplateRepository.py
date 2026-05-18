from bot.models.toolTemplate import ToolTemplate


class ToolTemplateRepository:
    def __init__(self, session):
        self.session = session

    def findActiveByItemId(self, itemId: int):
        return (
            self.session.query(ToolTemplate)
            .filter(
                ToolTemplate.item_id == itemId,
                ToolTemplate.is_active == 1,
            )
            .first()
        )