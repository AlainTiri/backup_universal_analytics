# Google Universal Analytics Reporting Script

This script fetches data from the Google Analytics Reporting API v4 and saves it into a CSV file.

Hurry up. Google will cut data the 1st july 2024...

## Prerequisites

- Python 3.x
- `google-auth`
- `google-api-python-client`
- `pandas`

You can install the required packages using pip:

```sh
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client pandas
```

## The content
There are one full request adapted for me and a loop through divers dimensions.

You need a specific service account (add his .json file on a config directory to create) on GCP for Google Analytics. It's easy to find on Youtube.

Normally, if you can code, there is no difficulties (except maybe GCP and GAU config). My code is basic and write with ChatGPT...

More fields on : https://ga-dev-tools.google/dimensions-metrics-explorer/

Limits are: 
- 10 request by sec
- 50 000 request by days
- max 9 dimensions and (maybe) 7 metrics. I think, also minimum 2 dimensions. 
- Maximum 10000 rows by requests.

Don't forget to add the ID of your view (viewId) on GAU.

(I know, I could do better, but, there are 1 day left before end of GAU ;-) )
