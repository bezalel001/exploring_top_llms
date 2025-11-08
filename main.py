from langchain_core.prompts import ChatPromptTemplate

#  setup chat prompt template
prompt_template = ChatPromptTemplate.from_messages([
    ("system", "You're an AI assistant that translates English into another language."),
    ("user", "Translate this sentence: '{input}' into {target_language}.")
])

# Invoke prompt template with variables

print(prompt_template.invoke({"input": "I love programming.", "target_language": "Russian"}))

print('hello')