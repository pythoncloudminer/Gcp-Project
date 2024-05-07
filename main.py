import logging
import pandas as pd
import requests
import concurrent.futures
from lambda_function import get_xyleme_token

# Configure logging
logging.basicConfig(level=logging.INFO)

API_URL = "https://ac-cisco.bravais.com/api/v1/statements"
MAX_CONCURRENT_REQUESTS = 5
PAGE_SIZE = 500  # Number of records per page

def fetch_data(page):
    url = API_URL
    headers = {
        "Bravais-Prod-Us-Context": xyleme_token
    }
    params = {
        "offset": page * PAGE_SIZE,
        "limit": PAGE_SIZE,
        "from": "20240502",
        "to": "20240503",
        "clid[0][id]": "96944cc4-864c-420c-836b-3a8116259002",
        "clid[0][display]": "TC2E",
        "clid": "96944cc4-864c-420c-836b-3a8116259002"
    }

    logging.info(f"Fetching data from page {page}")
    response = requests.get(url, headers=headers, params=params, timeout=10)
    data = response.json()

    if not data or not data.get('items'):
        logging.warning(f"No data received from page {page}")
        return None
    # Slice the list of items to return only the first ten records
    return data['items'][:10]

def extract_data_from_item(item):
    keys_to_extract = ["id", "employeeId", "timestamp", "verb", "object", "type", "status"]
    return {key: item.get(key) for key in keys_to_extract}

def extract_statements():
    combined_df = pd.DataFrame()
    page = 0
    empty_responses_count = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_CONCURRENT_REQUESTS) as executor:
        while empty_responses_count < 5:
            logging.info(f"Fetching statements from page {page}")
            futures = [executor.submit(fetch_data, page) for _ in range(MAX_CONCURRENT_REQUESTS)]
            for future in concurrent.futures.as_completed(futures):
                data = future.result()
                if data:
                    logging.info(f"Received data from page {page}")
                    empty_responses_count = 0
                    for item in data:
                        extracted_data = extract_data_from_item(item)
                        combined_df = pd.concat([combined_df,extracted_data], ignore_index=True)
                    page += 1
                else:
                    logging.warning(f"No data received from page {page}")
                    empty_responses_count += 1
                    if empty_responses_count >= 5:
                        break
    return combined_df

def fetch_statement_details(id, employeeId, is_course):
    additional_data_url = f"{API_URL}/{id}"
    headers = {"Bravais-Prod-Us-Context": xyleme_token}
    response = requests.get(additional_data_url, headers=headers, timeout=10)
    res = {}
    data = response.json()
    try:
        res['id'] = id
        res["employeeId"] = employeeId
        if is_course:
            res["documentId"] = data["object"]["definition"]["extensions"]["documentCdsId"]
            res["documentVersion"] = data["object"]["definition"]["extensions"]["versionId"].split("/")[-1]
        else:
            res["documentId"] = data["context"]["extensions"]["document"].split("/")[-1]
            res["documentVersion"] = data["context"]["extensions"]["documentVersion"].split("/")[-1]
        res["courseVersionId"] = data["courseVersionId"]
        res["courseSectionGuid"] = data["courseSectionGuid"]
        res["courseId"] = data["courseId"]
    except Exception as e:
        logging.debug(e)
    return res

def fetch_statement_details_for_df(df):
    statement_details = []
    for index, row in df.iterrows():
        statement_details.append(fetch_statement_details(row['id'], row['employeeId'], row['type'] == "Course"))
    return pd.DataFrame(statement_details)

# Call the function to fetch statements
logging.info("Fetching statements...")
xyleme_token = get_xyleme_token()["value"]
statements_df = extract_statements()
statements_df.to_csv("statements_df.csv", index=False) 

xyleme_token = get_xyleme_token()["value"]
statement_details_df = fetch_statement_details_for_df(statements_df)

statement_details_df.to_csv("statement_details_df.csv", index=False)


def extract_scores(df):
    scores_details =[]
    for i in df["courseId"]:
        url = f"https://ac-cisco.bravais.com/api/v1/courses/{i}/scores"
        headers = {
            "Bravais-Prod-Us-Context": xyleme_token
        }
        body = {
            "aid": "",
        }
        res = requests.post(url, headers=headers, json=body).json()
        tmp ={}
        tmp["courseId"] = i
        tmp["startedDate"] = res["items"]["started"]
        tmp["completedDate"] = res["items"]["ended"]
        tmp["completedStatus"] = res["items"]["completed"]
        tmp["status"] = res["items"]["status"]
        tmp["score"] = res["items"]["score"]
        tmp["attempt"] = res["items"]["attempt"]
        scores_details.append(tmp)
    return pd.createDataFrame(tmp)

scores_df = extract_scores(statements_details_df)

transit_df = pd.merge(statements_df, scores_df, on="courseId", how="left")

final_df = pd.merge(transit_df, statement_details_df, on="id", how="inner")
