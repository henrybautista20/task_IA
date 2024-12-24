import json
import os
import logging
import datetime as dt
from ..services.elasticsearch import connector
from ..services.odoo import connector_odoo
from . import nice_schema
import json
import requests
from datetime import timedelta
import time
from elasticsearch.helpers import bulk


class NicecxoneElasticsearch:
    def __init__(self):
        self.exporter_odoo_sources = os.environ.get("NICE_ODOO_SOURCES").split(";")
        self.nice_username = os.environ.get("NICE_USERNAMES").split(";")
        self.nice_password = os.environ.get("NICE_PASSWORDS").split(";")
        self.nice_auth = os.environ.get("NICE_AUTH_COOKIES").split(";")
        self.nice_customer = os.environ.get("NICE_CUSTOMERS").split(";")
        self.nice_url = os.environ.get("NICE_URLS").split(";")
        self.elasticServer = connector.ElasticsearchConnection()
        self.odoo_connector = connector_odoo.OdooConnection()
        self.app_source_servers = self.odoo_connector.get_elasticsearch_servers()
        self.app_source_customers = [{} for i in self.nice_username]

    def nice_app_login(self):
        self.odoo_connector.get_customers_with_servers(self.exporter_odoo_sources[0])
        for index, app in enumerate(self.nice_username):
            self.app_source_customers[index] = {
                "username": self.nice_username[index],
                "password": self.nice_password[index],
                "auth_cookies": self.nice_auth[index],
                "nice_urls": self.nice_url[index],
                "customers": self.odoo_connector.get_customers_with_servers(self.exporter_odoo_sources[index]),
            }
            (self.app_source_customers[index]["customers"].pop(False)
             if False in self.app_source_customers[index]["customers"] else None)
            for ctm in self.app_source_customers[index]["customers"]:
                try:
                    customer = self.app_source_customers[index]["customers"][ctm]
                    customer["dragonfly_customer"] = (
                        customer["elastic_customer_id"][1]
                        if len(customer["elastic_customer_id"]) == 2
                        else self.app_source_customers[index]["customers"].pop(ctm)
                    )
                except:
                    (self.app_source_customers[index]["customers"].pop(False)
                     if False in self.app_source_customers[index]["customers"] else None)

    def get_token(self, username, password, auth):
        url = "https://api.incontact.com/InContactAuthorizationServer/Token"

        payload = {"grant_type": "password", "username": username, "password": password}
        headers = {"cookie": "BIGipServerpool_api=",
                   "Content-Type": "application/json", "Authorization": "basic " + auth}

        response = requests.request("POST", url, json=payload, headers=headers)
        nice_token = json.loads(response.text)
        return nice_token

    def transform_qm_questions(self, register):
        if "firstName" in register and "lastName" in register:
            register["fullNameAgent"] = (
                register["firstName"] + " " + register["lastName"]
                if register["firstName"] != None and register["lastName"] != None
                else None
            )

        register["id"] = str(register["contactId"])
        register_no = {i: register[i] for i in register if register[i] is not None}
        return register_no

    def transform_skill_agent(self, register):
        doc = {i: register[i] for i in register if register[i] is not None}
        doc["id"] = str(doc["agentId"]) + str(doc["skillId"])
        return doc

    def transform_agent(self, register):
        doc = {i: register[i] for i in register if register[i] is not None}
        doc["full_name"] = str(doc["firstName"]) + ' ' + str(doc["lastName"])
        return doc

    def transform_jobs(self, register):
        start_job = dt.datetime.strptime(register["jobStart"], "%Y-%m-%dT%H:%M:%S.%f%z")
        end_job = dt.datetime.strptime(register["jobEnd"], "%Y-%m-%dT%H:%M:%S.%f%z")
        register["jobDuration"] = (end_job - start_job).total_seconds()
        return register

    def generate_bulk(self, data, index_name, id_name):
        """
        Build a genrator to sent data to Elasticsearch
        """
        for doc in data:
            yield {
                "_index": index_name,
                "_id": doc[id_name] if id_name in doc else None,
                "_source": doc,
            }

    def get_data(self, url_endpoint, token, path, key_endpoint, index, transf_doc):
        url = url_endpoint + path
        cookies = {
            "AWSALB": "HThLhOnQnPizZikH0ufHzwk71yl7wtcRWen8xNC7lPfnqI%2FaV9slouisuSY%2Fg2MHXYIGhhUhvM7XdX1cykG404ktykU0lwxcca%2Be6Ji4h%2BXjkIDlKwZ%2FVQpGVNII",
            "AWSALBCORS": "HThLhOnQnPizZikH0ufHzwk71yl7wtcRWen8xNC7lPfnqI%2FaV9slouisuSY%2Fg2MHXYIGhhUhvM7XdX1cykG404ktykU0lwxcca%2Be6Ji4h%2BXjkIDlKwZ%2FVQpGVNII",
        }
        headers = {
            "Authorization": "bearer " + token["access_token"],
            "Content-Type": "application/x-www-form-urlencoded",
        }

        start_date = dt.datetime.today() - timedelta(hours=1) if self.hour_of_day != 21 else dt.datetime.today() - \
            timedelta(hours=48)
        params = {
            "startDate": start_date.strftime("%Y-%m-%dT%H:%M:%S"),
        }

        """
        params = {
            "startDate": '2024-07-04T00:29:12',
            "endDate": '2024-07-08T00:29:12'
        }
        """
        retry = 0
        max_retries = 3
        params = params if path == "contacts/completed" else None

        logging.info(
            f"Information {str(headers['Authorization'][:23])} 200 get_data_HTTP extract: start download data {self.hour_of_day}")
        response = requests.get(
            url,
            params=params,
            cookies=cookies,
            headers=headers
        )
        # logging.info(f"Information {response.status_code} 0 get_data_HTTP extract: start download data")
        # total = len(response.json()['completedContacts']) if  'completedContacts' in response.json() else 1
        # logging.info(f"Information {path} {total} get_data_HTTP extract: total data in index")
        # new link
        try:
            if response.status_code == 200:
                retry = 3
                body_df = response.json()
                next_link = body_df["_links"]["next"] if "_links" in body_df else None

                while next_link != None:
                    response = requests.get(
                        next_link,
                        cookies=cookies,
                        headers=headers,
                    )
                    logging.info(f"Information {path} 200 get_data_HTTP extract: start download data")
                    total = len(response.json()['completedContacts']
                                ) if 'completedContacts' in response.json() else 1
                    logging.info(f"Information {path} {total} get_data_HTTP extract: total data in index")
                    body_dfa = response.json()
                    body_df[key_endpoint] = body_dfa[key_endpoint] + body_df[key_endpoint]
                    next_link = body_dfa["_links"]["next"] if "next" in body_dfa["_links"] else None

                result = body_df[key_endpoint] if key_endpoint != "jobResults" else body_df[key_endpoint]["completedJobs"]
                customers = self.app_source_customers[index]["customers"]
                if key_endpoint == "completedContacts" or key_endpoint == "skills" or key_endpoint == "agentSkillAssignments":

                    for k in customers:
                        try:
                            data = [j for j in result if j["skillName"].split(
                                "-")[0] == k or k in j["skillName"]]
                            customers[k][key_endpoint] = data
                            list_values = []
                            for item in customers[k][key_endpoint]:
                                item = transf_doc(item) if transf_doc is not None else item
                                item["dragonfly_customer"] = customers[k]["dragonfly_customer"]
                                list_values = list_values + [item]
                            customers[k][key_endpoint] = list_values
                        except:
                            logging.info(f"Error {path} 0 get_data extract: {k} max retry in {path}")

                            pass

                else:
                    self.app_source_customers[index][key_endpoint] = [transf_doc(
                        i) for i in result] if transf_doc is not None else result
            elif response.status_code == 408:
                retry = retry = + 1
                time.sleep(10)
                if max_retries == retry:
                    logging.info(f"Error {path} 0 get_data extract: max retry in {path}")

            else:
                erro1 = response.json()['reason'] if 'reason' in response else 'No reason'
                logging.info(f"Error {erro1} .")
                error2 = response['text'].json() if 'text' in response else 'No text'
                logging.info(f"Error {error2} .")

                logging.info(f"Error { str(response.json())}   {path}")

        except requests.exceptions.HTTPError as e:
            logging.info(f"Error {path} 0 get_data_HTTP extract: {e}")
            retry = retry = + 1

        except requests.exceptions.Timeout as e:
            logging.info(f"Error {path} 0 get_data_timeout extract: {e}")
            retry = retry = + 1

        except requests.exceptions.TooManyRedirects as e:
            logging.info(f"Error {path} 0 get_data_manyrequest extract: {e}")
            retry = retry = + 1

        except requests.exceptions.RequestException as e:
            logging.info(f"Unknown error: {e}")
            retry = retry = + 1

        except Exception as e:
            logging.info(f"Error {path} 0 get_data extract: {e}")
            retry = retry = + 1

    def load_data(self, data, schemas, index_name, tranform_doc, id=None):
        logging.info(f"Working with index {index_name}")
        self.elasticServer.create_index(index_name, schemas.getSchema(index_name))
        for register in data:
            try:
                doc = tranform_doc(register) if tranform_doc != None else register
                (
                    self.elasticServer.populate_index(index_name, doc, doc[id])
                    if id != None
                    else self.elasticServer.populate_index(index_name, doc)
                )
            except:
                logging.info(f"Working with index ")
                pass

    def get_all_data(self, update_data):
        for index, app in enumerate(self.app_source_customers):
            app = self.app_source_customers[index]
            token = self.get_token(app["username"], app["password"], app["auth_cookies"])
            self.get_data(app["nice_urls"], token, "contacts/completed",
                          "completedContacts", index, self.transform_contacts)

            if update_data:
                self.get_data(app["nice_urls"], token, "skills", "skills", index, None)
                logging.info(f" Update data ")
                self.get_data(app["nice_urls"], token, "reports", "reports", index, None)

                self.get_data(app["nice_urls"], token, "report-jobs",
                              "jobResults", index, self.transform_jobs)

                self.get_data(app["nice_urls"], token, "agents", "agents", index, self.transform_agent)
                self.get_data(
                    app["nice_urls"], token, "agents/skills", "agentSkillAssignments", index, self.transform_skill_agent
                )

    def sync_data(self):
        today_time = dt.datetime.now(dt.timezone.utc)
        day_of_week = today_time.weekday()
        self.hour_of_day = today_time.hour
        update_data = True if self.hour_of_day == 16 and day_of_week == 3 else False

        update_data = True
        self.get_all_data(update_data)

        schemas = nice_schema.Schemas()
        all_odoo_servers = {i["id"]: i for i in self.app_source_servers}
        all_servers_to_connect = [
            x["customers"][y]["elasticsearch_server_ids"] for x in self.app_source_customers for y in x["customers"]
        ]
        all_server_flattened = [x for server_array in all_servers_to_connect for x in server_array]
        server_to_connect = list(set(all_server_flattened))

        for server_id in server_to_connect:
            server = all_odoo_servers[1]
            self.elastic_server = connector.ElasticsearchConnection(
                "https://" + server["server_ip"] + ":" + server["server_port"] + "/",
                server["elastic_api_id"],
                server["elastic_token"],
                os.environ["ELASTICSEARCH_CA_CERT_FILE"],
            )
            # Elasticsearch Connection

            connection = self.elastic_server.authenticate()
            es = self.elastic_server.get_client()
            if not connection:
                logging.info(f"Error connection elasticserver {sr}")
            else:
                for index, app in enumerate(self.app_source_customers):
                    app = self.app_source_customers[index]
                    if update_data:
                        for customer_key in app["customers"]:
                            customer = app["customers"][customer_key]
                            if server_id in customer["elasticsearch_server_ids"]:
                                success, failed = bulk(es, self.generate_bulk(
                                    app["reports"], "nice.reports", "reportId"))
                                logging.info(f"Information {customer_key} {success} bulk load: nice.reports")

                                success, failed = bulk(es, self.generate_bulk(
                                    app["jobResults"], "nice.jobs", "jobId"))
                                logging.info(f"Information {customer_key} {success} bulk load: nice.jobs")

                                success, failed = bulk(es, self.generate_bulk(
                                    app["agents"], "nice.agents", "agentId"))
                                logging.info(f"Information {customer_key} {success} bulk load: nice.agents")

                                success, failed = bulk(es, self.generate_bulk(
                                    customer["skills"], "nice.sskills", "skillId"))
                                logging.info(f"Information {customer_key} {success} bulk load: nice.sskills")

                                success, failed = bulk(
                                    es, self.generate_bulk(
                                        customer["agentSkillAssignments"], "nice.skillsagents", "id")
                                )
                                logging.info(
                                    f"Information {customer_key} {success} bulk load: nice.skillsagents")

                    for customer_key in app["customers"]:
                        customer = app["customers"][customer_key]
                        if server_id in customer["elasticsearch_server_ids"]:
                            if 'completedContacts' in customer:
                                success, failed = bulk(es, self.generate_bulk(
                                    customer["completedContacts"], "nice.contacts", "id"))
                                logging.info(f"Information {customer_key} {success} bulk load: nice.contacts")
