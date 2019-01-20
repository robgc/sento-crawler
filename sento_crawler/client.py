from peony import PeonyClient, task

from sento_crawler.logger import get_logger
from sento_crawler.model import Model


class TwitterClient(PeonyClient):
    @classmethod
    async def create(cls):
        cls.model = Model()
        cls.logger = get_logger()
        await cls.model.create()

    @task
    async def get_topics(self):
        response = await self.api.trends.place.get(id=1)
        self.logger.debug(response)
