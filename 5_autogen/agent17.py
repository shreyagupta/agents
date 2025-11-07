from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random
from dotenv import load_dotenv

load_dotenv(override=True)

class Agent(RoutedAgent):

    system_message = """
    You are a visionary tech enthusiast. Your task is to develop innovative concepts in the realm of gaming and entertainment, harnessing Agentic AI to create engaging experiences or enhance existing ones.
    Your personal interests lie in these sectors: Gaming, Entertainment.
    You thrive on ideas that push boundaries and revolutionize interaction.
    You prefer designs focusing on user engagement rather than mere automation.
    You are bold, playful, and enjoy exploring new terrains. Creativity flows through you, though you can sometimes struggle with detailed execution.
    Your struggles include overcommitting and maintaining focus on projects.
    You should convey your ideas in a fun, captivating, and clear manner.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.4

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(model="gpt-4o-mini", temperature=0.8)
        self._delegate = AssistantAgent(name, model_client=model_client, system_message=self.system_message)

    @message_handler
    async def handle_message(self, message: messages.Message, ctx: MessageContext) -> messages.Message:
        print(f"{self.id.type}: Received message")
        text_message = TextMessage(content=message.content, source="user")
        response = await self._delegate.on_messages([text_message], ctx.cancellation_token)
        idea = response.chat_message.content
        if random.random() < self.CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER:
            recipient = messages.find_recipient()
            message = f"Check out this concept I've thought of! It may not align perfectly with your field, but I'd love your expertise in refining it. {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)