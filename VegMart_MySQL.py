import mysql.connector as db
from tabulate import tabulate
from datetime import datetime
import pandas as pd
from matplotlib import pyplot as pt
from sqlalchemy import create_engine as ce
class VegetableOwner:
    cart={}
    def __init__(self):
        self.conn = db.connect(
            host="localhost",
            user="root",           
            password="$1234Abcd",
            database="inventory1"
        )
        self.cur = self.conn.cursor()
    # Add a new vegetable to the inventory
    def add_vegetable(self):
        vname = input("Please enter the name of the vegetable you would like to add: ")#.strip().lower().title()
        vname.strip().lower().title()
        self.cur.execute("SELECT VEG_NAME FROM VEGETABLE WHERE VEG_NAME = %s", (vname,))
        if self.cur.fetchone():
            print(f"'{vname}' already exists in the database. Cannot insert duplicates.")
        else:
            try:
                vquant = float(input("Please specify the quantity of the vegetable you wish to add: "))
                sprice = float(input(f"Please enter the selling price for {vname}: "))
                cprice = float(input(f"Please enter the cost price for {vname}: "))
            except ValueError:
                print("It seems you may have entered incorrect values.\
                    Please review your input and ensure it is accurate before trying again.")
            except Exception as e:
                print(f"Operation failed due to an error. Please check and retry. \n{e}")
            else:
                self.cur.execute("INSERT INTO VEGETABLE (VEG_NAME, QUANTITY, SELLING_PRICE, COST_PRICE) VALUES (%s, %s, %s, %s)",
                                (vname, vquant, sprice, cprice))
                self.conn.commit()
                print(f"'{vname}' added successfully.")
    # Display all vegetables available in the inventory
    def view_vegetables(self):
        self.cur.execute("SELECT * FROM VEGETABLE")
        data = self.cur.fetchall()
        column_name=[i[0] for i in self.cur.description]
        print(tabulate(data,headers=column_name,tablefmt="fancy_grid"))
    # Update details (quantity/price) of an existing vegetable
    def update_vegetable(self):
        vname = input("Please enter the name of the vegetable you would like to add: ").strip().lower().title()
        self.cur.execute("SELECT VEG_NAME FROM VEGETABLE WHERE VEG_NAME = %s", (vname,))
        if self.cur.fetchone():
            try:
                vquant = float(input("Please specify the quantity of the vegetable you wish to add: "))
                sprice = float(input(f"Please enter the selling price for {vname}: "))
                cprice = float(input(f"Please enter the cost price for {vname}: "))
            except ValueError:
                print("It seems you may have entered incorrect values.\
                    Please review your input and ensure it is accurate before trying again.")
            except Exception as e:
                print(f"Operation failed due to an error. Please check and retry. \n{e}")
            else:
                self.cur.execute("SELECT QUANTITY FROM VEGETABLE WHERE VEG_NAME=%s",(vname,))
                vq=self.cur.fetchone()[0]
                newq=float(vq)+vquant
                self.cur.execute("UPDATE VEGETABLE SET QUANTITY = %s WHERE VEG_NAME = %s",(newq,vname))
                self.cur.execute("UPDATE VEGETABLE SET SELLING_PRICE= %s WHERE VEG_NAME=%s",(sprice,vname))
                self.cur.execute("UPDATE VEGETABLE SET COST_PRICE= %s WHERE VEG_NAME=%s",(cprice,vname))
                self.conn.commit()
                print(f"{vname} updated!")
        else:
            print(f"{vname} does not exists.")
    # Remove a vegetable from the inventory
    def delete_vegetable(self):
        vname = input("Please enter the name of the vegetable you would like to add: ").strip().lower().title()
        self.cur.execute("SELECT VEG_NAME FROM VEGETABLE WHERE VEG_NAME = %s", (vname,))
        if self.cur.fetchone():
            self.cur.execute("DELETE FROM VEGETABLE WHERE VEG_NAME = %s", (vname,))
            self.conn.commit()
            print(f"{vname} deleted!")
        else:
            print(f"{vname} does not exists")
    # Display the list of all registered customers
    def view_user_details(self):
        self.cur.execute("SELECT * FROM CUSTOMER")
        data = self.cur.fetchall()
        columns = [i[0] for i in self.cur.description]
        print("Displaying all registered customer details:\n")
        print(tabulate(data, headers=columns, tablefmt="fancy_grid"))
    # Show daily sales report for a specific date
    def view_report(self):
        from datetime import datetime as dt
        t_date=input("Enter the date to view report (dd/mm/yyy): ").strip()
        try:
            format_date=dt.strptime(t_date, "%d/%m/%Y").date()
        except  ValueError:
            print("Invalid date format. Please enter the date as dd/mm/yyyy.")
        except Exception as e:
            print(f"Something went wrong while generating the report: \n{e}")
        else:
            self.cur.callproc('DisplaySales',(format_date,))
            for result in self.cur.stored_results():
                data = result.fetchall()
                columns = [desc[0] for desc in result.description]
                print("\nSales Report:\n")
                print(tabulate(data, headers=columns, tablefmt="fancy_grid"))
            self.cur.execute("SELECT FindProfit(%s)", (format_date,))
            amount = self.cur.fetchone()[0]
            print(f"\nThe profit gained on {format_date.strftime('%d-%m-%Y')} is ₹{amount:.2f}")
    # To represent data in visualization
    def represent_report(self):
        username = 'root'
        password = '$1234Abcd'
        host = 'localhost'
        port = '3306'
        database = 'inventory1'
        # Create database connection string
        engine = ce(f'mysql+mysqlconnector://{username}:{password}@{host}:{port}/{database}')
        # Read data from a table
        df1 = pd.read_sql('SELECT DATE_ID,PROFIT FROM PROFITS', con=engine)
        df2 = pd.read_sql('SELECT * FROM DATES', con=engine)
        # Aggregate profits by DATE_ID
        profit_summary=df1.groupby('DATE_ID', as_index=False)['PROFIT'].sum()
        # Merge with df2 to get actual dates (assuming df2 has 'DATE_ID' and 'DATE' columns)
        merged_df = profit_summary.merge(df2, on='DATE_ID')
        merged_df=merged_df.sort_values(by='PURCHASE_DATE')
        # Plotting
        merged_df.plot(x='PURCHASE_DATE', y='PROFIT', kind='line', marker='o')
        pt.xlabel('Date')
        pt.ylabel('Total Profit')
        pt.title('Profit Over Time')
        pt.show()

    # Display today's profit summary and exit the application
    def exit(self):
        try:
            self.cur.callproc('DisplayTodaySales')
            for result in self.cur.stored_results():
                data = result.fetchall()
                columns = [desc[0] for desc in result.description]
                print("\nToday's Sales Report:\n")
                print(tabulate(data, headers=columns, tablefmt="fancy_grid"))
            self.cur.execute("SELECT FindTodayProfit()")
            amount = self.cur.fetchone()[0]
            print(f"\nThe total profit gained today is ₹{amount:.2f}")
        except Exception as e:
            print(f"An error occurred while exiting and displaying the report: \n{e}")
        finally:
            print("\nThank you for using VegMart. See you again!")
    # Add a selected vegetable to the customer's cart
    def add_to_cart(self):
        vname=input("Please enter the name of the vegetable you would like to buy: ").strip().lower().title()
        self.cur.execute("SELECT VEG_NAME FROM VEGETABLE WHERE VEG_NAME = %s", (vname,))
        if self.cur.fetchone():
            try:
                vquant = float(input("Please enter the quantity of the vegetable you wish to add (in KG): "))
            except ValueError:
                print("It seems you may have entered incorrect values.\
                    Please review your input and ensure it is accurate before trying again.")
            except Exception as e:
                print(f"Operation failed due to an error. Please check and retry. \n{e}")
            else:
                self.cur.execute("SELECT QUANTITY FROM VEGETABLE WHERE VEG_NAME=%s",(vname,))
                available_quantity = self.cur.fetchone()[0]
                if available_quantity>=vquant:
                    self.cur.execute("SELECT SELLING_PRICE FROM VEGETABLE WHERE VEG_NAME=%s",(vname,))
                    price=self.cur.fetchone()[0]
                    if vname in VegetableOwner.cart:
                        VegetableOwner.cart[vname][0] = vquant
                        VegetableOwner.cart[vname][1] = vquant*float(price)
                    else:
                        VegetableOwner.cart[vname] = [vquant, vquant*float(price)]
                    print(f"{vname} has been successfully added to the cart.")
                else:
                     print(f"Sorry, only {available_quantity} kg of {vname} is available in stock.")
        else:
             print(f"Sorry, {vname} is not available in our inventory.")
    # Remove a vegetable from the cart
    def remove_from_cart(self):
        vname = input("Please enter the name of the vegetable you would like to remove from your cart: ").strip().lower().title()
        if vname in VegetableOwner.cart:
            del VegetableOwner.cart[vname]
            print(f"{vname} has been successfully removed from your cart.")
        else:
            print(f"{vname} is not present in your cart.")
    # Change the quantity of a vegetable in the cart
    def modify_cart(self):
        vname = input("Enter the name of the vegetable you want to modify in your cart: ").strip().lower().title()

        if vname in VegetableOwner.cart:
            try:
                vquant = float(input("Please enter the quantity of the vegetable you wish to add (in KG): "))
            except ValueError:
                print("Invalid input. Please enter a numeric value for quantity.")
            except Exception as e:
                print(f"An unexpected error occurred. Please try again. \n{e}")
            else:
                self.cur.execute("SELECT QUANTITY FROM VEGETABLE WHERE VEG_NAME = %s", (vname,))
                available_quantity = self.cur.fetchone()[0]
                if available_quantity >= vquant:
                    self.cur.execute("SELECT SELLING_PRICE FROM VEGETABLE WHERE VEG_NAME = %s", (vname,))
                    price = self.cur.fetchone()[0]
                    VegetableOwner.cart[vname][0] = vquant
                    VegetableOwner.cart[vname][1] = round(vquant * float(price), 2)
                    print(f"The quantity of {vname} in your cart has been updated to {vquant} kg.")
                else:
                    print(f"Insufficient stock. Only {available_quantity} kg of {vname} is currently available.")
        else:
            print(f"{vname} is not found in your cart.")
    # Show all items currently in the customer's cart
    def view_cart(self):
        if not VegetableOwner.cart:
            print("Your cart is currently empty.")
            return
        print("\nItems in your cart:\n")
        headers = ["Vegetable", "Quantity (kg)", "Total Price (₹)"]
        data = [[veg, details[0], details[1]] for veg, details in VegetableOwner.cart.items()]
        print(tabulate(data, headers=headers, tablefmt="fancy_grid"))
    # Generate bill, update stock, store profits, and clear cart
    def billing(self):
        if not VegetableOwner.cart:
            print("Your cart is empty. Please add items before billing.")
            return
        while True:
            try:
                mobile = int(input("Enter your mobile number: "))
            except ValueError:
                print("Input must be numeric.")
                return
            except Exception as e:
                print(f"Something went wrong. \n{e}")
                return
            if len(str(mobile)) == 10:
                break
            else:
                print("The mobile number must be exactly 10 digits.")
        # Check if customer exists
        self.cur.execute("SELECT FindCustomer(%s)", (mobile,))
        is_existing = self.cur.fetchone()[0]
        if is_existing<1:
            try:
                name = input("Please enter your name: ").strip().lower().title()
            except Exception as e:
                print(f"Something went wrong while taking name. \n{e}")
                return
        else:
            name = None  # Existing customer, name not needed
        # Get today's DATE_ID or prepare to insert after billing
        self.cur.execute("SELECT DATE_ID FROM DATES WHERE PURCHASE_DATE = CURDATE()")
        date_result = self.cur.fetchone()
        date_id = None
        insert_today_date = False
        if date_result:
            date_id = date_result[0]
        else:
            insert_today_date = True  # Insert after billing
        print("\n----- BILL RECEIPT -----")
        print(f"Customer Mobile: {mobile}")
        print(f"Date: {datetime.today().strftime('%d-%m-%Y')}")
        print("\nItems Purchased:")
        bill_data = []
        total = 0.0
        try:
            for veg, details in VegetableOwner.cart.items():
                quantity_sold = details[0]
                self.cur.execute("SELECT VEG_ID, COST_PRICE, SELLING_PRICE, QUANTITY FROM VEGETABLE WHERE VEG_NAME = %s", (veg,))
                veg_id, cost_price, selling_price, available_qty = self.cur.fetchone()
                if quantity_sold > available_qty:
                    print(f"Insufficient stock for {veg}. Only {available_qty} kg available.")
                    return
                profit = (float(selling_price) - float(cost_price)) * quantity_sold
                new_qty = float(available_qty) - quantity_sold
                price = float(selling_price) * quantity_sold
                total += price
                # Update stock
                self.cur.execute("UPDATE VEGETABLE SET QUANTITY = %s WHERE VEG_ID = %s", (new_qty, veg_id))
                # Delay profit insertion until DATE_ID is confirmed
                bill_data.append({
                    "veg_id": veg_id,
                    "veg_name": veg,
                    "quantity": quantity_sold,
                    "price": price,
                    "profit": profit
                })
            # Display bill
            print(tabulate([[d["veg_name"], d["quantity"], d["price"]] for d in bill_data],
                            headers=["Vegetable", "Quantity (kg)", "Total Price (Rs.)"],
                            tablefmt="grid"))
            print(f"\nTotal Amount: Rs. {total:.2f}")
            # Insert customer after billing success
            if not is_existing:
                self.cur.execute("INSERT INTO CUSTOMER(CUSTOMER_NAME, MOBILE) VALUES (%s, %s)", (name, mobile))
            # Insert today's date if not already present
            if insert_today_date:
                self.cur.execute("INSERT INTO DATES(PURCHASE_DATE) VALUES (CURDATE())")
                self.cur.execute("SELECT DATE_ID FROM DATES WHERE PURCHASE_DATE = CURDATE()")
                date_id = self.cur.fetchone()[0]
            # Now insert profits
            for d in bill_data:
                self.cur.execute(
                    "INSERT INTO PROFITS(VEG_ID, DATE_ID, QUANTITY, PROFIT) VALUES (%s, %s, %s, %s)",
                    (d["veg_id"], date_id, d["quantity"], d["profit"])
                )
            self.conn.commit()
            print("\nThank you for shopping with us!")
            # Clear cart after billing
            VegetableOwner.cart.clear()
        except Exception as e:
            self.conn.rollback()
            print(f"Billing failed due to: \n{e}")

    def close_connection(self):
        print(f"Closing the shop.....")
        self.cur.close()
        self.conn.close()
# Main menu to navigate between admin and customer functionalities
def main():
    obj=VegetableOwner()
    user_name='User123'
    password='user678'
    print(f"Welcome")
    print(f"Let me know who are you?")
    while True:
        print("1.Owner")
        print("2.Customer")
        try:
            ask=int(input('Who are you?: '))
        except ValueError:
            print(f"Only integer values are accepted as input.")
        else:
            if ask==1:
                try:
                    user=input("Enter user name: ")
                    Pass=input("Enter Pasword: ")
                except Exception as e:
                    print(f"Something went wrong. \n{e}")
                else:
                    if user==user_name and Pass==password:
                        print('What do you want to do?')
                        print('1. Update Inventory')
                        print('2. View Inventory')
                        print('3. View User details')
                        print('4. View Report')
                        print('5. Exit')
                        try:
                            action=int(input('Which operation would you like to perform? '))
                        except ValueError:
                            print("Only integer values are accepted as input.")
                        except Exception as e:
                            print(f"Operation failed due to an error. Please check and retry. \n{e}")
                        else:
                            if 1<=action<=5:
                                if action==1:
                                    print('Select one operation')
                                    print('1. Add Vegetable')
                                    print('2. Remove Vegetable')
                                    print('3. Update Vegetable Info')
                                    try:
                                        op=int(input("Enter an option: "))
                                    except ValueError:
                                        print("Invalid input. Please enter a numeric value only.")
                                    except Exception as e:
                                        print(f"An unexpected error occurred. Please try again. \n{e}")
                                    else:
                                        if 1<=op<=3:
                                            if op==1:  
                                                obj.add_vegetable()
                                            elif op==2:
                                                obj.delete_vegetable()
                                            elif op==3:
                                                obj.update_vegetable()
                                        else:
                                            print("Invalid input. Kindly enter a number between 1 and 3.")
                                elif action==2:
                                    obj.view_vegetables()
                                elif action==3:
                                    obj.view_user_details()
                                elif action == 4:
                                    print("Please choose a report type:")
                                    print("1. Single Day Report")
                                    print("2. Overall Report")
                                    try:
                                        op = int(input("Enter your choice (1 or 2): "))
                                    except ValueError:
                                        print("Invalid input. Please enter a number.")
                                    except Exception as e:
                                        print(f"An unexpected error occurred: \n{e}")
                                    else:
                                        if op == 1:
                                            obj.view_report()
                                        elif op == 2:
                                            obj.represent_report()
                                        else:
                                            print("Invalid choice. Please enter either 1 or 2.")
                                elif action==5:
                                    obj.exit()
                                    obj.close_connection()
                                    break
                            else:
                                print("Invalid input. Kindly enter a number between 1 and 5.")
                    else:
                        print("The username or password you entered is incorrect. Please try again.")
            elif ask==2:
                while True:
                    print('Which operation would you like to perform? ')
                    print('1. Add to cart') 
                    print('2. Remove from cart')
                    print('3. Modify Cart')
                    print('4. View Cart')
                    print('5. Billing')
                    print('6. Exit')
                    try:
                        action=int(input('Which operation would you like to perform? '))
                    except ValueError:
                        print("Only integer values are accepted as input.")
                    except Exception as e:
                        print(f"An error occurred while processing your request. Please check your input and try again. \n{e}")
                    else:
                        if 1<=action<=6:
                            if action==1:
                                obj.add_to_cart()
                            elif action==2:
                                obj.remove_from_cart()
                            elif action==3:
                                obj.modify_cart()
                            elif action==4:
                                obj.view_cart()
                            elif action==5:
                                obj.billing()
                            elif action==6:
                                VegetableOwner.cart.clear()
                                print("Your cart has been cleared. Exiting Customer Mode.")
                                break
                        else:
                            print("Invalid input. Kindly enter a number between 1 and 6.")
            else:
                print("Please choose appropriate option.")
main()
