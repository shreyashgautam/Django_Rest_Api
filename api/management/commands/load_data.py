import pandas as pd
from django.core.management.base import BaseCommand
from api.models import Customer, Loan
from django.db import IntegrityError
from datetime import datetime

class Command(BaseCommand):
    help = 'Load customers and loans data from CSV files'

    def handle(self, *args, **kwargs):
        self.load_customers()
        self.load_loans()

    def load_customers(self):
        try:
            df = pd.read_csv('customer.csv')
            df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

            required_columns = [
                'customer_id', 'first_name', 'last_name', 'age',
                'phone_number', 'monthly_salary', 'approved_limit'
            ]

            missing = [col for col in required_columns if col not in df.columns]
            if missing:
                self.stderr.write(self.style.ERROR(f"Missing customer columns: {missing}"))
                return

            inserted, skipped = 0, 0

            for _, row in df.iterrows():
                try:
                    Customer.objects.update_or_create(
                        customer_id=row['customer_id'],
                        defaults={
                            'first_name': row['first_name'],
                            'last_name': row['last_name'],
                            'age': row['age'],
                            'phone_number': row['phone_number'],
                            'monthly_income': row['monthly_salary'],
                            'approved_limit': row['approved_limit'],
                            'current_debt': 0  # set default
                        }
                    )
                    inserted += 1
                except Exception as e:
                    self.stderr.write(self.style.ERROR(
                        f"Error processing customer row {row.to_dict()}: {e}"))
                    skipped += 1

            self.stdout.write(self.style.SUCCESS(
                f"✅ Loaded Customers: Inserted/Updated {inserted}, Skipped {skipped}"))

        except FileNotFoundError:
            self.stderr.write(self.style.ERROR("❌ File 'customers.csv' not found"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Unexpected customer load error: {e}"))

    def load_loans(self):
        try:
            df = pd.read_csv('loan.csv')
            df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

            required_columns = [
                'customer_id', 'loan_id', 'loan_amount', 'tenure',
                'interest_rate', 'monthly_payment', 'emis_paid_on_time',
                'start_date', 'end_date'
            ]

            missing = [col for col in required_columns if col not in df.columns]
            if missing:
                self.stderr.write(self.style.ERROR(f"Missing loan columns: {missing}"))
                return

            inserted, skipped = 0, 0

            for _, row in df.iterrows():
                try:
                    customer = Customer.objects.get(customer_id=row['customer_id'])

                    Loan.objects.update_or_create(
                        loan_id=row['loan_id'],
                        defaults={
                            'customer': customer,
                            'loan_amount': row['loan_amount'],
                            'tenure': row['tenure'],
                            'interest_rate': row['interest_rate'],
                            'monthly_payment': row['monthly_payment'],
                            'emis_paid_on_time': row['emis_paid_on_time'],
                            'start_date': pd.to_datetime(row['start_date']).date(),
                            'end_date': pd.to_datetime(row['end_date']).date()
                        }
                    )
                    inserted += 1

                except Customer.DoesNotExist:
                    self.stderr.write(self.style.WARNING(
                        f"⚠️ Customer ID {row['customer_id']} not found. Skipping Loan ID {row['loan_id']}"))
                    skipped += 1
                except IntegrityError as e:
                    self.stderr.write(self.style.WARNING(
                        f"⚠️ Loan ID {row['loan_id']} error: {e}"))
                    skipped += 1
                except Exception as e:
                    self.stderr.write(self.style.ERROR(
                        f"❌ Error processing loan row {row.to_dict()}: {e}"))
                    skipped += 1

            self.stdout.write(self.style.SUCCESS(
                f"✅ Loaded Loans: Inserted/Updated {inserted}, Skipped {skipped}"))

        except FileNotFoundError:
            self.stderr.write(self.style.ERROR("❌ File 'loans.csv' not found"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Unexpected loan load error: {e}"))
