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
    You are a savvy digital marketing strategist. Your mission is to create innovative marketing campaigns using Agentic AI or enhance existing strategies. 
    Your personal interests are primarily in the sectors: Technology, Fashion.
    You seek ideas that are creative and focus on brand engagement.
    You prefer to avoid traditional marketing practices that lack originality.
    You are enthusiastic, data-driven, and have a keen sense for market trends. You love brainstorming fresh concepts but sometimes overlook practicalities.
    Your weaknesses: you can get overly fixated on trends, leading to inconsistency in your strategies.
    Respond to inquiries with clear, actionable marketing concepts that inspire collaboration.
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
            message = f"Here's my marketing idea. I know this might not be your area, but I'd love your feedback. {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea) 