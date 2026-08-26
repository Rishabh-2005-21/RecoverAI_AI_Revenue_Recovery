import os
import random
from datetime import datetime
from typing import Dict, Any, List

# Try importing gTTS for optional voice audio generation
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

AUDIO_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "audio")

def generate_hinglish_script(event: Dict[str, Any], action_type: str = "payment_reminder") -> Dict[str, Any]:
    """
    Generates a personalized Hinglish voice script and dialog flow for AI Voice Call recovery.
    """
    cust = event.get("customer") or {}
    cust_name = cust.get("name", "Valued Customer").split()[0]
    amount = float(event.get("amount", 0.0))
    formatted_amount = f"₹{amount:,.0f}"
    category = event.get("category", "payment_failure")
    items = event.get("cart_items") or ["your items"]
    item_str = ", ".join(items)

    if category == "cart_abandonment":
        greeting = f"Namaste {cust_name} ji! Main RecoverAI Assistant bol raha hoon."
        opening = f"Aapne aapke cart mein {item_str} add kiya tha par checkout complete nahi ho paya ({formatted_amount})."
        pitch = "Kya aapko checkout karne mein koi payment issue aa rahi hai? Aaj hum standard 5% instant UPI cashback code offer kar rahe hain!"
        cta = "Main abhi aapke WhatsApp par direct 1-click Razorpay UPI Payment Link bhej deta hoon."
    elif category == "failed_subscription":
        greeting = f"Hello {cust_name} ji, hope you are doing well!"
        opening = f"Aapka {formatted_amount} ka auto-subscription payment decline ho gaya hai."
        pitch = "Bank security rules ki wajah se mandate update ki zaroorat pad sakti hai."
        cta = "Kya main aapke mobile pe 1-click Card/UPI Update portal link WhatsApp kar doon?"
    elif category == "b2b_receivable":
        greeting = f"Namaste {cust_name} ji, good morning from Accounts & Finance Team."
        opening = f"Aapke account par Invoice #{event.get('invoice_id', 'INV-102')} for {formatted_amount} overdue chal raha hai."
        pitch = "Kya hum is payment ke liye koi specific Promise-to-Pay (P2P) date fix kar sakte hain, so overall account credit clear rahe?"
        cta = "Aap kab tak payment process kar payenge — kal 12 Baje tak ya Monday tak?"
    else:
        greeting = f"Namaste {cust_name} ji!"
        opening = f"Aapka recent payment request of {formatted_amount} attempt approve nahi ho paya."
        pitch = "Network issue ki wajah se transaction timeout ho gaya tha. Pareshan hone ki koi baat nahi hai."
        cta = "Aap abhi humare direct Razorpay UPI link se securely pay kar sakte hain."

    dialog_turns = [
        {"speaker": "AI Voice Agent", "text": greeting + " " + opening},
        {"speaker": "Customer (Simulated)", "text": "Haan, main payment karna chahta hoon par kal bank server down tha."},
        {"speaker": "AI Voice Agent", "text": pitch + " " + cta},
        {"speaker": "Customer (Simulated)", "text": "Ji bilkul, mere WhatsApp pe payment link bhej dijiye, main abhi UPI se pay kar deta hoon."},
        {"speaker": "AI Voice Agent", "text": f"Bahut badiya {cust_name} ji! Link generate ho gaya hai aur aapke WhatsApp no pe bhej diya gaya hai. Thank you!"}
    ]

    full_transcript = " ".join([t["text"] for t in dialog_turns if t["speaker"] == "AI Voice Agent"])

    # Generate real MP3 file if gTTS is available
    audio_path = None
    if GTTS_AVAILABLE:
        try:
            os.makedirs(AUDIO_DIR, exist_ok=True)
            filename = f"call_{event.get('event_id', 'demo')}.mp3"
            filepath = os.path.join(AUDIO_DIR, filename)
            if not os.path.exists(filepath):
                tts = gTTS(text=greeting + " " + opening + " " + pitch + " " + cta, lang="hi")
                tts.save(filepath)
            audio_path = filepath
        except Exception:
            audio_path = None

    return {
        "event_id": event.get("event_id"),
        "customer_name": cust_name,
        "language": "Hinglish",
        "greeting": greeting,
        "full_script": full_transcript,
        "dialog_turns": dialog_turns,
        "audio_file_path": audio_path,
        "call_status": "completed",
        "duration_seconds": 38,
        "sentiment": "positive",
        "outcome": "P2P_AGREED_UPI_SENT"
    }

def simulate_interactive_objection(objection_type: str, cust_name: str, amount: float) -> Dict[str, str]:
    """
    Handles live dynamic objections during UI voice call simulation.
    """
    formatted_amount = f"₹{amount:,.0f}"
    
    if objection_type == "will_pay_tomorrow":
        return {
            "customer": "Main abhi thoda busy hoon, main kal shaam tak pay kar doonga.",
            "agent": f"Koyi baat nahi {cust_name} ji! Main aapka Promise-to-Pay kal shaam 6:00 PM tak record kar leta hoon. Reminder link WhatsApp pe rahega."
        }
    elif objection_type == "discount_request":
        return {
            "customer": "Kya isme thoda discount mil sakta hai?",
            "agent": f"Ji {cust_name} ji, humne abhi instant 5% cashback auto-apply kar diya hai! Naya total {f'₹{amount*0.95:,.0f}'} hai."
        }
    elif objection_type == "wrong_invoice":
        return {
            "customer": "Yeh invoice amount galat lag raha hai.",
            "agent": f"Samajh gaya {cust_name} ji. Main is invoice ko review ke liye hold pe dal ke humari finance team ko audit tag bhej deta hoon."
        }
    else: # upi_request
        return {
            "customer": "Kya main PhonePe / Google Pay UPI se kar sakta hoon?",
            "agent": f"Ji bilkul! 1-click Razorpay link saare UPI Apps (GPay, PhonePe, Paytm, BHIM) support karta hai."
        }
