from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Journey, PrimaryExpense,SecondaryExpense
from .serializers import JourneySerializer, PrimaryExpenseSerializer,SecondaryExpenseSerializer

# Optional: you can add custom permission classes if needed
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from .models import Journey, SecondaryExpense
from .serializers import JourneySerializer, SecondaryExpenseSerializer

from rest_framework import viewsets, permissions
from rest_framework.response import Response
from .models import Journey, SecondaryExpense
from .serializers import JourneySerializer, SecondaryExpenseSerializer

class JourneyViewSet(viewsets.ModelViewSet):
    queryset = Journey.objects.all().order_by('-created_at')
    serializer_class = JourneySerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        data = request.data.copy()

        driver_id = data.pop("driver_id", None)
        vehicle_id = data.pop("vehicle", None)
        if vehicle_id:
            data["vehicle"] = vehicle_id

        # 1️⃣ Create Journey — pass driver_id via save() to bypass read-only field
        journey_serializer = self.get_serializer(data=data)
        journey_serializer.is_valid(raise_exception=True)
        save_kwargs = {}
        if driver_id:
            try:
                save_kwargs["driver_id"] = int(driver_id)
            except (TypeError, ValueError):
                pass
        journey = journey_serializer.save(**save_kwargs)

        # 2️⃣ Create SecondaryExpense if provided
        expense_type = data.get("expenseType")
        expense_cost = data.get("expenseCost")
        expense_desc = data.get("expenseDescription")

        if expense_type and expense_cost:
            expense_serializer = SecondaryExpenseSerializer(data={
                "type": expense_type,
                "cost": expense_cost,
                "description": expense_desc,
            })
            expense_serializer.is_valid(raise_exception=True)
            expense_serializer.save(journey=journey, created_by=request.user)

        # 3️⃣ Return full journey with expenses
        journey_serializer = JourneySerializer(journey, context={"request": request})
        return Response(journey_serializer.data)


class PrimaryExpenseViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing Expenses linked to Journeys.
    """
    queryset = PrimaryExpense.objects.all().order_by('-created_at')
    serializer_class = PrimaryExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        """
        Automatically set the logged-in user as the creator.
        """
        serializer.save(created_by=self.request.user)


class SecondaryExpenseViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing Expenses linked to Journeys.
    """
    queryset = SecondaryExpense.objects.all().order_by('-created_at')
    serializer_class = SecondaryExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        """
        Automatically set the logged-in user as the creator.
        """
        serializer.save(created_by=self.request.user)