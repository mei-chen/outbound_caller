import streamlit as st
import requests
import time

# Streamlit app configuration
st.set_page_config(page_title="Bulk Phone Caller", page_icon="📞")

# VAPI and Twilio credentials - these should be stored securely
VAPI_API_KEY = st.secrets["VAPI_API_KEY"]
VAPI_ASSISTANT_ID = st.secrets["VAPI_ASSISTANT_ID"]
TWILIO_ACCOUNT_SID = st.secrets["TWILIO_ACCOUNT_SID"]
TWILIO_AUTH_TOKEN = st.secrets["TWILIO_AUTH_TOKEN"]
TWILIO_PHONE_NUMBER = st.secrets["TWILIO_PHONE_NUMBER"]

def validate_phone_number(phone):
    """Basic phone number validation"""
    # Remove any spaces, dashes, or parentheses
    cleaned = ''.join(filter(str.isdigit, phone))
    return len(cleaned) >= 10

def make_call(to_number, first_message="Hey am I speaking with Mei?"):
    """Make a phone call using VAPI"""
    try:
        response = requests.post(
            "https://api.vapi.ai/call",
            headers={
                "Authorization": f"Bearer {VAPI_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "assistantId": VAPI_ASSISTANT_ID,
                "customer": {
                    "number": to_number
                },
                "phoneNumber": {
                    "twilioAccountSid": TWILIO_ACCOUNT_SID,
                    "twilioAuthToken": TWILIO_AUTH_TOKEN,
                    "twilioPhoneNumber": TWILIO_PHONE_NUMBER
                },
                "assistantOverrides": {
                    "firstMessage": first_message
                }
            }
        )
        
        # Consider both 200 and 201 as success codes
        if response.status_code in [200, 201]:
            return True, response.json()
        else:
            return False, f"API Error: {response.status_code} - {response.text}"
            
    except Exception as e:
        return False, str(e)

def main():
    st.title("📞 Outbound Phone caller")
    st.write("Enter phone numbers (one per line) to make calls")

    # Text area for phone numbers input
    phone_numbers = st.text_area(
        "Phone Numbers",
        placeholder="Enter phone numbers (one per line)\nExample:\n+14163128929\n+14162326807",
        height=200
    )

    # Optional first message override
    first_message = st.text_input(
        "Custom First Message",
        value="Hey I'm Sam calling from Dr. Carlos Yu's office. Do you have a moment to speak??",
        help="This is the first message the AI assistant will say"
    )

    if st.button("Make Calls"):
        if not phone_numbers.strip():
            st.warning("Please enter at least one phone number")
            return

        numbers_list = phone_numbers.strip().split('\n')
        progress_bar = st.progress(0)
        status_container = st.empty()

        for idx, number in enumerate(numbers_list):
            number = number.strip()
            if not validate_phone_number(number):
                st.error(f"Invalid phone number format: {number}")
                continue

            status_container.info(f"Initiating call to {number}...")
            success, result = make_call(number, first_message)

            if success:
                st.success(f"Successfully initiated call to {number}")
                st.json(result)
            else:
                st.error(f"Failed to call {number}: {result}")

            # Update progress bar
            progress_bar.progress((idx + 1) / len(numbers_list))
            time.sleep(1)  # Add delay to prevent hitting rate limits

        status_container.success("All calls completed!")

if __name__ == "__main__":
    main()
