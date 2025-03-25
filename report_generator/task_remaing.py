import os
import asyncio
from openai import AzureOpenAI
from openai import OpenAI

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

        client = OpenAI(api_key=f" {os.getenv("DEEPSEAK_API_KEY")}", base_url="https://api.deepseek.com")    
        final_task =  True
        while final_task:
           
            system_message = """
            You are an AI assistant that helps make neuropsychological.
            """


            file = open(file="/home/henryx/hen_projects/task_IA/report_generator/report_in.txt", encoding="utf8").read()
            

            prompt = user_input + file
            
        
            messages_array = [{"role": "system", "content": system_message}, {"role": "user", "content": prompt}]


            response = client.chat.completions.create(
                model="deepseek-reasoner" ,#azure_oai_deployment
                temperature=0.7,
                max_tokens=5600,
                messages=messages_array
            )
            
            generated_text = response.choices[0].message.content

            file_path = "/home/henryx/hen_projects/task_IA/report_generator/report_out.txt"

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
            Necesito que utilices el siguiente texto para generar un reporte neuro psicológico de un estudiante de maestria, 
            utilizando la información que se encuentra en el archivo adjunto, y un json con el resultado del test aplicado.
              Ayudem a completar el reporte con la siguiente requisitos:
            - Minimo 2500 palabras.
            - Se argumentativo.
            - Utiza parrafos en las respuestas.
            - Utiliza un lenguaje formal.
            JSON:
            {
  "Resultados": {
    "Pruebas": {
      "Memoria Verbal": {
        "CVLT": {
          "Lis1": -2.6,
          "LisApr": -2.7,
          "LisB": -2,
          "LisCPLib": -3.2,
          "LisCPPist": -2.3,
          "LisLPLib": -2.4,
          "LisLPPist": -3.2,
          "LisDis": -1.2
        }
      },
      "Memoria Visual": {
        "RCFT": {
          "R. Inmediato": -1.93,
          "R. Diferido": -2.072,
          "Reconocimiento": -2.296
        }
      },
      "Visoconstrucción": {
        "Copia RCFT": -5.067,
        "Tiempo": -2.912
      },
      "Lenguaje": {
        "Boston": -5.45,
        "Fluencia Verbal": "n/a",
        "Fluencia Semántica": -1.862
      },
      "Atención": {
        "Dígitos adelante": -1,
        "Dígitos atrás": -2.4,
        "Trail A": "int"
      },
      "Función Ejecutiva": {
        "Trail B": "n/a",
        "Estrategia Copia": "V",
        "WCST": {
          "Resp. Perseverat.": -1.7,
          "Nivel Conceptual": -1
        }
      }
    }
  }
}


       """
    asyncio.run(main(user_message))
