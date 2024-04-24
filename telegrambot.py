import websocket
import json
import requests

# Constants for the Telegram
BOT_TOKEN = '6994076837:AAF7P8aVloqIEqJzF21apxDYoDLkN7nE5II'  #
CHAT_ID = '4006071179'  # Replace with your chat ID


def send_telegram_message(message):
  """
    Send a message to a Telegram chat via bot.
    """
  url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
  data = {'chat_id': CHAT_ID, 'text': message}
  try:
    response = requests.post(url, data=data)
    response.raise_for_status()
  except requests.exceptions.RequestException as e:
    print(f"Error sending message: {e}")


def on_message(ws, message):
  """
    Callback function that processes received messages from the websocket.
    """
  message = json.loads(message)
  if 'e' in message and message['e'] == 'trade':
    price = float(message['p'])
    quantity = float(message['q'])
    is_buyer_maker = message[
        'm']  # False if the buyer is the taker (buy order), True if the seller is the maker (sell order)

    # Define what you consider a "whale" transaction; here we assume any trade over 5 BTC
    whale_threshold = 5.0
    if not is_buyer_maker and quantity >= whale_threshold:
      alert_message = f"🐋 BUY WHALE DETECTED [{quantity:.2f}] BTC at price {price}"
      print(alert_message)
      send_telegram_message(alert_message)
    elif is_buyer_maker and quantity >= whale_threshold:
      alert_message = f"🐋 SELL WHALE DETECTED [{quantity:.2f}] BTC at price {price}"
      print(alert_message)
      send_telegram_message(alert_message)


def on_error(ws, error):
  print("Error:", error)


def on_close(ws, close_status_code, close_msg):
  print("### Connection Closed ###")
  print("Code:", close_status_code)
  print("Message:", close_msg)


def on_open(ws):
  print("Connection Opened")
  # Subscribe to trade messages for BTCUSDT
  ws.send(
      json.dumps({
          'method': 'SUBSCRIBE',
          'params': ['btcusdt@trade'],
          'id': 1
      }))


def run_websocket():
  # WebSocket URL for Binance
  ws_url = "wss://stream.binance.com:9443/ws"
  ws = websocket.WebSocketApp(ws_url,
                              on_open=on_open,
                              on_message=on_message,
                              on_error=on_error,
                              on_close=on_close)
  ws.run_forever()


if __name__ == "__main__":
  run_websocket()
