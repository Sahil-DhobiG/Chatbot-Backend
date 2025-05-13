from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import json
import os
import requests
from django.urls import reverse

# Try importing DynamicDataView, handle gracefully if module doesn't exist
try:
    from .dynamic_data_view import DynamicDataView
    dynamic_data_available = True
except ImportError:
    dynamic_data_available = False


# Create your views here.
class ChatbotDataView(APIView):
    def get(self, request, format=None):
        try:
            # Get the absolute path to the static JSON file
            json_file_path = os.path.join(os.path.dirname(__file__), "static_data.json")

            # Read the static data JSON file
            with open(json_file_path, "r") as file:
                static_data = json.load(file)
                
            # Create an instance of the dynamic data view if available
            if dynamic_data_available:
                dynamic_data_provider = DynamicDataView()
            else:
                # If DynamicDataView is not available, return only static data
                return Response(static_data, status=status.HTTP_200_OK)

            # Get the consolidated query parameter
            query_param = request.query_params.get("query")
            # Legacy support for individual parameters
            type_param = request.query_params.get("type")
            option_id = request.query_params.get("id")
            search_query = request.query_params.get("q")
            
            # If using the new consolidated query parameter
            if query_param:
                # Map the query to the appropriate data type and action
                if query_param == "order-data":
                    # Get all dynamic data
                    all_data_response = dynamic_data_provider.get(
                        request._request,
                        format=format,
                        data_type="all-data",
                    ).data
                    return Response(all_data_response, status=status.HTTP_200_OK)
                    
                elif query_param == "current-orders":
                    # Get current orders from dynamic data
                    current_orders_response = dynamic_data_provider.get(
                        request._request, format=format, data_type="current-orders"
                    ).data
                    return Response(current_orders_response, status=status.HTTP_200_OK)
                    
                elif query_param == "previous-orders":
                    # Get previous orders from dynamic data
                    previous_orders_response = dynamic_data_provider.get(
                        request._request, format=format, data_type="previous-orders"
                    ).data
                    return Response(previous_orders_response, status=status.HTTP_200_OK)
                    
                elif query_param == "slot-availability":
                    # Get slot availability from dynamic data
                    slot_availability_response = dynamic_data_provider.get(
                        request._request, format=format, data_type="slot-availability"
                    ).data
                    return Response(slot_availability_response, status=status.HTTP_200_OK)
                    
                elif query_param == "subscription-status":
                    # Get subscription status from dynamic data
                    subscription_status_response = dynamic_data_provider.get(
                        request._request, format=format, data_type="subscription-status"
                    ).data
                    return Response(subscription_status_response, status=status.HTTP_200_OK)
                
                else:
                    # Treat any other query as a search
                    # Get dynamic data for search
                    all_data_response = dynamic_data_provider.get(
                        request._request, format=format, data_type="all-data"
                    ).data

                    # Enhance static data with dynamic data where needed
                    chatbot_data = self._enhance_static_data_with_dynamic(
                        static_data, all_data_response
                    )

                    # Continue with search implementation
                    search_term = query_param.lower().strip()
                    results = []
                    suggestions = []
                    
                    # Direct match for main options like "Current Order Status"
                    direct_match_option = None
                    exact_match = False
                    highest_match_score = 0
                    
                    for option in chatbot_data["options"]:
                        title_lower = option["title"].lower()

                        # Check for exact match first
                        if search_term == title_lower:
                            direct_match_option = option
                            exact_match = True
                            break

                        # Check for partial match in title or description
                        match_score = 0
                        if search_term in title_lower:
                            # Calculate how much of the query matches the title
                            match_score = len(search_term) / len(title_lower) * 100
                            # Add to suggestions if partial match
                            if match_score > 30:  # At least 30% match for suggestion
                                suggestions.append(
                                    {
                                        "id": option["id"],
                                        "title": option["title"],
                                        "match_score": match_score,
                                    }
                                )

                        # Update best match if this is better
                        if match_score > highest_match_score:
                            highest_match_score = match_score
                            direct_match_option = option

                    # Sort suggestions by match score (highest first)
                    suggestions = sorted(
                        suggestions, key=lambda x: x["match_score"], reverse=True
                    )
                    
                    # If we have an exact match or high quality match (>70%), return the specific data
                    if exact_match or highest_match_score > 70:
                        option_id = direct_match_option["id"]
                        data = None

                        try:
                            # Get the appropriate data based on the option type
                            if option_id == 1:  # Current Order Status
                                data = all_data_response["current_orders"]
                            elif option_id == 2:  # Slot Availability
                                data = all_data_response["slots"]
                            elif option_id == 3:  # Previous Order Details
                                data = all_data_response["previous_orders"]
                            elif option_id == 4:  # Subscription Status
                                data = all_data_response["subscription"]
                            elif option_id == 5:  # Contact Us
                                data = direct_match_option.get("subOptions", [])

                            # If we found a match and have data, return it
                            return Response(
                                {
                                    "match_type": "direct",
                                    "option": direct_match_option,
                                    "data": data if data is not None else [],
                                    "suggestions": suggestions[:3],  # Add top 3 suggestions
                                },
                                status=status.HTTP_200_OK,
                            )
                        except Exception as e:
                            print(f"Error handling direct match: {str(e)}")
                            # Return a valid response with empty data
                            return Response(
                                {
                                    "match_type": "direct",
                                    "option": direct_match_option,
                                    "data": [],
                                    "suggestions": suggestions[:3],
                                },
                                status=status.HTTP_200_OK,
                            )

                    # If no direct match, perform regular search across all options
                    for option in chatbot_data["options"]:
                        # Check title and description
                        if (
                            search_term in option["title"].lower()
                            or search_term in option["description"].lower()
                        ):
                            results.append(option)
                            continue

                        # Check in option data
                        if option["id"] in [1, 2, 3, 4]:  # These are dynamic data options
                            data_found = False

                            # Determine which data to search in
                            if option["id"] == 1:
                                data = all_data_response["current_orders"]
                            elif option["id"] == 2:
                                data = all_data_response["slots"]
                            elif option["id"] == 3:
                                data = all_data_response["previous_orders"]
                            elif option["id"] == 4:
                                data = all_data_response["subscription"]
                            else:
                                continue

                            # For array type data (orders)
                            if isinstance(data, list):
                                for item in data:
                                    if any(
                                        search_term in str(value).lower()
                                        for value in item.values()
                                    ):
                                        data_found = True
                                        break
                            # For dictionary type data (slot availability, subscription status)
                            elif isinstance(data, dict):
                                for key, value in data.items():
                                    if (
                                        search_term in str(key).lower()
                                        or search_term in str(value).lower()
                                    ):
                                        data_found = True
                                        break

                            if data_found:
                                results.append(option)
                                continue

                        # Check subOptions
                        if "subOptions" in option and option["subOptions"]:
                            for sub_option in option["subOptions"]:
                                if search_term in sub_option["title"].lower() or (
                                    "content" in sub_option
                                    and search_term in sub_option["content"].lower()
                                ):
                                    results.append(option)
                                    break

                    # Generate query suggestions for next possible searches
                    # Get top 5 options by match score + any additional results
                    top_suggestions = suggestions[:5]
                    suggestion_ids = [s["id"] for s in top_suggestions]

                    # Add any other matches that weren't in the top match scores
                    for option in results:
                        if option["id"] not in suggestion_ids:
                            top_suggestions.append(
                                {
                                    "id": option["id"],
                                    "title": option["title"],
                                    "match_score": 30,  # Default score for other matches
                                }
                            )

                    return Response(
                        {
                            "match_type": "search",
                            "results": results,
                            "suggestions": top_suggestions[:5],  # Limit to top 5 suggestions
                        },
                        status=status.HTTP_200_OK,
                    )
            
            # Legacy support for individual parameters
            elif type_param:
                if type_param == "current-orders":
                    # Get current orders from dynamic data
                    current_orders_response = dynamic_data_provider.get(
                        request._request, format=format, data_type="current-orders"
                    ).data
                    return Response(current_orders_response, status=status.HTTP_200_OK)

                elif type_param == "previous-orders":
                    # Get previous orders from dynamic data
                    previous_orders_response = dynamic_data_provider.get(
                        request._request, format=format, data_type="previous-orders"
                    ).data
                    return Response(previous_orders_response, status=status.HTTP_200_OK)

                elif type_param == "slot-availability":
                    # Get slot availability from dynamic data
                    slot_availability_response = dynamic_data_provider.get(
                        request._request, format=format, data_type="slot-availability"
                    ).data
                    return Response(
                        slot_availability_response, status=status.HTTP_200_OK
                    )

                elif type_param == "subscription-status":
                    # Get subscription status from dynamic data
                    subscription_status_response = dynamic_data_provider.get(
                        request._request, format=format, data_type="subscription-status"
                    ).data
                    return Response(
                        subscription_status_response, status=status.HTTP_200_OK
                    )

                elif type_param == "search":
                    # Search through all options
                    if not search_query:
                        return Response(
                            {"error": "Search query is required"},
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                    # Get dynamic data for search
                    all_data_response = dynamic_data_provider.get(
                        request._request, format=format, data_type="all-data"
                    ).data

                    # Enhance static data with dynamic data where needed
                    chatbot_data = self._enhance_static_data_with_dynamic(
                        static_data, all_data_response
                    )

                    # Continue with search implementation
                    search_term = search_query.lower().strip()
                    results = []
                    suggestions = []

                    # Direct match for main options like "Current Order Status"
                    direct_match_option = None
                    exact_match = False
                    highest_match_score = 0
                    for option in chatbot_data["options"]:
                        title_lower = option["title"].lower()

                        # Check for exact match first
                        if search_term == title_lower:
                            direct_match_option = option
                            exact_match = True
                            break

                        # Check for partial match in title or description
                        match_score = 0
                        if search_term in title_lower:
                            # Calculate how much of the query matches the title
                            match_score = len(search_term) / len(title_lower) * 100
                            # Add to suggestions if partial match
                            if match_score > 30:  # At least 30% match for suggestion
                                suggestions.append(
                                    {
                                        "id": option["id"],
                                        "title": option["title"],
                                        "match_score": match_score,
                                    }
                                )

                        # Update best match if this is better
                        if match_score > highest_match_score:
                            highest_match_score = match_score
                            direct_match_option = option

                    # Sort suggestions by match score (highest first)
                    suggestions = sorted(
                        suggestions, key=lambda x: x["match_score"], reverse=True
                    )
                    # If we have an exact match or high quality match (>70%), return the specific data
                    if exact_match or highest_match_score > 70:
                        option_id = direct_match_option["id"]
                        data = None

                        try:
                            # Get the appropriate data based on the option type
                            if option_id == 1:  # Current Order Status
                                data = all_data_response["current_orders"]
                            elif option_id == 2:  # Slot Availability
                                data = all_data_response["slots"]
                            elif option_id == 3:  # Previous Order Details
                                data = all_data_response["previous_orders"]
                            elif option_id == 4:  # Subscription Status
                                data = all_data_response["subscription"]
                            elif option_id == 5:  # Contact Us
                                data = direct_match_option.get("subOptions", [])

                            # If we found a match and have data, return it
                            return Response(
                                {
                                    "match_type": "direct",
                                    "option": direct_match_option,
                                    "data": data if data is not None else [],
                                    "suggestions": suggestions[
                                        :3
                                    ],  # Add top 3 suggestions
                                },
                                status=status.HTTP_200_OK,
                            )
                        except Exception as e:
                            print(
                                f"Error handling direct match: {str(e)}"
                            )  # Return a valid response with empty data
                            return Response(
                                {
                                    "match_type": "direct",
                                    "option": direct_match_option,
                                    "data": [],
                                    "suggestions": suggestions[:3],
                                },
                                status=status.HTTP_200_OK,
                            )

                    # If no direct match, perform regular search across all options
                    for option in chatbot_data["options"]:
                        # Check title and description
                        if (
                            search_term in option["title"].lower()
                            or search_term in option["description"].lower()
                        ):
                            results.append(option)
                            continue

                        # Check in option data
                        if option["id"] in [
                            1,
                            2,
                            3,
                            4,
                        ]:  # These are dynamic data options
                            data_found = False

                            # Determine which data to search in
                            if option["id"] == 1:
                                data = all_data_response["current_orders"]
                            elif option["id"] == 2:
                                data = all_data_response["slots"]
                            elif option["id"] == 3:
                                data = all_data_response["previous_orders"]
                            elif option["id"] == 4:
                                data = all_data_response["subscription"]
                            else:
                                continue

                            # For array type data (orders)
                            if isinstance(data, list):
                                for item in data:
                                    if any(
                                        search_term in str(value).lower()
                                        for value in item.values()
                                    ):
                                        data_found = True
                                        break
                            # For dictionary type data (slot availability, subscription status)
                            elif isinstance(data, dict):
                                for key, value in data.items():
                                    if (
                                        search_term in str(key).lower()
                                        or search_term in str(value).lower()
                                    ):
                                        data_found = True
                                        break

                            if data_found:
                                results.append(option)
                                continue

                        # Check subOptions
                        if "subOptions" in option and option["subOptions"]:
                            for sub_option in option["subOptions"]:
                                if search_term in sub_option["title"].lower() or (
                                    "content" in sub_option
                                    and search_term in sub_option["content"].lower()
                                ):
                                    results.append(option)
                                    break

                    # Generate query suggestions for next possible searches
                    # Get top 5 options by match score + any additional results
                    top_suggestions = suggestions[:5]
                    suggestion_ids = [s["id"] for s in top_suggestions]

                    # Add any other matches that weren't in the top match scores
                    for option in results:
                        if option["id"] not in suggestion_ids:
                            top_suggestions.append(
                                {
                                    "id": option["id"],
                                    "title": option["title"],
                                    "match_score": 30,  # Default score for other matches
                                }
                            )

                    return Response(
                        {
                            "match_type": "search",
                            "results": results,
                            "suggestions": top_suggestions[
                                :5
                            ],  # Limit to top 5 suggestions
                        },
                        status=status.HTTP_200_OK,
                    )

                elif type_param == "order-data":
                    # Get all dynamic data
                    all_data_response = dynamic_data_provider.get(
                        request._request,
                        format=format,
                        data_type="all-data",
                    ).data
                    return Response(all_data_response, status=status.HTTP_200_OK)

            # If option_id is specified, return that specific option
            if option_id:
                for option in static_data["options"]:
                    if str(option["id"]) == option_id:
                        # Enhance with dynamic data if needed
                        if option["id"] in [1, 2, 3, 4]:
                            all_data_response = dynamic_data_provider.get(
                                request._request, format=format, data_type="all-data"
                            ).data

                            if option["id"] == 1:
                                option["data"] = all_data_response["current_orders"]
                            elif option["id"] == 2:
                                option["data"] = all_data_response["slots"]
                            elif option["id"] == 3:
                                option["data"] = all_data_response["previous_orders"]
                            elif option["id"] == 4:
                                option["data"] = all_data_response["subscription"]

                        return Response(option, status=status.HTTP_200_OK)

                return Response(
                    {"error": f"Option with id {option_id} not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Return all options data if no specific type is requested
            return Response(static_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request, format=None):
        try:
            # Get either the consolidated query parameter or the legacy type parameter
            query_param = request.query_params.get("query")
            type_param = request.query_params.get("type")
            
            # Handle greeting request regardless of parameter name
            if query_param == "greet-user" or type_param == "greet-user":
                name = request.data.get("name", "User")

                # Get the greeting from the static JSON file
                json_file_path = os.path.join(
                    os.path.dirname(__file__), "static_data.json"
                )
                with open(json_file_path, "r") as file:
                    static_data = json.load(file)

                greeting_template = static_data.get(
                    "greeting", "Hi {name}, how may I help you?"
                )
                greeting = greeting_template.format(name=name)

                return Response(
                    {"greeting": greeting, "options": static_data.get("options", [])},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"error": "Invalid request type"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _enhance_static_data_with_dynamic(self, static_data, dynamic_data):
        """Helper method to combine static and dynamic data"""
        enhanced_data = static_data.copy()

        # Find options that need dynamic data and add it
        for option in enhanced_data["options"]:
            if option["id"] == 1:  # Current Order Status
                option["data"] = dynamic_data["current_orders"]
            elif option["id"] == 2:  # Slot Availability
                option["data"] = dynamic_data["slots"]
            elif option["id"] == 3:  # Previous Order Details
                option["data"] = dynamic_data["previous_orders"]
            elif option["id"] == 4:  # Subscription Status
                option["data"] = dynamic_data["subscription"]

        return enhanced_data
