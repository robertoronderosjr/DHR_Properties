import os
import argparse
import logging
from property_search import PropertySearch

# Set up logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Create maps for property styles and sewer filters
style_map = {
    "1/2 Duplex": "21907",
    "Condo - Hotel": "21902",
    "Condominium": "21903",
    "Dock-Rackominium": "21904",
    "Farm": "21906",
    "Garage Condo": "32051",
    "Manufactured Home": "27087",
    "Mobile Home": "21909",
    "Modular Home": "33504",
    "Single Family Residence": "21916",
    "Townhouse": "21917",
    "Villa": "21920",
}

sewer_map = {
    "Aerobic Septic": "26289",
    "None": "26290",
    "PEP-Holding Tank": "33510",
    "Private Sewer": "26291",
    "Public Sewer": "26292",
    "Septic Needed": "26293",
    "Septic Tank": "26294",
    "Other": "27177",
}


def main():
    # Define command-line arguments
    parser = argparse.ArgumentParser(description='DHR Property Lookup.')
    parser.add_argument('--price', type=str, help='price of the property, e.g. 500-')
    parser.add_argument('--year-built', type=str, help='year the property was built', default='1960+')
    parser.add_argument('--beds', type=int, default=3, help='minimum number of bedrooms')
    parser.add_argument('--baths', type=int, default=2, help='minimum number of full bathrooms')
    parser.add_argument('--sqft', type=int, default=1000, help='minimum square footage of the property')
    parser.add_argument('--style', type=str, default='Single Family Residence', choices=style_map.keys(),
                        help='property style')
    parser.add_argument('--county', type=str, default='Orange,Seminole,Lake,Osceola,Volusia,Polk',
                        help='list of counties to search')
    parser.add_argument('--garage', type=bool, default=True, help='property should have a garage or carport')
    parser.add_argument('--sewer', type=str, default=['Aerobic Septic', 'Septic Needed', 'Septic Tank'],
                        choices=sewer_map.keys(), nargs='+', help='sewer filter')

    # parser.add_argument("--email", help="Email for sending results", required=True)
    # parser.add_argument("--cap-rate-threshold", help="Minimum cap rate threshold", type=float, required=True)
    parser.add_argument('--username', type=str, help='MLS username')
    parser.add_argument('--password', type=str, help='MLS password')

    args = parser.parse_args()

    # Read secrets from environment variables
    username = os.getenv("MLS_USERNAME") or args.username
    password = os.getenv("MLS_PASSWORD") or args.password

    # Define search parameters
    search_params = {
        "price": args.price,
        "beds": args.beds,
        "baths": args.baths,
        "sqft": args.sqft,
        "style": style_map[args.style],
        "county": args.county,
        "garage": args.garage,
        "sewer": [sewer_map[sewer] for sewer in args.sewer],
    }

    # Create a new instance of PropertySearch
    ps = PropertySearch(username, password, **search_params)

    # Search for properties and generate report
    ps.search_properties()


if __name__ == '__main__':
    main()
