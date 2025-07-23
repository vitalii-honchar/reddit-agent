from typing import Callable, Dict, Any

from langchain_core.messages import HumanMessage, BaseMessage, ToolMessage, AIMessage
from langchain_core.messages.utils import count_tokens_approximately
from langchain_core.language_models import BaseLanguageModel

from prompt.prompt_manager import PromptManager
import logging

logger = logging.getLogger(__name__)


class SummarizationHook:
    def __init__(self, llm: BaseLanguageModel, prompt_manager: PromptManager, max_tokens: int, max_summary_tokens: int):
        self.llm = llm
        self.prompt_manager = prompt_manager
        self.max_tokens = max_tokens
        self.max_summary_tokens = max_summary_tokens

    def create_hook(self) -> Callable:
        def summarize_messages(state: Dict[str, Any]) -> Dict[str, Any]:
            messages = state.get("messages", [])
            
            total_tokens = sum(count_tokens_approximately(msg.content) for msg in messages)
            
            if total_tokens <= self.max_tokens:
                return state
            
            logger.info(f"Message summarization triggered: {total_tokens} tokens > {self.max_tokens} limit")
            
            if len(messages) <= 3:
                return state
            
            system_msg = messages[0] if messages[0].type == "system" else None
            initial_query = messages[1] if len(messages) > 1 else None
            recent_messages = messages[-3:]
            
            start_idx = 2 if system_msg else 1
            end_idx = len(messages) - 3
            
            if end_idx <= start_idx:
                return state
            
            messages_to_summarize = messages[start_idx:end_idx]
            conversation_text = self._build_conversation_context(messages_to_summarize)
            
            try:
                summary_content = self._create_llm_summary(conversation_text)
                summary_message = AIMessage(content=summary_content)
                
                new_messages = []
                if system_msg:
                    new_messages.append(system_msg)
                if initial_query:
                    new_messages.append(initial_query)
                new_messages.append(summary_message)
                new_messages.extend(recent_messages)
                
                logger.info(f"LLM summarized {len(messages_to_summarize)} messages into 1 summary message")
                return {"messages": new_messages}
                
            except Exception as e:
                logger.warning(f"LLM summarization failed, returning original messages: {e}")
                return state
        
        return summarize_messages

    def _build_conversation_context(self, messages: list[BaseMessage]) -> str:
        conversation_parts = []
        for msg in messages:
            if isinstance(msg, ToolMessage):
                conversation_parts.append(f"TOOL_RESULT[{msg.name}]: {msg.content}")
            elif isinstance(msg, AIMessage):
                if msg.tool_calls:
                    tool_calls = []
                    for tc in msg.tool_calls:
                        if isinstance(tc, dict):
                            args = tc.get('args', {})
                            tool_calls.append(f"{tc['name']}({args})")
                        else:
                            tool_calls.append(f"{tc.name}({getattr(tc, 'args', {})})")
                    conversation_parts.append(f"AI_TOOLS_CALLED: {', '.join(tool_calls)}")
                if msg.content:
                    conversation_parts.append(f"AI_RESPONSE: {msg.content}")
            elif isinstance(msg, HumanMessage):
                conversation_parts.append(f"HUMAN: {msg.content}")
            else:
                conversation_parts.append(f"{msg.type.upper()}: {msg.content}")
        
        return "\n\n".join(conversation_parts)

    def _create_llm_summary(self, conversation_text: str) -> str:
        summarization_prompt = self.prompt_manager.load_prompt("summarization", "system")
        
        prompt_content = summarization_prompt.format(
            conversation_text=conversation_text,
            max_summary_tokens=self.max_summary_tokens
        )
        
        summary_response = self.llm.invoke([HumanMessage(content=prompt_content)])
        summary_content = f"CONVERSATION SUMMARY:\n{summary_response.content}"
        
        if count_tokens_approximately(summary_content) > self.max_summary_tokens:
            char_limit = self.max_summary_tokens * 3
            summary_content = summary_content[:char_limit] + "..."
        
        return summary_content