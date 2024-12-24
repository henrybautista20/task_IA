import os
import asyncio
from openai import AzureOpenAI


async def main(user_input): 
        
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


            file = open(file="/home/henryx/hen_projects/task_IA/project_task/time_remain.json", encoding="utf8").read()
            

            prompt = user_input + file
            
        
            messages_array = [{"role": "system", "content": system_message}, {"role": "user", "content": prompt}]


            response = client.chat.completions.create(
                model=azure_oai_deployment,
                temperature=0.7,
                max_tokens=1600,
                messages=messages_array
            )
            
            generated_text = response.choices[0].message.content

            file_path = "/home/henryx/hen_projects/task_IA/project_task/document_solved.txt"

            try:
                with open(file=file_path, mode="w", encoding="utf8") as results_file:
                    results_file.write(generated_text)
                print(f"Generated text successfully written to {file_path}")
            except Exception as e:
                print(f"An error occurred: {e}")
            final_task =  False

              
    except:
        pass

if __name__ == '__main__': 

    user_message  = """
                    You have a list of task in  2024, provide a json with activities in order to complete timesheets (time_required_hours) each activity 
                    should ha around 30 minutes to 2 hours.
                    Note: merge the task in diferent days, prove a json with the name of task and a short activity related with the task.
                    Example : {
                                "date": "2024-04-01",
                                "tasks": [
                                    {"task": "Label to all field in Kibana Views", "duration_hours": 2, "activity": "explore the api kibana" }
                                ]
                            }


                    TASKS:

                    Task 1 : NICE QA Surveys
                    Around : 8:30 Hours
                    Description: Create a connector that gets data from nice qa service, Include dashboard, index in elastiseach and schema.

                    Task 2: KBRA Dashboards
                    Around : 10:00 Hours
                    Description:  Investigate qualys api to build a dashboard to get data from kbra customers and inculcate devices al vulnerabilities.

                    

       """
    asyncio.run(main(user_message))
