"""constant variables"""
import os

BASKING_API_URL = os.getenv('BASKING_API_URL', 'https://api.basking.io/api/')
TIMEOUT_MESSAGE = 'The Basking API returned a timeout. Please try this request again in a few minutes. If the problem persists, please reach out to support under support@basking.io'
