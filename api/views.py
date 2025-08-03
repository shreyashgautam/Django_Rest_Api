from datetime import datetime, date

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

from .models import Customer, Loan
from .serializers import RegisterCustomerSerializer
from .utils import calculate_approved_limit
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Loan
import math

from datetime import datetime
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Loan

class RegisterCustomerView(APIView):
    def post(self, request):
        serializer = RegisterCustomerSerializer(data=request.data)
        if serializer.is_valid():
            try:
                income = serializer.validated_data['monthly_income']
                approved_limit = calculate_approved_limit(income)

                customer, created = Customer.objects.get_or_create(
                    phone_number=serializer.validated_data['phone_number'],
                    defaults={
                        'first_name': serializer.validated_data['first_name'],
                        'last_name': serializer.validated_data['last_name'],
                        'age': serializer.validated_data['age'],
                        'monthly_income': income,
                        'approved_limit': approved_limit,
                    }
                )

                response_serializer = RegisterCustomerSerializer(customer)
                if created:
                    return Response(response_serializer.data, status=status.HTTP_201_CREATED)
                else:
                    return Response(
                        {
                            "detail": "Customer with this phone number already exists.",
                            "customer": response_serializer.data,
                        },
                        status=status.HTTP_200_OK
                    )
            except Exception as e:
                return Response({"error": f"Server error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def calculate_credit_score(customer):
    loans = Loan.objects.filter(customer=customer)
    past_loans = loans.exclude(end_date__gte=date.today())
    current_year = date.today().year

    if customer.current_debt > customer.approved_limit:
        return 0

    past_paid_loans = sum(1 for loan in past_loans if loan.emis_paid_on_time >= loan.tenure)
    no_of_loans = loans.count()
    current_year_loans = loans.filter(start_date__year=current_year).count()
    total_approved_amount = sum(loan.loan_amount for loan in loans)

    credit_score = (
        (past_paid_loans * 10)
        - (no_of_loans * 2)
        + (current_year_loans * 5)
        + (total_approved_amount / 100000)
    )
    return max(0, min(100, credit_score))


def get_interest_rate_by_score(score):
    if score > 50:
        return 0
    elif score > 30:
        return 12
    elif score > 10:
        return 16
    else:
        return None


@api_view(["POST"])
def check_eligibility(request):
    try:
        data = request.data
        customer_id = data["customer_id"]
        loan_amount = float(data["loan_amount"])
        interest_rate = float(data["interest_rate"])
        tenure = int(data["tenure"])

        customer = Customer.objects.get(customer_id=customer_id)
        credit_score = calculate_credit_score(customer)

        current_loans = Loan.objects.filter(customer=customer, end_date__gte=date.today())

        # Total EMI including new loan
        r = interest_rate / (12 * 100)
        new_emi = (loan_amount * r * (1 + r) ** tenure) / ((1 + r) ** tenure - 1)

        existing_emi = sum(
            (l.loan_amount * (l.interest_rate / (12 * 100)) * (1 + (l.interest_rate / (12 * 100))) ** l.tenure) /
            ((1 + (l.interest_rate / (12 * 100))) ** l.tenure - 1)
            for l in current_loans
        )
        total_emi = new_emi + existing_emi

        if total_emi > 0.5 * customer.monthly_income:
            return Response({
                "customer_id": customer_id,
                "approval": False,
                "interest_rate": interest_rate,
                "corrected_interest_rate": interest_rate,
                "tenure": tenure,
                "monthly_installment": 0
            })

        corrected_interest_rate = interest_rate
        approval = False

        if credit_score > 50:
            approval = True
        elif 30 < credit_score <= 50 and interest_rate >= 12:
            approval = True
        elif 10 < credit_score <= 30 and interest_rate >= 16:
            approval = True

        if credit_score <= 10:
            corrected_interest_rate = 16.0
        elif 10 < credit_score <= 30 and interest_rate < 16:
            corrected_interest_rate = 16.0
        elif 30 < credit_score <= 50 and interest_rate < 12:
            corrected_interest_rate = 12.0

        if corrected_interest_rate != interest_rate:
            r = corrected_interest_rate / (12 * 100)
            new_emi = (loan_amount * r * (1 + r) ** tenure) / ((1 + r) ** tenure - 1)

        return Response({
            "customer_id": customer_id,
            "approval": approval,
            "interest_rate": interest_rate,
            "corrected_interest_rate": corrected_interest_rate,
            "tenure": tenure,
            "monthly_installment": round(new_emi, 2)
        })

    except Customer.DoesNotExist:
        return Response({"error": f"Customer with ID {customer_id} not found."}, status=404)
    except Exception as e:
        return Response({"error": f"Server error: {str(e)}"}, status=500)


@api_view(['POST'])
def create_loan(request):
    try:
        customer_id = request.data.get('customer_id')
        loan_amount = float(request.data.get('loan_amount'))
        interest_rate = float(request.data.get('interest_rate'))
        tenure = int(request.data.get('tenure'))

        customer = Customer.objects.get(pk=customer_id)
        credit_score = calculate_credit_score(customer)

        # Monthly installment calculation
        r = interest_rate / (12 * 100)
        emi = (loan_amount * r * (1 + r) ** tenure) / ((1 + r) ** tenure - 1)

        existing_loans = Loan.objects.filter(customer=customer, end_date__gte=date.today())
        total_existing_emi = sum(
            (l.loan_amount * (l.interest_rate / (12 * 100)) * (1 + (l.interest_rate / (12 * 100))) ** l.tenure) /
            ((1 + (l.interest_rate / (12 * 100))) ** l.tenure - 1)
            for l in existing_loans
        )
        if (total_existing_emi + emi) > (0.5 * customer.monthly_income):
            return Response({
                "loan_id": None,
                "customer_id": customer_id,
                "loan_approved": False,
                "message": "Loan rejected: EMI exceeds 50% of monthly income",
                "monthly_installment": round(emi, 2)
            })

        required_rate = get_interest_rate_by_score(credit_score)
        if required_rate is None:
            return Response({
                "loan_id": None,
                "customer_id": customer_id,
                "loan_approved": False,
                "message": "Loan rejected: credit score too low",
                "monthly_installment": round(emi, 2)
            })

        corrected_interest_rate = interest_rate
        if required_rate and interest_rate < required_rate:
            corrected_interest_rate = required_rate
            r = corrected_interest_rate / (12 * 100)
            emi = (loan_amount * r * (1 + r) ** tenure) / ((1 + r) ** tenure - 1)

        loan = Loan.objects.create(
            customer=customer,
            loan_amount=loan_amount,
            tenure=tenure,
            interest_rate=corrected_interest_rate,
            monthly_payment=round(emi, 2),
            emis_paid_on_time=0,
            start_date=date.today(),
            end_date=date(date.today().year + tenure // 12, date.today().month, date.today().day)
        )

        customer.current_debt += loan_amount
        customer.save()

        return Response({
            "loan_id": loan.loan_id,
            "customer_id": customer_id,
            "loan_approved": True,
            "message": "Loan approved successfully",
            "monthly_installment": round(emi, 2)
        })

    except Customer.DoesNotExist:
        return Response({
            "loan_id": None,
            "customer_id": customer_id,
            "loan_approved": False,
            "message": "Customer not found",
            "monthly_installment": 0
        })
    except Exception as e:
        return Response({
            "loan_id": None,
            "customer_id": customer_id,
            "loan_approved": False,
            "message": f"Server error: {str(e)}",
            "monthly_installment": 0
        })

@api_view(['GET'])
def view_loan(request, loan_id):
    try:
        loan = Loan.objects.select_related('customer').get(pk=loan_id)
        customer = loan.customer

        # Calculate monthly installment (EMI)
        P = loan.loan_amount
        R = loan.interest_rate / (12 * 100)
        N = loan.tenure
        monthly_installment = (P * R * (1 + R)**N) / ((1 + R)**N - 1)
        monthly_installment = round(monthly_installment, 2)

        data = {
            "loan_id": loan.loan_id,
            "customer": {
                "customer_id": customer.customer_id,
                "first_name": customer.first_name,
                "last_name": customer.last_name,
                "phone_number": customer.phone_number,
                "age": customer.age
            },
            "loan_amount": loan.loan_amount,
            "interest_rate": loan.interest_rate,
            "monthly_installment": monthly_installment,
            "tenure": loan.tenure
        }
        return Response(data, status=status.HTTP_200_OK)

    except Loan.DoesNotExist:
        return Response({"error": "Loan not found"}, status=status.HTTP_404_NOT_FOUND)
    

@api_view(['GET'])
def view_loans_by_customer(request, customer_id):
    try:
        loans = Loan.objects.filter(customer_id=customer_id)

        if not loans.exists():
            return Response({"error": "No loans found for this customer."}, status=status.HTTP_404_NOT_FOUND)

        result = []

        for loan in loans:
            # EMI Calculation
            P = loan.loan_amount
            R = loan.interest_rate / (12 * 100)  # monthly interest
            N = loan.tenure

            monthly_installment = (P * R * (1 + R)**N) / ((1 + R)**N - 1)
            monthly_installment = round(monthly_installment, 2)

            # Calculate EMIs left
            if loan.start_date:
                today = datetime.today().date()
                months_elapsed = (today.year - loan.start_date.year) * 12 + (today.month - loan.start_date.month)
                repayments_left = max(0, loan.tenure - months_elapsed)
            else:
                repayments_left = loan.tenure  # fallback

            result.append({
                "loan_id": loan.loan_id,
                "loan_amount": loan.loan_amount,
                "interest_rate": loan.interest_rate,
                "monthly_installment": monthly_installment,
                "repayments_left": repayments_left
            })

        return Response(result, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)