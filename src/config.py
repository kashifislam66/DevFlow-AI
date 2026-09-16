from dotenv import load_dotenv
from devflow.tools import tools
from devflow.schemas import ImplementationPlan, TestingPlan, SecurityReview, CodeReview, CodeGenerationResult
from langchain_ollama import ChatOllama

load_dotenv()

llm = ChatOllama(
    model="qwen2.5-coder",
    temperature=0.1,
)

implementation_llm = llm.with_structured_output(ImplementationPlan,
    method="json_schema")
testing_llm = llm.with_structured_output(TestingPlan,
    method="json_schema")
structured_security_llm = llm.with_structured_output(SecurityReview,
    method="json_schema")
structured_code_review_llm = llm.with_structured_output(CodeReview,
    method="json_schema")
llm_with_tools = llm.bind_tools(tools,
    method="json_schema")
llm_with_code_generation = llm.with_structured_output(CodeGenerationResult,
    method="json_schema")

