import googleapiclient.discovery
from google.oauth2 import service_account
import time
import pandas as pd

# Authentication to the Google Analytics Reporting API v4
# Replace 'config/service-account.json' with the path to your service account key file
SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
SERVICE_ACCOUNT_FILE = 'config/service-account.json'
viewID = ''    # Fill with your Google Analytics view ID


def get_google_analytics_reporting_service():
    """
    Authenticate and return the Google Analytics reporting service.
    """
    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return googleapiclient.discovery.build('analyticsreporting', 'v4', credentials=credentials)


def run_report(report_request):
    """
    Execute a Google Analytics report request and return the response.
    """
    reporting_service = get_google_analytics_reporting_service()
    response = reporting_service.reports().batchGet(body={'reportRequests': [report_request]}).execute()
    return response['reports'][0]


def fetch_all_data(report_request):
    """
    Fetch all data while handling pagination.
    """
    all_rows = []
    page_token = None
    page_number = 0

    while True:
        try:
            if page_token:
                report_request['pageToken'] = page_token
            response = run_report(report_request)
            rows = response['data']['rows']
            all_rows.extend(rows)
            page_number += 1
            print(f"Page {page_number} retrieved.\nFirst row of data:\t{rows[0]}")
            page_token = response.get('nextPageToken')
            if not page_token:
                break
        except googleapiclient.errors.HttpError as e:
            if e.resp.status in [403, 429]:
                print("Quota exceeded. Waiting before retrying...")
                time.sleep(10)  # Wait before retrying
            else:
                raise

    return all_rows


def fetch(request):
    # Execute the report and fetch data
    all_rows = fetch_all_data(request)

    # Extract data into a Pandas DataFrame
    rows = []
    for report_row in all_rows:
        row = {}
        for i, dimension in enumerate(report_row['dimensions']):
            row[request['dimensions'][i]['name']] = dimension
        for i, metric in enumerate(report_row['metrics'][0]['values']):
            row[request['metrics'][i]['expression']] = metric
        rows.append(row)

    df = pd.DataFrame(rows)

    # Rename columns to remove the 'ga:' prefix
    df.columns = [name[3:] for name in df.columns]

    return df


# Report configuration
full_report_request = {
    'viewId': viewID,  # Replace with your Google Analytics view ID
    'dateRanges': [{'startDate': '2016-01-01', 'endDate': '2026-07-01'}],  # Date range
    'metrics': [
        {'expression': 'ga:pageViews'},  # Number of page views
        {'expression': 'ga:sessions'},  # Number of sessions
        {'expression': 'ga:sessionsWithEvent'},  # Number of sessions
        {'expression': 'ga:newUsers'}  # Number of new users
    ],   # Number of page views
    'dimensions': [
        {'name': 'ga:date'},  # Date
        {'name': 'ga:pagePath'},  # Page URL
        {'name': 'ga:sourceMedium'},  # Medium
        {'name': 'ga:channelGrouping'},  # Source
        {'name': 'ga:deviceCategory'},  # Device type
        {'name': 'ga:language'},  # Language
        {'name': 'ga:fullReferrer'},  # Country
        {'name': 'ga:hostname'},  # Device type
        {'name': 'ga:Country'},  # Device type
  ],
    'pageSize': 10000  # Maximum number of rows per page (can be up to 10000)
}

dimensions_names = ['channelGrouping', 'deviceCategory', 'language'  #, 'Country'
  ]

# Report configuration
responsive_report_request = {
    'viewId': viewID,
    'dateRanges': [{'startDate': '2016-01-01', 'endDate': '2024-10-01'}],  # Date range
    'metrics': [
        {'expression': 'ga:pageViews'},  # Number of page views
        {'expression': 'ga:sessions'},  # Number of sessions
        {'expression': 'ga:sessionsWithEvent'},  # Number of sessions
        {'expression': 'ga:newUsers'}  # Number of new users
    ],
    'pageSize': 10000  # Maximum number of rows per page (can be up to 10000)
}

# loop to construct the list of requests to send
requests: list = []
for name in dimensions_names:
    print(name)
    dimensions_values: list[dict] = [{'name': 'ga:date'}, {'name': f'ga:{name}'}]
    new_request = responsive_report_request.copy()
    new_request['dimensions'] = dimensions_values
    requests.append(new_request)

# Loop through requests to fetch
for request in requests:
    print(request['dimensions'])
    df = fetch(request)

    name = request['dimensions'][-1]['name'][3:]

    # Save DataFrame to a CSV file
    filename = f'google_analytics_data_{name}.csv'
    df.to_csv(filename, index=False)

    print(f'Data has been saved to {filename}')

