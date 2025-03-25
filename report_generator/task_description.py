import os
import asyncio
from openai import AzureOpenAI


async def main(): 
        
    try: 
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
            You are an AI assistant that helps to provide information about task taking a short description, you are able to provide more informacion.
            Provide a list of step to complete the task.
            """

            input_text = """
                    Task: Create UG2 and Lummus dashboard 
                    Description: Combine the information from umbrella and crowdstrike in orde to create a new dashboard.
                    The dashboard should be in Kibana and these will be copy to respective space (UG2 and Lummus).  
                    Note: The data exist in or data base
                 """
            time=8
            
            cron_data = "schedule cron : 0 10 * * * *"

            prompt = f"""
            Take the following short description and expand it:
            Description: {input_text}
            - Step 1: Provive a short description with the task.
            - Step 2: Provide steps to complete the task in {time} hours  with an interval of 1 to 3 hours.
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
