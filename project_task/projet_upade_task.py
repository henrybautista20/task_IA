import os
import asyncio
from openai import AzureOpenAI


async def main(): 
        
    try: 
    
        # Get configuration settings 
        azure_oai_endpoint = os.getenv("AZURE_OAI_ENDPOINT")
        azure_oai_key = os.getenv("AZURE_OAI_KEY")
        azure_oai_deployment = os.getenv("AZURE_OAI_DEPLOYMENT")
        client = AzureOpenAI(
         azure_endpoint = azure_oai_endpoint, 
         api_key=azure_oai_key,  
         api_version="2024-02-15-preview"
         )        
        final_task =  True
        while final_task:
           
            system_message = """
            You are an AI assistant that helps to provide information about the data extracted  with a conector (connector is a resource that extract data from an endpoint). 
            Your task is to take a brief description the source of data and the data.
            """

            input_text = """
Qualys is a leading company specializing in cybersecurity and compliance solutions. Their products and services are designed to assist organizations in managing and securing their IT infrastructure while ensuring compliance with industry standards and regulations.

Qualys offers a comprehensive suite of security and compliance solutions, including vulnerability management, threat intelligence, and cloud security services.

DATASETS:
- Qualys scans: .
- Qualys vulnerability management: .
- Qualys Assets: .
  """
            
            cron_data = "schedule cron : 0 10 * * * *"

            prompt = f"""
            Take the following short description and expand it:
            Description: {input_text}
            - Step 1: Describe the resource where the data is extracted (max_tokens=100).
            - Step 2: Provive a list with the datasets extracted whit a short description.
            - Step 3: Add a short note about how this data fits into a larger project or objective and the time where data is updated {cron_data}.
            """

            # Initialize messages array
            messages_array = [{"role": "system", "content": system_message}, {"role": "user", "content": prompt}]

            response = client.chat.completions.create(
                model=azure_oai_deployment,
                temperature=0.7,
                max_tokens=300,
                messages=messages_array
            )
            generated_text = response.choices[0].message.content
            # Add generated text to messages array
            messages_array.append({"role": "assistant", "content": generated_text})

            # Print generated text
            print("Summary: " + generated_text + "\n")
            final_task =  False

              
    except:
        pass

if __name__ == '__main__': 
    asyncio.run(main())
