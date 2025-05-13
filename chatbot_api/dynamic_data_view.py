from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import json
import os
from datetime import datetime, timedelta
import random

class DynamicDataView(APIView):
    """
    This view provides dynamic data for the chatbot application.
    It simulates fetching data from external services or databases.
    """
    def get(self, request, format=None, data_type=None):
        try:
            # Get the requested data type from either query params or the direct parameter
            if data_type is None:
                data_type = request.query_params.get('type')
            
            # Handle case where data_type is still None after checking query params
            if data_type is None:
                # Default to all-data if no type specified
                data_type = 'all-data'
            
            # Return appropriate data based on the requested type
            if data_type == 'current-orders':
                return Response(self.get_current_orders(), status=status.HTTP_200_OK)
                
            elif data_type == 'previous-orders':
                return Response(self.get_previous_orders(), status=status.HTTP_200_OK)
                
            elif data_type == 'slot-availability':
                return Response(self.get_slot_availability(), status=status.HTTP_200_OK)
                
            elif data_type == 'subscription-status':
                return Response(self.get_subscription_status(), status=status.HTTP_200_OK)
                
            elif data_type == 'all-data':
                # Return all dynamic data in one call
                try:
                    all_data = {
                        'current_orders': self.get_current_orders(),
                        'previous_orders': self.get_previous_orders(),
                        'slots': self.get_slot_availability(),
                        'subscription': self.get_subscription_status()
                    }
                    return Response(all_data, status=status.HTTP_200_OK)
                except Exception as e:
                    print(f"Error generating all-data: {str(e)}")
                    # Return empty but valid data structure in case of error
                    all_data = {
                        'current_orders': [],
                        'previous_orders': [],
                        'slots': {
                            "today": [],
                            "tomorrow": [],
                            "this_week": []
                        },
                        'subscription': {
                            "active": {
                                "plan": "None",
                                "expires": "",
                                "price": 0,
                                "auto_renew": False,
                                "includes": []
                            },
                            "available_plans": []
                        }
                    }
                    return Response(all_data, status=status.HTTP_200_OK)
                
            else:
                return Response(
                    {"error": f"Unknown data type: {data_type}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            print(f"DynamicDataView error: {str(e)}")
            # Return a graceful error response that won't break the caller
            return Response(
                {"error": str(e), "data": {}},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get_current_orders(self):
        try:
            """Generate current orders data dynamically"""
            # This would typically fetch from a database
            today = datetime.now()
            
            return [
                {
                    "order_id": f"ORD-{today.year}-001",
                    "customer_name": "John Doe",
                    "service_type": "Laundry and Ironing",
                    "status": "Picked Up",
                    "pickup_date": (today - timedelta(days=3)).strftime("%Y-%m-%d"),
                    "delivery_date": (today + timedelta(days=1)).strftime("%Y-%m-%d"),
                    "total_amount": 45.99,
                    "items": ["Shirts (5)", "Pants (3)", "Bed Sheets (2)"]
                },
                {
                    "order_id": f"ORD-{today.year}-002",
                    "customer_name": "Jane Smith",
                    "service_type": "Dry Cleaning",
                    "status": "Processing",
                    "pickup_date": (today - timedelta(days=2)).strftime("%Y-%m-%d"),
                    "delivery_date": (today + timedelta(days=2)).strftime("%Y-%m-%d"),
                    "total_amount": 67.50,
                    "items": ["Suits (2)", "Dress (1)", "Jacket (1)"]
                },
                {
                    "order_id": f"ORD-{today.year}-003",
                    "customer_name": "Mike Johnson",
                    "service_type": "Express Laundry",
                    "status": "Out for Delivery",
                    "pickup_date": (today - timedelta(days=1)).strftime("%Y-%m-%d"),
                    "delivery_date": today.strftime("%Y-%m-%d"),
                    "total_amount": 38.25,
                    "items": ["Shirts (4)", "Jeans (2)"]
                },
                {
                    "order_id": f"ORD-{today.year}-005",
                    "customer_name": "David Wilson",
                    "service_type": "Laundry Only",
                    "status": "Scheduled for Pickup",
                    "pickup_date": (today + timedelta(days=1)).strftime("%Y-%m-%d"),
                    "delivery_date": (today + timedelta(days=3)).strftime("%Y-%m-%d"),
                    "total_amount": 29.99,
                    "items": ["T-Shirts (10)", "Underwear (7)", "Socks (5 pairs)"]
                }
            ]
        except Exception as e:
            print(f"Error in get_current_orders: {str(e)}")
            return []  # Return empty list on error
    
    def get_previous_orders(self):
        try:
            """Generate previous orders data dynamically"""
            # This would typically fetch from a database
            today = datetime.now()
            
            return [
                {
                    "order_id": f"ORD-{today.year}-901",
                    "customer_name": "John Doe",
                    "service_type": "Dry Cleaning",
                    "status": "Delivered",
                    "pickup_date": (today - timedelta(days=15)).strftime("%Y-%m-%d"),
                    "delivery_date": (today - timedelta(days=12)).strftime("%Y-%m-%d"),
                    "total_amount": 89.50,
                    "items": ["Winter Coat", "Curtains (2 sets)", "Formal Suit"]
                },
                {
                    "order_id": f"ORD-{today.year}-845",
                    "customer_name": "Jane Smith",
                    "service_type": "Wash and Fold",
                    "status": "Delivered",
                    "pickup_date": (today - timedelta(days=10)).strftime("%Y-%m-%d"),
                    "delivery_date": (today - timedelta(days=8)).strftime("%Y-%m-%d"),
                    "total_amount": 34.99,
                    "items": ["Mixed Laundry (8 kg)"]
                },
                {
                    "order_id": f"ORD-{today.year}-780",
                    "customer_name": "Mike Johnson",
                    "service_type": "Premium Laundry",
                    "status": "Delivered",
                    "pickup_date": (today - timedelta(days=20)).strftime("%Y-%m-%d"),
                    "delivery_date": (today - timedelta(days=18)).strftime("%Y-%m-%d"),
                    "total_amount": 75.25,
                    "items": ["Dress Shirts (8)", "Slacks (4)", "Blazers (2)"]
                }
            ]
        except Exception as e:
            print(f"Error in get_previous_orders: {str(e)}")
            return []  # Return empty list on error
        
    def get_slot_availability(self):
        try:
            """Generate slot availability data dynamically"""
            # This would typically come from a scheduling system
            today = datetime.now()
            tomorrow = today + timedelta(days=1)
            
            # Log for debugging
            print("Generating slot availability data")
            
            # Generate random availability with more True values to ensure data is available
            today_slots = [
                {"time": "2:00 PM - 4:00 PM", "available": random.choice([True, True, False])},
                {"time": "5:00 PM - 7:00 PM", "available": random.choice([True, True, True, False])}
            ]
            
            tomorrow_slots = [
                {"time": "10:00 AM - 12:00 PM", "available": random.choice([True, True, False])},
                {"time": "1:00 PM - 3:00 PM", "available": random.choice([True, True, False])},
                {"time": "4:00 PM - 6:00 PM", "available": random.choice([True, True, True, False])}
            ]
            
            # Generate this week's available slots
            weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
            this_week = []
            
            for i in range(2, 5):  # Next few days after tomorrow
                day_date = today + timedelta(days=i)
                
                # Make sure we don't go beyond the length of the weekdays list
                weekday_index = day_date.weekday()
                if weekday_index >= len(weekdays):
                    day_name = "Weekend"
                else:
                    day_name = weekdays[weekday_index]
                
                day_slots = []
                
                # Generate 2-3 random time slots
                possible_slots = [
                    "9:00 AM - 11:00 AM", 
                    "10:00 AM - 12:00 PM",
                    "12:00 PM - 2:00 PM", 
                    "1:00 PM - 3:00 PM",
                    "3:00 PM - 5:00 PM",
                    "4:00 PM - 6:00 PM"
                ]
                
                # Select 2-3 random slots (but don't try to sample more than available)
                num_slots = min(random.randint(2, 3), len(possible_slots))
                day_slots = random.sample(possible_slots, num_slots)
                
                this_week.append({
                    "day": f"{day_name} ({day_date.strftime('%B %d')})",
                    "slots": day_slots
                })
            
            return {
                "today": today_slots,
                "tomorrow": tomorrow_slots,
                "this_week": this_week
            }
        except Exception as e:
            print(f"Error generating slot availability: {str(e)}")
            # Return empty but valid slot structure in case of error
            return {
                "today": [],
                "tomorrow": [],
                "this_week": []
            }
    
    def get_subscription_status(self):
        try:
            """Generate subscription status data dynamically"""
            # This would typically come from a user account system
            today = datetime.now()
            expiry_date = today + timedelta(days=random.randint(15, 90))
            
            return {
                "active": {
                    "plan": "Premium",
                    "expires": expiry_date.strftime("%Y-%m-%d"),
                    "price": 119.00,
                    "auto_renew": True,
                    "includes": [
                        "Unlimited laundry and dry cleaning",
                        "Free pickup and delivery",
                        "Priority processing",
                        "24/7 customer support",
                        "Garment repairs included"
                    ]
                },
                "available_plans": [
                    {
                        "name": "Basic",
                        "price": 49.00,
                        "features": [
                            "Up to 20 items per month",
                            "Standard delivery (2-3 days)",
                            "Basic garment care"
                        ]
                    },
                    {
                        "name": "Standard",
                        "price": 79.00,
                        "features": [
                            "Up to 40 items per month",
                            "Express delivery available",
                            "Extended garment care",
                            "Weekend service"
                        ]
                    },
                    {
                        "name": "Premium",
                        "price": 119.00,
                        "features": [
                            "Unlimited items",
                            "Free pickup and delivery",
                            "Priority processing",
                            "24/7 customer support",
                            "Garment repairs included"
                        ]
                    }
                ]
            }
        except Exception as e:
            print(f"Error in get_subscription_status: {str(e)}")
            # Return empty but valid subscription structure
            return {
                "active": {
                    "plan": "None",
                    "expires": "",
                    "price": 0,
                    "auto_renew": False,
                    "includes": []
                },
                "available_plans": []
            }
