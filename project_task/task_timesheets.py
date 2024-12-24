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
            You are an AI assistant that provide a list of steps to complete some tasks in order to complete a list of timeshets.
            """

            input_text = """
                    You have a list of task in february 2024, provide a list with activities, merge in days, to complete timesheets each activity 
                    should ha around 30 minutes to 2 hours.
                    Note: merge the task between different days, in order to near range 

                    Task 1:Label to all field in Kibana Views
                    Description: Rename all labels offields in kibana data views, create an script that update the fields

                    Task 2:Change runtine fields into ingest pipeline
                    Around : 4:00 Hours
                    Description: Get all data views in kibana that have runtine fields, rewrite the code in a pipeline

                    Task 3:Nerdio Integration
                    Around : 5 hours 
                    Description: Establish  connection with nerdio, We need to get savings information, devices and pools.

                    Task 4:SLO How it Works in Kibana
                    Around : 10 Hours
                    Description: Investigate how slo works in kibana and create an example of integration with our data

                    Task 5:Dashboard Links in Converge Scores Dashboard
                    Around : 10 hours
                    Description: Add URL link from converge dashboard to category dashboard with a preselected link 

                    Task 6:Enhanced Table for Kibana 8.12.1
                    Around : 15 hours
                    Description: Update enhanced table for kibana 8.12.1

                    Task 7: knowBe training
                    Around : 3 hours
                    Description: Complete trinig of security, and data managements

                    Task 8: Create canvas for TDFG
                    Around : 12 hours
                    Description: Create a canvas with information of tickes, sla task, nice call for TDFG

                    Task 9: Graph Section of Kibana
                    Around : 10 hours
                    Description: Investigate about the use of Graph Section of Kibana and create and integration with our data.

                 """
            time=8
            

            prompt = input_text

            # Initialize messages array
            messages_array = [{"role": "system", "content": system_message}, {"role": "user", "content": prompt}]

            response = client.chat.completions.create(
                model=azure_oai_deployment,
                temperature=0.7,
                max_tokens=4000,
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
