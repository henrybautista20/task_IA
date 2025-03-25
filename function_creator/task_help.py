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
            You are a Data Science IA assistant helping 
            """
            """ prompt = f
            Take the following short description and expand it:
            Description: {input_text}
            - Step 1: Provide a list with ideas to build the dashboard.
            Fields from agents: ['agentId', 'firstName', 'lastName', 'isActive', 'teamId', 'teamName', 'reportToName', 'isSupervisor', 'lastUpdated', 'profileId', 'profileName', 'timeZone', 'country', 'countryName', 'state', 'useTeamMaxConcurrentChats', 'maxConcurrentChats', 'createDate', 'inactiveDate', 'rehireStatus', 'employmentTypeName', 'referral', 'atHome', 'hiringSource', 'scheduleNotification', 'useTeamEmailAutoParkingLimit', 'maxEmailAutoParkingLimit', 'useAgentTimeZone', 'timeDisplayFormat', 'sendEmailNotifications', 'isWhatIfAgent', 'timeZoneOffset', 'requestContact', 'chatThreshold', 'useTeamChatThreshold', 'emailThreshold', 'useTeamEmailThreshold', 'workItemThreshold', 'useTeamWorkItemThreshold', 'contactAutoFocus', 'useTeamContactAutoFocus', 'useTeamRequestContact', 'voiceThreshold', 'useTeamVoiceThreshold', 'recordingNumbers', 'isOpenIdProfileComplete', 'teamUuid', 'maxPreview', 'deliveryMode', 'totalContactCount', 'useTeamDeliveryModeSettings', 'isBillable', 'agentVoiceThreshold', 'agentChatThreshold', 'agentEmailThreshold', 'agentWorkItemThreshold', 'agentContactAutoFocus', 'agentRequestContact', 'agentMaxVersion', 'locked', 'combinedUserNameDomain', 'rowNumber', 'SmsThreshold', 'DigitalThreshold']
            Fields from contacts:['teamName', 'postQueueSeconds', 'time_hours', 'isLogged', 'holdCount', 'time_day_number', 'mediaSubTypeName', 'primaryDispositionId', 'callbackTime', 'refuseTime', 'time_day', 'preQueueSeconds', 'id', 'abandoned', 'contactStart', 'dateContactWarehoused', 'toAddr', 'mediaTypeName', 'isOutbound', 'contactId', 'endReason', 'campaignId', 'masterContactId', 'mediaType', 'firstName', 'skillId', 'confSeconds', 'acwSeconds', 'analyticsProcessedDate', 'dateACWWarehoused', 'lastUpdateTime', 'totalDurationSeconds', 'lastName', 'agentId', 'abandonSeconds', 'routingTime', 'fullNameAgent', 'mediaSubTypeId', 'isShortAbandon', 'isAnalyticsProcessed', 'inQueueSeconds', 'contactStartDate', 'skillName', 'releaseSeconds', 'agentSeconds', 'serviceLevelFlag', 'isRefused', 'pointOfContactName', 'pointOfContactId', 'secondaryDispositionId', 'transferIndicatorId', 'isTakeover', 'teamId', 'transferIndicatorName', 'holdSeconds', 'fromAddr', 'campaignName', 'refuseReason', 'dispositionNotes']
            """


            # Print generated text
            ## print("Summary: " + generated_text + "\n")
            file = open(file="/home/henryx/hen_projects/task_IA/function_creator/function_use.py", encoding="utf8").read()
            

            prompt = user_input + file
            
            # Initialize messages array
            messages_array = [{"role": "system", "content": system_message}, {"role": "user", "content": prompt}]

            
            # Add generated text to messages array
            #messages_array.append({"role": "assistant", "content": generated_text})

            response = client.chat.completions.create(
                model=azure_oai_deployment,
                temperature=0.7,
                max_tokens=6000,
                messages=messages_array
            )
            
            generated_text = response.choices[0].message.content

            file_path = "/home/henryx/hen_projects/task_IA/function_creator/function_solved.txt"

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
        rewite the code for multi modal distribution anaylsis
       """
    asyncio.run(main(user_message))
