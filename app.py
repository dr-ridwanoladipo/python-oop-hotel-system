import pandas as pd
import streamlit as st
from datetime import datetime

# Load data from CSV files
df = pd.read_csv("hotels.csv", dtype={"id": str})
df_cards = pd.read_csv("cards.csv", dtype=str).to_dict(orient="records")
df_cards_security = pd.read_csv("card_security.csv", dtype=str)


class Hotel:
    """Base class for hotel objects"""
    def __init__(self, hotel_id):
        self.hotel_id = hotel_id
        self.name = df.loc[df["id"] == self.hotel_id, "name"].squeeze()

    def book(self):
        """Mark the hotel as booked in the dataframe"""
        df.loc[df["id"] == self.hotel_id, "available"] = "no"
        df.to_csv("hotels.csv", index=False)

    def available(self):
        """Check if the hotel is available"""
        availability = df.loc[df["id"] == self.hotel_id, "available"].squeeze()
        return availability == "yes"


class SpaHotel(Hotel):
    """Subclass of Hotel with spa package booking functionality"""
    def book_spa_package(self):
        pass  # Implement spa package booking logic here


class ReservationTicket:
    """Generate a reservation ticket for a hotel booking"""
    def __init__(self, customer_name, hotel_object):
        self.customer_name = customer_name
        self.hotel = hotel_object

    def generate(self):
        return f"""
        Thank you for your reservation!
        Here are your booking data:
        Name: {self.customer_name}
        Hotel name: {self.hotel.name}
        """


class SpaTicket:
    """Generate a ticket for a spa package booking"""
    def __init__(self, customer_name, hotel_object):
        self.customer_name = customer_name
        self.hotel = hotel_object

    def generate(self):
        return f"""
        Thank you for your SPA reservation!
        Here are you SPA booking data:
        Name: {self.customer_name}
        Hotel name: {self.hotel.name}
        """


class CreditCard:
    """Base class for credit card validation"""
    def __init__(self, number):
        self.number = number

    def validate(self, expiration, holder, cvc):
        card_data = {"number": self.number, "expiration": expiration,
                     "holder": holder, "cvc": cvc}
        return card_data in df_cards


class SecureCreditCard(CreditCard):
    """Subclass of CreditCard with additional authentication"""
    def authenticate(self, given_password):
        password = df_cards_security.loc[df_cards_security["number"] == self.number, "password"].squeeze()
        return password == given_password


class HotelUI:
    """Main class for the Streamlit user interface"""
    def __init__(self):
        st.set_page_config(page_title="Hotel Booking App", page_icon="🏨", layout="wide")
        st.title("🏨 Hotel Booking System")

    def run(self):
        """Run the main Streamlit application"""
        st.sidebar.header("Navigation")
        page = st.sidebar.radio("Go to", ["Available Hotels", "Book a Hotel", "About"])

        if page == "Available Hotels":
            self.show_available_hotels()
        elif page == "Book a Hotel":
            self.book_hotel()
        else:
            self.show_about()

    def show_available_hotels(self):
        """Display a list of available hotels"""
        st.header("Available Hotels")
        available_hotels = df[df["available"] == "yes"]
        st.dataframe(available_hotels[["id", "name", "city", "price"]])

    def book_hotel(self):
        """Handle the hotel booking process"""
        st.header("Book a Hotel")
        hotel_id = st.selectbox("Select a hotel", df[df["available"] == "yes"]["id"].tolist(),
                                format_func=lambda x: f"{x} - {df.loc[df['id'] == x, 'name'].squeeze()}")

        if hotel_id:
            hotel = SpaHotel(hotel_id)
            st.write(f"You selected: {hotel.name}")

            # Collect user information and payment details
            name = st.text_input("Enter your name")
            card_number = st.text_input("Enter your credit card number")
            card_expiration = st.text_input("Enter card expiration date (MM/YY)")
            card_holder = st.text_input("Enter card holder name")
            card_cvc = st.text_input("Enter card CVC")
            card_password = st.text_input("Enter card password", type="password")

            if st.button("Book Hotel"):
                credit_card = SecureCreditCard(number=card_number)
                if credit_card.validate(expiration=card_expiration, holder=card_holder, cvc=card_cvc):
                    if credit_card.authenticate(given_password=card_password):
                        hotel.book()
                        reservation_ticket = ReservationTicket(customer_name=name, hotel_object=hotel)
                        st.success(reservation_ticket.generate())

                        # Optional spa package booking
                        if st.checkbox("Book a spa package"):
                            hotel.book_spa_package()
                            spa_ticket = SpaTicket(customer_name=name, hotel_object=hotel)
                            st.success(spa_ticket.generate())
                    else:
                        st.error("Credit card authentication failed.")
                else:
                    st.error("There was a problem with your payment")

    def show_about(self):
        """Display information about the Hotel Booking System"""
        st.header("About Hotel Booking System")
        st.write("""
        Welcome to our Hotel Booking System! This application allows you to:
        - View available hotels
        - Book a hotel room
        - Add a spa package to your booking

        We hope you enjoy your stay!
        """)


if __name__ == "__main__":
    ui = HotelUI()
    ui.run()