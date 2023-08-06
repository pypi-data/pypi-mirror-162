import requests
import json
from typing import List, Optional, NoReturn
from typing_extensions import Literal
from .exceptions import YextException, RequestException
from .answers_universal_results import AnswersUniversalResults

FormatOptions = Literal["html", "markdown"]


class YextClient:

    """
    A class for making querying and interfacing with the Yext Live API and
    knowledge API easy.

    Args:
    ----
        api_key: str
            The API key for the account. (See developer console.)
            We may add a way to infer this for Answers experiences in the future.
        v: str, defaul `20200101`
            The version of the Live API as of this date. This does not affect
            Answers functionality, only other endpoints.
    """

    KNOWLEDGE_ENDPOINTS = {
        "PRODUCTION": {
            "profiles": "https://api.yext.com/v2/accounts/me/entityprofiles",
            "entities": "https://api.yext.com/v2/accounts/me/entities",
            "entity": "https://api.yext.com/v2/accounts/me/entities/{entity_id}",
            "profile": "https://api.yext.com/v2/accounts/me/entityprofiles/{entity_id}/{locale}",
        },
        "SANDBOX": {
            "profiles": "https://api-sandbox.yext.com/v2/accounts/me/entityprofiles",
            "entities": "https://api-sandbox.yext.com/v2/accounts/me/entities",
            "entity": "https://api-sandbox.yext.com/v2/accounts/me/entities/{entity_id}",
            "profile": "https://api-sandbox.yext.com/v2/accounts/me/entityprofiles/{entity_id}/{locale}",
        },
        "DEV": {
            "profiles": "https://dev.yext.com/v2/accounts/me/entities",
            "entities": "https://dev.yext.com/v2/accounts/me/entityprofiles",
            "entity": "https://dev.yext.com/v2/accounts/me/entities/{entity_id}",
            "profile": "https://dev.yext.com/v2/accounts/me/entityprofiles/{entity_id}/{locale}",
        },
    }
    ANSWERS_ENDPOINTS = {
        "PRODUCTION": {
            "answers_universal": "https://liveapi.yext.com/v2/accounts/me/answers/query",
            "answers_vertical": "https://liveapi.yext.com/v2/accounts/me/answers/vertical/query",
        },
        "SANDBOX": {
            "answers_universal": "https://liveapi-sandbox.yext.com/v2/accounts/me/answers/query",
            "answers_vertical": "https://liveapi-sandbox.yext.com/v2/accounts/me/answers/vertical/query",
        },
        "DEV": {
            "answers_universal": "https://dev.yext.com/v2/accounts/me/answers/query",
            "answers_vertical": "https://dev.yext.com/v2/accounts/me/answers/vertical/query",
        },
    }

    def __init__(
        self, api_key: str, v: str = "20200101", env: str = "PRODUCTION"
    ):
        self.api_key = api_key
        self.env = env
        self.v = v

    def __repr__(self):
        return f"Yext API client, API key: {self.api_key}"

    def _validate_response(self, response: requests.Response) -> NoReturn:
        """Validates the HTTP response and raises user-friendly errors."""
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            rj = response.json()
            codes = []
            status = response.status_code
            if "errors" in rj["meta"]:
                full_msg = ""
                for error in rj["meta"]["errors"]:
                    codes.append(error["code"])
                    msg = f"""\n\t{error['message']}\n\ttype: {error['type']}\n\tcode: {str(error['code'])}
                    """
                    full_msg += msg
            else:
                full_msg = json.dumps(rj)
            raise RequestException(full_msg, status, codes)

    def search_answers_vertical(
        self,
        query: str,
        experience_key: str,
        vertical_key: str,
        locale: str = "en",
        version: str = "PRODUCTION",
        headers: Optional[dict] = {},
    ):
        """
        Searches the Answers vertical search endpoint.

        Args:
        ----
            query: str
                The query string (what you'd type in the search bar).
            experience_key: str
                The key for the Answers experience.
            vertical_key: str
                The key for the vertical.
            locale: str, default `en`
                The locale to pass. This controls the language profiles
                returned as well as the query understanding behavior.
            version: str, default `PRODUCTION`
                The version of the experience. This can be `PRODUCTION`,
                `STAGING` or a number.
        """
        endpoint = self.ANSWERS_ENDPOINTS[self.env]["answers_universal"]
        params = {
            "input": query,
            "api_key": self.api_key,
            "locale": locale,
            "v": self.v,
            "experienceKey": experience_key,
            "version": version,
            "verticalKey": vertical_key,
        }
        response = requests.get(
            endpoint, params=params, headers=headers
        ).json()
        return response

    def search_answers_universal(
        self,
        query: str,
        experience_key: str,
        locale: str = "en",
        version: str = "PRODUCTION",
        headers: Optional[dict] = {},
    ):
        """
        Searches the Answers universal search endpoint.

        Args:
        ----
            query: str
                The query string (what you'd type in the search bar).
            experience_key: str
                The key for the Answers experience.
            locale: str, default `en`
                The locale to pass. This controls the language profiles
                returned as well as the query understanding behavior.
            version: str, default `PRODUCTION`
                The version of the experience. This can be `PRODUCTION`,
                `STAGING` or a number.
        """
        endpoint = self.ANSWERS_ENDPOINTS[self.env]["answers_universal"]
        params = {
            "input": query,
            "api_key": self.api_key,
            "locale": locale,
            "v": self.v,
            "experienceKey": experience_key,
            "version": version,
        }
        response = requests.get(endpoint, params=params, headers=headers)
        results = AnswersUniversalResults(response)
        return results

    def get_all_entities(self, params: dict = {}) -> List[dict]:
        """
        Fetches all the entities within an account by making successive API
        calls to paginate through the results.

        Args:
        ----
            params: dict
                Additional parameters to pass to the API. See:
                https://developer.yext.com/docs/api-reference/#operation/KnowledgeApiServer.listEntities
        """
        endpoint = self.KNOWLEDGE_ENDPOINTS[self.env]["entities"]
        results = []
        page_token = ""
        while True:
            if page_token:
                params["pageToken"] = page_token
            full_params = {
                "api_key": self.api_key,
                "v": "20200101",
                "limit": 50,
                **params,
            }
            response = requests.get(endpoint, full_params)
            if response.status_code != 200:
                error_text = response.text
                raise Exception("Invalid response: \n{}".format(error_text))
            else:
                response = response.json()
            next_results = response["response"]["entities"]
            results += next_results
            if "pageToken" in response["response"]:
                page_token = response["response"]["pageToken"]
            else:
                break
        return results

    def get_entity(self, id: str, country_code: Optional[str] = "US") -> List[dict]:
        """
        Fetches entity within an account by making an API
        call to get the result.

        Args:
        ----
            id: str
                Additional parameters to pass to the API. See:
                https://developer.yext.com/docs/api-reference/#operation/getEntity
        """
        endpoint = self.KNOWLEDGE_ENDPOINTS[self.env]["entity"].format(
            entity_id=id
        )
        params = {'country_code': country_code}
        full_params = {
            "api_key": self.api_key,
            "v": "20200101",
            **params,
        }
        response = requests.get(endpoint, full_params)
        self._validate_response(response)
        return response.json()


    def create_entity(
        self,
        entity_type: str,
        profile: dict,
        id: Optional[str] = None,
        country_code: Optional[str] = "US",
        format: Optional[Literal[FormatOptions]] = "html",
        strip_unsupported_formats: Optional[bool] = False,
    ):
        """
        Creates an entity in the Knowledge Graph.

        Args:
        ----
            entity_type: str
                The API name of the entity type to create.
            profile: dict
                The JSON of the entity profile, including the `meta` which
                details the entity ID and country code, as well as the body
                where the keys are the API names of the fields.
            id: str
                The entity ID of the profile. This can either be defined as an
                argument or specified in the `meta` key of the `profile`
                dictionary.
            country_code: str, default `US`
                The country code of the entity. This can either be defined as
                an argument or specified in the `meta` key of the `profile`
                dictionary.
            format: str
                The format for rich text fields. Either 'html' or or 'markdown'.
            strip_unsupported_formats: bool, default False
                For rich text fields uploaded as HTML, whether or not to strip
                unsupported tags/formats on upload.
        """
        params = {
            "entityType": entity_type,
            "api_key": self.api_key,
            "v": self.v,
            "format": format,
            "stripUnsupportedFormats": strip_unsupported_formats,
        }
        if "meta" not in profile:
            profile["meta"] = {}
        if "id" not in profile["meta"]:
            if not id:
                raise YextException("Must provide an entity ID.")
            else:
                profile["id"]: id
        if "countryCode" not in profile["meta"]:
            profile["meta"]["countryCode"] = country_code

        endpoint = self.KNOWLEDGE_ENDPOINTS[self.env]["entities"]
        response = requests.post(endpoint, params=params, json=profile)
        self._validate_response(response)
        return response.json()

    def update_entity(
        self,
        profile: dict,
        id: Optional[str] = None,
        format: Optional[Literal[FormatOptions]] = "html",
        strip_unsupported_formats: Optional[bool] = False,
        **kwargs,
    ):
        """
        Updates an entity in the Knowledge Graph.

        Args:
        ----
            profile:
                The JSON of the entity profile, including the `meta` which
                details the entity ID and country code, as well as the body
                where the keys are the API names of the fields.
            id: str
                The entity ID of the profile. If this is not provided, then
                it is inferred from the meta.id of the profile itself. If
                this is not present, an error is raised.
            format: str
                The format for rich text fields. Either 'html' or or 'markdown'.
            strip_unsupported_formats: bool, default False
                For rich text fields uploaded as HTML, whether or not to strip
                unsupported tags/formats on upload.
        """
        params = {"api_key": self.api_key, "v": self.v, "format": format}
        if not id:
            try:
                id = profile["meta"]["id"]
            except ValueError:
                msg = 'Entity ID must be provided either as a keyword argument or part of the "meta" object of the profile.'
                raise YextException(msg)
        endpoint = self.KNOWLEDGE_ENDPOINTS[self.env]["entity"].format(
            entity_id=id
        )
        response = requests.put(endpoint, params=params, json=profile)
        self._validate_response(response)
        return response.json()

    def upsert_entity(self, **kwargs):
        """
        Upserts an entity in the knowledge graph. If the entity doesn't exist,
        create it. If it does, update it.

        For args, see YextClient.create_entity().
        """
        try:
            return self.create_entity(**kwargs)
        except YextException as e:
            if 2302 in e.codes:
                return self.update_entity(**kwargs)
            else:
                raise YextException(e.message)

    def upsert_profile(
        self,
        entity_id: str,
        locale: str,
        profile: dict,
        format: Optional[Literal[FormatOptions]] = "html",
    ):
        """
        Upsert a new language profile for a given entity.

        Args:
        ----
            entity_id: str
                The ID of the entity.
            locale: str
                The locale code of the language profile to upsert.
            profile: dict
                The JSON of the entity profile. The keys are the API names of
                the fields.
            format: str
                The format for rich text fields. Either 'html' or or 'markdown'.
        """
        endpoint = self.knowledge_endpoints["profile"]
        endpoint = endpoint.format(entity_id=entity_id, locale=locale)
        params = {"api_key": self.api_key, "v": self.v, "format": format}
        response = requests.put(endpoint, params=params, json=profile)
        if str(response.status_code).startswith("2"):
            return response.json()
        else:
            error_text = response.text
            fmt_json = json.dumps(profile)
            msg = f"Invalid response: \n{error_text}\n Request: {fmt_json}"
            raise Exception(msg)


    def delete_entity(
        self,
        entity_id,
        country_code: Optional[str] = "US"
    ):
        """
        Delete an entity in the Knowledge Graph.

        Args:
        ----
            entity_id: str
                The entity ID of the profile. This can either be defined as an
                argument or specified in the `meta` key of the `profile`
                dictionary.
            country_code: str, default `US`
                The country code of the entity. This can either be defined as
                an argument or specified in the `meta` key of the `profile`
                dictionary.
        """
        params = {"api_key": self.api_key, "v": self.v}
        params["countryCode"] = country_code
        endpoint = self.KNOWLEDGE_ENDPOINTS[self.env]["entity"].format(entity_id=entity_id)
        response = requests.delete(endpoint, params=params)
        self._validate_response(response)
        return response.json()
