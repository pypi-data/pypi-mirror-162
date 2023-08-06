"""
Client for GetSmarter API Gateway.
"""

from getsmarter_api_clients.oauth import OAuthApiClient


class GetSmarterEnterpriseApiClient(OAuthApiClient):
    """
    Client to interface with the GetSmarter Enterprise API Gateway (GEAG).

    For full documentation, visit https://www.getsmarter.com/api-docs.
    """

    def get_terms_and_policies(self):
        """
        Fetch and return the terms and policies from GEAG.

        Returns:
            Dict containing the keys 'privacyPolicy', 'websiteTermsOfUse',
            'studentTermsAndConditions', and 'cookiePolicy'.
        """
        url = f'{self.api_url}/terms'
        response = self.get(url)
        response.raise_for_status()
        return response.json()

    def create_allocation(
        self,
        payment_reference,
        address_line1,
        city,
        postal_code,
        state,
        state_code,
        country,
        country_code,
        first_name,
        last_name,
        email,
        date_of_birth,
        terms_accepted_at,
        currency,
        order_items,
        address_line2=None,
        mobile_phone=None,
        work_experience=None,
        education_highest_level=None
    ):
        """
        Create an allocation (enrollment) through GEAG.

        :Parameters:
          - `file_id`: The id to use for this file. The id must not have
            already been used for another file.
          - `payment_reference (str)`: Reference used by enterprise partner
            when payment is made to GetSmarter
          - `address_line1`: Address Line 1
          - `city`: City
          - `postal_code`: Postal code
          - `state`: State
          - `state_code`: State code
          - `country` (str): Country
          - `country_code` (str): Country code,
          - `first_name` (str): First name
          - `last_name` (str): Last name
          - `email` (str): Email
          - `date_of_birth` (str): Date of birth
          - `terms_accepted_at` (str): ISO 8601 timestamp of
            when the terms and policies were accepted
          - `currency`: One of ['USD', 'GBP', 'ZAR', 'EUR', 'AED',
            'SGD', 'HKD', 'SAR', 'INR', 'CAD']
          - `order_items (list of dict)`: Items ordered
          - `address_line2 (str)`: Adress Line 2
          - `mobile_phone` (str): Mobile phone number
          - `work_experience (str)`: One of ['None', '1 to 5 years',
            '5 to 15 years', 'More than 15 years']
          - `education_highest_level (str)`: One of ['High school',
            'Bachelor’s degree', 'Master’s degree', 'Doctoral degree',
            'Other tertiary qualification', 'Honours degree',
            'Bachelors degree']

        **Example payload**
        {

            "paymentReference": "GS-12304",
            "addressLine1": "Oak Glen",
            "city": "Cape Town",
            "postalCode": "7570",
            "country": "South Africa",
            "countryCode": "ZA",
            "firstName": "Jan",
            "lastName": "Pan",
            "email": "janpan@gs.com",
            "dateOfBirth": "2021-05-12",
            "termsAcceptedAt": "2021-05-21T17:32:28Z",
            "currency": "ZAR",
            "orderItems": [{ "productId": "product_id", "quantity": 1,
            "normalPrice": 1000, "discount": 500, "finalPrice": 500 }]

        }
        """
        url = f'{self.api_url}/allocations'

        payload = {
            'paymentReference': payment_reference,
            'addressLine1': address_line1,
            'city': city,
            'postalCode': postal_code,
            'state': state,
            'stateCode': state_code,
            'country': country,
            'countryCode': country_code,
            'firstName': first_name,
            'lastName': last_name,
            'email': email,
            'dateOfBirth': date_of_birth,
            'termsAcceptedAt': terms_accepted_at,
            'currency': currency,
            'orderItems': order_items,
            # optional fields
            'addressLine2': address_line2,
            'mobilePhone': mobile_phone,
            'workExperience': work_experience,
            'educationHighestLevel': education_highest_level,
        }
        # remove keys with empty values
        payload = {k: v for k, v in payload.items() if v is not None}

        response = self.post(url, json=payload)
        response.raise_for_status()
