from pydantic import BaseModel
from .. import models

# IMPORTANT: This mapping is like a table definition for data in Redis. Do not alter the value of the key
# It is however possible to alter the classname without issues, however, the same values for those classes will apply going forward.
# Altering the key names requires a migration of data.
model_to_key_mapping = {
    models.ChatMessage: "ChatMessage",
    models.ChatMessageWithMeta: "ChatMessage",
    models.Chat: "Chat",
    models.ChatWithMeta: "Chat",
    models.PromptTemplate: "PromptTemplate",
    models.PromptTemplateWithMeta: "PromptTemplate",
    models.Prompt: "Prompt",
    models.PromptWithMeta: "Prompt",
    models.CompletionParameters: "CompletionParameters",
    models.CompletionParametersWithMeta: "CompletionParameters",
    models.UserProfile: "UserProfile",
    models.UserProfileWithMeta: "UserProfile",
}


def get_class_name(_class: BaseModel) -> str:
    return model_to_key_mapping[_class]
