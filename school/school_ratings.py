from typing import Dict

import pandas as pd


class SchoolRatings:
    def __init__(self, ratings_data: Dict[str, Dict]):
        """
        Initialize a new SchoolRatings object with the provided dictionary of school rating data.
        """
        self.ratings_data = ratings_data

    def get_rating(self, school_name: str):
        """
        Get the rating for the specified school.
        """
        return self.ratings_data.get(school_name, {}).get('rating')


def filter_low_rated_schools(properties_df: pd.DataFrame, ratings: dict, threshold: int) -> pd.DataFrame:
    """
    Filter out properties with low-rated schools based on the threshold.

    :param properties_df: pandas DataFrame containing property data
    :param ratings: dictionary of school ratings
    :param threshold: threshold for school ratings below which properties will be filtered out
    :return: filtered pandas DataFrame
    """
    # Create a set of school names that have a rating below the threshold
    low_rated_schools = set(name for name, rating in ratings.items() if rating < threshold)

    # Filter out properties with low-rated schools
    filtered_properties_df = properties_df[~properties_df['schools'].apply(
        lambda schools: any(school in low_rated_schools for school in schools.split(',')))]

    return filtered_properties_df

