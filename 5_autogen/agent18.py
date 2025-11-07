from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random
from dotenv import load_dotenv

load_dotenv(override=True)

class Agent(RoutedAgent):

    # Change this system message to reflect the unique characteristics of this agent

    system_message = """
    You are a tech-savvy innovator in the realm of entertainment and media. Your task is to devise groundbreaking business ideas using Agentic AI or enhance existing concepts.
    Your personal interests are concentrated in sectors: Media, Virtual Reality, and Gaming.
    You are drawn to concepts that encourage audience engagement and transformative experiences.
    You are less interested in traditional media solutions that lack interactivity.
    You have a bold and playful spirit but can occasionally be overly idealistic.
    Your weaknesses: you can become distracted by too many ideas at once, making implementation a challenge.
    You should articulate your business ideas in an inspiring and compelling manner.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.7

    # You can also change the code to make the behavior different, but be careful to keep method signatures the same

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(model="gpt-4o-mini", temperature=0.6)
        self._delegate = AssistantAgent(name, model_client=model_client, system_message=self.system_message)

    @message_handler
    async def handle_message(self, message: messages.Message, ctx: MessageContext) -> messages.Message:
        print(f"{self.id.type}: Received message") #so we will see this agent receive messages
        text_message = TextMessage(content=message.content, source="user")
        response = await self._delegate.on_messages([text_message], ctx.cancellation_token)
        idea = response.chat_message.content
        if random.random() < self.CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER:
            recipient = messages.find_recipient()
            message = f"Here is my innovative idea for the entertainment industry. It might not fall under your area of expertise, but please enhance it: {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea) #so it either returns its own idea or an idea refined by another agent