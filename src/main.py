import os
import pandas as pd
import gradio as gr
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.kernel import Kernel
from semantic_kernel.functions.function_library import FunctionChoiceBehavior
from src.plugins.reconciliation_plugin import ReconciliationPlugin




# Assuming src is in the python path or run from project root
from src.core.kernel_manager import KernelManager
from src.core.chat_manager import ChatManager
from src.plugins.transaction_plugin import TransactionPlugin
from src.plugins.analytics_plugin import AnalyticsPlugin
from src.plugins.fraud_plugin import FraudPlugin
from src.utils.csv_loader import CSVLoader
from src.models.transaction import Transaction

# --- Configuration ---
# You might want to move these to a config file or environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_ORG_ID = os.getenv("OPENAI_ORG_ID")
AZURE_DEPLOYMENT_NAME = os.getenv("AZURE_DEPLOYMENT_NAME") # For Azure OpenAI
AZURE_ENDPOINT = os.getenv("AZURE_ENDPOINT")             # For Azure OpenAI

# --- Initialize Kernel and Chat Manager ---
kernel_manager = KernelManager(
    api_key=OPENAI_API_KEY,
    org_id=OPENAI_ORG_ID,
    azure_deployment_name=AZURE_DEPLOYMENT_NAME, # Pass if using Azure
    azure_endpoint=AZURE_ENDPOINT               # Pass if using Azure
)
kernel: Kernel = kernel_manager.get_kernel()
chat_manager = ChatManager(kernel)

# --- Register Plugins ---
# These plugins will operate on the loaded transaction data
transaction_plugin = TransactionPlugin()
analytics_plugin = AnalyticsPlugin()
fraud_plugin = FraudPlugin()
reconciliation_plugin = ReconciliationPlugin()


kernel.add_plugin(transaction_plugin, plugin_name="TransactionPlugin")
kernel.add_plugin(analytics_plugin, plugin_name="AnalyticsPlugin")
kernel.add_plugin(fraud_plugin, plugin_name="FraudPlugin")
kernel.add_plugin(reconciliation_plugin, plugin_name="ReconciliationPlugin")



# --- Global Data Store ---
# This will hold our processed transactions
global_transactions: list[Transaction] = []
global_df: pd.DataFrame = pd.DataFrame()

# --- Gradio UI Functions ---
def load_and_process_csv(file):
    """Loads, validates, and processes the uploaded CSV file."""
    global global_transactions, global_df
    if file is None:
        return "No file uploaded.", gr.update(interactive=False), gr.update(interactive=False)

    file_path = file.name
    csv_loader = CSVLoader(file_path)
    try:
        global_transactions = csv_loader.load_transactions()
        global_df = pd.DataFrame([t.model_dump() for t in global_transactions])
        
        # Link the data to the plugins
        transaction_plugin.set_transactions(global_transactions, global_df)
        analytics_plugin.set_transactions(global_transactions, global_df)
        fraud_plugin.set_transactions(global_transactions, global_df)
        reconciliation_plugin.set_transactions(global_transactions, global_df)

        success_message = f"Successfully loaded {len(global_transactions)} transactions."
        return success_message, gr.update(interactive=True), gr.update(interactive=True)
    except ValueError as e:
        error_message = f"Error processing CSV: {e}"
        return error_message, gr.update(interactive=False), gr.update(interactive=False)
    except Exception as e:
        error_message = f"An unexpected error occurred: {e}"
        return error_message, gr.update(interactive=False), gr.update(interactive=False)

async def chat_with_agent(message: str, history: list[list[str]]):
    """Handles chat interaction with the AI agent."""
    global global_transactions
    if not global_transactions:
        yield "Please upload a CSV file first."
        return

    # Add user message to chat history
    chat_manager.add_message("user", message)
    
    # Get AI response using automatic function calling
    # We use stream_chat_async for a better UX with Gradio
    full_response_content = ""
    async for content in kernel.stream_chat_async(
        chat_manager.chat_history,
        settings=kernel_manager.get_chat_service_settings(),
        execution_settings=kernel_manager.get_execution_settings(
            FunctionChoiceBehavior.Auto() # Enable auto function calling
        )
    ):
        if content.content:
            full_response_content += content.content
            yield full_response_content

    # Add AI response to chat history
    chat_manager.add_message("assistant", full_response_content)


# --- Gradio Interface Layout ---
with gr.Blocks(title="PSP Transaction Analysis Agent") as demo:
    gr.Markdown(
        """
        # PSP Transaction Analysis Agent
        Upload your transaction CSV and ask me anything about your data!
        """
    )

    with gr.Row():
        with gr.Column(scale=1):
            csv_file_input = gr.File(label="Upload CSV File", type="filepath")
            csv_load_status = gr.Textbox(label="CSV Load Status", interactive=False)
            load_button = gr.Button("Process CSV")
            
            load_button.click(
                load_and_process_csv,
                inputs=[csv_file_input],
                outputs=[csv_load_status, gr.update(interactive=False), gr.update(interactive=False)]
            )
            # Re-enable chat components after successful load
            csv_load_status.change(
                lambda s: (gr.update(interactive=True), gr.update(interactive=True)) 
                          if "Successfully loaded" in s else (gr.update(interactive=False), gr.update(interactive=False)),
                inputs=[csv_load_status],
                outputs=[gr.Textbox(label="Chat Input", interactive=False), gr.Chatbot(label="Chat History", interactive=False)]
            )
        
        with gr.Column(scale=2):
            chatbot = gr.Chatbot(label="Chat History", interactive=False, height=500)
            msg = gr.Textbox(label="Chat Input", placeholder="Ask about transactions, analytics, or fraud...", interactive=False)
            clear = gr.ClearButton([msg, chatbot])

            msg.submit(chat_with_agent, inputs=[msg, chatbot], outputs=chatbot, concurrency_limit=None)
            clear.click(lambda: (None, None), inputs=None, outputs=[msg, chatbot])

if __name__ == "__main__":
    demo.launch(debug=True, share=False)
