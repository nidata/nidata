from .aws_fetcher import AmazonS3Fetcher
from .http_fetcher import HttpFetcher
from .base import Fetcher, FetcherFunctionFetcher

__all__ = ['AmazonS3Fetcher', 'HttpFetcher', 'Fetcher',
           'FetcherFunctionFetcher']
